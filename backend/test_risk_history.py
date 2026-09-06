"""
Automated Test Suite for KrushiRakshak AI Risk Prediction System & History Storage.
Tests the end-to-end lifecycle:
Farm -> Climate Data -> ML Model -> Risk Scores -> Risk Level & Explanation -> PostgreSQL DB -> API History
"""

import time
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.risk_prediction import RiskPrediction
from app.models.farm import Farm

client = TestClient(app)


def test_risk_prediction_and_history():
    print("=" * 70)
    print("TESTING AI RISK PREDICTION STORAGE & HISTORY SYSTEM (PostgreSQL + ML)")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Check that Farm #1 exists
        farm = db.query(Farm).filter(Farm.id == 1).first()
        assert farm is not None, "Farm #1 must exist in DB"
        print(f"[SETUP] Target Farm found: #{farm.id} '{farm.farm_name}' ({farm.crop})")

        # Record initial count of predictions for Farm #1
        initial_count = db.query(RiskPrediction).filter(RiskPrediction.farm_id == 1).count()
        print(f"[SETUP] Initial stored predictions count for Farm #1: {initial_count}")

        # -------------------------------------------------------------
        # 1. Test Prediction Pipeline (Farm -> Telemetry -> ML -> DB)
        # -------------------------------------------------------------
        print("\n[TEST 1] Triggering live risk evaluation: GET /api/risk/farm/1...")
        res1 = client.get("/api/risk/farm/1")
        assert res1.status_code == 200, f"Failed prediction request: {res1.text}"
        data1 = res1.json()

        print(f"  -> Prediction ID generated: {data1['id']}")
        print(f"  -> Farm: {data1['farm_name']}")
        print(f"  -> Overall Risk: {data1['overall_risk']}")
        print(f"  -> Highest Risk Type: {data1['highest_risk_type']}")
        print(f"  -> Risk Score: {data1['risk_score']} / 100")
        print(f"  -> Risk Level: {data1['risk_level']}")
        print(f"  -> Main Contributing Factors: {data1['main_contributing_factors']}")
        print(f"  -> Drought Score: {data1['drought']['score']} ({data1['drought']['level']})")
        print(f"  -> Flood Score: {data1['flood']['score']} ({data1['flood']['level']})")
        print(f"  -> Heat Score: {data1['heat']['score']} ({data1['heat']['level']})")
        print(f"  -> Rainfall Score: {data1['extreme_rainfall']['score']} ({data1['extreme_rainfall']['level']})")

        assert data1["id"] is not None, "Prediction ID must be returned from DB"
        assert data1["created_at"] is not None, "Timestamp must be returned"
        assert data1["overall_risk"] in ["LOW", "MEDIUM", "HIGH"]
        assert data1["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0 <= data1["risk_score"] <= 100
        assert len(data1["main_contributing_factors"]) > 0

        # Verify DB directly
        db_rec1 = db.query(RiskPrediction).filter(RiskPrediction.id == data1["id"]).first()
        assert db_rec1 is not None, "Record must exist in PostgreSQL table"
        assert db_rec1.farm_id == 1
        assert db_rec1.drought_score == data1["drought"]["score"]
        assert db_rec1.flood_score == data1["flood"]["score"]
        assert db_rec1.heat_score == data1["heat"]["score"]
        assert db_rec1.extreme_rainfall_score == data1["extreme_rainfall"]["score"]
        assert db_rec1.risk_level == data1["overall_risk"]
        print("  [OK] Direct PostgreSQL database query confirmed persistence!")

        # -------------------------------------------------------------
        # 2. Trigger Multiple Predictions to Build History
        # -------------------------------------------------------------
        print("\n[TEST 2] Generating additional predictions to populate history...")
        time.sleep(1)  # ensure small timestamp difference
        res2 = client.get("/api/risk/farm/1")
        assert res2.status_code == 200
        pred2_id = res2.json()["id"]

        time.sleep(1)
        res3 = client.get("/api/risk/farm/1")
        assert res3.status_code == 200
        pred3_id = res3.json()["id"]

        print(f"  -> Generated 3 predictions in sequence: IDs [{data1['id']}, {pred2_id}, {pred3_id}]")

        # -------------------------------------------------------------
        # 3. Test GET /api/risk/farm/{farm_id}/history
        # -------------------------------------------------------------
        print("\n[TEST 3] Querying GET /api/risk/farm/1/history...")
        hist_res = client.get("/api/risk/farm/1/history")
        assert hist_res.status_code == 200, f"Failed history request: {hist_res.text}"
        history = hist_res.json()

        print(f"  -> Total history records returned: {len(history)}")
        assert len(history) >= 3, f"Expected at least 3 records, found {len(history)}"

        # Validate descending sort order
        first_item = history[0]
        second_item = history[1]
        assert first_item["id"] == pred3_id, "Most recent prediction must be first in history"
        assert second_item["id"] == pred2_id

        # Validate structure of each history item
        for idx, item in enumerate(history[:3]):
            print(f"     Record #{idx+1} [ID={item['id']}]: Overall={item['overall_risk']} | Highest={item['highest_risk_type']} ({item['risk_score']}) | Time={item['created_at']}")
            assert "id" in item
            assert item["farm_id"] == 1
            assert 0 <= item["drought_score"] <= 100
            assert 0 <= item["flood_score"] <= 100
            assert 0 <= item["heat_score"] <= 100
            assert 0 <= item["extreme_rainfall_score"] <= 100
            assert item["overall_risk"] in ["LOW", "MEDIUM", "HIGH"]
            assert item["highest_risk_type"] in ["Drought", "Flood / Inundation", "Heat Stress", "Extreme Rainfall"]
            assert 0 <= item["risk_score"] <= 100
            assert isinstance(item["main_contributing_factors"], list)
            assert "created_at" in item

        print("  [OK] History endpoint correctly returned descending predictions with complete explanations!")

        # -------------------------------------------------------------
        # 4. Test Error Handling for Non-Existent Farm
        # -------------------------------------------------------------
        print("\n[TEST 4] Testing non-existent farm error handling...")
        res_404_pred = client.get("/api/risk/farm/99999")
        assert res_404_pred.status_code == 404, "Expected 404 for invalid farm prediction"
        res_404_hist = client.get("/api/risk/farm/99999/history")
        assert res_404_hist.status_code == 404, "Expected 404 for invalid farm history"
        print("  [OK] 404 Not Found successfully raised for non-existent farm!")

        # -------------------------------------------------------------
        # 5. Test Custom Prediction Endpoint with Explanation
        # -------------------------------------------------------------
        print("\n[TEST 5] Testing custom prediction POST /api/risk/predict explanation...")
        custom_payload = {
            "temperature": 43.0,
            "rainfall": 0.0,
            "humidity": 18.0,
            "soil_moisture": 10.0,
            "forecast_rainfall": 0.0,
            "historical_rainfall": 0.0,
            "historical_temperature": 42.0,
            "crop_type": "Wheat",
            "soil_type": "Sandy Loam",
            "water_availability": "Critical Deficit"
        }
        res_custom = client.post("/api/risk/predict", json=custom_payload)
        assert res_custom.status_code == 200
        custom_data = res_custom.json()
        print(f"  -> Custom Overall: {custom_data['overall_risk']} | Highest: {custom_data['highest_risk_type']} ({custom_data['risk_score']})")
        print(f"  -> Factors: {custom_data['main_contributing_factors']}")
        assert custom_data["overall_risk"] == "HIGH"
        assert custom_data["highest_risk_type"] == "Drought"
        print("  [OK] Custom evaluation correctly synthesizes explanation!")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! RISK PREDICTION PERSISTENCE & HISTORY VERIFIED!")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    test_risk_prediction_and_history()
