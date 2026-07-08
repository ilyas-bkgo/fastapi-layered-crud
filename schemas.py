from pydantic import BaseModel, Field


# USER SCHEMAS
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="Unique username")
    email: str
    password: str = Field(min_length=6, description="Raw password sent by user")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


# ITEM SCHEMAS


# Inbound model = > what the client sends
class ItemCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    completed: bool = False


# Outbound model => what we guarentee we return to the client
class ItemResponse(BaseModel):
    id: int
    name: str
    completed: bool
    user_id: int

    class Config:
        from_attributes = True



class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
