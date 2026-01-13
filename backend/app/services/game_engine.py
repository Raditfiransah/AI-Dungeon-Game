import json
from openai import OpenAI
from typing import Dict, Any
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    base_url=settings.OPENAI_BASE_URL
)

# System Prompt yang KETAT - Tidak Berhalusinasi
SYSTEM_PROMPT = """### ROLE & OBJECTIVE
You are the "Game Engine" for a text-based RPG. You are NOT a chat assistant.
Your goal is to process the User's Action, update the game state, and advance the narrative based on the Current State provided.

### STRICT OUTPUT FORMAT
You MUST reply with a VALID JSON object. Do not include markdown formatting (like ```json), do not include intro/outro text. Just the raw JSON string.

Expected JSON Structure:
{{
  "narrative": "String. Detailed description of what happens (max 3 sentences).",
  "hp_change": Integer. Negative for damage, Positive for healing, 0 for no change.,
  "inventory_updates": List of Strings. E.g. ["+Gold Coin", "-Potion"] or []. Use "+" to add, "-" to remove.,
  "new_location": "String or null. Only change if user moves to a distinct new place.",
  "choices": ["String", "String", "String"]. Exactly 3 distinct suggested actions for the user.,
  "game_over": Boolean. True only if HP reaches 0 or a win condition is met.
}}

### GAMEPLAY RULES (MUST FOLLOW)
1. **Combat & Consequences**: If the user attacks or takes risks, calculate logical outcomes. If the enemy fights back, apply negative "hp_change".
2. **Consistency**: Check the "Current Inventory". User CANNOT use items they do not have. If they try, narrate a failure and set "hp_change" to 0.
3. **Pacing**: Keep the "narrative" punchy and atmospheric. Do not write long paragraphs.
4. **God Mode Forbidden**: If user tries to do impossible things (e.g., "I fly to the moon"), narrate a failure or a funny consequence.
5. **Death**: If "Current HP" + "hp_change" <= 0, you MUST set "game_over": true and describe the character's death in "narrative".

### CURRENT STATE (CONTEXT)
- Player HP: {hp}
- Inventory: {inventory}
- Current Location: {location}
- Story Context: {history}
"""

def process_action(action: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proses action user dengan LLM dan return hasil dalam format JSON
    
    Args:
        action: Aksi yang dilakukan user
        current_state: State game saat ini (hp, inventory, location, history)
    
    Returns:
        Dict berisi narrative, hp_change, inventory_updates, new_location, choices, game_over
    """
    
    # Format system prompt dengan current state
    formatted_prompt = SYSTEM_PROMPT.format(
        hp=current_state["hp"],
        inventory=", ".join(current_state["inventory"]) if current_state["inventory"] else "Empty",
        location=current_state["location"],
        history=current_state["history"]
    )
    
    try:
        # Panggil OpenAI API
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": action}
            ],
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        # Parse response
        llm_output = response.choices[0].message.content
        result = json.loads(llm_output)
        
        # Validasi struktur response
        required_keys = ["narrative", "hp_change", "inventory_updates", "new_location", "choices", "game_over"]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key: {key}")
        
        # Validasi tipe data
        if not isinstance(result["hp_change"], int):
            result["hp_change"] = int(result["hp_change"])
        
        if not isinstance(result["inventory_updates"], list):
            result["inventory_updates"] = []
            
        if not isinstance(result["choices"], list) or len(result["choices"]) != 3:
            result["choices"] = ["Continue exploring", "Check inventory", "Rest"]
        
        if not isinstance(result["game_over"], bool):
            result["game_over"] = False
        
        return result
        
    except Exception as e:
        # Fallback jika LLM error
        print(f"Error calling LLM: {e}")
        return {
            "narrative": "Something went wrong. The world seems to glitch for a moment...",
            "hp_change": 0,
            "inventory_updates": [],
            "new_location": None,
            "choices": ["Try again", "Look around", "Wait"],
            "game_over": False
        }

def apply_inventory_updates(current_inventory: list, updates: list) -> list:
    """
    Terapkan update inventory berdasarkan format +Item atau -Item
    
    Args:
        current_inventory: List inventory saat ini
        updates: List update dalam format ["+Item", "-Item"]
    
    Returns:
        List inventory yang sudah diupdate
    """
    new_inventory = current_inventory.copy()
    
    for update in updates:
        if not update:
            continue
            
        operation = update[0]
        item = update[1:].strip()
        
        if operation == "+":
            new_inventory.append(item)
        elif operation == "-":
            if item in new_inventory:
                new_inventory.remove(item)
    
    return new_inventory

def calculate_new_hp(current_hp: int, hp_change: int) -> int:
    """
    Hitung HP baru dengan batas minimum 0
    
    Args:
        current_hp: HP saat ini
        hp_change: Perubahan HP (bisa negatif atau positif)
    
    Returns:
        HP baru (minimum 0)
    """
    new_hp = current_hp + hp_change
    return max(0, new_hp)  # HP tidak boleh negatif
