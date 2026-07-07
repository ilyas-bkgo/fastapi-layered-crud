import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

import crud
import schemas
from database import get_db

# Router initialization
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: sqlite3.Connection = Depends(get_db)):
    new_user = crud.insert_user(db, user.username, user.email)
    if not new_user:
        raise HTTPException(status_code=404, detail="Username or email already exists")
    return new_user


@router.get("/{user_id}/items", response_model=list[schemas.ItemResponse])
def get_items(
    user_id: int,
    completed: bool | None = None,
    db: sqlite3.Connection = Depends(get_db),
):
    return crud.fetch_todos_by_user(db, user_id, completed=completed)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted succesfully"}
