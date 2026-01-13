#  AI Driven Dungeon - Backend Documentation Index

Selamat datang! Ini adalah index lengkap untuk dokumentasi backend AI Driven Dungeon.

---

##  Getting Started

Jika Anda baru memulai, ikuti urutan ini:

1. **[OPENROUTER_SETUP.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/OPENROUTER_SETUP.md)**  **SETUP API KEY**
   - Cara mendapatkan OpenRouter API key
   - Konfigurasi model
   - Pricing & model recommendations

2. **[QUICKSTART.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/QUICKSTART.md)**  **START HERE**
   - Setup environment
   - Install dependencies
   - Setup OpenRouter API key
   - Jalankan server
   - Test API

2. **[VISUAL_GUIDE.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/VISUAL_GUIDE.md)**
   - Diagram arsitektur visual
   - Component breakdown
   - Data flow sequence

3. **[README.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/README.md)**
   - API documentation lengkap
   - Troubleshooting guide
   - Development notes

---

## 📖 Deep Dive Documentation

Untuk memahami sistem lebih dalam:

### **[ARCHITECTURE.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/ARCHITECTURE.md)**
Penjelasan mendalam tentang:
- Alur logika backend (dengan Mermaid diagram)
- Step-by-step data flow
- Kenapa system prompt dirancang ketat
- Fitur anti-halusinasi
- Struktur data flow

### **[SYSTEM_PROMPT_EXAMPLES.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/SYSTEM_PROMPT_EXAMPLES.md)**
Contoh konkret:
-  LLM tanpa system prompt (berhalusinasi)
-  LLM dengan system prompt ketat
- 4 scenario comparison
- Penjelasan kenapa prompt penting

---

##  Code Files

### **Core Application**

1. **[app/main.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/main.py)**
   - FastAPI application
   - 3 endpoint utama: `/game/new`, `/game/action`, `/game/{id}`
   - CORS middleware
   - Database initialization

2. **[app/services/game_engine.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/services/game_engine.py)**  **INTI SISTEM**
   - System Prompt ketat (anti-halusinasi)
   - `process_action()` - LLM integration
   - `apply_inventory_updates()` - Update inventory
   - `calculate_new_hp()` - Hitung HP baru

3. **[app/db/database.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/db/database.py)**
   - SQLite database layer
   - `init_db()` - Create tables
   - `save_game_state()` - Persist state
   - `get_game_state()` - Load state

4. **[app/models/game_state.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/models/game_state.py)**
   - Pydantic models
   - `GameState`, `ActionRequest`, `ActionResponse`

5. **[app/core/config.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/core/config.py)**
   - Configuration management
   - Load environment variables

---

##  Utility Files

### **[run.sh](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/run.sh)**
Script untuk menjalankan server:
```bash
chmod +x run.sh
./run.sh
```

### **[test_api.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/test_api.py)**
Script untuk testing semua endpoint:
```bash
python test_api.py
```

### **[.env.example](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/.env.example)**
Template untuk environment variables:
```
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### **[requirements.txt](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/requirements.txt)**
Python dependencies:
```
fastapi[standard]
uvicorn
openai
python-dotenv
pydantic
pydantic-settings
```

---

##  Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── models/
│   │   ├── game_state.py          # Pydantic models
│   │   └── __init__.py
│   ├── db/
│   │   ├── database.py            # SQLite layer
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py              # Settings
│   │   └── __init__.py
│   └── services/
│       ├── game_engine.py         # LLM integration 
│       └── __init__.py
│
├──  Documentation
│   ├── INDEX.md                   # This file
│   ├── QUICKSTART.md              # Quick start guide
│   ├── README.md                  # Full documentation
│   ├── ARCHITECTURE.md            # System design
│   ├── VISUAL_GUIDE.md            # Visual architecture
│   └── SYSTEM_PROMPT_EXAMPLES.md  # Prompt examples
│
├──  Utilities
│   ├── run.sh                     # Run server script
│   ├── test_api.py                # Test script
│   ├── .env.example               # Env template
│   └── requirements.txt           # Dependencies
│
└──  Data (auto-generated)
    └── game_data.db               # SQLite database
```

---

##  Common Tasks

### **Menjalankan Server**
```bash
conda activate nlp_general
cd /home/radit/MachineLearning/AI-Driven-Dungeon/backend
./run.sh
```

### **Testing API**
```bash
# Terminal baru
conda activate nlp_general
cd /home/radit/MachineLearning/AI-Driven-Dungeon/backend
python test_api.py
```

### **Membuat Game Baru (cURL)**
```bash
curl -X POST http://localhost:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{"starting_scenario": "You wake up in a dark cave."}'
```

### **Proses Aksi (cURL)**
```bash
curl -X POST http://localhost:8000/game/action \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "action": "I look around"
  }'
```

---

##  Troubleshooting

Jika ada masalah, cek:

1. **[QUICKSTART.md - Troubleshooting](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/QUICKSTART.md#-troubleshooting)**
2. **[README.md - Troubleshooting](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/README.md#-troubleshooting)**

Common issues:
-  "OPENAI_API_KEY not found" → Check `.env` file
-  "ModuleNotFoundError" → Run `pip install -r requirements.txt`
-  "Address already in use" → Port 8000 sudah dipakai

---

##  Next Steps

Setelah backend siap:

1.  Test backend dengan `python test_api.py`
2. 🔨 Build frontend (React/Vue/HTML)
3. 🔗 Integrate frontend dengan backend API
4.  Deploy ke production

---

##  Key Concepts

### **System Prompt Anti-Halusinasi**
LLM diberi aturan ketat untuk:
-  Check inventory sebelum use item
-  Return JSON valid (no markdown)
-  Enforce death condition (HP <= 0)
-  Prevent god mode (impossible actions)

**Lihat:** [SYSTEM_PROMPT_EXAMPLES.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/SYSTEM_PROMPT_EXAMPLES.md)

### **Math Delegation**
LLM hanya return **delta** (perubahan), Python yang hitung:
```python
# LLM: {"hp_change": -10}
# Python: new_hp = max(0, current_hp + hp_change)
```

**Lihat:** [ARCHITECTURE.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/ARCHITECTURE.md)

### **State Persistence**
Semua state disimpan di SQLite:
- Session ID (UUID)
- HP, Inventory, Location
- History (full game narrative)
- Game Over status

**Lihat:** [app/db/database.py](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/app/db/database.py)

---

##  Quick Reference

| Task | Command |
|------|---------|
| Start server | `./run.sh` |
| Test API | `python test_api.py` |
| Check logs | Terminal output |
| Stop server | `Ctrl+C` |
| View docs | `http://localhost:8000/docs` |

---

**Happy Coding! **

Jika ada pertanyaan, baca dokumentasi yang relevan di atas atau check source code langsung.
