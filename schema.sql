CREATE TABLE IF NOT EXISTS key_value_store (
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_queries (
    id INTEGER NOT NULL PRIMARY KEY,
    hashtags TEXT NOT NULL,
    start_date_time TEXT NOT NULL,
    end_date_time TEXT NOT NULL
);