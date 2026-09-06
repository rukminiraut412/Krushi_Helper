from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AlertItemResponse(BaseModel):
    id: int = Field(..., example=1)
    farmer_id: int = Field(..., example=1)
    farm_id: int = Field(..., example=1)
    farm_name: str = Field(..., example="Sunrise Organic Field")
    crop: str = Field(..., example="Cotton")
    risk_type: str = Field(..., example="Drought")
    risk_score: int = Field(..., example=85)
    risk_level: str = Field(..., example="HIGH")
    short_explanation: str = Field(..., example="Critical soil moisture deficit below 15%.")
    recommended_action: str = Field(..., example="Apply protective irrigation and potassium nitrate foliar spray.")
    is_read: bool = Field(False, example=False)
    created_at: datetime = Field(..., example="2026-09-06T17:45:00Z")

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    farmer_id: int = Field(..., example=1)
    unread_count: int = Field(..., example=2)
    alerts: List[AlertItemResponse] = Field(default_factory=list)


class AlertSimulateRequest(BaseModel):
    farm_id: int = Field(..., example=1)
    risk_type: Optional[str] = Field("Drought", example="Drought")
    risk_score: Optional[int] = Field(85, example=85)
    short_explanation: Optional[str] = Field(None, example="Simulated high thermal spike and moisture deficit.")
    recommended_action: Optional[str] = Field(None, example="Provide emergency irrigation immediately.")
