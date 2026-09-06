from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Ramesh Kumar")
    mobile: str = Field(..., min_length=10, max_length=15, example="9876543210")
    role: UserRole = Field(default=UserRole.FARMER, example=UserRole.FARMER)
    preferred_language: str = Field(default="en", example="hi")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="SecurePass123!")


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
