from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert import Alert
from app.models.farm import Farm
from app.models.farmer_profile import FarmerProfile
from app.schemas.alert import AlertListResponse, AlertItemResponse, AlertSimulateRequest
from app.services.alert_service import alert_service, get_default_action_for_hazard

router = APIRouter(prefix="/alerts", tags=["AI Climate Risk Alerts"])


@router.get(
    "/{farmer_id}",
    response_model=AlertListResponse,
    summary="Get Farmer Alerts & Unread Count",
    description="Returns all high-priority risk alerts and unread counter for the specified farmer."
)
def get_farmer_alerts(
    farmer_id: int,
    db: Session = Depends(get_db)
) -> AlertListResponse:
    # Verify farmer exists (by farmer_profile.id or user.id)
    profile = (
        db.query(FarmerProfile)
        .filter((FarmerProfile.id == farmer_id) | (FarmerProfile.user_id == farmer_id))
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found."
        )

    result = alert_service.get_farmer_alerts(profile.id, db)
    return AlertListResponse(**result)


@router.patch(
    "/{alert_id}/read",
    response_model=AlertItemResponse,
    summary="Mark Alert as Read",
    description="Updates the read status of a specific alert to True."
)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db)
) -> AlertItemResponse:
    alert = alert_service.mark_alert_read(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found."
        )
    return AlertItemResponse.model_validate(alert)


@router.post(
    "/simulate",
    response_model=AlertItemResponse,
    summary="Simulate High Risk Alert",
    description="Generates an immediate HIGH risk alert for testing and demonstration on the farmer dashboard."
)
def simulate_alert(
    payload: AlertSimulateRequest,
    db: Session = Depends(get_db)
) -> AlertItemResponse:
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {payload.farm_id} not found."
        )

    risk_score = payload.risk_score or 85
    risk_level = "HIGH"
    short_explanation = (
        payload.short_explanation
        or f"Critical {payload.risk_type} risk threshold exceeded ({risk_score}/100) on {farm.farm_name}."
    )
    recommended_action = (
        payload.recommended_action
        or get_default_action_for_hazard(payload.risk_type or "Drought", farm.crop or "crop")
    )

    alert = Alert(
        farmer_id=farm.farmer_id,
        farm_id=farm.id,
        farm_name=farm.farm_name,
        crop=farm.crop or "Field Crop",
        risk_type=payload.risk_type or "Drought",
        risk_score=risk_score,
        risk_level=risk_level,
        short_explanation=short_explanation,
        recommended_action=recommended_action,
        is_read=False
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return AlertItemResponse.model_validate(alert)
