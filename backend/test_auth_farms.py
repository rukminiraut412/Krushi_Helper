import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("STARTING TEST SUITE: KrushiRakshak Auth & Farm Management")
    print("=" * 60)

    test_mobile = "9876500001"
    test_password = "SecurePassword123"

    # 1. Health checks
    print("\n[TEST 1] Testing /api/health and /api/db-health...")
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("  -> /api/health OK:", res_health.json())

    res_db = client.get("/api/db-health")
    assert res_db.status_code == 200, f"DB health check failed: {res_db.text}"
    assert res_db.json().get("connected") is True
    print("  -> /api/db-health OK:", res_db.json())

    # 2. Farmer registration
    print("\n[TEST 2] Farmer Registration...")
    reg_payload = {
        "name": "Arjun Patel",
        "mobile": test_mobile,
        "password": test_password,
        "preferred_language": "hi",
        "village": "Shivapur",
        "district": "Pune",
        "state": "Maharashtra",
        "latitude": 18.3542,
        "longitude": 73.8541
    }
    res_reg = client.post("/api/auth/register", json=reg_payload)
    if res_reg.status_code == 409:
        print("  -> User already registered from previous run, proceeding to test duplicate & login.")
    else:
        assert res_reg.status_code == 201, f"Registration failed: {res_reg.text}"
        data = res_reg.json()
        assert "access_token" in data
        assert data["role"] == "FARMER"
        print("  -> Registered farmer successfully:", data["user"]["name"], f"(ID: {data['user']['id']})")

    # 3. Duplicate mobile number
    print("\n[TEST 3] Testing Duplicate Mobile Number Rejection...")
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 409, f"Expected 409 Conflict, got {res_dup.status_code}: {res_dup.text}"
    print("  -> Duplicate mobile correctly rejected with 409 Conflict:", res_dup.json()["detail"])

    # 4. Incorrect password
    print("\n[TEST 4] Testing Incorrect Password Rejection...")
    res_wrong_pw = client.post("/api/auth/login", json={
        "mobile": test_mobile,
        "password": "WrongPassword999"
    })
    assert res_wrong_pw.status_code == 401, f"Expected 401 Unauthorized, got {res_wrong_pw.status_code}"
    print("  -> Incorrect password correctly rejected with 401 Unauthorized:", res_wrong_pw.json()["detail"])

    # 5. Successful login
    print("\n[TEST 5] Testing Successful Login...")
    res_login = client.post("/api/auth/login", json={
        "mobile": test_mobile,
        "password": test_password
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.text}"
    login_data = res_login.json()
    token = login_data["access_token"]
    assert token, "Token missing from login response"
    assert login_data["role"] == "FARMER"
    headers = {"Authorization": f"Bearer {token}"}
    print("  -> Login successful! Token acquired. Role:", login_data["role"])

    # 6. Protected endpoint without token
    print("\n[TEST 6] Testing Protected Endpoint Without Token...")
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401, f"Expected 401, got {res_no_token.status_code}"
    print("  -> Access denied without token (401 Unauthorized):", res_no_token.json()["detail"])

    # 7. Protected endpoint with valid token
    print("\n[TEST 7] Testing Protected Endpoint With Valid Token...")
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200, f"Failed to get /me: {res_me.text}"
    print("  -> Authenticated user verified:", res_me.json()["name"], "Mobile:", res_me.json()["mobile"])

    # 8. Role-based protection: Farmer accessing admin route
    print("\n[TEST 8] Testing Role Protection (Farmer accessing Admin endpoint)...")
    res_admin = client.get("/api/auth/admin-check", headers=headers)
    assert res_admin.status_code == 403, f"Expected 403 Forbidden for farmer, got {res_admin.status_code}"
    print("  -> Farmer correctly blocked from Admin endpoint (403 Forbidden):", res_admin.json()["detail"])

    # 9. Add Farm (Farm 1)
    print("\n[TEST 9] Adding Farm 1...")
    farm1_payload = {
        "farm_name": "Sunrise Organic Field",
        "area": 4.5,
        "crop": "Cotton",
        "sowing_date": "2026-06-20",
        "soil_type": "Black Cotton Soil",
        "irrigation_available": True,
        "latitude": 18.5204,
        "longitude": 73.8567
    }
    res_f1 = client.post("/api/farms", json=farm1_payload, headers=headers)
    assert res_f1.status_code == 201, f"Failed to add farm 1: {res_f1.text}"
    farm1 = res_f1.json()
    farm1_id = farm1["id"]
    print("  -> Farm 1 created:", farm1["farm_name"], f"(ID: {farm1_id}, Area: {farm1['area']} acres)")

    # 10. Add Multiple Farms (Farm 2)
    print("\n[TEST 10] Adding Farm 2 (Verifying Multiple Farms support)...")
    farm2_payload = {
        "farm_name": "Riverbend Paddy Terrace",
        "area": 2.75,
        "crop": "Paddy / Basmati Rice",
        "sowing_date": "2026-07-05",
        "soil_type": "Alluvial Loam",
        "irrigation_available": True,
        "latitude": 18.5310,
        "longitude": 73.8690
    }
    res_f2 = client.post("/api/farms", json=farm2_payload, headers=headers)
    assert res_f2.status_code == 201, f"Failed to add farm 2: {res_f2.text}"
    farm2 = res_f2.json()
    farm2_id = farm2["id"]
    print("  -> Farm 2 created:", farm2["farm_name"], f"(ID: {farm2_id}, Area: {farm2['area']} acres)")

    # 11. View Farmer's Farms list
    print("\n[TEST 11] Viewing Farmer's Farm List...")
    res_list = client.get("/api/farms", headers=headers)
    assert res_list.status_code == 200, f"Failed to list farms: {res_list.text}"
    farms_list = res_list.json()
    farm_ids = [f["id"] for f in farms_list]
    assert farm1_id in farm_ids and farm2_id in farm_ids, "Farms missing from list"
    print(f"  -> Total farms retrieved: {len(farms_list)}")
    for f in farms_list:
        print(f"     - [ID: {f['id']}] {f['farm_name']} | Crop: {f['crop']} | {f['area']} acres")

    # 12. View Farm Details
    print(f"\n[TEST 12] Viewing Farm Details for ID {farm1_id}...")
    res_detail = client.get(f"/api/farms/{farm1_id}", headers=headers)
    assert res_detail.status_code == 200, f"Failed to get farm details: {res_detail.text}"
    print("  -> Farm details retrieved successfully:", res_detail.json()["farm_name"])

    # 13. Edit Farm Details
    print(f"\n[TEST 13] Editing Farm Details for ID {farm1_id}...")
    update_payload = {
        "farm_name": "Sunrise Organic Field (Updated)",
        "area": 5.0,
        "crop": "Organic Hybrid Cotton",
        "soil_type": "Enriched Black Soil"
    }
    res_edit = client.put(f"/api/farms/{farm1_id}", json=update_payload, headers=headers)
    assert res_edit.status_code == 200, f"Failed to edit farm: {res_edit.text}"
    updated_farm = res_edit.json()
    assert updated_farm["farm_name"] == "Sunrise Organic Field (Updated)"
    assert updated_farm["area"] == 5.0
    print("  -> Farm updated successfully:", updated_farm["farm_name"], f"New area: {updated_farm['area']} acres")

    # 14. Delete Farm
    print(f"\n[TEST 14] Deleting Farm ID {farm2_id}...")
    res_del = client.delete(f"/api/farms/{farm2_id}", headers=headers)
    assert res_del.status_code == 200, f"Failed to delete farm: {res_del.text}"
    print("  -> Farm deleted successfully:", res_del.json()["message"])

    # Verify deleted farm is no longer accessible
    res_del_check = client.get(f"/api/farms/{farm2_id}", headers=headers)
    assert res_del_check.status_code == 404, "Deleted farm still returned 200!"
    print("  -> Verified: Farm ID", farm2_id, "returns 404 Not Found.")

    print("\n" + "=" * 60)
    print("ALL 14 TESTS PASSED FLAWLESSLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
