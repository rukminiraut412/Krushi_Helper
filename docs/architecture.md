# KrushiRakshak Architecture Documentation

## Overview

**KrushiRakshak** is an AI-powered climate-resilient agriculture platform designed to:
1. Predict farm-level climate risks (drought, unseasonal rainfall, extreme heat, pest vulnerabilities).
2. Deliver personalized, crop-specific, multilingual advisories directly to farmers.
3. Provide an interactive Government Dashboard for regional risk mapping and vulnerability assessment.

---

## High-Level System Architecture

```
                       +-----------------------------------+
                       |      KrushiRakshak Next.js        |
                       |       Frontend (Port 3000)        |
                       |                                   |
                       |  - Farmer Advisory Portal         |
                       |  - Government Vulnerability Maps  |
                       |  - Multilingual Interface         |
                       +-----------------+-----------------+
                                         |
                                         | REST / JSON (CORS Enabled)
                                         v
                       +-----------------------------------+
                       |       FastAPI Backend API         |
                       |           (Port 8000)             |
                       |                                   |
                       |  - /api/health (Health check)     |
                       |  - Authentication & RBAC (Future) |
                       |  - Advisory Generation (Future)   |
                       |  - Risk Mapping Endpoints (Future)|
                       +-------+-------------------+-------+
                               |                   |
               Internal Python |                   | SQLAlchemy
               Inference       v                   v
        +-------------------------+      +-------------------------+
        |  Machine Learning Core  |      |   PostgreSQL Database   |
        |      (ml/ workspace)    |      |       (Port 5432)       |
        |                         |      |                         |
        | - Risk Prediction Models|      | - Farmer Profiles       |
        | - Preprocessing Pipeline|      | - Geo-Farms & Crops     |
        | - Joblib Model Registry |      | - Advisories & History  |
        +-------------------------+      +-------------------------+
```

---

## Directory Organization

- **`frontend/`**: Next.js 14/15 App router with Tailwind CSS, React, TypeScript, Leaflet for maps, and Recharts for climate/crop data visualization.
- **`backend/`**: FastAPI modular application organized by domain (`api/`, `models/`, `schemas/`, `services/`, `database/`, `utils/`, `ml/`).
- **`ml/`**: Self-contained machine learning engineering modules (`dataset/`, `preprocessing/`, `training/`, `prediction/`, `models/`).
- **`docs/`**: Architectural guides, design decisions, and interface specifications.
