from database import get_connection


def fetch_all_todos(completed: bool | None = None):
    conn, cursor = get_connection()

    if completed is None:
        cursor.execute("SELECT id, name, completed FROM todos")
    else:
        cursor.execute(
            "SELECT id, name, completed FROM todos WHERE completed = ?", (completed,)
        )

    rows = cursor.fetchall()
    conn.close()

    return [{"id": row[0], "name": row[1], "completed": bool(row[2])} for row in rows]


def insert_todo(name: str, completed: bool):
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO todos (name, completed) VALUES(?,?)", (name, completed))

    conn.commit()
    new_id = cursor.lastrowid  # Identify the row SQLite just created
    conn.close()

    return {"id": new_id, "name": name, "completed": completed}


def update_todo(item_id: int, name: str, completed: bool):
    conn, cursor = get_connection()
    cursor.execute(
        "UPDATE todos SET name = ?, completed = ? WHERE id = ?",
        (name, completed, item_id),
    )
    conn.commit()
    changes = cursor.rowcount  # Check whether a write operation had an effect
    conn.close()

    return changes > 0


def delete_todo(item_id: int):
    conn, cursor = get_connection()
    cursor.execute("DELETE FROM todos WHERE id = ?", (item_id,))
    conn.commit()
    changes = cursor.rowcount
    conn.close()

    return changes > 0  # Returns trus if item deleted
