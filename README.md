# KrushiRakshak (कृषि रक्षक)

> **"Predict. Prepare. Protect."**

**KrushiRakshak** is an AI-powered climate-resilient agriculture platform that predicts farm-level climate risks and delivers personalized, crop-specific, and multilingual advisories directly to farmers. Concurrently, it equips government bodies and agricultural departments with a centralized risk-mapping dashboard for proactive vulnerability assessment and disaster relief planning.

---

## 🌾 Project Purpose

Smallholder and commercial farmers face accelerating climate volatility—unseasonal monsoons, flash droughts, severe heatwaves, and pest outbreaks. Traditional weather forecasts are often macro-level and lack farm-specific context. 

**KrushiRakshak bridges this critical gap by:**
1. **Predicting Farm-Level Climate Risks:** Downscaling meteorological, remote sensing, and soil telemetry to predict risks for specific parcel locations.
2. **Delivering Personalized Crop Advisories:** Formulating step-by-step guidance tailored to the farmer's crop variety, sowing date, and local soil conditions.
3. **Multilingual Inclusion:** Presenting alerts and advisories in regional languages to ensure maximum accessibility.
4. **Government & Institutional Intelligence:** Offering spatial risk heatmaps, crop vulnerability indexes, and loss-mitigation analytics for regional planning.

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | Next.js 14 (App Router), React, TypeScript, Tailwind CSS | High-performance responsive web application, SSR/CSR, accessible components |
| **Maps & Charts** | Leaflet, Recharts, Lucide Icons | Geospatial GIS parcel views, time-series agro-climate charts, iconography |
| **Backend** | Python, FastAPI, Pydantic, Uvicorn | High-throughput asynchronous REST API services with OpenAPI/Swagger docs |
| **Database** | PostgreSQL, SQLAlchemy 2.0, Alembic | Relational storage for farmer registries, farm boundaries, advisories, migrations |
| **AI / ML** | Python, Scikit-learn, Pandas, NumPy, Joblib | Climate risk classification, time-series anomaly detection, feature pipelines |
| **Infrastructure** | Docker, Docker Compose | Containerized database and microservice orchestration |

---

## 📁 Folder Structure

```
KrushiRakshak/
├── frontend/                     # Next.js frontend application
│   ├── app/                      # App router (layout, pages, globals.css)
│   ├── components/               # UI components (Navbar, Hero, Features, StatusBadge, Footer)
│   ├── services/                 # Backend API client (api.ts)
│   ├── hooks/                    # React custom hooks (useHealthCheck.ts)
│   ├── types/                    # TypeScript interfaces & domain types
│   ├── lib/                      # Utility functions (cn, formatting)
│   ├── package.json              # Frontend dependencies & scripts
│   ├── tailwind.config.ts        # Tailwind CSS styling configuration
│   └── tsconfig.json             # TypeScript configuration
├── backend/                      # FastAPI backend application
│   ├── app/
│   │   ├── api/                  # API routers (routes.py with /api/health)
│   │   ├── models/               # SQLAlchemy ORM models (placeholder)
│   │   ├── schemas/              # Pydantic schemas (health.py)
│   │   ├── services/             # Core business & advisory services (placeholder)
│   │   ├── database/             # DB engine & session configuration (placeholder)
│   │   ├── utils/                # Helper utilities (placeholder)
│   │   ├── ml/                   # ML inference adapter bindings (placeholder)
│   │   └── main.py               # FastAPI entrypoint, CORS configuration
│   └── requirements.txt          # Python dependencies
├── ml/                           # AI & Machine Learning pipeline workspace
│   ├── dataset/                  # Raw & processed training datasets (.gitkeep)
│   ├── preprocessing/            # Data cleaning & feature transformers
│   ├── training/                 # Model training & hyperparameter tuning
│   ├── prediction/               # Batch and offline inference routines
│   ├── models/                   # Serialized model weights & joblib artifacts (.gitkeep)
│   └── requirements.txt          # ML dependencies (pandas, scikit-learn, numpy, joblib)
├── docs/
│   └── architecture.md           # System architecture & interface specifications
├── .env.example                  # Environment configuration template
├── README.md                     # Project documentation
└── docker-compose.yml            # PostgreSQL container configuration
```

---

## ⚙️ Environment Variables

Before running the services, create your `.env` configuration:

```bash
# Copy example environment file
cp .env.example .env
```

Key environment variables:

| Variable | Description | Example / Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://krushirakshak:krushirakshak_secret@localhost:5432/krushirakshak_db` |
| `JWT_SECRET` | Secret key for signing authentication tokens | `your_super_secret_jwt_key_here` |
| `WEATHER_API_KEY` | Telemetry API key (OpenWeather/IMD) | `your_weather_api_key` |
| `BACKEND_CORS_ORIGINS` | JSON list of allowed origins | `["http://localhost:3000","http://127.0.0.1:3000"]` |
| `NEXT_PUBLIC_API_URL` | Base URL used by Next.js frontend | `http://localhost:8000/api` |

---

## 🚀 How to Run Backend (FastAPI)

### 1. Prerequisites
- Python 3.10+ (Python 3.14 compatible)

### 2. Navigate and Setup
```bash
cd backend
```

*(Optional) Create and activate a virtual environment:*
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the API Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will now be running at:
- Health check: `http://localhost:8000/api/health`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

Expected response from `/api/health`:
```json
{
  "status": "healthy",
  "service": "KrushiRakshak API"
}
```

---

## 💻 How to Run Frontend (Next.js)

### 1. Prerequisites
- Node.js 18.17+ or 20+

### 2. Navigate and Install Dependencies
```bash
cd frontend
npm install
```

### 3. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The landing page features a live **FastAPI Backend Status Badge** at the top that automatically pings `http://localhost:8000/api/health` to confirm end-to-end connectivity.

---

## 🐳 Running PostgreSQL via Docker (Optional)

To spin up the local PostgreSQL database service:

```bash
docker-compose up -d db
```
Database credentials default to those defined in `docker-compose.yml` and `.env.example`.
