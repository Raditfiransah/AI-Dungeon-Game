from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Individual message in conversation"""
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    choices_options: Optional[List[str]] = None
    chosen_option: Optional[str] = None


class Session(BaseModel):
    """Full game session state"""
    id: str
    hp: int
    max_hp: int
    inventory: List[str]
    location: str
    level: int
    exp: int
    turn_count: int
    game_variables: Dict[str, Any]
    active_quests: List[str]
    summary: str
    game_over: bool
    messages: List[Message]
    choices: List[str] = []


class NewGameRequest(BaseModel):
    """Request to start a new game"""
    starting_scenario: Optional[str] = "You wake up in a dark cave with only a rusty sword in your hand."
    player_name: Optional[str] = "Adventurer"


class ActionRequest(BaseModel):
    """Request to perform an action"""
    session_id: str
    action: str


class ActionResponse(BaseModel):
    """Response after processing an action"""
    narrative: str
    hp: int
    hp_change: int
    inventory: List[str]
    location: str
    choices: List[str]
    game_over: bool
    messages: List[Message]
    # Stats for UI
    level: int
    exp: int
    turn_count: int


class UndoRequest(BaseModel):
    """Request to undo last action"""
    session_id: str


# AI Response Schema (what we expect from the LLM)
class AIGameResponse(BaseModel):
    """Structured response expected from AI"""
    narrative: str              # Story text (2-3 sentences)
    damage: int = 0             # HP damage to player
    heal: int = 0               # HP healing for player
    gain_item: Optional[str] = None
    lose_item: Optional[str] = None
    new_location: Optional[str] = None
    choices: List[str]          # Exactly 3 choices
    game_over: bool = False
    exp_gain: int = 0           # Experience gained
    event_trigger: Optional[str] = None  # Special event flags
