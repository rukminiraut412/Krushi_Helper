"""
Synthetic Agro-Meteorological Climate Risk Dataset Generator for KrushiRakshak.
NOTE: This dataset is generated synthetically for prototype modeling and algorithm verification.
It does not claim to represent scientifically validated ground truth observations.
It follows realistic agronomic and meteorological relationships designed to be
seamlessly replaced with regional IMD/ICAR agricultural telemetry in production.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

NUM_SAMPLES = 2500

CROPS = ["Cotton", "Wheat", "Paddy", "Sugarcane", "Maize", "Soybean", "Pulses", "Mustard"]
SOIL_TYPES = ["Black Soil", "Alluvial Soil", "Red Soil", "Sandy Loam", "Clayey Loam"]
WATER_AVAILABILITY = ["Adequate", "Critical Deficit", "Low / Moderate Deficit", "Saturated"]

def generate_climate_risk_dataset():
    data = []

    for _ in range(NUM_SAMPLES):
        crop = np.random.choice(CROPS)
        soil = np.random.choice(SOIL_TYPES)
        water = np.random.choice(WATER_AVAILABILITY, p=[0.45, 0.20, 0.25, 0.10])

        # Temperature (15 to 46 C)
        temp = np.random.normal(loc=30.0, scale=6.0)
        temp = float(np.clip(round(temp, 1), 14.0, 48.0))

        # Relative Humidity (20 to 98 %)
        humidity = np.random.normal(loc=60.0, scale=18.0)
        humidity = float(np.clip(round(humidity, 1), 15.0, 98.0))

        # Current Rainfall (mm)
        rain_prob = 0.25 if humidity > 60 else 0.08
        if np.random.rand() < rain_prob:
            rainfall = float(round(np.random.exponential(scale=18.0), 1))
        else:
            rainfall = 0.0

        # Forecast Rainfall in next 24-48h (mm)
        if humidity > 70 or rainfall > 10:
            forecast_rainfall = float(round(np.random.exponential(scale=25.0), 1))
        else:
            forecast_rainfall = float(round(np.random.exponential(scale=3.0), 1))

        # Soil moisture (10% to 60%)
        base_moisture = 35.0 if "Black" in soil else 25.0
        if water == "Critical Deficit":
            soil_moisture = float(np.clip(round(np.random.normal(16.0, 3.0), 1), 8.0, 22.0))
        elif water == "Saturated":
            soil_moisture = float(np.clip(round(np.random.normal(52.0, 4.0), 1), 45.0, 65.0))
        else:
            soil_moisture = float(np.clip(round(np.random.normal(base_moisture, 6.0), 1), 18.0, 48.0))

        # Historical rainfall past 14 days (mm)
        if water == "Critical Deficit":
            historical_rainfall = float(round(np.random.uniform(0.0, 15.0), 1))
        elif water == "Saturated":
            historical_rainfall = float(round(np.random.uniform(90.0, 250.0), 1))
        else:
            historical_rainfall = float(round(np.random.uniform(20.0, 85.0), 1))

        # Historical temperature past 14 days
        historical_temp = float(round(temp + np.random.normal(0, 1.5), 1))

        # --- GROUND TRUTH RISK LABELS (Physics-Informed Agronomic Rules) ---
        # 1. Drought Risk
        drought_condition = (
            (soil_moisture < 22.0 and water in ["Critical Deficit", "Low / Moderate Deficit"])
            or (temp > 35.0 and historical_rainfall < 15.0 and forecast_rainfall < 5.0)
            or (water == "Critical Deficit" and rainfall == 0.0 and forecast_rainfall < 2.0)
        )
        drought_risk = 1 if drought_condition else 0

        # 2. Flood Risk
        flood_condition = (
            (soil_moisture > 40.0 and forecast_rainfall > 25.0)
            or (historical_rainfall > 90.0 and (rainfall > 15.0 or forecast_rainfall > 20.0))
            or (water == "Saturated" and (rainfall > 10.0 or forecast_rainfall > 15.0))
            or (rainfall > 40.0 and soil_moisture > 35.0)
        )
        flood_risk = 1 if flood_condition else 0

        # 3. Heat Stress Risk
        heat_condition = (
            temp >= 38.0
            or (temp >= 35.0 and humidity < 40.0 and soil_moisture < 25.0)
            or (temp >= 36.5 and crop in ["Wheat", "Mustard"])  # Rabi crops sensitive to heat
        )
        heat_risk = 1 if heat_condition else 0

        # 4. Extreme Rainfall Risk
        extreme_rain_condition = (
            forecast_rainfall >= 50.0
            or rainfall >= 45.0
            or (forecast_rainfall >= 35.0 and humidity >= 85.0)
        )
        extreme_rainfall_risk = 1 if extreme_rain_condition else 0

        data.append({
            "temperature": temp,
            "rainfall": rainfall,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "forecast_rainfall": forecast_rainfall,
            "historical_rainfall": historical_rainfall,
            "historical_temperature": historical_temp,
            "crop_type": crop,
            "soil_type": soil,
            "water_availability": water,
            "drought_risk": drought_risk,
            "flood_risk": flood_risk,
            "heat_risk": heat_risk,
            "extreme_rainfall_risk": extreme_rainfall_risk,
        })

    df = pd.DataFrame(data)
    dataset_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(dataset_dir, "climate_risk_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} records saved to: {out_path}")
    print("Class distributions:")
    for col in ["drought_risk", "flood_risk", "heat_risk", "extreme_rainfall_risk"]:
        pos = df[col].sum()
        pct = (pos / len(df)) * 100
        print(f"  - {col}: {pos}/{len(df)} ({pct:.1f}% positive)")

    return out_path

if __name__ == "__main__":
    generate_climate_risk_dataset()
