from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import datetime


# USER SCHEMAS
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="Unique username")
    email: EmailStr
    password: str = Field(min_length=6, description="Raw password sent by user")

    # costum validator to prevent whitespace-only usernames
    @field_validator("username")
    @classmethod
    def validate_username(cls, value:str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Username cannot be empty or whitespace")
        if " " in cleaned_value:
            raise ValueError("Username cannot contain whitespace")
        return cleaned_value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime

    # class Config:
    #     from_attributes = True


# ITEM SCHEMAS
# Inbound model => what the client sends
class ItemCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    completed: bool = False

    @field_validator("name")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        cleaned_value = value.strip()
        if len(cleaned_value) < 3:
            raise ValueError("Task name must be at leat 3 non-whitespace characters")
        return cleaned_value

# Outbound model => what we guarentee we return to the client
class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    completed: bool
    user_id: int
    created_at: datetime

    # class Config:
    #     from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
