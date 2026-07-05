from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(min_length=3, max_length=50, description="Title of the todo item")
    completed: bool = False
