from fastapi import APIRouter, Response, status
from app.schemas.health import HealthCheckResponse, DatabaseHealthResponse
from app.database.database import check_db_connection
from app.api.auth import router as auth_router
from app.api.farms import router as farms_router
from app.api.climate import router as climate_router
from app.api.risk import router as risk_router
from app.api.advisories import router as advisories_router
from app.api.alerts import router as alerts_router
from app.api.admin import router as admin_router
from app.api.simulation import router as simulation_router

router = APIRouter()

# Health checks
@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Service Health Check",
    description="Returns the current operational status of the KrushiRakshak API service."
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="healthy",
        service="KrushiRakshak API"
    )


@router.get(
    "/db-health",
    response_model=DatabaseHealthResponse,
    summary="Database Connectivity Check",
    description="Tests the connection to the PostgreSQL database and returns connection status."
)
async def db_health_check(response: Response) -> DatabaseHealthResponse:
    result = check_db_connection()
    if result.get("connected"):
        return DatabaseHealthResponse(
            status="healthy",
            service="KrushiRakshak Database",
            database="PostgreSQL",
            connected=True,
            message="Database connection established successfully",
            details=result
        )
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return DatabaseHealthResponse(
            status="unhealthy",
            service="KrushiRakshak Database",
            database="PostgreSQL",
            connected=False,
            message="Database connection failed",
            details={"error": result.get("error")}
        )


# Mount Sub-routers
router.include_router(auth_router)
router.include_router(farms_router)
router.include_router(climate_router)
router.include_router(risk_router)
router.include_router(advisories_router)
router.include_router(alerts_router)
router.include_router(admin_router)
router.include_router(simulation_router)
