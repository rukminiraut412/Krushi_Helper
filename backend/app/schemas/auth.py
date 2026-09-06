import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.user import UserRole


class FarmerRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Ramesh Patel")
    mobile: str = Field(..., min_length=10, max_length=15, example="9876543210")
    password: str = Field(..., min_length=6, max_length=100, example="Pass1234")
    preferred_language: str = Field(default="en", max_length=20, example="hi")
    village: Optional[str] = Field(None, max_length=100, example="Khed Shivapur")
    district: Optional[str] = Field(None, max_length=100, example="Pune")
    state: Optional[str] = Field(None, max_length=100, example="Maharashtra")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, example=18.3541)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, example=73.8543)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        clean = re.sub(r"[\s\-+]", "", v)
        if not clean.isdigit() or len(clean) < 10 or len(clean) > 15:
            raise ValueError("Mobile number must be between 10 and 15 digits.")
        return clean

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_strip = v.strip()
        if len(v_strip) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v_strip


class LoginRequest(BaseModel):
    mobile: str = Field(..., example="9876543210")
    password: str = Field(..., example="Pass1234")

    @field_validator("mobile")
    @classmethod
    def clean_mobile(cls, v: str) -> str:
        return re.sub(r"[\s\-+]", "", v)


class UserProfileDTO(BaseModel):
    id: int
    name: str
    mobile: str
    role: UserRole
    preferred_language: str
    created_at: datetime
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user: UserProfileDTO
