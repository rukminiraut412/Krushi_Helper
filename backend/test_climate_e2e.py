import sys
import httpx

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"

def main():
    print("=" * 65)
    print("RUNNING END-TO-END VERIFICATION: CLIMATE & FARM TELEMETRY")
    print("=" * 65)

    with httpx.Client(base_url=BACKEND_URL, timeout=10.0) as client:
        # 1. Check API & DB Health
        print("\n[1] Checking /api/health & /api/db-health...")
        r_health = client.get("/api/health")
        assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
        print("  -> /api/health OK:", r_health.json())

        r_db = client.get("/api/db-health")
        assert r_db.status_code == 200, f"DB check failed: {r_db.text}"
        assert r_db.json()["connected"] is True
        print("  -> /api/db-health OK (PostgreSQL connected):", r_db.json())

        # 2. Login test farmer
        print("\n[2] Logging in farmer (mobile: 9876500001)...")
        r_login = client.post("/api/auth/login", json={
            "mobile": "9876500001",
            "password": "SecurePassword123"
        })
        assert r_login.status_code == 200, f"Login failed: {r_login.text}"
        token = r_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  -> Farmer authenticated! Role:", r_login.json()["role"])

        # 3. Retrieve farms
        print("\n[3] Fetching farmer's farm parcels...")
        r_farms = client.get("/api/farms", headers=headers)
        assert r_farms.status_code == 200, f"Failed to get farms: {r_farms.text}"
        farms = r_farms.json()
        assert len(farms) > 0, "No farms found for farmer"
        farm = farms[0]
        farm_id = farm["id"]
        print(f"  -> Selected Farm ID {farm_id}: '{farm['farm_name']}' | Crop: {farm['crop']} | Area: {farm['area']} acres")

        # 4. Fetch Weather Data for farm
        print(f"\n[4] Querying GET /api/weather/{farm_id}...")
        r_weather = client.get(f"/api/weather/{farm_id}")
        assert r_weather.status_code == 200, f"Weather request failed: {r_weather.text}"
        w = r_weather.json()
        print("  -> Weather Data Received:")
        print(f"     - Temperature: {w['temperature']} °C")
        print(f"     - Current Rainfall: {w['rainfall']} mm")
        print(f"     - 24-48h Forecast Rainfall: {w['forecast_rainfall']} mm")
        print(f"     - Relative Humidity: {w['humidity']} %")
        print(f"     - Wind Speed: {w['wind_speed']} km/h")
        print(f"     - Condition: {w['condition']}")
        print(f"     - Is Demo Mode: {w['is_demo']}")
        print(f"     - Data Source: {w['data_source']}")
        print(f"     - Timestamp: {w['timestamp']}")

        assert "temperature" in w
        assert "rainfall" in w
        assert "humidity" in w
        assert "wind_speed" in w
        assert "forecast_rainfall" in w
        assert "timestamp" in w
        assert w["is_demo"] is True, "Expected demo mode flag to be clearly marked"

        # 5. Fetch Soil Data for farm
        print(f"\n[5] Querying GET /api/soil/{farm_id}...")
        r_soil = client.get(f"/api/soil/{farm_id}")
        assert r_soil.status_code == 200, f"Soil request failed: {r_soil.text}"
        s = r_soil.json()
        print("  -> Soil Data Received:")
        print(f"     - Soil Moisture: {s['soil_moisture']} %")
        print(f"     - Water Availability: {s['water_availability']}")
        print(f"     - Soil Condition: {s['soil_condition']}")
        print(f"     - Soil Type: {s['soil_type']}")
        print(f"     - Sensor Gateway Status: {s['sensor_status']}")
        print(f"     - Data Source: {s['data_source']}")

        assert "soil_moisture" in s
        assert "water_availability" in s
        assert "soil_condition" in s
        assert "soil_type" in s
        assert s["is_demo"] is True

        # 6. Fetch Historical Climate Series
        print(f"\n[6] Querying GET /api/weather/{farm_id}/history...")
        r_hist = client.get(f"/api/weather/{farm_id}/history?days=7")
        assert r_hist.status_code == 200
        hist = r_hist.json()
        print(f"  -> Historical points returned: {len(hist)} days")
        for pt in hist[:3]:
            print(f"     - Date: {pt['date']} | Rain: {pt['rainfall_mm']}mm | Max Temp: {pt['temp_max_c']}°C")

    # 7. Check Frontend Next.js Pages
    print("\n[7] Verifying Frontend Web Pages on Port 3000...")
    with httpx.Client(base_url=FRONTEND_URL, timeout=10.0) as fe_client:
        pages = [
            ("/", "Landing Page"),
            ("/login", "Farmer & Admin Login"),
            ("/register", "Farmer Registration"),
            ("/farmer/farms", "Farm Management Dashboard"),
            ("/farmer/climate", "Climate & Soil Telemetry Page")
        ]
        for path, label in pages:
            res = fe_client.get(path)
            assert res.status_code == 200, f"Frontend {path} returned {res.status_code}"
            print(f"  -> [HTTP 200 OK] {label} ({path})")

    print("\n" + "=" * 65)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
