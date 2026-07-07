import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

import crud
import schemas
from database import get_db

# Router initialization
router = APIRouter(prefix="/items", tags=["Items"])


@router.post(
    "/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED
)
def creat_item(
    user_id: int, item: schemas.ItemCreate, db: sqlite3.Connection = Depends(get_db)
):
    try:
        return crud.insert_todo(db, item.name, item.completed, user_id)
    except Exception:
        raise HTTPException(
            status_code=400, detail=f"User with {user_id} does not exists"
        )


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    updated_item: schemas.ItemCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    todo = crud.update_todo(db, item_id, updated_item.name, updated_item.completed)
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    return todo
