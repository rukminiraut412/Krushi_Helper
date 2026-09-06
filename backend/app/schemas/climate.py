from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class WeatherDataResponse(BaseModel):
    farm_id: int
    farm_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    temperature: float = Field(..., description="Temperature in degrees Celsius", example=28.4)
    rainfall: float = Field(..., description="Current rainfall in mm", example=0.0)
    humidity: float = Field(..., description="Relative humidity percentage", example=62.0)
    wind_speed: float = Field(..., description="Wind speed in km/h", example=14.2)
    forecast_rainfall: float = Field(..., description="Forecasted rainfall for next 24-48 hours in mm", example=12.5)
    condition: str = Field(..., description="Short weather condition description", example="Partly Cloudy")
    timestamp: datetime
    is_demo: bool = Field(True, description="Indicates if telemetry is simulated demo mode data")
    data_source: str = Field(..., description="Source of the weather data")


class HistoricalClimatePoint(BaseModel):
    date: str
    rainfall_mm: float
    temp_max_c: float
    temp_min_c: float


class SoilDataResponse(BaseModel):
    farm_id: int
    farm_name: str
    soil_type: str
    soil_moisture: float = Field(..., description="Volumetric soil moisture percentage (0-100%)", example=38.5)
    water_availability: str = Field(..., description="Water availability index", example="Adequate")
    soil_condition: str = Field(..., description="Agronomic condition of the soil", example="Optimal moisture for crop root zone")
    ph_level: Optional[float] = Field(6.8, description="Estimated soil pH", example=6.8)
    organic_matter_pct: Optional[float] = Field(1.2, description="Organic matter percentage", example=1.2)
    timestamp: datetime
    is_demo: bool = Field(True, description="Indicates if telemetry is simulated demo mode data")
    data_source: str = Field(..., description="Source of the soil data / sensor gateway")
    sensor_status: str = Field("Simulated IoT Gateway", description="IoT sensor gateway operational status")
