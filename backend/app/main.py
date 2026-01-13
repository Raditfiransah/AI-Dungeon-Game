from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Optional

from app.models.game_state import (
    GameState, ActionRequest, ActionResponse, NewGameRequest
)
from app.db.database import init_db, save_game_state, get_game_state
from app.services.game_engine import (
    process_action, apply_inventory_updates, calculate_new_hp
)

app = FastAPI(title="AI Driven Dungeon Backend")

# CORS middleware untuk frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dalam production, ganti dengan domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Inisialisasi database saat aplikasi start"""
    init_db()
    print("Database initialized")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI Driven Dungeon Backend",
        "endpoints": {
            "POST /game/new": "Start a new game",
            "POST /game/action": "Process player action",
            "GET /game/{session_id}": "Get current game state"
        }
    }

@app.post("/game/new", response_model=GameState)
def create_new_game(request: NewGameRequest):
    """
    Endpoint untuk memulai game baru
    
    Returns:
        GameState: State awal game dengan session_id baru
    """
    session_id = str(uuid.uuid4())
    
    # State awal
    initial_state = {
        "session_id": session_id,
        "hp": 100,
        "inventory": ["Rusty Sword"],
        "location": "Dark Cave",
        "history": request.starting_scenario,
        "game_over": False
    }
    
    # Simpan ke database
    save_game_state(
        session_id=session_id,
        hp=initial_state["hp"],
        inventory=initial_state["inventory"],
        location=initial_state["location"],
        history=initial_state["history"],
        game_over=False
    )
    
    return GameState(**initial_state)

@app.post("/game/action", response_model=ActionResponse)
def process_player_action(request: ActionRequest):
    """
    Endpoint untuk memproses aksi pemain
    
    Args:
        request: ActionRequest berisi session_id dan action
    
    Returns:
        ActionResponse: Hasil dari aksi (narrative, HP, inventory, dll)
    """
    # Ambil state saat ini dari database
    current_state = get_game_state(request.session_id)
    
    if not current_state:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    if current_state["game_over"]:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    # Proses aksi dengan LLM
    llm_result = process_action(request.action, current_state)
    
    # Hitung HP baru
    new_hp = calculate_new_hp(current_state["hp"], llm_result["hp_change"])
    
    # Update inventory
    new_inventory = apply_inventory_updates(
        current_state["inventory"], 
        llm_result["inventory_updates"]
    )
    
    # Update location jika ada
    new_location = llm_result["new_location"] if llm_result["new_location"] else current_state["location"]
    
    # Update history (tambahkan aksi dan narrative ke history)
    new_history = f"{current_state['history']}\n\nPlayer: {request.action}\n{llm_result['narrative']}"
    
    # Check game over condition
    game_over = llm_result["game_over"] or new_hp <= 0
    
    # Simpan state baru ke database
    save_game_state(
        session_id=request.session_id,
        hp=new_hp,
        inventory=new_inventory,
        location=new_location,
        history=new_history,
        game_over=game_over
    )
    
    # Return response
    return ActionResponse(
        narrative=llm_result["narrative"],
        hp=new_hp,
        hp_change=llm_result["hp_change"],
        inventory=new_inventory,
        location=new_location,
        choices=llm_result["choices"],
        game_over=game_over
    )

@app.get("/game/{session_id}", response_model=GameState)
def get_game(session_id: str):
    """
    Endpoint untuk mendapatkan state game saat ini
    
    Args:
        session_id: ID sesi game
    
    Returns:
        GameState: State game saat ini
    """
    state = get_game_state(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return GameState(**state)
