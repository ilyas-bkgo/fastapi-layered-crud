from exceptions import ItemNotFounError
import sqlite3

import schemas

# ----- user crud --------
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

        cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

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

    cursor.execute("SELECT id, name, completed, user_id , created_at FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()

    if row:
        todo_dict = dict(row)
        todo_dict["completed"] = bool(todo_dict["completed"])
        return todo_dict

    return None


def fetch_todos_by_user(
    db: sqlite3.Connection, user_id: int, completed: bool | None = None,
    limit: int = 10,
    offset: int = 0
):
    cursor = db.cursor()

    if completed is None:
        cursor.execute("SELECT * FROM todos WHERE user_id= ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset))
    else:
        cursor.execute(
            "SELECT * FROM  todos WHERE user_id=? AND completed = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, int(completed), limit, offset),
        )

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def update_todo(db: sqlite3.Connection, item_id: int, name: str, completed: bool, user_id: int):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE todos SET name = ?, completed = ? WHERE id = ? AND user_id = ?",
        (name, int(completed), item_id, user_id),
    )
    db.commit()
    if cursor.rowcount == 0:
      raise ItemNotFounError(item_id=item_id)  # Check whether a write operation had an effect

    cursor.execute("SELECT created_at FROM todos WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    created_at = row["created_at"] if row else None

    return {
            "id": item_id,
            "name": name,
            "completed": bool(completed),
            "user_id": user_id,
            "created_at": created_at
        }


def patch_todo(db: sqlite3.Connection,
    item_id: int,
    patch_data: schemas.ItemUpdate,
    user_id: int
):
    update_dict = patch_data.model_dump(exclude_unset= True)

    if not update_dict:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM todos WHERE id = ? AND user_id = ?",
            (item_id, user_id,))
        row = cursor.fetchone()
        if not row:
            raise ItemNotFounError(item_id=item_id)
        return dict(row)

    sql_assignments = []
    query_parameters = []
    for column_name, value in update_dict.items():
        if isinstance(value, bool):
            value = int(value)
        sql_assignments.append(f"{column_name} = ?")
        query_parameters.append(value)

    query_parameters.extend([item_id, user_id])

    sql_query = f"UPDATE todos SET {','.join(sql_assignments)} WHERE id = ? AND user_id = ?"

    cursor = db.cursor()
    cursor.execute(sql_query, tuple(query_parameters))
    db.commit()

    if cursor.rowcount == 0:
        raise ItemNotFounError(item_id=item_id)

    cursor.execute("SELECT * FROM todos WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if row:
        todo_dict = dict(row)
        todo_dict["completed"] = bool(todo_dict["completed"])
        return todo_dict
    return None



def delete_todo(db: sqlite3.Connection, item_id: int, user_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", (item_id,user_id))
    db.commit()

    if cursor.rowcount == 0:
        raise ItemNotFounError(item_id=item_id)

    return True
