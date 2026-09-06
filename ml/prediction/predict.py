"""
Inference and Risk Scoring Pipeline for KrushiRakshak.
Loads trained model bundle from ml/models/climate_risk_models.joblib
and computes calibrated risk scores, risk levels, and explainable contributing factors.
"""

import os
from typing import Dict, Any, List
import joblib
import pandas as pd
import numpy as np

# Cache loaded bundle in memory
_MODEL_BUNDLE = None

def get_model_bundle():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ml_dir = os.path.dirname(current_dir)
        model_path = os.path.join(ml_dir, "models", "climate_risk_models.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Run train_model.py first.")
        _MODEL_BUNDLE = joblib.load(model_path)
    return _MODEL_BUNDLE


def classify_risk_level(score: int) -> str:
    """
    0–30 = LOW
    31–70 = MEDIUM
    71–100 = HIGH
    """
    if score <= 30:
        return "LOW"
    elif score <= 70:
        return "MEDIUM"
    return "HIGH"


def extract_contributing_factors(risk_type: str, features: Dict[str, Any], score: int) -> List[str]:
    """
    Provides clear, explainable factors justifying the risk classification.
    """
    factors = []
    temp = float(features.get("temperature", 28.0))
    rain = float(features.get("rainfall", 0.0))
    hum = float(features.get("humidity", 60.0))
    moist = float(features.get("soil_moisture", 30.0))
    fc_rain = float(features.get("forecast_rainfall", 0.0))
    hist_rain = float(features.get("historical_rainfall", 30.0))
    water = str(features.get("water_availability", "Adequate"))
    crop = str(features.get("crop_type", "Crop"))

    if risk_type == "drought":
        if moist < 25.0:
            factors.append(f"Low root-zone soil moisture ({moist}%)")
        if "Deficit" in water:
            factors.append(f"Severe water availability deficit ({water})")
        if temp > 33.0:
            factors.append(f"High ambient temperature ({temp}°C) accelerating evapotranspiration")
        if fc_rain < 5.0:
            factors.append(f"Dry forecast over next 48h ({fc_rain}mm)")
        if hist_rain < 20.0:
            factors.append(f"Prolonged dry spell over past 14 days ({hist_rain}mm total)")

    elif risk_type == "flood":
        if fc_rain > 25.0:
            factors.append(f"Heavy upcoming precipitation forecast ({fc_rain}mm)")
        if rain > 15.0:
            factors.append(f"Elevated immediate rainfall ({rain}mm)")
        if moist > 40.0:
            factors.append(f"High soil saturation limiting runoff drainage ({moist}%)")
        if water == "Saturated":
            factors.append("Parcel field already waterlogged")
        if hist_rain > 90.0:
            factors.append(f"High antecedent rainfall accumulation ({hist_rain}mm)")

    elif risk_type == "heat":
        if temp >= 35.0:
            factors.append(f"High ambient temperature ({temp}°C)")
        if hum < 45.0:
            factors.append(f"Low relative humidity ({hum}%) compounding thermal stress")
        if crop in ["Wheat", "Mustard"] and temp > 32.0:
            factors.append(f"{crop} variety exhibits high sensitivity to thermal spikes")
        if moist < 25.0:
            factors.append(f"Depleted soil moisture reduces transpirational cooling")

    elif risk_type == "extreme_rainfall":
        if fc_rain >= 35.0:
            factors.append(f"Forecast rainfall volume exceeds safe threshold ({fc_rain}mm)")
        if rain >= 25.0:
            factors.append(f"High active precipitation intensity ({rain}mm/hr)")
        if hum >= 80.0:
            factors.append(f"Near-saturated atmospheric moisture ({hum}%)")

    # If score is elevated but no specific trigger caught, provide general indicator
    if not factors and score > 30:
        factors.append(f"Aggregated micro-climate vulnerability for {crop}")
    elif not factors:
        factors.append("All climatic indicators within safe operational bounds")

    return factors


def predict_climate_risks(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes trained ML models on input features and returns structured risk predictions.
    """
    bundle = get_model_bundle()
    preprocessor = bundle["preprocessor"]
    models = bundle["models"]

    num_cols = bundle["numeric_features"]
    cat_cols = bundle["categorical_features"]
    expected_cols = num_cols + cat_cols

    # Ensure required features exist with defaults
    prepared = {}
    for col in expected_cols:
        prepared[col] = [features.get(col, 0.0 if col in num_cols else "Standard")]

    input_df = pd.DataFrame(prepared)
    X_trans = preprocessor.transform(input_df)

    predictions = {}
    for risk_name, model in models.items():
        prob = model.predict_proba(X_trans)[0][1]
        score = int(round(prob * 100))
        level = classify_risk_level(score)
        factors = extract_contributing_factors(risk_name, features, score)

        predictions[risk_name] = {
            "score": score,
            "level": level,
            "contributing_factors": factors
        }

    return predictions


RISK_DISPLAY_NAMES = {
    "drought": "Drought",
    "flood": "Flood / Inundation",
    "heat": "Heat Stress",
    "extreme_rainfall": "Extreme Rainfall"
}


def synthesize_risk_explanation(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes overall risk, highest risk type, risk score, risk level,
    and main contributing factors from the ensemble predictions.
    """
    sorted_hazards = sorted(
        predictions.items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

    highest_key, highest_data = sorted_hazards[0]
    highest_risk_type = RISK_DISPLAY_NAMES.get(highest_key, highest_key.replace("_", " ").title())
    risk_score = highest_data["score"]
    risk_level = highest_data["level"]
    overall_risk = risk_level

    # Gather main contributing factors
    main_factors: List[str] = []
    # Primary hazard factors
    for factor in highest_data.get("contributing_factors", []):
        if factor not in main_factors:
            main_factors.append(factor)

    # Secondary hazards if score > 30
    for hazard_key, hazard_data in sorted_hazards[1:]:
        if hazard_data["score"] > 30:
            name = RISK_DISPLAY_NAMES.get(hazard_key, hazard_key.title())
            for factor in hazard_data.get("contributing_factors", []):
                formatted = f"[{name}] {factor}"
                if formatted not in main_factors and factor not in main_factors:
                    main_factors.append(formatted)

    if not main_factors:
        main_factors.append("All agro-climatic indicators remain within safe operational bounds")

    return {
        "overall_risk": overall_risk,
        "highest_risk_type": highest_risk_type,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "main_contributing_factors": main_factors
    }


if __name__ == "__main__":
    test_sample = {
        "temperature": 38.5,
        "rainfall": 0.0,
        "humidity": 32.0,
        "soil_moisture": 16.0,
        "forecast_rainfall": 0.0,
        "historical_rainfall": 4.0,
        "historical_temperature": 37.0,
        "crop_type": "Wheat",
        "soil_type": "Black Soil",
        "water_availability": "Critical Deficit",
    }
    result = predict_climate_risks(test_sample)
    print("Test Sample Prediction Output:")
    import pprint
    pprint.pprint(result)
