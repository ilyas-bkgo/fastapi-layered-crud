import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import crud
import schemas
from database import get_db
from security import hash_password, verify_password, create_access_token, get_current_user

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


@router.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    print("\n[DEBUG] --- Login Attempt ---")
    print(f"[DEBUG] Username provided: '{form_data.username}'")

    user = crud.get_user_by_username(db, form_data.username)
    if not user:
        print(f"[DEBUG] Result: FAILED - Username '{form_data.username}' not found in database.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    print("[DEBUG] Result: SUCCESS - User found. Verifying password hash...")
    if not verify_password(form_data.password, user["hashed_password"]):
        print(f"[DEBUG] Result: FAILED - Password mismatch for user '{form_data.username}'.")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    print("[DEBUG] Result: SUCCESS - Password verified. Generating token.")
    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})

    return {"access_token": token, "token_type": "bearer"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check if the authenticated user is attempting to delete their own account
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this user profile"
        )

    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted successfully"}
