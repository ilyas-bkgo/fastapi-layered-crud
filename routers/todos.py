import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status, Query
import crud
import schemas
from database import get_db
from security import get_current_user


# Router initialization
router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model= list[schemas.ItemResponse])
def get_todos(
    completed: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100, description="How many items to return"),
    offset: int = Query(default=0, ge=0, description="How many items to skip"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    return crud.fetch_todos_by_user(
        db,
        user_id=user_id,
        completed=completed,
        limit= limit,
        offset= offset
    )

@router.post(
    "/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED
)
def creat_todo(
    item: schemas.ItemCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    return crud.insert_todo(db, item.name, item.completed, user_id)



@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    updated_item: schemas.ItemCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    todo = crud.update_todo(db, item_id, updated_item.name, updated_item.completed, user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")
    return todo


@router.delete("/{item_id}", status_code= status.HTTP_200_OK)
def delete_item(
    item_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    crud.delete_todo(db, item_id, current_user["id"])

    return None
