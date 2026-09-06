from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.risk_prediction import RiskPrediction
from app.models.alert import Alert
from app.ml.risk_engine import run_risk_inference, get_risk_explanation
from app.services.alert_service import alert_service
from app.services.advisory_service import advisory_service
from app.schemas.risk import RiskPredictionResponse, RiskItem
from app.schemas.alert import AlertItemResponse
from app.schemas.advisory import AdvisoryResponse


SCENARIO_PRESETS: Dict[str, Dict[str, Any]] = {
    "heavy_rainfall": {
        "key": "heavy_rainfall",
        "title": "Severe Heavy Rainfall / Cloudburst Scenario",
        "temperature": 23.5,
        "rainfall": 125.0,
        "humidity": 94.0,
        "soil_moisture": 88.0,
        "forecast_rainfall": 95.0,
        "historical_rainfall": 180.0,
        "historical_temperature": 25.0,
        "water_availability": "Excessive / Waterlogged",
        "description": "Simulates 125mm deluge within 24h with saturated topsoil and extreme waterlogging.",
        "sim_factor": "SIMULATED: 125mm deluge with severe drainage impediment and waterlogging",
    },
    "drought": {
        "key": "drought",
        "title": "Severe Meteorological Drought Scenario",
        "temperature": 40.5,
        "rainfall": 0.0,
        "humidity": 16.0,
        "soil_moisture": 11.0,
        "forecast_rainfall": 0.0,
        "historical_rainfall": 5.0,
        "historical_temperature": 39.0,
        "water_availability": "Critical Deficit / Parched",
        "description": "Simulates 40°C+ heat with 0mm precipitation and soil moisture depleted below wilting point.",
        "sim_factor": "SIMULATED: Prolonged 0mm rainfall with severe root-zone moisture deficit",
    },
    "heatwave": {
        "key": "heatwave",
        "title": "Extreme Canopy Heatwave Stress Scenario",
        "temperature": 44.8,
        "rainfall": 0.0,
        "humidity": 21.0,
        "soil_moisture": 19.0,
        "forecast_rainfall": 0.0,
        "historical_rainfall": 12.0,
        "historical_temperature": 43.0,
        "water_availability": "Low",
        "description": "Simulates 44.8°C scorching solar radiation causing rapid canopy desiccation.",
        "sim_factor": "SIMULATED: Dangerous 44.8°C thermal spike during critical crop phenology",
    },
}


class SimulationService:

    def get_available_scenarios(self) -> list[Dict[str, Any]]:
        return [
            {
                "key": s["key"],
                "title": s["title"],
                "description": s["description"],
                "simulated_inputs": {
                    "temperature": s["temperature"],
                    "rainfall": s["rainfall"],
                    "humidity": s["humidity"],
                    "soil_moisture": s["soil_moisture"],
                    "forecast_rainfall": s["forecast_rainfall"],
                    "water_availability": s["water_availability"],
                }
            }
            for s in SCENARIO_PRESETS.values()
        ]

    def run_simulation(
        self,
        farm_id: int,
        scenario_key: str,
        db: Session,
        lang: str = "en"
    ) -> Dict[str, Any]:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if not farm:
            raise ValueError(f"Farm with ID {farm_id} not found.")

        scenario = SCENARIO_PRESETS.get(scenario_key.lower())
        if not scenario:
            raise ValueError(
                f"Invalid scenario '{scenario_key}'. Choose from: {list(SCENARIO_PRESETS.keys())}"
            )

        # 1. Construct modified feature vector based on simulation preset + farm characteristics
        features = {
            "temperature": scenario["temperature"],
            "rainfall": scenario["rainfall"],
            "humidity": scenario["humidity"],
            "soil_moisture": scenario["soil_moisture"],
            "forecast_rainfall": scenario["forecast_rainfall"],
            "historical_rainfall": scenario["historical_rainfall"],
            "historical_temperature": scenario["historical_temperature"],
            "crop_type": farm.crop or "Cotton",
            "soil_type": farm.soil_type or "Black Soil",
            "water_availability": scenario["water_availability"],
        }

        # 2. Run actual Random Forest ML risk inference
        predictions = run_risk_inference(features)
        explanation = get_risk_explanation(predictions)

        # 3. Augment contributing factors with explicit [SIMULATED SCENARIO] badge
        annotated_factors = [scenario["sim_factor"]] + explanation["main_contributing_factors"]

        # 4. Persist simulation prediction in PostgreSQL
        prediction_record = RiskPrediction(
            farm_id=farm.id,
            drought_score=predictions["drought"]["score"],
            flood_score=predictions["flood"]["score"],
            heat_score=predictions["heat"]["score"],
            extreme_rainfall_score=predictions["extreme_rainfall"]["score"],
            risk_level=explanation["overall_risk"],
            contributing_factors=annotated_factors
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        # 5. Automatically create HIGH-risk alert in PostgreSQL if score >= 71
        alert_obj: Optional[Alert] = None
        if explanation["overall_risk"] == "HIGH" or explanation["risk_score"] >= 71:
            alert_obj = alert_service.create_alert_if_high_risk(
                farm=farm,
                risk_type=explanation["highest_risk_type"],
                risk_score=explanation["risk_score"],
                risk_level=explanation["overall_risk"],
                factors=annotated_factors,
                db=db
            )

        # 6. Generate updated agronomic advisory for the simulated scenario
        advisory_data = advisory_service.generate_advisory(
            farm_id=farm.id,
            farm_name=farm.farm_name,
            crop=farm.crop or "Cotton",
            soil_type=farm.soil_type or "Black Soil",
            soil_moisture=float(features["soil_moisture"]),
            water_availability=str(features["water_availability"]),
            temperature=float(features["temperature"]),
            rainfall=float(features["rainfall"]),
            forecast_rainfall=float(features["forecast_rainfall"]),
            humidity=float(features["humidity"]),
            risk_type=explanation["highest_risk_type"],
            risk_score=explanation["risk_score"],
            risk_level=explanation["overall_risk"],
            language=lang
        )

        prediction_dto = RiskPredictionResponse(
            id=prediction_record.id,
            farm_id=farm.id,
            farm_name=farm.farm_name,
            created_at=prediction_record.created_at,
            drought=RiskItem(**predictions["drought"]),
            flood=RiskItem(**predictions["flood"]),
            heat=RiskItem(**predictions["heat"]),
            extreme_rainfall=RiskItem(**predictions["extreme_rainfall"]),
            overall_risk=explanation["overall_risk"],
            highest_risk_type=explanation["highest_risk_type"],
            risk_score=explanation["risk_score"],
            risk_level=explanation["risk_level"],
            main_contributing_factors=annotated_factors
        )

        return {
            "is_simulation": True,
            "scenario": scenario_key,
            "scenario_title": scenario["title"],
            "simulated_inputs": {
                "temperature": scenario["temperature"],
                "rainfall": scenario["rainfall"],
                "humidity": scenario["humidity"],
                "soil_moisture": scenario["soil_moisture"],
                "forecast_rainfall": scenario["forecast_rainfall"],
                "water_availability": scenario["water_availability"],
            },
            "prediction": prediction_dto.model_dump(),
            "advisory": advisory_data,
            "alert_created": alert_obj is not None,
            "alert": AlertItemResponse.model_validate(alert_obj).model_dump() if alert_obj else None,
        }


simulation_service = SimulationService()
