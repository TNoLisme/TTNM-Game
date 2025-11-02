
-- Bảng users (aggregate root: User)
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('child', 'admin')),
    name VARCHAR(100) NOT NULL
);


-- Bảng children (kế thừa từ User, aggregate root: Child)
CREATE TABLE children (
    user_id UUID PRIMARY KEY REFERENCES users(user_id),
    age INTEGER CHECK (age >= 0),
    last_played TIMESTAMP,
    report_preferences VARCHAR(10) CHECK (report_preferences IN ('daily', 'weekly', 'monthly')),
    created_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);


-- Bảng games (aggregate root: Game)
CREATE TABLE games (
    game_id UUID PRIMARY KEY,
    game_type VARCHAR(10) NOT NULL CHECK (game_type IN ('GameClick', 'GameCV')),
    name VARCHAR(100) NOT NULL,
    level INTEGER NOT NULL CHECK (level >= 1),
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 10),
    max_errors INTEGER NOT NULL DEFAULT 3,
    level_threshold INTEGER NOT NULL,
    time_limit INTEGER NOT NULL
);


-- Bảng game_content (thực thể thuộc aggregate Game)
CREATE TABLE game_content (
    content_id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(game_id),
    level INTEGER NOT NULL CHECK (level >= 1),
    content_type VARCHAR(10) NOT NULL CHECK (content_type IN ('text', 'image', 'video', 'audio')),
    media_path VARCHAR(255),
    question_text TEXT,
    correct_answer VARCHAR(50),
    emotion VARCHAR(50),
    explanation TEXT
);


-- Bảng game_data (thực thể thuộc aggregate Game)
CREATE TABLE game_data (
    data_id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(game_id),
    level INTEGER NOT NULL CHECK (level >= 1)
);


-- Bảng game_data_contents (bảng liên kết giữa game_data và game_content)
CREATE TABLE game_data_contents (
    data_id UUID REFERENCES game_data(data_id),
    content_id UUID REFERENCES game_content(content_id),
    PRIMARY KEY (data_id, content_id)
);


-- Bảng questions (thực thể thuộc aggregate Game)
CREATE TABLE questions (
    question_id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(game_id),
    level INTEGER NOT NULL CHECK (level >= 1),
    content_id UUID REFERENCES game_content(content_id),
    correct_answer VARCHAR(50) NOT NULL
);


-- Bảng question_answer_options (bảng liên kết cho answer_options)
CREATE TABLE question_answer_options (
    question_id UUID REFERENCES questions(question_id),
    content_id UUID REFERENCES game_content(content_id),
    PRIMARY KEY (question_id, content_id)
);


-- Bảng sessions (aggregate root: Session)
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    game_id UUID REFERENCES games(game_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    state VARCHAR(10) NOT NULL CHECK (state IN ('playing', 'pause', 'end')),
    score INTEGER NOT NULL DEFAULT 0,
    emotion_errors JSONB NOT NULL DEFAULT '{}',
    max_errors INTEGER NOT NULL,
    level_threshold INTEGER NOT NULL,
    ratio DOUBLE PRECISION[] NOT NULL DEFAULT '{}',
    time_limit INTEGER NOT NULL,
    question_ids UUID[] NOT NULL DEFAULT '{}' -- Lưu danh sách 10 question_id được random từ đầu level
);


-- Bảng session_questions (thực thể thuộc aggregate Session)
CREATE TABLE session_questions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    question_id UUID REFERENCES questions(question_id),
    user_answer JSONB,
    correct_answer JSONB,
    is_correct BOOLEAN NOT NULL,
    response_time_ms INTEGER NOT NULL,
    check_hint BOOLEAN NOT NULL,
    cv_confidence FLOAT,
    timestamp TIMESTAMP NOT NULL
);


-- Bảng game_history (thực thể thuộc aggregate Child)
CREATE TABLE game_history (
    history_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    session_id UUID REFERENCES sessions(session_id),
    game_id UUID REFERENCES games(game_id),
    score INTEGER NOT NULL,
    level INTEGER NOT NULL
);


-- Bảng session_history (thực thể thuộc aggregate Child)
CREATE TABLE session_history (
    session_history_id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(user_id), -- Ánh xạ user_id thành child_id
    game_id UUID REFERENCES games(game_id),
    session_id UUID REFERENCES sessions(session_id),
    level INTEGER NOT NULL CHECK (level >= 1),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    score INTEGER NOT NULL
);


-- Bảng emotion_concepts (thực thể độc lập)
CREATE TABLE emotion_concepts (
    concept_id UUID PRIMARY KEY,
    emotion VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL CHECK (level >= 1),
    title VARCHAR(100) NOT NULL,
    video_path VARCHAR(255),
    image_path VARCHAR(255),
    audio_path VARCHAR(255),
    description TEXT
);


-- Bảng child_progress (thực thể thuộc aggregate Child)
CREATE TABLE child_progress (
    progress_id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(user_id),
    game_id UUID REFERENCES games(game_id),
    level INTEGER NOT NULL CHECK (level >= 1),
    accuracy FLOAT NOT NULL,
    avg_response_time FLOAT NOT NULL,
    score INTEGER NOT NULL,
    last_played TIMESTAMP NOT NULL,
    ratio DOUBLE PRECISION[] NOT NULL DEFAULT '{}',
    review_emotions UUID[] NOT NULL DEFAULT '{}' -- Lưu danh sách concept_id cần ôn tập
);


-- Bảng reports (thực thể thuộc aggregate Child)
CREATE TABLE reports (
    report_id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(user_id),
    report_type VARCHAR(10) NOT NULL CHECK (report_type IN ('daily', 'weekly', 'monthly')),
    generated_at TIMESTAMP NOT NULL,
    summary TEXT NOT NULL,
    data JSONB NOT NULL
);


-- Index để tối ưu truy vấn
CREATE INDEX idx_session_history_child_game ON session_history(child_id, game_id, start_time DESC);
CREATE INDEX idx_child_progress_child_game ON child_progress(child_id, game_id);
CREATE INDEX idx_session_questions_session ON session_questions(session_id);
CREATE INDEX idx_game_content_game_level ON game_content(game_id, level);
CREATE INDEX idx_questions_session ON sessions(question_ids);

