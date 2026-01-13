import sqlite3
import json
import time
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import os

# Database paths
DB_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(DB_DIR, "session")
DATABASE_PATH = os.path.join(SESSION_DIR, "game_data.db")

os.makedirs(SESSION_DIR, exist_ok=True)


def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Sessions Table - Player state & progression
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            
            -- Player Stats
            hp INTEGER DEFAULT 100,
            max_hp INTEGER DEFAULT 100,
            inventory TEXT DEFAULT '[]',
            location TEXT,
            
            -- Progression System
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            turn_count INTEGER DEFAULT 0,
            
            -- State Memory
            game_variables TEXT DEFAULT '{}',
            active_quests TEXT DEFAULT '[]',
            completed_quests TEXT DEFAULT '[]',
            
            -- Narrative Memory
            summary TEXT,
            last_event_trigger TEXT,
            
            game_over INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Messages Table - Conversation history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            
            choices_options TEXT,
            chosen_option TEXT,
            
            tokens_used INTEGER,
            model_name TEXT,
            latency_ms INTEGER,
            
            sequence INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Snapshots Table - Undo system
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            turn_count INTEGER NOT NULL,
            
            hp INTEGER,
            inventory TEXT,
            location TEXT,
            game_variables TEXT,
            active_quests TEXT,
            summary TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized")


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ==================== SESSION FUNCTIONS ====================

def create_session(session_id: str, location: str = "Dark Cave Entrance", 
                   inventory: List[str] = None) -> Dict[str, Any]:
    """Create a new game session"""
    inventory = inventory or ["Rusty Sword"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (id, location, inventory, summary)
            VALUES (?, ?, ?, ?)
        """, (session_id, location, json.dumps(inventory), "You begin your adventure..."))
        conn.commit()
    
    return get_session(session_id)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row["id"],
                "hp": row["hp"],
                "max_hp": row["max_hp"],
                "inventory": json.loads(row["inventory"]),
                "location": row["location"],
                "level": row["level"],
                "exp": row["exp"],
                "turn_count": row["turn_count"],
                "game_variables": json.loads(row["game_variables"]) if row["game_variables"] else {},
                "active_quests": json.loads(row["active_quests"]) if row["active_quests"] else [],
                "completed_quests": json.loads(row["completed_quests"]) if row["completed_quests"] else [],
                "summary": row["summary"],
                "last_event_trigger": row["last_event_trigger"],
                "game_over": bool(row["game_over"])
            }
        return None


def update_session(session_id: str, **kwargs) -> bool:
    """Update session fields"""
    allowed_fields = [
        "hp", "max_hp", "inventory", "location", "level", "exp", 
        "turn_count", "game_variables", "active_quests", "completed_quests",
        "summary", "last_event_trigger", "game_over"
    ]
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            # JSON encode lists and dicts
            if isinstance(value, (list, dict)):
                values.append(json.dumps(value))
            elif isinstance(value, bool):
                values.append(int(value))
            else:
                values.append(value)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(session_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE sessions SET {', '.join(updates)} WHERE id = ?
        """, values)
        conn.commit()
        return cursor.rowcount > 0


# ==================== MESSAGE FUNCTIONS ====================

def add_message(session_id: str, role: str, content: str, 
                choices_options: List[str] = None, chosen_option: str = None,
                tokens_used: int = None, model_name: str = None, 
                latency_ms: int = None) -> int:
    """Add a message to the conversation"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get next sequence number
        cursor.execute("""
            SELECT COALESCE(MAX(sequence), 0) + 1 FROM messages WHERE session_id = ?
        """, (session_id,))
        sequence = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO messages 
            (session_id, role, content, choices_options, chosen_option, 
             tokens_used, model_name, latency_ms, sequence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, role, content,
            json.dumps(choices_options) if choices_options else None,
            chosen_option,
            tokens_used, model_name, latency_ms, sequence
        ))
        conn.commit()
        return cursor.lastrowid


def get_messages(session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Get last N messages for a session (for context window)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages 
            WHERE session_id = ? 
            ORDER BY sequence DESC 
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        messages = []
        for row in reversed(rows):  # Reverse to get chronological order
            messages.append({
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "choices_options": json.loads(row["choices_options"]) if row["choices_options"] else None,
                "chosen_option": row["chosen_option"],
                "sequence": row["sequence"]
            })
        return messages


def get_all_messages(session_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages 
            WHERE session_id = ? 
            ORDER BY sequence ASC
        """, (session_id,))
        
        rows = cursor.fetchall()
        return [{
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "choices_options": json.loads(row["choices_options"]) if row["choices_options"] else None,
            "chosen_option": row["chosen_option"],
            "sequence": row["sequence"]
        } for row in rows]


def get_message_count(session_id: str) -> int:
    """Get total message count for a session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,))
        return cursor.fetchone()[0]


def delete_old_messages(session_id: str, keep_last: int = 10):
    """Delete older messages, keeping only the last N"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM messages 
            WHERE session_id = ? AND id NOT IN (
                SELECT id FROM messages 
                WHERE session_id = ? 
                ORDER BY sequence DESC 
                LIMIT ?
            )
        """, (session_id, session_id, keep_last))
        conn.commit()
        return cursor.rowcount


# ==================== SNAPSHOT FUNCTIONS ====================

def save_snapshot(session_id: str) -> bool:
    """Save current session state as a snapshot for undo"""
    session = get_session(session_id)
    if not session:
        return False
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots 
            (session_id, turn_count, hp, inventory, location, game_variables, active_quests, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            session["turn_count"],
            session["hp"],
            json.dumps(session["inventory"]),
            session["location"],
            json.dumps(session["game_variables"]),
            json.dumps(session["active_quests"]),
            session["summary"]
        ))
        conn.commit()
        return True


def restore_last_snapshot(session_id: str) -> Optional[Dict[str, Any]]:
    """Restore session to last snapshot and delete it"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get last snapshot
        cursor.execute("""
            SELECT * FROM snapshots 
            WHERE session_id = ? 
            ORDER BY id DESC LIMIT 1
        """, (session_id,))
        
        snapshot = cursor.fetchone()
        if not snapshot:
            return None
        
        # Restore session
        cursor.execute("""
            UPDATE sessions SET
                hp = ?, inventory = ?, location = ?,
                game_variables = ?, active_quests = ?, summary = ?,
                turn_count = ?, game_over = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            snapshot["hp"],
            snapshot["inventory"],
            snapshot["location"],
            snapshot["game_variables"],
            snapshot["active_quests"],
            snapshot["summary"],
            snapshot["turn_count"],
            session_id
        ))
        
        # Delete used snapshot
        cursor.execute("DELETE FROM snapshots WHERE id = ?", (snapshot["id"],))
        
        # Delete messages after this turn
        cursor.execute("""
            DELETE FROM messages 
            WHERE session_id = ? AND sequence > (
                SELECT COALESCE(MAX(sequence), 0) FROM messages 
                WHERE session_id = ? AND sequence <= ?
            )
        """, (session_id, session_id, snapshot["turn_count"] * 2))  # Approx 2 messages per turn
        
        conn.commit()
        
        return get_session(session_id)


def get_snapshot_count(session_id: str) -> int:
    """Get number of available undo snapshots"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM snapshots WHERE session_id = ?", (session_id,))
        return cursor.fetchone()[0]
