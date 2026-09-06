from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.farm import Farm
from app.models.advisory import Advisory
from app.schemas.advisory import AdvisoryGenerateRequest, AdvisoryResponse
from app.services.weather_service import weather_service
from app.services.soil_service import soil_service
from app.services.advisory_service import advisory_service, SUPPORTED_LANGUAGES
from app.ml.risk_engine import run_risk_inference, get_risk_explanation

router = APIRouter(prefix="/advisories", tags=["Personalized Multilingual Advisories"])


@router.post(
    "/generate",
    response_model=AdvisoryResponse,
    summary="Generate Crop-Specific Climate Advisory",
    description="Generates personalized agronomic recommendations based on farm telemetry, AI risk evaluation, and language preference. Stores result in PostgreSQL."
)
async def generate_advisory(
    payload: AdvisoryGenerateRequest,
    db: Session = Depends(get_db)
) -> AdvisoryResponse:
    # 1. Verify farm exists
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {payload.farm_id} not found."
        )

    # 2. Gather live/calibrated agro-climatic telemetry
    weather = await weather_service.get_weather_for_farm(
        farm_id=farm.id,
        farm_name=farm.farm_name,
        latitude=farm.latitude,
        longitude=farm.longitude
    )

    soil = soil_service.get_soil_data_for_farm(
        farm_id=farm.id,
        farm_name=farm.farm_name,
        soil_type=farm.soil_type,
        irrigation_available=farm.irrigation_available
    )

    history = weather_service.get_historical_climate(farm_id=farm.id, days=14)
    if history:
        hist_rain = sum(h.rainfall_mm for h in history)
        hist_temp = sum(h.temp_max_c for h in history) / len(history)
    else:
        hist_rain = 25.0
        hist_temp = weather.temperature

    crop_target = payload.crop or farm.crop or "Cotton"

    # 3. Determine Risk Context (from ML Model or explicit scenario test)
    if payload.risk_type and payload.risk_level:
        risk_type = payload.risk_type
        risk_level = payload.risk_level.upper()
        risk_score = 85 if risk_level == "HIGH" else (50 if risk_level == "MEDIUM" else 20)
    else:
        # Run live ML risk inference
        features = {
            "temperature": weather.temperature,
            "rainfall": weather.rainfall,
            "humidity": weather.humidity,
            "soil_moisture": soil.soil_moisture,
            "forecast_rainfall": weather.forecast_rainfall,
            "historical_rainfall": round(hist_rain, 1),
            "historical_temperature": round(hist_temp, 1),
            "crop_type": crop_target,
            "soil_type": farm.soil_type or "Black Soil",
            "water_availability": soil.water_availability,
        }
        predictions = run_risk_inference(features)
        explanation = get_risk_explanation(predictions)
        risk_type = explanation["highest_risk_type"]
        risk_score = explanation["risk_score"]
        risk_level = explanation["overall_risk"]

    # 4. Generate Localized Advisory via Agronomic Engine
    language = payload.language if payload.language in SUPPORTED_LANGUAGES else "en"

    adv = advisory_service.generate_advisory(
        farm_id=farm.id,
        farm_name=farm.farm_name,
        crop=crop_target,
        soil_type=farm.soil_type or "Black Soil",
        soil_moisture=soil.soil_moisture,
        water_availability=soil.water_availability,
        temperature=weather.temperature,
        rainfall=weather.rainfall,
        forecast_rainfall=weather.forecast_rainfall,
        humidity=weather.humidity,
        risk_type=risk_type,
        risk_score=risk_score,
        risk_level=risk_level,
        language=language
    )

    # 5. Persist into PostgreSQL
    record = Advisory(
        farm_id=farm.id,
        crop=adv["crop"],
        risk_type=adv["risk_type"],
        risk_score=adv["risk_score"],
        risk_level=adv["risk_level"],
        title=adv["title"],
        explanation=adv["explanation"],
        recommendations=adv["recommendations"],
        preventive_actions=adv["preventive_actions"],
        urgency=adv["urgency"],
        time_window=adv["time_window"],
        language=adv["language"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AdvisoryResponse(
        id=record.id,
        farm_id=farm.id,
        farm_name=farm.farm_name,
        crop=record.crop,
        risk_type=record.risk_type,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        title=record.title,
        explanation=record.explanation,
        recommendations=record.recommendations,
        preventive_actions=record.preventive_actions,
        urgency=record.urgency,
        time_window=record.time_window,
        language=record.language,
        created_at=record.created_at
    )


@router.get(
    "/{farm_id}",
    response_model=AdvisoryResponse,
    summary="Get Advisory for a Farm",
    description="Retrieves the latest advisory stored in PostgreSQL for the farm in the requested language (or generates one dynamically)."
)
async def get_advisory_for_farm(
    farm_id: int,
    lang: str = Query("en", description="Language code: en, mr, hi, kn"),
    db: Session = Depends(get_db)
) -> AdvisoryResponse:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found."
        )

    target_lang = lang.lower() if lang in SUPPORTED_LANGUAGES else "en"

    # Query latest advisory for this farm in requested language
    existing = (
        db.query(Advisory)
        .filter(Advisory.farm_id == farm_id, Advisory.language == target_lang)
        .order_by(Advisory.created_at.desc())
        .first()
    )

    if existing:
        return AdvisoryResponse(
            id=existing.id,
            farm_id=existing.farm_id,
            farm_name=farm.farm_name,
            crop=existing.crop,
            risk_type=existing.risk_type,
            risk_score=existing.risk_score,
            risk_level=existing.risk_level,
            title=existing.title,
            explanation=existing.explanation,
            recommendations=existing.recommendations,
            preventive_actions=existing.preventive_actions,
            urgency=existing.urgency,
            time_window=existing.time_window,
            language=existing.language,
            created_at=existing.created_at
        )

    # If no advisory in this language yet, generate one automatically
    generate_req = AdvisoryGenerateRequest(farm_id=farm_id, language=target_lang)
    return await generate_advisory(generate_req, db)
