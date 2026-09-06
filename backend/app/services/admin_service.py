from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User, UserRole
from app.models.farmer_profile import FarmerProfile
from app.models.farm import Farm
from app.models.risk_prediction import RiskPrediction
from app.models.alert import Alert
from app.schemas.admin import (
    AdminDashboardStatsResponse,
    PriorityInterventionItem,
    RecentHighRiskFarm,
    CropCount,
    RiskDistribution,
    RiskMapPoint,
    VulnerabilityAssessmentResponse,
    VulnerableAreaSummary,
    AdminFarmerItem
)
from app.services.alert_service import get_default_action_for_hazard


def compute_vulnerability(
    risk_score: int,
    irrigation_available: bool,
    crop: str,
    repeated_high_risks: int
) -> tuple[int, str]:
    """
    Computes a composite vulnerability score (0-100) and classification (LOW, MEDIUM, HIGH)
    combining AI risk score, irrigation dependency, crop sensitivity, and historical repeated risk.
    """
    score = float(risk_score)

    # 1. Irrigation factor: Rainfed farms have higher vulnerability to drought/heat
    if not irrigation_available:
        score += 15.0

    # 2. Crop sensitivity factor
    crop_lower = (crop or "").lower()
    if any(c in crop_lower for c in ["cotton", "soybean", "groundnut", "chilli"]):
        score += 8.0
    elif any(c in crop_lower for c in ["wheat", "mustard"]):
        score += 5.0

    # 3. Repeated high risk occurrence
    if repeated_high_risks > 1:
        score += 12.0
    elif repeated_high_risks == 1:
        score += 5.0

    final_score = int(min(100, max(0, round(score))))
    if final_score >= 70:
        level = "HIGH"
    elif final_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"

    return final_score, level


class AdminService:

    def get_dashboard_stats(self, db: Session) -> AdminDashboardStatsResponse:
        total_farmers = db.query(User).filter(User.role == UserRole.FARMER).count()
        total_farms = db.query(Farm).count()

        farms = db.query(Farm).all()

        high_risk_count = 0
        med_risk_count = 0
        low_risk_count = 0

        drought_count = 0
        flood_count = 0
        heat_count = 0
        extreme_count = 0

        priority_items: List[PriorityInterventionItem] = []
        recent_high_list: List[RecentHighRiskFarm] = []

        crop_stats: Dict[str, Dict[str, float]] = {}

        for farm in farms:
            # Crop stats aggregation
            c_name = farm.crop or "Other"
            if c_name not in crop_stats:
                crop_stats[c_name] = {"count": 0, "area": 0.0}
            crop_stats[c_name]["count"] += 1
            crop_stats[c_name]["area"] += float(farm.area or 0.0)

            # Get latest risk prediction for this farm
            latest_pred = (
                db.query(RiskPrediction)
                .filter(RiskPrediction.farm_id == farm.id)
                .order_by(desc(RiskPrediction.created_at))
                .first()
            )

            # High risk history count for vulnerability calculation
            high_risk_history_count = (
                db.query(RiskPrediction)
                .filter(
                    RiskPrediction.farm_id == farm.id,
                    RiskPrediction.risk_level == "HIGH"
                )
                .count()
            )

            farmer_user = db.query(User).filter(User.id == farm.farmer_id).first()
            farmer_profile = (
                db.query(FarmerProfile)
                .filter((FarmerProfile.id == farm.farmer_id) | (FarmerProfile.user_id == farm.farmer_id))
                .first()
            )

            farmer_name = farmer_user.name if farmer_user else "Farmer"
            farmer_mobile = farmer_user.mobile if farmer_user else "N/A"

            if latest_pred:
                r_scores = {
                    "Drought": latest_pred.drought_score,
                    "Flood": latest_pred.flood_score,
                    "Heat Stress": latest_pred.heat_score,
                    "Extreme Rainfall": latest_pred.extreme_rainfall_score,
                }
                highest_type = max(r_scores, key=r_scores.get)
                dominant_score = r_scores[highest_type]
                r_level = latest_pred.risk_level.upper() if latest_pred.risk_level else "LOW"

                vuln_score, vuln_level = compute_vulnerability(
                    dominant_score,
                    farm.irrigation_available,
                    farm.crop or "",
                    high_risk_history_count
                )

                if r_level == "HIGH" or dominant_score >= 71:
                    high_risk_count += 1
                elif r_level == "MEDIUM" or dominant_score >= 31:
                    med_risk_count += 1
                else:
                    low_risk_count += 1

                # Specific hazard counts
                if highest_type == "Drought" and dominant_score >= 31:
                    drought_count += 1
                elif highest_type == "Flood" and dominant_score >= 31:
                    flood_count += 1
                elif highest_type == "Heat Stress" and dominant_score >= 31:
                    heat_count += 1
                elif highest_type == "Extreme Rainfall" and dominant_score >= 31:
                    extreme_count += 1

                action = get_default_action_for_hazard(highest_type, farm.crop or "crop")

                item = PriorityInterventionItem(
                    farm_id=farm.id,
                    farm_name=farm.farm_name,
                    farmer_id=farm.farmer_id,
                    farmer_name=farmer_name,
                    mobile=farmer_mobile,
                    crop=farm.crop or "Field Crop",
                    area=float(farm.area or 0.0),
                    latitude=farm.latitude,
                    longitude=farm.longitude,
                    village=farmer_profile.village if farmer_profile else None,
                    district=farmer_profile.district if farmer_profile else None,
                    state=farmer_profile.state if farmer_profile else None,
                    risk_type=highest_type,
                    risk_score=dominant_score,
                    risk_level=r_level,
                    vulnerability_level=vuln_level,
                    recommended_action=action,
                    timestamp=latest_pred.created_at
                )
                priority_items.append(item)

                if r_level == "HIGH":
                    recent_high_list.append(
                        RecentHighRiskFarm(
                            farm_id=farm.id,
                            farm_name=farm.farm_name,
                            farmer_name=farmer_name,
                            crop=farm.crop or "Field Crop",
                            risk_type=highest_type,
                            risk_score=dominant_score,
                            risk_level=r_level,
                            created_at=latest_pred.created_at
                        )
                    )
            else:
                # No prediction run yet -> baseline low risk
                low_risk_count += 1

        # Sort priority interventions by risk score descending
        priority_items.sort(key=lambda x: (x.risk_score, x.area), reverse=True)
        recent_high_list.sort(key=lambda x: x.created_at, reverse=True)

        crop_distribution = [
            CropCount(crop=k, count=v["count"], area_acres=round(v["area"], 1))
            for k, v in crop_stats.items()
        ]
        crop_distribution.sort(key=lambda x: x.count, reverse=True)

        total_evaluated = max(1, total_farms)
        risk_pcts = {
            "LOW": round((low_risk_count / total_evaluated) * 100, 1),
            "MEDIUM": round((med_risk_count / total_evaluated) * 100, 1),
            "HIGH": round((high_risk_count / total_evaluated) * 100, 1),
        }

        return AdminDashboardStatsResponse(
            total_farmers=total_farmers,
            total_farms=total_farms,
            high_risk_farms=high_risk_count,
            medium_risk_farms=med_risk_count,
            low_risk_farms=low_risk_count,
            drought_risk_farms=drought_count,
            flood_risk_farms=flood_count,
            heat_stress_farms=heat_count,
            extreme_rainfall_farms=extreme_count,
            risk_distribution=RiskDistribution(
                low=low_risk_count,
                medium=med_risk_count,
                high=high_risk_count
            ),
            risk_level_percentages=risk_pcts,
            crop_distribution=crop_distribution,
            recent_high_risk_farms=recent_high_list[:10],
            priority_intervention_list=priority_items
        )

    def get_risk_map_points(self, db: Session) -> List[RiskMapPoint]:
        farms = db.query(Farm).all()
        points: List[RiskMapPoint] = []

        for farm in farms:
            # Skip if farm has no geographic coordinates
            if farm.latitude is None or farm.longitude is None:
                continue

            farmer_user = db.query(User).filter(User.id == farm.farmer_id).first()
            farmer_profile = (
                db.query(FarmerProfile)
                .filter((FarmerProfile.id == farm.farmer_id) | (FarmerProfile.user_id == farm.farmer_id))
                .first()
            )

            latest_pred = (
                db.query(RiskPrediction)
                .filter(RiskPrediction.farm_id == farm.id)
                .order_by(desc(RiskPrediction.created_at))
                .first()
            )

            high_risk_history_count = (
                db.query(RiskPrediction)
                .filter(
                    RiskPrediction.farm_id == farm.id,
                    RiskPrediction.risk_level == "HIGH"
                )
                .count()
            )

            if latest_pred:
                r_scores = {
                    "Drought": latest_pred.drought_score,
                    "Flood": latest_pred.flood_score,
                    "Heat Stress": latest_pred.heat_score,
                    "Extreme Rainfall": latest_pred.extreme_rainfall_score,
                }
                highest_type = max(r_scores, key=r_scores.get)
                score = r_scores[highest_type]
                level = latest_pred.risk_level.upper() if latest_pred.risk_level else "LOW"
                factors = latest_pred.contributing_factors or []
                eval_date = latest_pred.created_at
            else:
                highest_type = "Baseline Safe"
                score = 15
                level = "LOW"
                factors = ["No adverse climate stress recorded"]
                eval_date = None

            vuln_score, vuln_level = compute_vulnerability(
                score,
                farm.irrigation_available,
                farm.crop or "",
                high_risk_history_count
            )

            points.append(
                RiskMapPoint(
                    farm_id=farm.id,
                    farm_name=farm.farm_name,
                    farmer_name=farmer_user.name if farmer_user else "Farmer",
                    mobile=farmer_user.mobile if farmer_user else "N/A",
                    crop=farm.crop or "Field Crop",
                    area=float(farm.area or 0.0),
                    latitude=float(farm.latitude),
                    longitude=float(farm.longitude),
                    village=farmer_profile.village if farmer_profile else None,
                    district=farmer_profile.district if farmer_profile else None,
                    state=farmer_profile.state if farmer_profile else None,
                    risk_type=highest_type,
                    risk_score=score,
                    risk_level=level,
                    vulnerability_score=vuln_score,
                    vulnerability_level=vuln_level,
                    contributing_factors=factors,
                    irrigation_available=farm.irrigation_available,
                    soil_type=farm.soil_type,
                    latest_evaluated_at=eval_date
                )
            )

        return points

    def get_vulnerability_assessment(self, db: Session) -> VulnerabilityAssessmentResponse:
        stats = self.get_dashboard_stats(db)
        interventions = stats.priority_intervention_list

        # Most vulnerable: sorted by vulnerability level (HIGH > MEDIUM > LOW) and risk score
        vuln_sorted = sorted(
            interventions,
            key=lambda x: (
                1 if x.vulnerability_level == "HIGH" else (2 if x.vulnerability_level == "MEDIUM" else 3),
                -x.risk_score
            )
        )

        # Regional Aggregation by District
        district_data: Dict[str, Dict[str, Any]] = {}
        for item in interventions:
            dist_key = item.district or "Central Agro Zone"
            state_key = item.state or "Maharashtra"
            if dist_key not in district_data:
                district_data[dist_key] = {
                    "district": dist_key,
                    "state": state_key,
                    "farms": 0,
                    "total_risk": 0,
                    "high_risk_count": 0,
                    "hazards": {}
                }
            district_data[dist_key]["farms"] += 1
            district_data[dist_key]["total_risk"] += item.risk_score
            if item.risk_level == "HIGH":
                district_data[dist_key]["high_risk_count"] += 1

            hz = item.risk_type
            district_data[dist_key]["hazards"][hz] = district_data[dist_key]["hazards"].get(hz, 0) + 1

        vulnerable_areas: List[VulnerableAreaSummary] = []
        for dist_key, d in district_data.items():
            f_count = d["farms"]
            avg_risk = round(d["total_risk"] / max(1, f_count), 1)
            dom_hz = max(d["hazards"], key=d["hazards"].get) if d["hazards"] else "Drought"
            vulnerable_areas.append(
                VulnerableAreaSummary(
                    district=dist_key,
                    state=d["state"],
                    farm_count=f_count,
                    avg_risk_score=avg_risk,
                    avg_vulnerability_score=round(avg_risk * 1.1, 1),
                    dominant_hazard=dom_hz,
                    high_risk_count=d["high_risk_count"]
                )
            )

        vulnerable_areas.sort(key=lambda x: (x.high_risk_count, x.avg_risk_score), reverse=True)

        priority_intervention_areas = [
            f"{a.district} ({a.state}) - {a.dominant_hazard} hazard cluster ({a.high_risk_count} high-risk farms)"
            for a in vulnerable_areas if a.high_risk_count > 0 or a.avg_risk_score >= 50
        ]
        if not priority_intervention_areas and vulnerable_areas:
            priority_intervention_areas = [
                f"{a.district} ({a.state}) - Monitored for climate volatility"
                for a in vulnerable_areas[:3]
            ]

        main_factors = [
            "Lack of micro-irrigation infrastructure on rainfed dryland holdings",
            "Elevated heat accumulation during terminal crop flowering stages",
            "Saturated soil conditions with poor infiltration in low-elevation parcels",
            "Recurrent unseasonal precipitation spikes exceeding drainage capacity"
        ]

        return VulnerabilityAssessmentResponse(
            most_vulnerable_farms=vuln_sorted[:15],
            vulnerable_areas=vulnerable_areas,
            priority_intervention_areas=priority_intervention_areas,
            main_risk_factors=main_factors,
            total_vulnerable_farms=len([x for x in interventions if x.vulnerability_level in ["HIGH", "MEDIUM"]])
        )

    def get_admin_farmers(self, db: Session) -> List[AdminFarmerItem]:
        farmers = db.query(User).filter(User.role == UserRole.FARMER).all()
        result: List[AdminFarmerItem] = []

        for f in farmers:
            profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == f.id).first()
            farms = db.query(Farm).filter(Farm.farmer_id == f.id).all()

            highest_score = 0
            highest_lvl = "LOW"

            for farm in farms:
                pred = (
                    db.query(RiskPrediction)
                    .filter(RiskPrediction.farm_id == farm.id)
                    .order_by(desc(RiskPrediction.created_at))
                    .first()
                )
                if pred:
                    max_s = max(pred.drought_score, pred.flood_score, pred.heat_score, pred.extreme_rainfall_score)
                    if max_s > highest_score:
                        highest_score = max_s
                        highest_lvl = pred.risk_level

            result.append(
                AdminFarmerItem(
                    id=profile.id if profile else f.id,
                    user_id=f.id,
                    name=f.name,
                    mobile=f.mobile,
                    village=profile.village if profile else None,
                    district=profile.district if profile else None,
                    state=profile.state if profile else None,
                    preferred_language=f.preferred_language or "en",
                    farm_count=len(farms),
                    highest_risk_level=highest_lvl if farms else "NONE",
                    highest_risk_score=highest_score if farms else None,
                    created_at=f.created_at
                )
            )

        result.sort(key=lambda x: (x.highest_risk_score or 0), reverse=True)
        return result


admin_service = AdminService()
