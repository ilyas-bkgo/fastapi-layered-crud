import sqlite3

DB_NAME = "todos.db"

SCHEMA = """
    CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0
    );
    """


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn, conn.cursor()


def init_db():
    conn, cursor = get_connection()
    cursor.execute(SCHEMA)

    conn.commit()
    conn.close()
