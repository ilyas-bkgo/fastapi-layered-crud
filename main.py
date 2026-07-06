import sqlite3

from fastapi import Depends, FastAPI, HTTPException, status

import crud
import schemas
from database import get_db, init_db

app = FastAPI()
init_db()


# ----- user endpoints ------
@app.post(
    "/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: sqlite3.Connection = Depends(get_db)):
    new_user = crud.insert_user(db, user.username, user.email)
    if not new_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return new_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} deleted successfully"}


# ----- item endpoints (scoped by user) ------
@app.get("/users/{user_id}/items", response_model=list[schemas.ItemResponse])
def get_items(
    user_id: int,
    completed: bool | None = None,
    db: sqlite3.Connection = Depends(get_db),
):
    return crud.fetch_todos_by_user(db, user_id, completed=completed)


@app.post(
    "/items", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED
)
def create_item(
    item: schemas.ItemCreate, user_id: int, db: sqlite3.Connection = Depends(get_db)
):
    try:
        return crud.insert_todo(db, item.name, item.completed, user_id)
    except Exception:
        raise HTTPException(
            status_code=400, detail=f"User with {user_id} does not exists"
        )


@app.put("/items/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    updated_item: schemas.ItemCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    todo = crud.update_todo(db, item_id, updated_item.name, updated_item.completed)
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    return todo


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    success = crud.delete_todo(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": f"Item {item_id} deleted successfully"}
