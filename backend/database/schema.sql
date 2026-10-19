CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS opening_positions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    quantity_micros INTEGER NOT NULL CHECK (quantity_micros > 0),
    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE (account_id, symbol)
);