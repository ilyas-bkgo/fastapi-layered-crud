# ----- user crud --------
import sqlite3


def insert_user(
    db: sqlite3.Connection, username: str, email: str, hashed_password: str
):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?,?,?)",
            (username, email, hashed_password),
        )
        db.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "username": username, "email": email}
    except Exception as e:
        print("crash reason :", e)
        return None

def get_user_by_username(db: sqlite3.Connection , username: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def delete_user(db: sqlite3.Connection, user_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    changes = cursor.rowcount
    return changes > 0


# -------- item crud --------
def insert_todo(db: sqlite3.Connection, name: str, completed: bool, user_id: int):
    cursor = db.cursor()
    # If the user_id doesn't exist, SQLite will instantly raise an IntegrityError
    cursor.execute(
        "INSERT INTO todos (name, completed, user_id) VALUES(?,?,?)",
        (name, int(completed), user_id),
    )

    db.commit()
    todo_id = cursor.lastrowid  # Identify the row SQLite just created

    return {
        "id": todo_id,
        "name": name,
        "completed": bool(completed),
        "user_id": user_id,
    }


def fetch_todos_by_user(
    db: sqlite3.Connection, user_id: int, completed: bool | None = None
):
    cursor = db.cursor()

    if completed is None:
        cursor.execute("SELECT * FROM todos WHERE user_id= ?", (user_id,))
    else:
        cursor.execute(
            "SELECT * FROM  todos WHERE user_id=? AND completed = ?",
            (user_id, int(completed)),
        )

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def update_todo(db: sqlite3.Connection, item_id: int, name: str, completed: bool):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE todos SET name = ?, completed = ? WHERE id = ?",
        (name, int(completed), item_id),
    )
    db.commit()
    changes = cursor.rowcount  # Check whether a write operation had an effect

    if changes > 0:
        cursor.execute("SELECT user_id FROM todos WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return {
            "id": item_id,
            "name": name,
            "completed": bool(completed),
            "user_id": row["user_id"],
        }

    return None


def delete_todo(db: sqlite3.Connection, item_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (item_id,))
    db.commit()
    changes = cursor.rowcount

    return changes > 0  # Returns true if item deleted
