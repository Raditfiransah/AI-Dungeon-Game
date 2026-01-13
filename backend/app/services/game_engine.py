import json
import time
from openai import OpenAI
from typing import Dict, Any, List
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    base_url=settings.OPENAI_BASE_URL
)

# Strict System Prompt - JSON only, no hallucination
SYSTEM_PROMPT = """### ROLE
You are a strict Dungeon Master for a text-based RPG called "AI Dungeon". 
You are NOT a helpful assistant. You are a narrator who controls the story.

### CRITICAL RULES
1. Output ONLY valid JSON. No markdown (```), no intro text, no explanations.
2. You control the STORY only. You do NOT decide final HP values.
3. Keep narratives SHORT (2-3 sentences max). Be atmospheric and punchy.
4. Always provide EXACTLY 3 choices in order: [Positive/Safe, Neutral, Negative/Risky]
5. If player tries impossible things, narrate failure with consequences.
6. Combat: Be fair. Enemies fight back. Set damage accordingly.
7. If damage would kill player (hp + damage <= 0), set game_over: true.

### JSON OUTPUT FORMAT
{{
  "narrative": "String. What happens (2-3 sentences).",
  "damage": Integer. Damage to player (positive number or 0),
  "heal": Integer. Healing for player (positive number or 0),
  "gain_item": "String or null. Item name if player gains something.",
  "lose_item": "String or null. Item name if player loses/uses something.",
  "new_location": "String or null. Only if player moves to new area.",
  "choices": ["Positive choice", "Neutral choice", "Risky choice"],
  "game_over": Boolean. True only if player dies or wins.,
  "exp_gain": Integer. Experience points gained (0-50).,
  "event_trigger": "String or null. Special event code like BOSS_DEFEATED, QUEST_COMPLETE."
}}

### CURRENT STATE
- Player HP: {hp}/{max_hp}
- Level: {level} (EXP: {exp})
- Inventory: {inventory}
- Location: {location}
- Story Summary: {summary}
"""


def build_context(session: Dict[str, Any], messages: List[Dict], action: str) -> List[Dict]:
    """Build context for AI with sliding window + summary"""
    
    # Format system prompt with current state
    system_content = SYSTEM_PROMPT.format(
        hp=session["hp"],
        max_hp=session["max_hp"],
        level=session["level"],
        exp=session["exp"],
        inventory=", ".join(session["inventory"]) if session["inventory"] else "Empty",
        location=session["location"],
        summary=session["summary"] or "You just started your adventure."
    )
    
    # Build conversation history (sliding window - last N messages)
    conversation = [{"role": "system", "content": system_content}]
    
    for msg in messages:
        conversation.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current action
    conversation.append({"role": "user", "content": action})
    
    return conversation


def process_action(action: str, session: Dict[str, Any], 
                   recent_messages: List[Dict]) -> Dict[str, Any]:
    """Process player action with LLM and return structured result"""
    
    # Build context with sliding window
    messages = build_context(session, recent_messages, action)
    
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        tokens_used = response.usage.total_tokens if response.usage else None
        
        # Parse response
        llm_output = response.choices[0].message.content
        result = json.loads(llm_output)
        
        # Validate and set defaults
        result.setdefault("narrative", "Something mysterious happens...")
        result.setdefault("damage", 0)
        result.setdefault("heal", 0)
        result.setdefault("gain_item", None)
        result.setdefault("lose_item", None)
        result.setdefault("new_location", None)
        result.setdefault("game_over", False)
        result.setdefault("exp_gain", 0)
        result.setdefault("event_trigger", None)
        
        # Ensure choices is valid
        if not isinstance(result.get("choices"), list) or len(result.get("choices", [])) != 3:
            result["choices"] = ["Continue exploring", "Look around", "Rest"]
        
        # Add metadata
        result["latency_ms"] = latency_ms
        result["tokens_used"] = tokens_used
        result["model_name"] = settings.OPENAI_MODEL
        
        return result
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {
            "narrative": "The world flickers... Something went wrong.",
            "damage": 0,
            "heal": 0,
            "gain_item": None,
            "lose_item": None,
            "new_location": None,
            "choices": ["Try again", "Look around", "Wait"],
            "game_over": False,
            "exp_gain": 0,
            "event_trigger": None,
            "latency_ms": 0,
            "tokens_used": 0,
            "model_name": settings.OPENAI_MODEL
        }


def generate_summary(messages: List[Dict]) -> str:
    """Generate a summary of old messages for long-term memory"""
    
    summary_prompt = """Summarize this RPG conversation history in 2-3 sentences. 
    Focus on: key events, items found, enemies defeated, current quest progress.
    Be concise. Output plain text only, no JSON."""
    
    conversation = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": "\n".join([f"{m['role']}: {m['content']}" for m in messages])}
    ]
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=conversation,
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "The adventure continues..."


def calculate_new_hp(current_hp: int, max_hp: int, damage: int, heal: int) -> int:
    """Calculate new HP with clamping"""
    new_hp = current_hp - damage + heal
    return max(0, min(max_hp, new_hp))


def apply_inventory_changes(inventory: List[str], gain: str = None, lose: str = None) -> List[str]:
    """Apply inventory changes"""
    new_inventory = inventory.copy()
    
    if gain:
        new_inventory.append(gain)
    
    if lose and lose in new_inventory:
        new_inventory.remove(lose)
    
    return new_inventory


def calculate_level_up(current_level: int, current_exp: int, exp_gain: int) -> tuple:
    """Calculate level progression. Returns (new_level, new_exp)"""
    new_exp = current_exp + exp_gain
    new_level = current_level
    
    # Simple leveling: 100 exp per level
    exp_for_next = current_level * 100
    
    while new_exp >= exp_for_next:
        new_exp -= exp_for_next
        new_level += 1
        exp_for_next = new_level * 100
    
    return new_level, new_exp
