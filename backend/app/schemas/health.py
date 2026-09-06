from typing import Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="healthy")
    service: str = Field(..., example="KrushiRakshak API")


class DatabaseHealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    service: str = Field(..., example="KrushiRakshak Database")
    database: str = Field(default="PostgreSQL", example="PostgreSQL")
    connected: bool = Field(..., example=True)
    message: str = Field(..., example="Database connection established successfully")
    details: Optional[dict] = None
