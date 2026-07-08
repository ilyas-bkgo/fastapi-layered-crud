import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

import crud
import schemas
from database import get_db
from security import hash_password, verify_password, create_access_token

# Router initialization
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: sqlite3.Connection = Depends(get_db)):
    hashed_pwd = hash_password(user.password)
    new_user = crud.insert_user(db, user.username, user.email, hashed_pwd)
    if not new_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return new_user

@router.get("/{user_id}/items", response_model=list[schemas.ItemResponse])
def get_items(
    user_id: int,
    completed: bool | None = None,
    db: sqlite3.Connection = Depends(get_db),
):
    return crud.fetch_todos_by_user(db, user_id, completed=completed)

@router.post("/login", response_model=schemas.TokenResponse)
def login(user_credentials: schemas.UserLogin, db: sqlite3.Connection = Depends(get_db)):
    user = crud.get_user_by_username(db, user_credentials.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})

    return {"access_token": token, "token_type": "bearer"}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted succesfully"}
