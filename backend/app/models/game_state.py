from pydantic import BaseModel
from typing import List, Optional

class GameState(BaseModel):
    """Model untuk state game saat ini"""
    session_id: str
    hp: int
    inventory: List[str]
    location: str
    history: str  # Ringkasan cerita sejauh ini
    game_over: bool = False
    
class ActionRequest(BaseModel):
    """Model untuk request action dari user"""
    session_id: str
    action: str
    
class ActionResponse(BaseModel):
    """Model untuk response dari game engine"""
    narrative: str
    hp: int
    hp_change: int
    inventory: List[str]
    location: str
    choices: List[str]
    game_over: bool
    
class NewGameRequest(BaseModel):
    """Model untuk memulai game baru"""
    starting_scenario: Optional[str] = "You wake up in a dark cave with only a rusty sword in your hand."
