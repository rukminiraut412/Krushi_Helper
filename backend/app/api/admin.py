from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.admin import (
    AdminDashboardStatsResponse,
    AdminFarmerItem,
    RiskMapPoint,
    VulnerabilityAssessmentResponse
)
from app.schemas.alert import AlertItemResponse
from app.services.admin_service import admin_service
from app.api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Government & Administration"])


@router.get(
    "/dashboard",
    response_model=AdminDashboardStatsResponse,
    summary="Government & Admin Aggregated Dashboard",
    description="Calculates comprehensive database-driven statistics across all farmers, farms, hazard distributions, and priority interventions."
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AdminDashboardStatsResponse:
    return admin_service.get_dashboard_stats(db)


@router.get(
    "/farmers",
    response_model=List[AdminFarmerItem],
    summary="List Registered Farmers for Administration",
    description="Returns full farmer directory with holdings count and current farm risk exposure."
)
def get_admin_farmers(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[AdminFarmerItem]:
    return admin_service.get_admin_farmers(db)


@router.get(
    "/alerts",
    response_model=List[AlertItemResponse],
    summary="System-Wide Alerts Roster",
    description="Returns all high-risk climate alerts generated across the platform."
)
def get_admin_alerts(
    unread_only: bool = Query(False, description="Filter for unread alerts only"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[AlertItemResponse]:
    query = db.query(Alert).order_by(desc(Alert.created_at))
    if unread_only:
        query = query.filter(Alert.is_read == False)
    alerts = query.limit(100).all()
    return [AlertItemResponse.model_validate(a) for a in alerts]


@router.get(
    "/risk-map",
    response_model=List[RiskMapPoint],
    summary="Government Geographic Risk Map Points",
    description="Retrieves registered farm coordinates, latest hazard predictions, and vulnerability levels for Leaflet mapping."
)
def get_risk_map_points(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[RiskMapPoint]:
    return admin_service.get_risk_map_points(db)


@router.get(
    "/vulnerability",
    response_model=VulnerabilityAssessmentResponse,
    summary="Government Vulnerability Assessment & Priority Hotspots",
    description="Calculates composite vulnerability analysis identifying top vulnerable farms, regional risk clusters, and policy interventions."
)
def get_vulnerability_assessment(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> VulnerabilityAssessmentResponse:
    return admin_service.get_vulnerability_assessment(db)
