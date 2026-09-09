import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router


# KrushiRakshak FastAPI Application Configuration
app = FastAPI(
    title="KrushiRakshak API",
    description="AI-powered climate-resilient agriculture platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================
# CORS Configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Local development
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",

        # Production frontend - Vercel
        "https://krushi-helper.vercel.app",
    ],

    # Allow localhost and Vercel deployments
    allow_origin_regex=(
        r"https://krushi-helper(-[a-zA-Z0-9-]+)?\.vercel\.app"
        r"|https?://(localhost|127\.0\.0\.1)(:\d+)?"
    ),

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)


# ============================================================
# API Router
# ============================================================

# Mount main API Router under /api
app.include_router(
    api_router,
    prefix="/api"
)


# ============================================================
# Startup - Seed Default Admin
# ============================================================

@app.on_event("startup")
def seed_default_admin():

    from app.database.database import SessionLocal
    from app.models.user import User, UserRole
    from app.utils.security import hash_password

    db = SessionLocal()

    try:
        admin_exists = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN)
            .first()
        )

        if not admin_exists:

            admin_user = User(
                name="Agriculture Dept Officer",
                mobile="9999900000",
                password_hash=hash_password("AdminPassword123"),
                role=UserRole.ADMIN,
                preferred_language="en",
            )

            db.add(admin_user)
            db.commit()

            print(
                "INFO: Default Admin user seeded successfully "
                "(mobile: 9999900000)."
            )

    except Exception as e:

        print(
            f"WARNING: Failed to seed default admin user: {e}"
        )

    finally:
        db.close()


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/", tags=["Root"])
async def root():

    return {
        "message": (
            "Welcome to KrushiRakshak API. "
            "Visit /docs for API documentation "
            "or /api/health for system status."
        ),
        "docs": "/docs",
        "health": "/api/health",
        "db_health": "/api/db-health"
    }


# ============================================================
# Run Application
# ============================================================

if __name__ == "__main__":

    import uvicorn

    host = os.getenv(
        "BACKEND_HOST",
        "0.0.0.0"
    )

    port = int(
        os.getenv(
            "BACKEND_PORT",
            8000
        )
    )

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
