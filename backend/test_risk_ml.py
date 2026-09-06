import pprint
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_risk_prediction():
    print("=" * 65)
    print("TESTING AI CLIMATE RISK PREDICTION ENGINE (RandomForest ML)")
    print("=" * 65)

    # 1. Test GET /api/risk/farm/1
    print("\n[TEST 1] Querying GET /api/risk/farm/1...")
    res = client.get("/api/risk/farm/1")
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    print("  -> AI Risk Assessment for Farm ID 1:")
    print(f"     - Farm: {data['farm_name']}")
    for risk in ["drought", "flood", "heat", "extreme_rainfall"]:
        item = data[risk]
        assert "score" in item and 0 <= item["score"] <= 100
        assert item["level"] in ["LOW", "MEDIUM", "HIGH"]
        assert isinstance(item["contributing_factors"], list)
        print(f"     - [{risk.upper()}]: Score={item['score']} | Level={item['level']} | Factors={item['contributing_factors']}")

    # 2. Test POST /api/risk/predict with severe Drought scenario
    print("\n[TEST 2] Testing POST /api/risk/predict with Severe Drought Scenario...")
    drought_payload = {
        "temperature": 41.5,
        "rainfall": 0.0,
        "humidity": 22.0,
        "soil_moisture": 11.0,
        "forecast_rainfall": 0.0,
        "historical_rainfall": 2.0,
        "historical_temperature": 40.0,
        "crop_type": "Wheat",
        "soil_type": "Sandy Loam",
        "water_availability": "Critical Deficit"
    }
    res_drought = client.post("/api/risk/predict", json=drought_payload)
    assert res_drought.status_code == 200
    d_out = res_drought.json()
    print(f"  -> Drought Prediction: Score={d_out['drought']['score']}, Level={d_out['drought']['level']}")
    print(f"     Contributing Factors: {d_out['drought']['contributing_factors']}")
    assert d_out["drought"]["level"] == "HIGH", f"Expected HIGH drought risk, got {d_out['drought']['level']}"

    # 3. Test POST /api/risk/predict with severe Flood & Extreme Rainfall scenario
    print("\n[TEST 3] Testing POST /api/risk/predict with Severe Inundation/Flood Scenario...")
    flood_payload = {
        "temperature": 27.0,
        "rainfall": 52.0,
        "humidity": 94.0,
        "soil_moisture": 52.0,
        "forecast_rainfall": 75.0,
        "historical_rainfall": 160.0,
        "historical_temperature": 28.0,
        "crop_type": "Paddy",
        "soil_type": "Clayey Loam",
        "water_availability": "Saturated"
    }
    res_flood = client.post("/api/risk/predict", json=flood_payload)
    assert res_flood.status_code == 200
    f_out = res_flood.json()
    print(f"  -> Flood Prediction: Score={f_out['flood']['score']}, Level={f_out['flood']['level']}")
    print(f"     Contributing Factors: {f_out['flood']['contributing_factors']}")
    print(f"  -> Extreme Rainfall: Score={f_out['extreme_rainfall']['score']}, Level={f_out['extreme_rainfall']['level']}")
    print(f"     Contributing Factors: {f_out['extreme_rainfall']['contributing_factors']}")
    assert f_out["flood"]["score"] > 50, f"Expected elevated flood score, got {f_out['flood']['score']}"
    assert f_out["extreme_rainfall"]["score"] > 50, f"Expected elevated rainfall score, got {f_out['extreme_rainfall']['score']}"

    # 4. Test POST /api/risk/predict with Optimal Low-Risk conditions
    print("\n[TEST 4] Testing POST /api/risk/predict with Optimal Mild Weather...")
    mild_payload = {
        "temperature": 26.5,
        "rainfall": 5.0,
        "humidity": 60.0,
        "soil_moisture": 34.0,
        "forecast_rainfall": 8.0,
        "historical_rainfall": 45.0,
        "historical_temperature": 26.0,
        "crop_type": "Cotton",
        "soil_type": "Black Soil",
        "water_availability": "Adequate"
    }
    res_mild = client.post("/api/risk/predict", json=mild_payload)
    assert res_mild.status_code == 200
    m_out = res_mild.json()
    print(f"  -> Mild Weather Scores: Drought={m_out['drought']['score']}, Flood={m_out['flood']['score']}, Heat={m_out['heat']['score']}")
    assert m_out["drought"]["level"] == "LOW"
    assert m_out["flood"]["level"] == "LOW"
    assert m_out["heat"]["level"] == "LOW"

    print("\n" + "=" * 65)
    print("ALL AI RISK PREDICTION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    test_risk_prediction()
