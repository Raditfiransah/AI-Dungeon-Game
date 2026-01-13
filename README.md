# AI Driven Dungeon - Backend

Backend untuk game text-based RPG yang menggunakan LLM (OpenAI) sebagai Game Engine.

## 🏗 Arsitektur

```
backend/
├── app/
│   ├── main.py              # FastAPI application & endpoints
│   ├── models/
│   │   └── game_state.py    # Pydantic models
│   ├── db/
│   │   └── database.py      # SQLite database layer
│   ├── core/
│   │   └── config.py        # Configuration & settings
│   └── services/
│       └── game_engine.py   # LLM integration & game logic
├── .env                     # Environment variables (JANGAN COMMIT!)
├── .env.example             # Template untuk .env
├── requirements.txt         # Python dependencies
├── run.sh                   # Script untuk menjalankan server
└── test_api.py              # Script untuk testing API
```

##  Setup & Installation

### 1. Activate Conda Environment
```bash
conda activate nlp_general
```

### 2. Install Dependencies
```bash
cd /home/radit/MachineLearning/AI-Driven-Dungeon/backend
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
# Copy template .env
cp .env.example .env

# Edit .env dan masukkan OpenRouter API Key Anda
nano .env
```

Isi `.env` dengan:
```
# OpenRouter API Configuration
OPENAI_API_KEY=sk-or-v1-your-openrouter-api-key-here
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_BASE_URL=https://openrouter.ai/api/v1

MAX_TOKENS=500
TEMPERATURE=0.7
```

**📖 Panduan OpenRouter Lengkap:** [OPENROUTER_SETUP.md](file:///home/radit/MachineLearning/AI-Driven-Dungeon/backend/OPENROUTER_SETUP.md)

### 4. Jalankan Server
```bash
# Berikan permission untuk run.sh
chmod +x run.sh

# Jalankan server
./run.sh
```

Server akan berjalan di: `http://localhost:8000`

## 📡 API Endpoints

### 1. **GET /** - Root Endpoint
Informasi tentang API

**Response:**
```json
{
  "message": "Welcome to AI Driven Dungeon Backend",
  "endpoints": {
    "POST /game/new": "Start a new game",
    "POST /game/action": "Process player action",
    "GET /game/{session_id}": "Get current game state"
  }
}
```

### 2. **POST /game/new** - Mulai Game Baru
Membuat sesi game baru dengan state awal

**Request Body:**
```json
{
  "starting_scenario": "You wake up in a dark cave with only a rusty sword in your hand."
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "hp": 100,
  "inventory": ["Rusty Sword"],
  "location": "Dark Cave",
  "history": "You wake up in a dark cave...",
  "game_over": false
}
```

### 3. **POST /game/action** - Proses Aksi Pemain
Memproses aksi pemain dan mendapatkan response dari LLM

**Request Body:**
```json
{
  "session_id": "uuid-here",
  "action": "I attack the goblin with my sword"
}
```

**Response:**
```json
{
  "narrative": "You swing your rusty sword at the goblin. It hits! The goblin screams and strikes back, dealing 10 damage.",
  "hp": 90,
  "hp_change": -10,
  "inventory": ["Rusty Sword"],
  "location": "Dark Cave",
  "choices": [
    "Attack again",
    "Defend yourself",
    "Run away"
  ],
  "game_over": false
}
```

### 4. **GET /game/{session_id}** - Get Game State
Mendapatkan state game saat ini

**Response:**
```json
{
  "session_id": "uuid-here",
  "hp": 90,
  "inventory": ["Rusty Sword", "Gold Coin"],
  "location": "Dark Cave",
  "history": "Full game history...",
  "game_over": false
}
```

##  Testing

### Manual Testing dengan Script
```bash
# Pastikan server sudah running di terminal lain
python test_api.py
```

### Manual Testing dengan cURL

**1. Buat game baru:**
```bash
curl -X POST http://localhost:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{"starting_scenario": "You wake up in a dark cave."}'
```

**2. Proses aksi:**
```bash
curl -X POST http://localhost:8000/game/action \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID_HERE",
    "action": "I look around the cave"
  }'
```

##  System Prompt - Cara Kerja LLM

Backend menggunakan **System Prompt yang Ketat** untuk memastikan LLM:
1.  Tidak berhalusinasi
2.  Selalu return JSON valid
3.  Mengikuti aturan game (HP, inventory, death condition)
4.  Konsisten dengan state yang ada

### Fitur Anti-Halusinasi:
- **Inventory Check**: User tidak bisa menggunakan item yang tidak dimiliki
- **God Mode Prevention**: Aksi impossible akan ditolak atau diberi konsekuensi lucu
- **Death Logic**: Otomatis game over jika HP <= 0
- **Math Delegation**: LLM hanya memberikan delta (+/-), Python yang menghitung

##  Database

Menggunakan **SQLite** dengan schema:

```sql
CREATE TABLE game_sessions (
    session_id TEXT PRIMARY KEY,
    hp INTEGER NOT NULL,
    inventory TEXT NOT NULL,  -- JSON array
    location TEXT NOT NULL,
    history TEXT NOT NULL,
    game_over INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

Database file: `game_data.db` (otomatis dibuat saat server start)

##  Troubleshooting

### Error: "OPENAI_API_KEY not found"
- Pastikan file `.env` sudah dibuat dan berisi API key yang valid

### Error: "ModuleNotFoundError"
- Pastikan sudah activate conda environment: `conda activate nlp_general`
- Install dependencies: `pip install -r requirements.txt`

### Error: "Address already in use"
- Port 8000 sudah digunakan, kill process atau ganti port di `run.sh`

##  Development Notes

- **Jangan commit `.env`** - File ini sudah ada di `.gitignore`
- Database `game_data.db` juga tidak perlu di-commit
- Untuk production, ganti `allow_origins=["*"]` di CORS dengan domain frontend yang spesifik
