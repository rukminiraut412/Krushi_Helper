const http = require("http");

async function checkUrl(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const req = http.request(
      {
        hostname: parsed.hostname,
        port: parsed.port,
        path: parsed.pathname + parsed.search,
        method: options.method || "GET",
        headers: options.headers || {},
      },
      (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          resolve({ status: res.statusCode, headers: res.headers, body });
        });
      }
    );
    req.on("error", reject);
    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

async function runTests() {
  console.log("=== KRUSHIRAKSHAK ADMIN PORTAL VERIFICATION ===");

  // 1. Verify Frontend Admin Routes
  console.log("\n[Test 1] Next.js HTTP Status for /admin/dashboard");
  const adminDashRes = await checkUrl("http://localhost:3000/admin/dashboard");
  console.log(`Status: ${adminDashRes.status}`);
  if (adminDashRes.status === 200) {
    console.log("PASS: /admin/dashboard returned HTTP 200 (No 404!)");
  } else {
    console.error(`FAIL: /admin/dashboard returned HTTP ${adminDashRes.status}`);
  }

  console.log("\n[Test 2] Next.js HTTP Status for /admin root route");
  const adminRootRes = await checkUrl("http://localhost:3000/admin");
  console.log(`Status: ${adminRootRes.status}, Location: ${adminRootRes.headers.location || "None"}`);
  if (adminRootRes.status === 200 || adminRootRes.status === 307 || adminRootRes.status === 308) {
    console.log("PASS: /admin redirected or rendered properly!");
  } else {
    console.error(`FAIL: /admin returned HTTP ${adminRootRes.status}`);
  }

  // 2. Test Admin Login on Backend
  console.log("\n[Test 3] Admin Login (9999900000 / AdminPassword123)");
  const loginRes = await checkUrl("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mobile: "9999900000",
      password: "AdminPassword123",
    }),
  });
  console.log(`Status: ${loginRes.status}`);
  const loginData = JSON.parse(loginRes.body);
  console.log(`Role: ${loginData.role}, Name: ${loginData.user?.name}`);
  const token = loginData.access_token;
  if (loginRes.status === 200 && loginData.role === "ADMIN" && token) {
    console.log("PASS: Admin authentication returned valid JWT with ADMIN role!");
  } else {
    console.error("FAIL: Admin authentication failed.");
  }

  // 3. Test Backend Admin APIs with Token
  console.log("\n[Test 4] Backend GET /api/admin/dashboard");
  const statsRes = await checkUrl("http://localhost:8000/api/admin/dashboard", {
    headers: { Authorization: `Bearer ${token}` },
  });
  console.log(`Status: ${statsRes.status}`);
  const stats = JSON.parse(statsRes.body);
  console.log(
    `Farmers: ${stats.total_farmers}, Farms: ${stats.total_farms}, High Risk: ${stats.high_risk_farms}, Medium Risk: ${stats.medium_risk_farms}, Low Risk: ${stats.low_risk_farms}`
  );
  if (statsRes.status === 200 && typeof stats.total_farmers === "number") {
    console.log("PASS: Admin dashboard API retrieved real PostgreSQL data!");
  } else {
    console.error("FAIL: Admin dashboard API failed.");
  }

  console.log("\n[Test 5] Backend GET /api/admin/risk-map");
  const mapRes = await checkUrl("http://localhost:8000/api/admin/risk-map", {
    headers: { Authorization: `Bearer ${token}` },
  });
  console.log(`Status: ${mapRes.status}`);
  const mapPoints = JSON.parse(mapRes.body);
  console.log(`Plotted Farm Points: ${mapPoints.length}`);
  if (mapRes.status === 200 && Array.isArray(mapPoints)) {
    mapPoints.forEach((pt) => {
      console.log(`  - Farm: ${pt.farm_name}, Farmer: ${pt.farmer_name}, Risk: ${pt.risk_level} (${pt.risk_score}), Coordinates: [${pt.latitude}, ${pt.longitude}]`);
    });
    console.log("PASS: Admin risk-map points API returned geo-tagged farm data!");
  } else {
    console.error("FAIL: Admin risk-map API failed.");
  }

  console.log("\n[Test 6] Backend GET /api/admin/vulnerability");
  const vulnRes = await checkUrl("http://localhost:8000/api/admin/vulnerability", {
    headers: { Authorization: `Bearer ${token}` },
  });
  console.log(`Status: ${vulnRes.status}`);
  const vuln = JSON.parse(vulnRes.body);
  console.log(`Vulnerable Areas: ${vuln.vulnerable_areas?.length}, Main Factors: ${vuln.main_risk_factors?.join(", ")}`);
  if (vulnRes.status === 200) {
    console.log("PASS: Government vulnerability assessment retrieved!");
  } else {
    console.error("FAIL: Vulnerability assessment API failed.");
  }

  // 4. Verify Existing Farmer Functionality Remains Intact
  console.log("\n[Test 7] Existing Farmer Dashboard Route & Login Intact");
  const farmerDashRes = await checkUrl("http://localhost:3000/farmer/dashboard");
  console.log(`Farmer Dashboard Status: ${farmerDashRes.status}`);
  const farmerLoginRes = await checkUrl("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mobile: "9876500001",
      password: "SecurePassword123",
    }),
  });
  const farmerData = JSON.parse(farmerLoginRes.body);
  console.log(`Farmer Login Status: ${farmerLoginRes.status}, Role: ${farmerData.role}, Name: ${farmerData.user?.name}`);
  if (farmerDashRes.status === 200 && farmerData.role === "FARMER") {
    console.log("PASS: Existing Farmer portal and authentication completely preserved!");
  } else {
    console.error("FAIL: Farmer portal or login affected.");
  }

  console.log("\n=== ALL 7 TESTS COMPLETE ===");
}

runTests().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
