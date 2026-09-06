from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.farm import Farm
from app.schemas.climate import WeatherDataResponse, SoilDataResponse, HistoricalClimatePoint
from app.services.weather_service import weather_service
from app.services.soil_service import soil_service
from app.api.deps import get_current_user

router = APIRouter(tags=["Climate & Soil Telemetry"])


@router.get(
    "/weather/{farm_id}",
    response_model=WeatherDataResponse,
    summary="Get Weather Telemetry for a Farm",
    description="Returns current temperature, rainfall, humidity, wind speed, and 24-48h rainfall forecast for a specific farm."
)
async def get_farm_weather(
    farm_id: int,
    db: Session = Depends(get_db)
) -> WeatherDataResponse:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} was not found."
        )

    weather_data = await weather_service.get_weather_for_farm(
        farm_id=farm.id,
        farm_name=farm.farm_name,
        latitude=farm.latitude,
        longitude=farm.longitude
    )
    return weather_data


@router.get(
    "/soil/{farm_id}",
    response_model=SoilDataResponse,
    summary="Get Soil Health & Moisture Telemetry for a Farm",
    description="Returns volumetric soil moisture, soil type, water availability category, and condition assessment."
)
async def get_farm_soil(
    farm_id: int,
    db: Session = Depends(get_db)
) -> SoilDataResponse:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} was not found."
        )

    soil_data = soil_service.get_soil_data_for_farm(
        farm_id=farm.id,
        farm_name=farm.farm_name,
        soil_type=farm.soil_type,
        irrigation_available=farm.irrigation_available
    )
    return soil_data


@router.get(
    "/weather/{farm_id}/history",
    response_model=List[HistoricalClimatePoint],
    summary="Get Historical Climate Data for a Farm",
    description="Returns past rainfall and temperature series for chart rendering."
)
async def get_farm_weather_history(
    farm_id: int,
    days: int = 14,
    db: Session = Depends(get_db)
) -> List[HistoricalClimatePoint]:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} was not found."
        )

    return weather_service.get_historical_climate(farm_id=farm_id, days=days)
