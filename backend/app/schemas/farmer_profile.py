from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FarmerProfileBase(BaseModel):
    village: Optional[str] = Field(None, max_length=100, example="Kisan Nagar")
    district: Optional[str] = Field(None, max_length=100, example="Pune")
    state: Optional[str] = Field(None, max_length=100, example="Maharashtra")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, example=18.5204)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, example=73.8567)


class FarmerProfileCreate(FarmerProfileBase):
    user_id: int


class FarmerProfileResponse(FarmerProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
