from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AdvisoryGenerateRequest(BaseModel):
    farm_id: int = Field(..., example=1)
    crop: Optional[str] = Field(None, example="Soybean")
    risk_type: Optional[str] = Field(None, example="Drought")
    risk_level: Optional[str] = Field(None, example="HIGH")
    language: Optional[str] = Field("en", example="mr")


class AdvisoryResponse(BaseModel):
    id: Optional[int] = Field(None, example=1)
    farm_id: int = Field(..., example=1)
    farm_name: Optional[str] = Field(None, example="Sunrise Organic Field")
    crop: str = Field(..., example="Soybean")
    risk_type: str = Field(..., example="Drought")
    risk_score: int = Field(..., example=85)
    risk_level: str = Field(..., example="HIGH")
    title: str = Field(..., example="Critical Drought & Moisture Deficit Advisory for Soybean")
    explanation: str = Field(..., example="Detailed agro-climatic context explanation...")
    recommendations: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)
    urgency: str = Field(..., example="CRITICAL")
    time_window: str = Field(..., example="Immediate (Within 6–12 hours)")
    language: str = Field("en", example="en")
    created_at: Optional[datetime] = Field(None, example="2026-09-06T17:30:00Z")

    class Config:
        from_attributes = True
