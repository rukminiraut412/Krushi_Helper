from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.farm import Farm
from app.models.risk_prediction import RiskPrediction
from app.schemas.risk import (
    RiskPredictionResponse,
    RiskCustomPredictionRequest,
    RiskItem,
    RiskHistoryItemResponse
)
from app.services.weather_service import weather_service
from app.services.soil_service import soil_service
from app.services.alert_service import alert_service
from app.ml.risk_engine import run_risk_inference, get_risk_explanation

router = APIRouter(prefix="/risk", tags=["AI Climate Risk Prediction"])


@router.post(
    "/predict",
    response_model=RiskPredictionResponse,
    summary="Predict Climate Risks with Custom Features",
    description="Runs the RandomForest ML pipeline on custom agro-meteorological features."
)
def predict_custom_risk(payload: RiskCustomPredictionRequest) -> RiskPredictionResponse:
    features = payload.model_dump()
    predictions = run_risk_inference(features)
    explanation = get_risk_explanation(predictions)

    return RiskPredictionResponse(
        id=None,
        farm_id=None,
        farm_name="Custom Feature Evaluation",
        created_at=None,
        drought=RiskItem(**predictions["drought"]),
        flood=RiskItem(**predictions["flood"]),
        heat=RiskItem(**predictions["heat"]),
        extreme_rainfall=RiskItem(**predictions["extreme_rainfall"]),
        overall_risk=explanation["overall_risk"],
        highest_risk_type=explanation["highest_risk_type"],
        risk_score=explanation["risk_score"],
        risk_level=explanation["risk_level"],
        main_contributing_factors=explanation["main_contributing_factors"]
    )


@router.get(
    "/farm/{farm_id}",
    response_model=RiskPredictionResponse,
    summary="Predict Climate Risks for a Farm",
    description="Executes complete prediction pipeline: Farm -> Climate Data -> ML Model -> Risk Scores -> Risk Level -> Database."
)
async def predict_farm_risk(
    farm_id: int,
    db: Session = Depends(get_db)
) -> RiskPredictionResponse:
    # 1. Farm: Verify farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found."
        )

    # 2. Climate Data: Gather live/calibrated weather, soil, and historical trends
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

    # Assemble complete feature vector for ML engine
    features = {
        "temperature": weather.temperature,
        "rainfall": weather.rainfall,
        "humidity": weather.humidity,
        "soil_moisture": soil.soil_moisture,
        "forecast_rainfall": weather.forecast_rainfall,
        "historical_rainfall": round(hist_rain, 1),
        "historical_temperature": round(hist_temp, 1),
        "crop_type": farm.crop or "Cotton",
        "soil_type": farm.soil_type or "Black Soil",
        "water_availability": soil.water_availability,
    }

    # 3. ML Model: Run inference pipeline
    predictions = run_risk_inference(features)

    # 4. Risk Scores, Risk Level, and Explanation Synthesis
    explanation = get_risk_explanation(predictions)

    # 5. Database: Persist prediction record in PostgreSQL
    db_record = RiskPrediction(
        farm_id=farm.id,
        drought_score=predictions["drought"]["score"],
        flood_score=predictions["flood"]["score"],
        heat_score=predictions["heat"]["score"],
        extreme_rainfall_score=predictions["extreme_rainfall"]["score"],
        risk_level=explanation["overall_risk"],
        contributing_factors=explanation["main_contributing_factors"]
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    # 6. Alert System: Automatically create alert if evaluated risk is HIGH (>= 71)
    if explanation["overall_risk"] == "HIGH" or explanation["risk_score"] >= 71:
        alert_service.create_alert_if_high_risk(
            farm=farm,
            risk_type=explanation["highest_risk_type"],
            risk_score=explanation["risk_score"],
            risk_level=explanation["overall_risk"],
            factors=explanation["main_contributing_factors"],
            db=db
        )

    return RiskPredictionResponse(
        id=db_record.id,
        farm_id=farm.id,
        farm_name=farm.farm_name,
        created_at=db_record.created_at,
        drought=RiskItem(**predictions["drought"]),
        flood=RiskItem(**predictions["flood"]),
        heat=RiskItem(**predictions["heat"]),
        extreme_rainfall=RiskItem(**predictions["extreme_rainfall"]),
        overall_risk=explanation["overall_risk"],
        highest_risk_type=explanation["highest_risk_type"],
        risk_score=explanation["risk_score"],
        risk_level=explanation["risk_level"],
        main_contributing_factors=explanation["main_contributing_factors"]
    )


@router.get(
    "/farm/{farm_id}/history",
    response_model=List[RiskHistoryItemResponse],
    summary="Get Farm Risk Prediction History",
    description="Returns chronological history of previous AI risk predictions stored in PostgreSQL for the specified farm."
)
def get_farm_risk_history(
    farm_id: int,
    db: Session = Depends(get_db)
) -> List[RiskHistoryItemResponse]:
    # 1. Verify farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found."
        )

    # 2. Query stored predictions in descending order of creation
    records = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.farm_id == farm_id)
        .order_by(RiskPrediction.created_at.desc())
        .all()
    )

    history_items = []
    for rec in records:
        scores = {
            "Drought": rec.drought_score,
            "Flood / Inundation": rec.flood_score,
            "Heat Stress": rec.heat_score,
            "Extreme Rainfall": rec.extreme_rainfall_score,
        }
        highest_type = max(scores, key=scores.get)
        highest_score = scores[highest_type]

        history_items.append(
            RiskHistoryItemResponse(
                id=rec.id,
                farm_id=rec.farm_id,
                drought_score=rec.drought_score,
                flood_score=rec.flood_score,
                heat_score=rec.heat_score,
                extreme_rainfall_score=rec.extreme_rainfall_score,
                overall_risk=rec.risk_level,
                highest_risk_type=highest_type,
                risk_score=highest_score,
                risk_level=rec.risk_level,
                main_contributing_factors=rec.contributing_factors or [],
                created_at=rec.created_at
            )
        )

    return history_items
