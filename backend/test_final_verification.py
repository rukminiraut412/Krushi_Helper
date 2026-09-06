"""
Final End-to-End Verification Script for KrushiRakshak Steps 8 & 9.
Tests live servers, database persistence, dynamic crop/risk advisories,
and multilingual support across English, Marathi, Hindi, and Kannada.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import urllib.request
import urllib.parse
import json


BASE_API = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"


def make_request(url: str, method: str = "GET", data: dict = None) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        status_code = res.getcode()
        body = json.loads(res.read().decode("utf-8"))
        return status_code, body


def run_final_tests():
    print("=" * 75)
    print("RUNNING FINAL TEST VERIFICATION FOR KRUSHIRAKSHAK STEPS 8 & 9")
    print("=" * 75)

    # 1. Health Checks
    print("\n[STEP 1] Checking Backend & PostgreSQL Daemons...")
    code, health = make_request(f"{BASE_API}/health")
    assert code == 200 and health["status"] == "healthy"
    code, db_health = make_request(f"{BASE_API}/db-health")
    assert code == 200 and db_health["connected"] is True
    print(f"  [OK] Backend: {health['service']} (HTTP {code})")
    print(f"  [OK] Database: {db_health['service']} connected successfully")

    # 2. Generate an Advisory
    print("\n[STEP 2] Generating an Advisory via POST /api/advisories/generate...")
    code, adv1 = make_request(f"{BASE_API}/advisories/generate", method="POST", data={"farm_id": 1, "language": "en"})
    assert code == 200
    print(f"  [OK] Stored Advisory Record ID #{adv1['id']}")
    print(f"       Title: '{adv1['title']}'")
    print(f"       Urgency: {adv1['urgency']} | Time Window: {adv1['time_window']}")
    print(f"       Crop: {adv1['crop']} | Risk: {adv1['risk_type']} ({adv1['risk_level']})")

    # 3. Change Crop / Risk & Verify Advisory Changes
    print("\n[STEP 3] Changing Crop / Risk and Verifying Dynamic Response...")
    # Scenario A: Soybean + High Drought
    code, adv_soy = make_request(
        f"{BASE_API}/advisories/generate",
        method="POST",
        data={"farm_id": 1, "crop": "Soybean", "risk_type": "Drought", "risk_level": "HIGH", "language": "en"}
    )
    assert code == 200
    print(f"  -> Scenario A [Soybean + Drought]: '{adv_soy['title']}'")
    assert "Soybean" in adv_soy["title"] or "Drought" in adv_soy["title"]

    # Scenario B: Cotton + High Flood
    code, adv_cotton = make_request(
        f"{BASE_API}/advisories/generate",
        method="POST",
        data={"farm_id": 1, "crop": "Cotton", "risk_type": "Flood", "risk_level": "HIGH", "language": "en"}
    )
    assert code == 200
    print(f"  -> Scenario B [Cotton + Flood]: '{adv_cotton['title']}'")
    assert "Cotton" in adv_cotton["title"] or "Drainage" in adv_cotton["title"]

    # Scenario C: Wheat + High Heat Stress
    code, adv_wheat = make_request(
        f"{BASE_API}/advisories/generate",
        method="POST",
        data={"farm_id": 1, "crop": "Wheat", "risk_type": "Heat Stress", "risk_level": "HIGH", "language": "en"}
    )
    assert code == 200
    print(f"  -> Scenario C [Wheat + Heat]: '{adv_wheat['title']}'")
    assert "Wheat" in adv_wheat["title"] or "Heat" in adv_wheat["title"]

    assert adv_soy["title"] != adv_cotton["title"] != adv_wheat["title"]
    print("  [OK] Advisories dynamically adapt to crop and climate hazard permutations!")

    # 4. Multilingual Tests
    print("\n[STEP 4] Testing Multilingual Support across All 4 Languages...")

    # 4a. English
    code, adv_en = make_request(f"{BASE_API}/advisories/1?lang=en")
    assert code == 200 and adv_en["language"] == "en"
    print(f"  [English / en]: {adv_en['title']}")
    print(f"                  Urgency: {adv_en['urgency']} | Time: {adv_en['time_window']}")

    # 4b. Marathi
    code, adv_mr = make_request(f"{BASE_API}/advisories/1?lang=mr")
    assert code == 200 and adv_mr["language"] == "mr"
    print(f"  [मराठी / mr]:    {adv_mr['title']}")
    print(f"                  Urgency: {adv_mr['urgency']} | Time: {adv_mr['time_window']}")
    print(f"                  शिफारस: {adv_mr['recommendations'][0]}")

    # 4c. Hindi
    code, adv_hi = make_request(f"{BASE_API}/advisories/1?lang=hi")
    assert code == 200 and adv_hi["language"] == "hi"
    print(f"  [हिंदी / hi]:    {adv_hi['title']}")
    print(f"                  Urgency: {adv_hi['urgency']} | Time: {adv_hi['time_window']}")
    print(f"                  परामर्श: {adv_hi['recommendations'][0]}")

    # 4d. Kannada
    code, adv_kn = make_request(f"{BASE_API}/advisories/1?lang=kn")
    assert code == 200 and adv_kn["language"] == "kn"
    print(f"  [ಕನ್ನಡ / kn]:    {adv_kn['title']}")
    print(f"                  Urgency: {adv_kn['urgency']} | Time: {adv_kn['time_window']}")
    print(f"                  ಸಲಹೆ: {adv_kn['recommendations'][0]}")

    print("  [OK] All 4 languages verified with controlled translations!")

    # 5. Frontend Pages Verification
    print("\n[STEP 5] Testing Next.js Frontend Pages on http://localhost:3000...")
    frontend_routes = ["/", "/farmer/climate", "/farmer/farms", "/login", "/register"]
    for route in frontend_routes:
        req = urllib.request.Request(f"{FRONTEND_URL}{route}")
        with urllib.request.urlopen(req) as res:
            assert res.getcode() == 200
            print(f"  [HTTP 200 OK] {route}")

    print("\n" + "=" * 75)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 75)


if __name__ == "__main__":
    run_final_tests()
