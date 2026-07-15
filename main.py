import sqlite3

from fastapi import FastAPI ,Request , status
from fastapi.responses import JSONResponse
from database import init_db
from routers import todos, users
from exceptions import UserNotFoundError, ItemNotFounError

app = FastAPI(title="Learning FastAPI")
init_db()


app.include_router(users.router)
app.include_router(todos.router)

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code= status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )

@app.exception_handler(ItemNotFounError)
async def item_not_found_handler(request: Request, exc: ItemNotFounError):
    return JSONResponse(
        status_code= status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )

@app.exception_handler(sqlite3.IntegrityError)
async def sqlite_integrity_handler(request: Request, exc: sqlite3.IntegrityError):
    print(f"Global database integrity violation: {exc}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity violation, Check your foreing keys or unique contraints"}
    )
