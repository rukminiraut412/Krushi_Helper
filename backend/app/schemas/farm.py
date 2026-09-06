from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FarmBase(BaseModel):
    farm_name: str = Field(..., min_length=1, max_length=100, example="Ganga Farm Parcel 1")
    area: float = Field(..., gt=0, example=3.5, description="Area in acres (must be positive)")
    crop: str = Field(..., min_length=1, max_length=100, example="Wheat", description="Primary crop cultivated")
    sowing_date: Optional[date] = Field(None, example="2026-06-15", description="Sowing date (YYYY-MM-DD)")
    soil_type: Optional[str] = Field(None, max_length=50, example="Black Soil (Vertisol)")
    irrigation_available: bool = Field(default=False, example=True)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, example=18.5204)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, example=73.8567)

    @field_validator("farm_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Farm name cannot be empty.")
        return s

    @field_validator("crop")
    @classmethod
    def validate_crop(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Crop cannot be empty.")
        return s

    @field_validator("area")
    @classmethod
    def validate_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Area must be a positive number greater than 0.")
        return round(v, 2)


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    farm_name: Optional[str] = Field(None, min_length=1, max_length=100)
    area: Optional[float] = Field(None, gt=0)
    crop: Optional[str] = Field(None, min_length=1, max_length=100)
    sowing_date: Optional[date] = None
    soil_type: Optional[str] = Field(None, max_length=50)
    irrigation_available: Optional[bool] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

    @field_validator("farm_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            if not s:
                raise ValueError("Farm name cannot be empty.")
            return s
        return v

    @field_validator("crop")
    @classmethod
    def validate_crop(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            if not s:
                raise ValueError("Crop cannot be empty.")
            return s
        return v


class FarmResponse(FarmBase):
    id: int
    farmer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
