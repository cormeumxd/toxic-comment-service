-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    login VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create credentials table
CREATE TABLE IF NOT EXISTS credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    password_hash VARCHAR(255) NOT NULL
);

-- Create ml_models table
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    price_per_char DECIMAL(10, 4) NOT NULL
);

-- Create wallet table
CREATE TABLE IF NOT EXISTS wallet (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- Create session table
CREATE TABLE IF NOT EXISTS session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    model_id INTEGER NOT NULL REFERENCES ml_models(id),
    start_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    total_words_for_classification INTEGER
);

INSERT INTO ml_models (type, name, price_per_char) VALUES ('text-classification', 'martin-ha/toxic-comment-model', 1.0);