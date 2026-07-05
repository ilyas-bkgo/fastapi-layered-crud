from fastapi import FastAPI, HTTPException

import crud
import schemas
from database import init_db

app = FastAPI()

# initialize db table when server boots up
init_db()


@app.get("/items")
def get_items(completed: bool | None = None):
    return crud.fetch_all_todos(completed=completed)


@app.post("/items")
def create_item(item: schemas.Item):
    return crud.insert_todo(item.name, item.completed)


@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: schemas.Item):
    success = crud.update_todo(item_id, updated_item.name, updated_item.completed)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Item {item_id} updated successfully."}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    success = crud.delete_todo(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": f"Item {item_id} deleted successfully"}
