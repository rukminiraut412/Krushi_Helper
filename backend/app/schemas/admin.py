from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HazardCount(BaseModel):
    drought: int = 0
    flood: int = 0
    heat: int = 0
    extreme_rainfall: int = 0


class RiskDistribution(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0


class CropCount(BaseModel):
    crop: str
    count: int
    area_acres: float


class PriorityInterventionItem(BaseModel):
    farm_id: int
    farm_name: str
    farmer_id: int
    farmer_name: str
    mobile: str
    crop: str
    area: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    risk_type: str
    risk_score: int
    risk_level: str
    vulnerability_level: str
    recommended_action: str
    timestamp: datetime


class RecentHighRiskFarm(BaseModel):
    farm_id: int
    farm_name: str
    farmer_name: str
    crop: str
    risk_type: str
    risk_score: int
    risk_level: str
    created_at: datetime


class AdminDashboardStatsResponse(BaseModel):
    total_farmers: int
    total_farms: int
    high_risk_farms: int
    medium_risk_farms: int
    low_risk_farms: int
    drought_risk_farms: int
    flood_risk_farms: int
    heat_stress_farms: int
    extreme_rainfall_farms: int
    risk_distribution: RiskDistribution
    risk_level_percentages: Dict[str, float]
    crop_distribution: List[CropCount]
    recent_high_risk_farms: List[RecentHighRiskFarm]
    priority_intervention_list: List[PriorityInterventionItem]


class RiskMapPoint(BaseModel):
    farm_id: int
    farm_name: str
    farmer_name: str
    mobile: str
    crop: str
    area: float
    latitude: float
    longitude: float
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    risk_type: str
    risk_score: int
    risk_level: str
    vulnerability_score: int
    vulnerability_level: str
    contributing_factors: List[str]
    irrigation_available: bool
    soil_type: Optional[str] = None
    latest_evaluated_at: Optional[datetime] = None


class VulnerableAreaSummary(BaseModel):
    district: str
    state: str
    farm_count: int
    avg_risk_score: float
    avg_vulnerability_score: float
    dominant_hazard: str
    high_risk_count: int


class VulnerabilityAssessmentResponse(BaseModel):
    most_vulnerable_farms: List[PriorityInterventionItem]
    vulnerable_areas: List[VulnerableAreaSummary]
    priority_intervention_areas: List[str]
    main_risk_factors: List[str]
    total_vulnerable_farms: int


class AdminFarmerItem(BaseModel):
    id: int
    user_id: int
    name: str
    mobile: str
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    preferred_language: str
    farm_count: int
    highest_risk_level: Optional[str] = None
    highest_risk_score: Optional[int] = None
    created_at: datetime
