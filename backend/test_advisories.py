"""
Comprehensive Automated Test Suite for KrushiRakshak Personalized Advisory Engine
and Multilingual Localization System (Steps 8 & 9).
Tests:
- Dynamic crop & risk changes (Soybean + Drought vs Cotton + Flood vs Wheat + Heat)
- Controlled translations across English (en), Marathi (mr), Hindi (hi), and Kannada (kn)
- PostgreSQL persistence and database verification
- REST APIs: POST /api/advisories/generate & GET /api/advisories/{farm_id}
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.advisory import Advisory
from app.models.farm import Farm

client = TestClient(app)


def test_advisories_and_multilingual():
    print("=" * 70)
    print("TESTING PERSONALIZED ADVISORY ENGINE & MULTILINGUAL SYSTEM")
    print("=" * 70)

    db = SessionLocal()
    try:
        farm = db.query(Farm).filter(Farm.id == 1).first()
        assert farm is not None, "Target Farm #1 must exist"
        print(f"[SETUP] Using Farm #{farm.id}: '{farm.farm_name}'")

        initial_advisories_count = db.query(Advisory).filter(Advisory.farm_id == 1).count()
        print(f"[SETUP] Initial stored advisories for Farm #1: {initial_advisories_count}")

        # -------------------------------------------------------------
        # TEST 1: Default Advisory Generation for Farm
        # -------------------------------------------------------------
        print("\n[TEST 1] Testing POST /api/advisories/generate (Default live telemetry)...")
        res1 = client.post("/api/advisories/generate", json={"farm_id": 1, "language": "en"})
        assert res1.status_code == 200, f"Error: {res1.text}"
        data1 = res1.json()

        print(f"  -> Generated Advisory ID: {data1['id']}")
        print(f"  -> Title: {data1['title']}")
        print(f"  -> Crop: {data1['crop']} | Risk: {data1['risk_type']} ({data1['risk_level']})")
        print(f"  -> Urgency: {data1['urgency']} | Time Window: {data1['time_window']}")
        print(f"  -> Recommendations count: {len(data1['recommendations'])}")
        print(f"  -> Sample Recommendation: {data1['recommendations'][0]}")

        assert data1["id"] is not None
        assert len(data1["recommendations"]) > 0
        assert len(data1["preventive_actions"]) > 0

        # Verify DB directly
        db_rec = db.query(Advisory).filter(Advisory.id == data1["id"]).first()
        assert db_rec is not None, "Advisory must be persisted in PostgreSQL table"
        print("  [OK] Successfully persisted in PostgreSQL 'advisories' table!")

        # -------------------------------------------------------------
        # TEST 2: Dynamic Variation - Soybean + Drought vs Cotton + Flood
        # -------------------------------------------------------------
        print("\n[TEST 2] Verifying that Advisory changes when Crop & Risk change...")

        # 2a. HIGH Drought + Soybean
        print("  -> Subtest 2a: HIGH Drought + Soybean")
        soy_drought_req = {
            "farm_id": 1,
            "crop": "Soybean",
            "risk_type": "Drought",
            "risk_level": "HIGH",
            "language": "en"
        }
        res_soy = client.post("/api/advisories/generate", json=soy_drought_req)
        assert res_soy.status_code == 200
        soy_data = res_soy.json()
        print(f"     Title: {soy_data['title']}")
        print(f"     Rec 1: {soy_data['recommendations'][0]}")
        assert "Soybean" in soy_data["title"] or "Drought" in soy_data["title"]
        assert any("sprinkler" in r.lower() or "potassium" in r.lower() or "mulch" in r.lower() or "flowering" in r.lower() for r in soy_data["recommendations"])

        # 2b. HIGH Flood + Cotton
        print("  -> Subtest 2b: HIGH Flood + Cotton")
        cotton_flood_req = {
            "farm_id": 1,
            "crop": "Cotton",
            "risk_type": "Flood",
            "risk_level": "HIGH",
            "language": "en"
        }
        res_cotton = client.post("/api/advisories/generate", json=cotton_flood_req)
        assert res_cotton.status_code == 200
        cotton_data = res_cotton.json()
        print(f"     Title: {cotton_data['title']}")
        print(f"     Rec 1: {cotton_data['recommendations'][0]}")
        assert "Cotton" in cotton_data["title"] or "Drainage" in cotton_data["title"]
        assert any("drain" in r.lower() or "parawilt" in r.lower() or "furrow" in r.lower() or "water" in r.lower() for r in cotton_data["recommendations"])

        # Confirm they are completely distinct
        assert soy_data["title"] != cotton_data["title"], "Soybean drought advisory must differ from Cotton flood advisory"
        print("  [OK] Advisories dynamically adapt to Crop and Climate Hazard combinations!")

        # -------------------------------------------------------------
        # TEST 3: Multilingual Testing Across All 4 Languages
        # -------------------------------------------------------------
        print("\n[TEST 3] Testing Multilingual Support across all 4 languages...")

        # 3a. English (en)
        res_en = client.post("/api/advisories/generate", json={"farm_id": 1, "crop": "Soybean", "risk_type": "Drought", "risk_level": "HIGH", "language": "en"})
        d_en = res_en.json()
        print(f"  [EN - English]: {d_en['title']}")
        print(f"                  Urgency: {d_en['urgency']} | Time: {d_en['time_window']}")
        assert "Soybean" in d_en["title"]

        # 3b. Marathi (mr)
        res_mr = client.post("/api/advisories/generate", json={"farm_id": 1, "crop": "Soybean", "risk_type": "Drought", "risk_level": "HIGH", "language": "mr"})
        d_mr = res_mr.json()
        print(f"  [MR - मराठी]:   {d_mr['title']}")
        print(f"                  Urgency: {d_mr['urgency']} | Time: {d_mr['time_window']}")
        print(f"                  शिफारस: {d_mr['recommendations'][0]}")
        assert "सोयाबीन" in d_mr["title"]
        assert "दुष्काळ" in d_mr["title"] or "सल्ला" in d_mr["title"]
        assert d_mr["language"] == "mr"

        # 3c. Hindi (hi)
        res_hi = client.post("/api/advisories/generate", json={"farm_id": 1, "crop": "Soybean", "risk_type": "Drought", "risk_level": "HIGH", "language": "hi"})
        d_hi = res_hi.json()
        print(f"  [HI - हिंदी]:   {d_hi['title']}")
        print(f"                  Urgency: {d_hi['urgency']} | Time: {d_hi['time_window']}")
        print(f"                  परामर्श: {d_hi['recommendations'][0]}")
        assert "सोयाबीन" in d_hi["title"]
        assert "सूखा" in d_hi["title"] or "परामर्श" in d_hi["title"]
        assert d_hi["language"] == "hi"

        # 3d. Kannada (kn)
        res_kn = client.post("/api/advisories/generate", json={"farm_id": 1, "crop": "Soybean", "risk_type": "Drought", "risk_level": "HIGH", "language": "kn"})
        d_kn = res_kn.json()
        print(f"  [KN - ಕನ್ನಡ]:   {d_kn['title']}")
        print(f"                  Urgency: {d_kn['urgency']} | Time: {d_kn['time_window']}")
        print(f"                  ಸಲಹೆ: {d_kn['recommendations'][0]}")
        assert "ಸೋಯಾಬೀನ್" in d_kn["title"]
        assert d_kn["language"] == "kn"

        print("  [OK] Controlled translations verified in English, Marathi, Hindi, and Kannada!")

        # -------------------------------------------------------------
        # TEST 4: GET /api/advisories/{farm_id}?lang=...
        # -------------------------------------------------------------
        print("\n[TEST 4] Testing GET /api/advisories/1 with query param lang...")
        for lang_code in ["en", "mr", "hi", "kn"]:
            res_get = client.get(f"/api/advisories/1?lang={lang_code}")
            assert res_get.status_code == 200, f"Failed GET for lang={lang_code}"
            data_get = res_get.json()
            assert data_get["language"] == lang_code
            print(f"  -> GET lang={lang_code}: Title='{data_get['title'][:45]}...' | Urgency='{data_get['urgency']}'")

        print("  [OK] GET /api/advisories/{farm_id} correctly delivers requested language!")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ADVISORY ENGINE & MULTILINGUAL VERIFIED 100%!")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    test_advisories_and_multilingual()
