"""
Database Layer untuk AI Dungeon dengan PostgreSQL
Skema: game_sessions, characters, inventory_items, quests, chat_history, 
       story_cards, world_state, game_presets
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import json
import time
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from uuid import UUID

from app.core.config import get_settings

# Connection pool (min 1, max 10 connections)
connection_pool = None


def get_connection_pool():
    """Get or create connection pool"""
    global connection_pool
    if connection_pool is None:
        settings = get_settings()
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=settings.POSTGRES_SERVER,
                    port=settings.POSTGRES_PORT,
                    database=settings.POSTGRES_DB,
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD.get_secret_value()
                )
                print(f"✅ Database connection pool created successfully")
                break
            except psycopg2.OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"❌ Failed to connect to database after {max_retries} attempts: {e}")
    
    return connection_pool


@contextmanager
def get_db():
    """Context manager for database connection"""
    db_pool = get_connection_pool()
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


# ==================== GAME SESSION FUNCTIONS ====================

def create_game_session() -> Dict[str, Any]:
    """Create a new game session, returns session with UUID"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO game_sessions (summary)
            VALUES (%s)
            RETURNING *
        """, ("Your adventure begins...",))
        session = cursor.fetchone()
        conn.commit()
        return dict(session)


def get_game_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get game session by UUID"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM game_sessions WHERE id = %s", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_game_session(session_id: str, **kwargs) -> bool:
    """Update game session fields"""
    allowed_fields = [
        "summary", "last_event_trigger", "game_variables", 
        "turn_count", "is_game_over"
    ]
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = %s")
            if isinstance(value, dict):
                values.append(json.dumps(value))
            else:
                values.append(value)
    
    if not updates:
        return False
    
    updates.append("updated_at = NOW()")
    values.append(session_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE game_sessions SET {', '.join(updates)} WHERE id = %s
        """, values)
        conn.commit()
        return cursor.rowcount > 0


def delete_game_session(session_id: str) -> bool:
    """Delete game session and all related data (CASCADE)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM game_sessions WHERE id = %s", (session_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== CHARACTER FUNCTIONS ====================

def create_character(session_id: str, name: str = "Adventurer", 
                     race: str = None, job_class: str = None,
                     background: str = None) -> Dict[str, Any]:
    """Create a new character for a session"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO characters (session_id, name, race, job_class, background)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (session_id, name, race, job_class, background))
        character = cursor.fetchone()
        conn.commit()
        return dict(character)


def get_character(session_id: str) -> Optional[Dict[str, Any]]:
    """Get character by session ID"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM characters WHERE session_id = %s", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_character(character_id: str, **kwargs) -> bool:
    """Update character fields"""
    allowed_fields = [
        "name", "race", "job_class", "background", "alignment", "appearance_desc",
        "level", "exp", "hp", "max_hp", "mana", "max_mana", "gold",
        "str", "dex", "con", "int", "wis", "cha", "skills"
    ]
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = %s")
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            else:
                values.append(value)
    
    if not updates:
        return False
    
    values.append(character_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE characters SET {', '.join(updates)} WHERE id = %s
        """, values)
        conn.commit()
        return cursor.rowcount > 0


# ==================== INVENTORY FUNCTIONS ====================

def add_inventory_item(character_id: str, item_name: str, 
                       description: str = None, quantity: int = 1,
                       item_type: str = None, stat_modifier: Dict = None) -> Dict[str, Any]:
    """Add item to character's inventory"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO inventory_items 
            (character_id, item_name, description, quantity, item_type, stat_modifier)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (character_id, item_name, description, quantity, item_type, 
              json.dumps(stat_modifier or {})))
        item = cursor.fetchone()
        conn.commit()
        return dict(item)


def get_inventory(character_id: str) -> List[Dict[str, Any]]:
    """Get all items in character's inventory"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM inventory_items 
            WHERE character_id = %s 
            ORDER BY added_at DESC
        """, (character_id,))
        return [dict(row) for row in cursor.fetchall()]


def update_inventory_item(item_id: str, **kwargs) -> bool:
    """Update inventory item (quantity, is_equipped, etc)"""
    allowed_fields = ["quantity", "is_equipped", "stat_modifier"]
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = %s")
            if isinstance(value, dict):
                values.append(json.dumps(value))
            else:
                values.append(value)
    
    if not updates:
        return False
    
    values.append(item_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE inventory_items SET {', '.join(updates)} WHERE id = %s
        """, values)
        conn.commit()
        return cursor.rowcount > 0


def delete_inventory_item(item_id: str) -> bool:
    """Remove item from inventory"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory_items WHERE id = %s", (item_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== QUEST FUNCTIONS ====================

def create_quest(session_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """Create a new quest"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO quests (session_id, title, description)
            VALUES (%s, %s, %s)
            RETURNING *
        """, (session_id, title, description))
        quest = cursor.fetchone()
        conn.commit()
        return dict(quest)


def get_quests(session_id: str, status: str = None) -> List[Dict[str, Any]]:
    """Get quests for session, optionally filtered by status"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if status:
            cursor.execute("""
                SELECT * FROM quests 
                WHERE session_id = %s AND status = %s
                ORDER BY started_at DESC
            """, (session_id, status))
        else:
            cursor.execute("""
                SELECT * FROM quests 
                WHERE session_id = %s
                ORDER BY started_at DESC
            """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]


def update_quest_status(quest_id: str, status: str) -> bool:
    """Update quest status (active, completed, failed)"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status == "completed":
            cursor.execute("""
                UPDATE quests SET status = %s, completed_at = NOW() WHERE id = %s
            """, (status, quest_id))
        else:
            cursor.execute("""
                UPDATE quests SET status = %s WHERE id = %s
            """, (status, quest_id))
        conn.commit()
        return cursor.rowcount > 0


# ==================== CHAT HISTORY FUNCTIONS ====================

def add_chat_message(session_id: str, role: str, content: str) -> Dict[str, Any]:
    """Add a message to chat history"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get next turn order
        cursor.execute("""
            SELECT COALESCE(MAX(turn_order), 0) + 1 FROM chat_history WHERE session_id = %s
        """, (session_id,))
        turn_order = cursor.fetchone()["coalesce"]
        
        cursor.execute("""
            INSERT INTO chat_history (session_id, role, content, turn_order)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (session_id, role, content, turn_order))
        message = cursor.fetchone()
        conn.commit()
        return dict(message)


def get_chat_history(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get last N messages for context window"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE session_id = %s 
            ORDER BY turn_order DESC 
            LIMIT %s
        """, (session_id, limit))
        rows = cursor.fetchall()
        # Reverse to get chronological order
        return [dict(row) for row in reversed(rows)]


def get_all_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a session"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE session_id = %s 
            ORDER BY turn_order ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]


# ==================== STORY CARD FUNCTIONS ====================

def create_story_card(session_id: str, title: str, card_type: str,
                       description: str, keys: List[str] = None,
                       once_only: bool = False) -> Dict[str, Any]:
    """Create a story card (lore/encyclopedia entry)"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO story_cards (session_id, title, type, description, keys, once_only)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (session_id, title, card_type, description, json.dumps(keys or []), once_only))
        card = cursor.fetchone()
        conn.commit()
        return dict(card)


def get_story_cards(session_id: str, card_type: str = None) -> List[Dict[str, Any]]:
    """Get story cards, optionally filtered by type"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if card_type:
            cursor.execute("""
                SELECT * FROM story_cards 
                WHERE session_id = %s AND type = %s AND is_active = TRUE
            """, (session_id, card_type))
        else:
            cursor.execute("""
                SELECT * FROM story_cards 
                WHERE session_id = %s AND is_active = TRUE
            """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]


def search_story_cards_by_keyword(session_id: str, keyword: str) -> List[Dict[str, Any]]:
    """Search story cards by keyword in keys JSONB array"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM story_cards 
            WHERE session_id = %s AND is_active = TRUE 
            AND keys @> %s
        """, (session_id, json.dumps([keyword])))
        return [dict(row) for row in cursor.fetchall()]


# ==================== WORLD STATE FUNCTIONS ====================

def set_world_state(session_id: str, entity_key: str, state: Dict,
                    related_card_id: str = None) -> Dict[str, Any]:
    """Set or update world state (upsert)"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO world_state (session_id, entity_key, current_state, related_card_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (session_id, entity_key) 
            DO UPDATE SET current_state = %s, updated_at = NOW()
            RETURNING *
        """, (session_id, entity_key, json.dumps(state), related_card_id, json.dumps(state)))
        result = cursor.fetchone()
        conn.commit()
        return dict(result)


def get_world_state(session_id: str, entity_key: str) -> Optional[Dict[str, Any]]:
    """Get specific world state by key"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM world_state 
            WHERE session_id = %s AND entity_key = %s
        """, (session_id, entity_key))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_world_states(session_id: str) -> List[Dict[str, Any]]:
    """Get all world states for a session"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM world_state WHERE session_id = %s
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]


# ==================== GAME PRESETS FUNCTIONS ====================

def get_presets_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all presets for a category (RACE, CLASS, BACKGROUND)"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM game_presets WHERE category = %s
        """, (category,))
        return [dict(row) for row in cursor.fetchall()]


def get_preset_by_value(category: str, value: str) -> Optional[Dict[str, Any]]:
    """Get specific preset by category and value"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM game_presets WHERE category = %s AND value = %s
        """, (category, value))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_presets() -> Dict[str, List[Dict[str, Any]]]:
    """Get all presets grouped by category"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM game_presets ORDER BY category, id")
        rows = cursor.fetchall()
        
        result = {"RACE": [], "CLASS": [], "BACKGROUND": []}
        for row in rows:
            category = row["category"]
            if category in result:
                result[category].append(dict(row))
        
        return result


# ==================== UTILITY FUNCTIONS ====================

def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def get_full_game_state(session_id: str) -> Optional[Dict[str, Any]]:
    """Get complete game state including session, character, inventory, quests"""
    session = get_game_session(session_id)
    if not session:
        return None
    
    character = get_character(session_id)
    inventory = get_inventory(character["id"]) if character else []
    quests = get_quests(session_id)
    chat = get_chat_history(session_id, limit=10)
    
    return {
        "session": session,
        "character": character,
        "inventory": inventory,
        "quests": quests,
        "recent_chat": chat
    }


# ==================== BACKWARD COMPATIBILITY LAYER ====================
# These functions maintain compatibility with old main.py API
# They map old session-based API to new game_sessions + characters schema

def create_session(session_id: str, location: str = "Dark Cave Entrance", 
                   inventory: List[str] = None) -> Dict[str, Any]:
    """
    LEGACY: Create session using old API format
    Maps to: game_sessions + characters + inventory_items
    """
    inventory = inventory or ["Rusty Sword"]
    
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create game session with custom UUID
        cursor.execute("""
            INSERT INTO game_sessions (id, summary)
            VALUES (%s, %s)
            RETURNING *
        """, (session_id, "You begin your adventure..."))
        session = cursor.fetchone()
        
        # Create default character
        cursor.execute("""
            INSERT INTO characters (session_id, name)
            VALUES (%s, %s)
            RETURNING *
        """, (session_id, "Adventurer"))
        character = cursor.fetchone()
        
        # Add inventory items
        for item in inventory:
            cursor.execute("""
                INSERT INTO inventory_items (character_id, item_name, quantity)
                VALUES (%s, %s, 1)
            """, (character["id"], item))
        
        conn.commit()
    
    return get_session(session_id)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    LEGACY: Get session in old format
    Combines: game_sessions + characters + inventory
    """
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get session
        cursor.execute("SELECT * FROM game_sessions WHERE id = %s", (session_id,))
        session = cursor.fetchone()
        if not session:
            return None
        
        # Get character
        cursor.execute("SELECT * FROM characters WHERE session_id = %s", (session_id,))
        character = cursor.fetchone()
        
        # Get inventory
        inventory = []
        if character:
            cursor.execute("""
                SELECT item_name, quantity FROM inventory_items 
                WHERE character_id = %s
            """, (character["id"],))
            for row in cursor.fetchall():
                for _ in range(row["quantity"]):
                    inventory.append(row["item_name"])
        
        # Get active quests
        cursor.execute("""
            SELECT title FROM quests 
            WHERE session_id = %s AND status = 'active'
        """, (session_id,))
        active_quests = [row["title"] for row in cursor.fetchall()]
        
        # Get completed quests
        cursor.execute("""
            SELECT title FROM quests 
            WHERE session_id = %s AND status = 'completed'
        """, (session_id,))
        completed_quests = [row["title"] for row in cursor.fetchall()]
        
        # Map to old format
        return {
            "id": str(session["id"]),
            "hp": character["hp"] if character else 100,
            "max_hp": character["max_hp"] if character else 100,
            "inventory": inventory,
            "location": "Unknown",  # Not in new schema
            "level": character["level"] if character else 1,
            "exp": character["exp"] if character else 0,
            "turn_count": session["turn_count"],
            "game_variables": session["game_variables"] if session["game_variables"] else {},
            "active_quests": active_quests,
            "completed_quests": completed_quests,
            "summary": session["summary"],
            "last_event_trigger": session["last_event_trigger"],
            "game_over": session["is_game_over"]
        }


def update_session(session_id: str, **kwargs) -> bool:
    """
    LEGACY: Update session using old API
    Maps to: game_sessions + characters
    """
    session_fields = ["summary", "last_event_trigger", "game_variables", "turn_count", "game_over"]
    character_fields = ["hp", "max_hp", "level", "exp"]
    
    session_updates = []
    session_values = []
    
    character_updates = []
    character_values = []
    
    for key, value in kwargs.items():
        if key in session_fields:
            if key == "game_over":
                session_updates.append("is_game_over = %s")
                session_values.append(value)
            elif isinstance(value, dict):
                session_updates.append(f"{key} = %s")
                session_values.append(json.dumps(value))
            else:
                session_updates.append(f"{key} = %s")
                session_values.append(value)
        elif key in character_fields:
            character_updates.append(f"{key} = %s")
            character_values.append(value)
        elif key == "inventory":
            # Handle inventory separately
            pass
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Update session
        if session_updates:
            session_updates.append("updated_at = NOW()")
            session_values.append(session_id)
            cursor.execute(f"""
                UPDATE game_sessions SET {', '.join(session_updates)} WHERE id = %s
            """, session_values)
        
        # Update character
        if character_updates:
            character_values.append(session_id)
            cursor.execute(f"""
                UPDATE characters SET {', '.join(character_updates)} 
                WHERE session_id = %s
            """, character_values)
        
        conn.commit()
        return True


def add_message(session_id: str, role: str, content: str, 
                choices_options: List[str] = None, chosen_option: str = None,
                tokens_used: int = None, model_name: str = None, 
                latency_ms: int = None) -> int:
    """
    LEGACY: Add message to chat history
    Maps to: chat_history table
    """
    result = add_chat_message(session_id, role, content)
    return int(result["turn_order"])  # Return turn_order as message ID


def get_messages(session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    LEGACY: Get last N messages
    Maps to: chat_history
    """
    messages = get_chat_history(session_id, limit)
    
    # Convert to old format
    return [{
        "id": msg["turn_order"],
        "role": msg["role"],
        "content": msg["content"],
        "choices_options": None,
        "chosen_option": None,
        "sequence": msg["turn_order"]
    } for msg in messages]


def get_all_messages(session_id: str) -> List[Dict[str, Any]]:
    """
    LEGACY: Get all messages
    Maps to: chat_history
    """
    messages = get_all_chat_history(session_id)
    
    return [{
        "id": msg["turn_order"],
        "role": msg["role"],
        "content": msg["content"],
        "choices_options": None,
        "chosen_option": None,
        "sequence": msg["turn_order"]
    } for msg in messages]


def get_message_count(session_id: str) -> int:
    """LEGACY: Get total message count"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE session_id = %s", (session_id,))
        return cursor.fetchone()[0]


def delete_old_messages(session_id: str, keep_last: int = 10):
    """LEGACY: Delete old messages, keep last N"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM chat_history 
            WHERE session_id = %s AND id NOT IN (
                SELECT id FROM chat_history 
                WHERE session_id = %s 
                ORDER BY turn_order DESC 
                LIMIT %s
            )
        """, (session_id, session_id, keep_last))
        conn.commit()
        return cursor.rowcount


def save_snapshot(session_id: str) -> bool:
    """
    LEGACY: Save snapshot for undo
    Note: Snapshots not implemented in new schema, returns True for compatibility
    """
    # TODO: Implement snapshot system with new schema if needed
    return True


def restore_last_snapshot(session_id: str) -> Optional[Dict[str, Any]]:
    """
    LEGACY: Restore last snapshot
    Note: Snapshots not implemented in new schema, returns None
    """
    # TODO: Implement snapshot system with new schema if needed
    return None


def get_snapshot_count(session_id: str) -> int:
    """LEGACY: Get snapshot count"""
    # TODO: Implement snapshot system with new schema if needed
    return 0
