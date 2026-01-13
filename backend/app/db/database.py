import sqlite3
import json
from typing import Optional, List
from contextlib import contextmanager

import os

# Get absolute path to the directory where this file is located
DB_DIR = os.path.dirname(os.path.abspath(__file__))
# Define session directory path
SESSION_DIR = os.path.join(DB_DIR, "session")
# Define database path
DATABASE_PATH = os.path.join(SESSION_DIR, "game_data.db")

# Ensure session directory exists
os.makedirs(SESSION_DIR, exist_ok=True)

def init_db():
    """Inisialisasi database dan buat tabel jika belum ada"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            session_id TEXT PRIMARY KEY,
            hp INTEGER NOT NULL,
            inventory TEXT NOT NULL,
            location TEXT NOT NULL,
            history TEXT NOT NULL,
            game_over INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager untuk koneksi database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def save_game_state(session_id: str, hp: int, inventory: List[str], 
                    location: str, history: str, game_over: bool):
    """Simpan atau update game state ke database"""
    with get_db() as conn:
        cursor = conn.cursor()
        inventory_json = json.dumps(inventory)
        
        cursor.execute("""
            INSERT INTO game_sessions (session_id, hp, inventory, location, history, game_over)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                hp = excluded.hp,
                inventory = excluded.inventory,
                location = excluded.location,
                history = excluded.history,
                game_over = excluded.game_over,
                updated_at = CURRENT_TIMESTAMP
        """, (session_id, hp, inventory_json, location, history, int(game_over)))
        
        conn.commit()

def get_game_state(session_id: str) -> Optional[dict]:
    """Ambil game state dari database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, hp, inventory, location, history, game_over
            FROM game_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "session_id": row["session_id"],
                "hp": row["hp"],
                "inventory": json.loads(row["inventory"]),
                "location": row["location"],
                "history": row["history"],
                "game_over": bool(row["game_over"])
            }
        return None
