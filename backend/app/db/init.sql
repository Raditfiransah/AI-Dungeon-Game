-- Pastikan ekstensi aktif untuk UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Tabel Utama: Sesi Permainan
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    summary TEXT,                 -- Rangkuman cerita jangka panjang
    last_event_trigger TEXT,      -- Event terakhir
    game_variables JSONB DEFAULT '{}', -- Variable global (hari, cuaca, relasi)
    
    turn_count INTEGER DEFAULT 0,
    is_game_over BOOLEAN DEFAULT FALSE
);

-- 2. Tabel Karakter: Detail RPG Player
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES game_sessions(id) ON DELETE CASCADE,
    
    -- Identity
    name VARCHAR(100) DEFAULT 'Adventurer',
    race VARCHAR(50),             -- Diambil dari presets
    job_class VARCHAR(50),        -- Diambil dari presets
    background VARCHAR(100),      -- Diambil dari presets
    alignment VARCHAR(50),
    
    -- Visual Context
    appearance_desc TEXT,
    
    -- Resources & RPG Stats [DITAMBAHKAN]
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    max_hp INTEGER DEFAULT 100,
    mana INTEGER DEFAULT 50,
    max_mana INTEGER DEFAULT 50,
    gold INTEGER DEFAULT 0,       -- [PENTING] Mata uang game
    
    -- Attributes
    str INTEGER DEFAULT 10,
    dex INTEGER DEFAULT 10,
    con INTEGER DEFAULT 10,
    int INTEGER DEFAULT 10,
    wis INTEGER DEFAULT 10,
    cha INTEGER DEFAULT 10,
    
    -- Abilities [PENTING]
    -- Contoh isi: ["Fireball", "Stealth", "Diplomacy"]
    skills JSONB DEFAULT '[]',    
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabel Inventory
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    item_name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    item_type VARCHAR(50),        -- Weapon, Armor, Potion, KeyItem
    
    is_equipped BOOLEAN DEFAULT FALSE,
    stat_modifier JSONB DEFAULT '{}', 
    
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabel Quest
CREATE TABLE quests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES game_sessions(id) ON DELETE CASCADE,
    
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 5. Tabel Chat History
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES game_sessions(id) ON DELETE CASCADE,
    
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    turn_order INTEGER            
);

-- [PENTING] Indexing untuk performa loading chat
CREATE INDEX idx_chat_history_session ON chat_history (session_id, turn_order DESC);

-- 6. Tabel Story Card (Lore/Ensiklopedia)
CREATE TABLE story_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    session_id UUID REFERENCES game_sessions(id) ON DELETE CASCADE,
    
    title VARCHAR(100) NOT NULL,
    type VARCHAR(50),             -- LOCATION, NPC, MONSTER
    description TEXT NOT NULL,
    
    keys JSONB DEFAULT '[]',      -- Trigger keywords
    
    -- Logic Trigger
    once_only BOOLEAN DEFAULT FALSE, 
    
    -- [REVISI] Kolom 'triggered' DIHAPUS agar tidak merusak Global Card.
    -- Tracking 'triggered' dilakukan via tabel 'world_state'.
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_story_cards_keys ON story_cards USING gin (keys);

-- 7. Tabel World State (Dinamika & Logika)
CREATE TABLE world_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES game_sessions(id) ON DELETE CASCADE,
    
    -- Key Unik. Contoh: "gate_status", "npc_king_alive"
    -- Atau untuk tracking card: "seen_card_UUIDNYA"
    entity_key VARCHAR(100) NOT NULL, 
    
    related_card_id UUID REFERENCES story_cards(id) ON DELETE SET NULL,
    
    -- State Value. Contoh: {"is_open": true} atau {"seen": true}
    current_state JSONB NOT NULL,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(session_id, entity_key)
);

-- 8. Tabel Presets (Template Data)
CREATE TABLE game_presets (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'RACE', 'CLASS', 'BACKGROUND'
    
    label VARCHAR(50) NOT NULL,    
    value VARCHAR(50) NOT NULL,    
    
    description TEXT,              
    
    base_stats JSONB DEFAULT '{}', 
    
    icon_key VARCHAR(50)           
);

CREATE INDEX idx_game_presets_category ON game_presets(category);

-- Bersihkan data lama
TRUNCATE TABLE game_presets RESTART IDENTITY;

-- =============================================
-- 1. RACES (RAS) - Stat Fisik & Bonus Rasial
-- =============================================
INSERT INTO game_presets (category, label, value, description, base_stats, icon_key) VALUES
('RACE', 'Human', 'human', 'Adaptable and ambitious. Good at everything, master of none.', 
 '{"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1}', 'user'),

('RACE', 'High Elf', 'elf', 'Magical beings of the forest. Agile and intelligent.', 
 '{"dex": 2, "int": 1, "mana": 10}', 'leaf'),

('RACE', 'Mountain Dwarf', 'dwarf', 'Forged in stone. Tough constitution and strong arms.', 
 '{"con": 2, "str": 2, "hp": 10}', 'hammer'),

('RACE', 'Orc', 'orc', 'Fierce warriors with terrifying strength but low patience.', 
 '{"str": 3, "con": 1, "int": -2}', 'axe'),

('RACE', 'Halfling', 'halfling', 'Small and stealthy. Lucky and charismatic.', 
 '{"dex": 2, "cha": 1}', 'footprints'),

('RACE', 'Tiefling', 'tiefling', 'Born with a dark heritage. High charisma and magical aptitude.', 
 '{"cha": 2, "int": 1, "mana": 20}', 'flame'),

('RACE', 'Dragonborn', 'dragonborn', 'Proud draconic heritage. Strong and imposing.', 
 '{"str": 2, "cha": 1}', 'dragon'),

('RACE', 'Gnome', 'gnome', 'Inventive and energetic. Masters of engineering and illusion.', 
 '{"int": 2, "con": 1}', 'gear');

-- =============================================
-- 2. CLASSES (PEKERJAAN) - HP, Mana, Stat Utama
-- =============================================
INSERT INTO game_presets (category, label, value, description, base_stats, icon_key) VALUES
('CLASS', 'Warrior', 'warrior', 'A master of martial combat and heavy armor.', 
 '{"hp": 120, "max_hp": 120, "str": 2, "con": 1}', 'sword'),

('CLASS', 'Wizard', 'wizard', 'A scholarly magic-user capable of manipulating reality.', 
 '{"hp": 60, "max_hp": 60, "mana": 100, "max_mana": 100, "int": 3}', 'wand'),

('CLASS', 'Rogue', 'rogue', 'A scoundrel who uses stealth and trickery.', 
 '{"hp": 80, "max_hp": 80, "dex": 3, "cha": 1}', 'mask'),

('CLASS', 'Cleric', 'cleric', 'A priestly champion who wields divine magic.', 
 '{"hp": 90, "max_hp": 90, "mana": 80, "max_mana": 80, "wis": 3}', 'cross'),

('CLASS', 'Paladin', 'paladin', 'A holy knight bound by a sacred oath.', 
 '{"hp": 110, "max_hp": 110, "mana": 40, "max_mana": 40, "str": 2, "cha": 1}', 'shield'),

('CLASS', 'Ranger', 'ranger', 'A warrior who uses martial prowess and nature magic.', 
 '{"hp": 90, "max_hp": 90, "dex": 2, "wis": 1}', 'bow'),

('CLASS', 'Bard', 'bard', 'An inspiring magician whose power echoes the music of creation.', 
 '{"hp": 80, "max_hp": 80, "mana": 60, "max_mana": 60, "cha": 3}', 'music'),

('CLASS', 'Monk', 'monk', 'A master of martial arts, harnessing the power of the body.', 
 '{"hp": 90, "max_hp": 90, "dex": 2, "wis": 2}', 'fist'),

('CLASS', 'Warlock', 'warlock', 'A wielder of magic derived from a bargain with an extraplanar entity.', 
 '{"hp": 70, "max_hp": 70, "mana": 90, "max_mana": 90, "cha": 2, "int": 1}', 'skull'),

('CLASS', 'Druid', 'druid', 'A priest of the Old Faith, wielding the powers of nature.', 
 '{"hp": 85, "max_hp": 85, "mana": 70, "max_mana": 70, "wis": 3}', 'tree');

-- =============================================
-- 3. BACKGROUNDS (LATAR BELAKANG) - Gold & Skill Sosial
-- =============================================
INSERT INTO game_presets (category, label, value, description, base_stats, icon_key) VALUES
('BACKGROUND', 'Noble', 'noble', 'You were raised in a castle. You understand politics and wealth.', 
 '{"gold": 200, "cha": 2}', 'crown'),

('BACKGROUND', 'Soldier', 'soldier', 'You served in an army. You know how to survive war.', 
 '{"gold": 10, "str": 1, "con": 1}', 'medal'),

('BACKGROUND', 'Criminal', 'criminal', 'You have a history of breaking the law and have contacts.', 
 '{"gold": 25, "dex": 1, "cha": 1}', 'key'),

('BACKGROUND', 'Scholar', 'scholar', 'You spent years studying in libraries or universities.', 
 '{"gold": 15, "int": 2, "wis": 1}', 'book'),

('BACKGROUND', 'Merchant', 'merchant', 'You know how to make a deal and spot a counterfeit.', 
 '{"gold": 100, "cha": 1, "wis": 1}', 'coin'),

('BACKGROUND', 'Hermit', 'hermit', 'You lived in seclusion. You know secrets of the universe.', 
 '{"gold": 5, "wis": 2, "mana": 10}', 'moon'),

('BACKGROUND', 'Entertainer', 'entertainer', 'You thrive in front of an audience. You know how to distract.', 
 '{"gold": 30, "cha": 2, "dex": 1}', 'star'),

('BACKGROUND', 'Urchin', 'urchin', 'You grew up on the streets alone, poor but quick.', 
 '{"gold": 0, "dex": 2, "con": 1}', 'rat');