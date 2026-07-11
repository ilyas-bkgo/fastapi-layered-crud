from fastapi import FastAPI

from database import init_db
from routers import todos, users

app = FastAPI()
init_db()


app.include_router(users.router)
app.include_router(todos.router)
