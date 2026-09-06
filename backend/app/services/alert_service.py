"""
Alert Service for KrushiRakshak.
Automatically generates and persists urgent agro-climatic alerts in PostgreSQL
when a farm parcel evaluates at HIGH risk (>= 71 score).
Provides alert triage, unread counting, and mark-as-read workflows.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.farm import Farm
from app.models.farmer_profile import FarmerProfile


def get_default_action_for_hazard(risk_type: str, crop: str) -> str:
    r = risk_type.lower()
    if "drought" in r:
        return f"Provide protective irrigation immediately and apply 1% potassium nitrate foliar spray to preserve {crop} canopy moisture."
    elif "flood" in r or "inundat" in r or "heavy" in r:
        return f"Clear boundary drainage furrows within 12–24h to prevent root asphyxiation and waterlogging in {crop} field."
    elif "heat" in r:
        return f"Deliver evening light sprinkler irrigation to reduce canopy temperature and prevent floral abortion in {crop}."
    elif "extreme" in r or "rain" in r:
        return f"Open drainage ditches, secure perimeter bunds, and postpone fertilizer broadcasting ahead of storm downpours."
    return f"Monitor {crop} field conditions closely and implement protective agricultural practices."


class AlertService:
    def create_alert_if_high_risk(
        self,
        farm: Farm,
        risk_type: str,
        risk_score: int,
        risk_level: str,
        factors: List[str],
        db: Session
    ) -> Optional[Alert]:
        """
        Creates an Alert in PostgreSQL if the evaluated risk is HIGH (>= 71).
        Debounces duplicate unread alerts for the same farm and risk within 10 minutes.
        """
        if risk_level != "HIGH" and risk_score < 71:
            return None

        ten_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        recent_unread = (
            db.query(Alert)
            .filter(
                Alert.farm_id == farm.id,
                Alert.risk_type == risk_type,
                Alert.is_read == False,
                Alert.created_at >= ten_mins_ago
            )
            .first()
        )
        if recent_unread:
            # Update score if higher
            if risk_score > recent_unread.risk_score:
                recent_unread.risk_score = risk_score
                db.commit()
                db.refresh(recent_unread)
            return recent_unread

        # Construct short explanation from primary contributing factors
        if factors:
            short_explanation = f"Critical agro-climatic hazard detected: {factors[0]}."
            if len(factors) > 1:
                short_explanation += f" Contributing: {factors[1]}."
        else:
            short_explanation = f"Severe {risk_type} threat detected with risk score {risk_score}/100."

        recommended_action = get_default_action_for_hazard(risk_type, farm.crop or "crop")

        alert = Alert(
            farmer_id=farm.farmer_id,
            farm_id=farm.id,
            farm_name=farm.farm_name,
            crop=farm.crop or "Field Crop",
            risk_type=risk_type,
            risk_score=risk_score,
            risk_level="HIGH" if risk_score < 85 else "CRITICAL",
            short_explanation=short_explanation,
            recommended_action=recommended_action,
            is_read=False
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def get_farmer_alerts(self, farmer_id: int, db: Session) -> Dict[str, Any]:
        """
        Retrieves all alerts for a farmer profile (supports either farmer_profile.id or user.id).
        """
        profile = (
            db.query(FarmerProfile)
            .filter((FarmerProfile.id == farmer_id) | (FarmerProfile.user_id == farmer_id))
            .first()
        )
        profile_id = profile.id if profile else farmer_id

        alerts = (
            db.query(Alert)
            .filter(Alert.farmer_id == profile_id)
            .order_by(Alert.created_at.desc())
            .all()
        )

        unread_count = sum(1 for a in alerts if not a.is_read)

        return {
            "farmer_id": profile_id,
            "unread_count": unread_count,
            "alerts": alerts
        }

    def mark_alert_read(self, alert_id: int, db: Session) -> Optional[Alert]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert


alert_service = AlertService()
