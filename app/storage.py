import sqlite3

DB_NAME = "records.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            name TEXT,
            gender TEXT,
            age INTEGER,
            arc INTEGER,
            arc_link TEXT,
            phone TEXT
        )
    """)

    return conn