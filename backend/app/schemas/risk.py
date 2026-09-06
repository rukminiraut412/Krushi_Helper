from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    score: int = Field(..., ge=0, le=100, example=82)
    level: str = Field(..., example="HIGH")
    contributing_factors: List[str] = Field(
        default_factory=list,
        example=["Low root-zone soil moisture (18.0%)", "Below-normal forecast rainfall"]
    )


class RiskPredictionResponse(BaseModel):
    id: Optional[int] = Field(None, example=42)
    farm_id: Optional[int] = Field(None, example=1)
    farm_name: Optional[str] = Field(None, example="Sunrise Organic Field")
    created_at: Optional[datetime] = Field(None, example="2026-09-06T17:00:00Z")
    drought: RiskItem
    flood: RiskItem
    heat: RiskItem
    extreme_rainfall: RiskItem
    overall_risk: str = Field(..., example="HIGH")
    highest_risk_type: str = Field(..., example="Drought")
    risk_score: int = Field(..., ge=0, le=100, example=82)
    risk_level: str = Field(..., example="HIGH")
    main_contributing_factors: List[str] = Field(
        default_factory=list,
        example=["Low root-zone soil moisture (18.0%)", "Severe water availability deficit"]
    )


class RiskHistoryItemResponse(BaseModel):
    id: int = Field(..., example=1)
    farm_id: int = Field(..., example=1)
    drought_score: int = Field(..., ge=0, le=100, example=82)
    flood_score: int = Field(..., ge=0, le=100, example=12)
    heat_score: int = Field(..., ge=0, le=100, example=45)
    extreme_rainfall_score: int = Field(..., ge=0, le=100, example=10)
    overall_risk: str = Field(..., example="HIGH")
    highest_risk_type: str = Field(..., example="Drought")
    risk_score: int = Field(..., ge=0, le=100, example=82)
    risk_level: str = Field(..., example="HIGH")
    main_contributing_factors: List[str] = Field(
        default_factory=list,
        example=["Low root-zone soil moisture (18.0%)"]
    )
    created_at: datetime = Field(..., example="2026-09-06T17:00:00Z")

    class Config:
        from_attributes = True


class RiskCustomPredictionRequest(BaseModel):
    temperature: float = Field(..., example=36.5)
    rainfall: float = Field(0.0, example=0.0)
    humidity: float = Field(..., example=42.0)
    soil_moisture: float = Field(..., example=19.5)
    forecast_rainfall: float = Field(0.0, example=2.0)
    historical_rainfall: float = Field(15.0, example=12.0)
    historical_temperature: float = Field(35.0, example=34.5)
    crop_type: str = Field("Cotton", example="Wheat")
    soil_type: str = Field("Black Soil", example="Black Soil")
    water_availability: str = Field("Low / Moderate Deficit", example="Critical Deficit")
