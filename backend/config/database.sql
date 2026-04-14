CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    phonetic VARCHAR(50),
    example TEXT,
    level INTEGER NOT NULL DEFAULT 1,
    frequency INTEGER NOT NULL DEFAULT 1,
    difficulty INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    level INTEGER NOT NULL,
    total_count INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    accuracy REAL NOT NULL,
    duration INTEGER,
    estimated_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS test_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    user_answer TEXT,
    is_correct INTEGER NOT NULL DEFAULT 0,
    time_spent INTEGER,
    question_type VARCHAR(20),
    FOREIGN KEY (record_id) REFERENCES test_records(id),
    FOREIGN KEY (word_id) REFERENCES vocabulary(id)
);

CREATE TABLE IF NOT EXISTS wrong_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    wrong_count INTEGER NOT NULL DEFAULT 1,
    last_wrong_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (word_id) REFERENCES vocabulary(id),
    UNIQUE(user_id, word_id)
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (word_id) REFERENCES vocabulary(id),
    UNIQUE(user_id, word_id)
);

INSERT INTO admins (username, password) VALUES ('admin', 'pbkdf2:sha256:260000$J9A0vq8f$e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');