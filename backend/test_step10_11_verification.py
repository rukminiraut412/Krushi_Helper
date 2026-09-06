import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_API = "http://127.0.0.1:8000/api"
FRONTEND_URL = "http://127.0.0.1:3000"

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8")

def post(url, payload=None, headers=None):
    h = headers or {}
    h["Content-Type"] = "application/json"
    data = json.dumps(payload).encode("utf-8") if payload else b""
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8")

def patch(url, headers=None):
    req = urllib.request.Request(url, data=b"", headers=headers or {}, method="PATCH")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8")

def run_verification():
    print("=== STARTING STEP 10 & 11 VERIFICATION ===", flush=True)

    # 1. Test Login
    status, body = post(f"{BASE_API}/auth/login", {
        "mobile": "9876500001",
        "password": "SecurePassword123"
    })
    assert status == 200, f"Login failed: {status}"
    auth_data = json.loads(body)
    token = auth_data["access_token"]
    user = auth_data["user"]
    farmer_id = user["id"]
    print(f"[PASS] 1. Authenticated as farmer: {user['name']} (ID: {farmer_id})", flush=True)

    # 2. Test Get Farms (Multi-farm)
    status, body = get(f"{BASE_API}/farms", {"Authorization": f"Bearer {token}"})
    assert status == 200
    farms = json.loads(body)
    assert len(farms) > 0, "No farms found for farmer"
    farm_id = farms[0]["id"]
    farm_name = farms[0]["farm_name"]
    print(f"[PASS] 2. Retrieved {len(farms)} farm(s). Primary farm: '{farm_name}' (ID: {farm_id})", flush=True)

    # 3. Test Weather & Soil Telemetry
    status, body = get(f"{BASE_API}/weather/{farm_id}")
    assert status == 200
    weather = json.loads(body)
    assert "temperature" in weather and "rainfall" in weather
    print(f"[PASS] 3a. Weather telemetry active: {weather['temperature']}°C, {weather['rainfall']} mm rainfall", flush=True)

    status, body = get(f"{BASE_API}/soil/{farm_id}")
    assert status == 200
    soil = json.loads(body)
    assert "soil_moisture" in soil and "soil_type" in soil
    print(f"[PASS] 3b. Soil telemetry active: moisture {soil['soil_moisture']}%, type {soil['soil_type']}", flush=True)

    # 4. Test AI Risk Assessment
    status, body = get(f"{BASE_API}/risk/farm/{farm_id}")
    assert status == 200
    risk = json.loads(body)
    assert "overall_risk" in risk and "risk_score" in risk
    print(f"[PASS] 4. AI Risk Assessment: Score {risk['risk_score']}/100, Level {risk['risk_level']}, Dominant threat: {risk['highest_risk_type']}", flush=True)

    # 5. Test Multilingual Advisory (en, mr, hi, kn)
    for lang in ["en", "mr", "hi", "kn"]:
        status, body = get(f"{BASE_API}/advisories/{farm_id}?lang={lang}")
        assert status == 200
        adv = json.loads(body)
        assert adv["language"] == lang
        print(f"[PASS] 5. Advisory in [{lang}]: '{adv['title'][:40]}...' (Urgency: {adv['urgency']})", flush=True)

    # 6. Test Alert Simulation (HIGH risk alert)
    status, body = post(f"{BASE_API}/alerts/simulate", {
        "farm_id": farm_id,
        "risk_type": "Extreme Rainfall",
        "risk_score": 89
    })
    assert status == 200
    sim_alert = json.loads(body)
    alert_id = sim_alert["id"]
    assert sim_alert["risk_level"] == "HIGH"
    assert sim_alert["is_read"] is False
    print(f"[PASS] 6. Simulated HIGH risk alert #{alert_id} for {sim_alert['farm_name']}", flush=True)

    # 7. Test Get Alerts & Unread count
    status, body = get(f"{BASE_API}/alerts/{farmer_id}")
    assert status == 200
    alert_list = json.loads(body)
    unread_count_before = alert_list["unread_count"]
    assert unread_count_before >= 1
    print(f"[PASS] 7. Alerts list retrieved: total {len(alert_list['alerts'])}, unread {unread_count_before}", flush=True)

    # 8. Test Mark Alert as Read
    status, body = patch(f"{BASE_API}/alerts/{alert_id}/read")
    assert status == 200
    read_alert = json.loads(body)
    assert read_alert["is_read"] is True
    print(f"[PASS] 8. Marked alert #{alert_id} as READ", flush=True)

    status, body = get(f"{BASE_API}/alerts/{farmer_id}")
    alert_list_after = json.loads(body)
    assert alert_list_after["unread_count"] == unread_count_before - 1
    print(f"[PASS] 8b. Verified unread count decremented from {unread_count_before} to {alert_list_after['unread_count']}", flush=True)

    # 9. Test Frontend route /farmer/dashboard
    status, body = get(f"{FRONTEND_URL}/farmer/dashboard")
    assert status == 200
    assert "Krushi" in body
    print(f"[PASS] 9. Frontend /farmer/dashboard returned HTTP 200 (Length: {len(body)} bytes)", flush=True)

    print("\n>>> ALL STEP 10 & STEP 11 VERIFICATIONS PASSED SUCCESSFULLY! <<<", flush=True)

if __name__ == "__main__":
    run_verification()
