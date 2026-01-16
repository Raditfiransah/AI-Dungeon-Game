from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.models.game_state import (
    Session, Message, NewGameRequest, ActionRequest, ActionResponse, UndoRequest
)
from app.db import database
from app.services.game_engine import (
    process_action, calculate_new_hp, apply_inventory_changes, 
    calculate_level_up, generate_summary
)

app = FastAPI(title="AI Driven Dungeon Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # Tables are created by init.sql, just test connection
    database.test_connection()


@app.get("/")
def read_root():
    return {
        "message": "AI Driven Dungeon API",
        "endpoints": {
            "POST /game/new": "Start new game",
            "POST /game/action": "Process action",
            "GET /game/{id}": "Get session",
            "POST /game/undo": "Undo last action"
        }
    }


@app.post("/game/new", response_model=Session)
def create_new_game(request: NewGameRequest):
    """Start a new game session"""
    session_id = str(uuid.uuid4())
    
    # Create session in database
    database.create_session(
        session_id=session_id,
        location="Dark Cave Entrance",
        inventory=["Rusty Sword", "Torch", "3 Rations"]
    )
    
    # Add initial AI message
    initial_narrative = f"{request.starting_scenario} The air is damp and cold. You grip your rusty sword tightly."
    initial_choices = ["Look around carefully", "Check your inventory", "Walk deeper into the cave"]
    
    database.add_message(
        session_id=session_id,
        role="assistant",
        content=initial_narrative,
        choices_options=initial_choices
    )
    
    # Get full session
    session = database.get_session(session_id)
    messages = database.get_all_messages(session_id)
    
    return Session(
        id=session["id"],
        hp=session["hp"],
        max_hp=session["max_hp"],
        inventory=session["inventory"],
        location=session["location"],
        level=session["level"],
        exp=session["exp"],
        turn_count=session["turn_count"],
        game_variables=session["game_variables"],
        active_quests=session["active_quests"],
        summary=session["summary"],
        game_over=session["game_over"],
        messages=[Message(
            role=m["role"],
            content=m["content"],
            choices_options=m["choices_options"]
        ) for m in messages],
        choices=initial_choices
    )


@app.post("/game/action", response_model=ActionResponse)
def process_player_action(request: ActionRequest):
    """Process a player action"""
    
    # Get current session
    session = database.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["game_over"]:
        raise HTTPException(status_code=400, detail="Game is over")
    
    # Save snapshot BEFORE processing (for undo)
    database.save_snapshot(request.session_id)
    
    # Add user message to history
    database.add_message(
        session_id=request.session_id,
        role="user",
        content=request.action,
        chosen_option=request.action
    )
    
    # Get recent messages for context (sliding window)
    recent_messages = database.get_messages(request.session_id, limit=15)
    
    # Process with AI
    ai_result = process_action(request.action, session, recent_messages)
    
    # Calculate new state (Python logic, not AI)
    new_hp = calculate_new_hp(
        session["hp"], session["max_hp"],
        ai_result["damage"], ai_result["heal"]
    )
    
    new_inventory = apply_inventory_changes(
        session["inventory"],
        ai_result["gain_item"],
        ai_result["lose_item"]
    )
    
    new_level, new_exp = calculate_level_up(
        session["level"], session["exp"], ai_result["exp_gain"]
    )
    
    new_location = ai_result["new_location"] or session["location"]
    game_over = ai_result["game_over"] or new_hp <= 0
    
    # Add AI response to history
    database.add_message(
        session_id=request.session_id,
        role="assistant",
        content=ai_result["narrative"],
        choices_options=ai_result["choices"],
        tokens_used=ai_result.get("tokens_used"),
        model_name=ai_result.get("model_name"),
        latency_ms=ai_result.get("latency_ms")
    )
    
    # Update session
    database.update_session(
        request.session_id,
        hp=new_hp,
        inventory=new_inventory,
        location=new_location,
        level=new_level,
        exp=new_exp,
        turn_count=session["turn_count"] + 1,
        last_event_trigger=ai_result.get("event_trigger"),
        game_over=game_over
    )
    
    # Auto-summarize if too many messages
    message_count = database.get_message_count(request.session_id)
    if message_count > 20:
        old_messages = database.get_messages(request.session_id, limit=message_count)[:10]
        new_summary = generate_summary(old_messages)
        database.update_session(request.session_id, summary=new_summary)
        database.delete_old_messages(request.session_id, keep_last=10)
    
    # Get all messages for response
    all_messages = database.get_all_messages(request.session_id)
    
    return ActionResponse(
        narrative=ai_result["narrative"],
        hp=new_hp,
        hp_change=-ai_result["damage"] + ai_result["heal"],
        inventory=new_inventory,
        location=new_location,
        choices=ai_result["choices"],
        game_over=game_over,
        messages=[Message(
            role=m["role"],
            content=m["content"],
            choices_options=m["choices_options"]
        ) for m in all_messages],
        level=new_level,
        exp=new_exp,
        turn_count=session["turn_count"] + 1
    )


@app.post("/game/undo", response_model=Session)
def undo_last_action(request: UndoRequest):
    """Undo the last action"""
    
    restored = database.restore_last_snapshot(request.session_id)
    if not restored:
        raise HTTPException(status_code=400, detail="Cannot undo further")
    
    messages = database.get_all_messages(request.session_id)
    
    # Get last choices from last assistant message
    last_choices = ["Continue", "Look around", "Rest"]
    for m in reversed(messages):
        if m["role"] == "assistant" and m["choices_options"]:
            last_choices = m["choices_options"]
            break
    
    return Session(
        id=restored["id"],
        hp=restored["hp"],
        max_hp=restored["max_hp"],
        inventory=restored["inventory"],
        location=restored["location"],
        level=restored["level"],
        exp=restored["exp"],
        turn_count=restored["turn_count"],
        game_variables=restored["game_variables"],
        active_quests=restored["active_quests"],
        summary=restored["summary"],
        game_over=restored["game_over"],
        messages=[Message(
            role=m["role"],
            content=m["content"],
            choices_options=m["choices_options"]
        ) for m in messages],
        choices=last_choices
    )


@app.get("/game/{session_id}", response_model=Session)
def get_game(session_id: str):
    """Get current game session"""
    
    session = database.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = database.get_all_messages(session_id)
    
    # Get last choices
    last_choices = ["Continue", "Look around", "Rest"]
    for m in reversed(messages):
        if m["role"] == "assistant" and m["choices_options"]:
            last_choices = m["choices_options"]
            break
    
    return Session(
        id=session["id"],
        hp=session["hp"],
        max_hp=session["max_hp"],
        inventory=session["inventory"],
        location=session["location"],
        level=session["level"],
        exp=session["exp"],
        turn_count=session["turn_count"],
        game_variables=session["game_variables"],
        active_quests=session["active_quests"],
        summary=session["summary"],
        game_over=session["game_over"],
        messages=[Message(
            role=m["role"],
            content=m["content"],
            choices_options=m["choices_options"]
        ) for m in messages],
        choices=last_choices
    )
