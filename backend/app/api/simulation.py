from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.simulation_service import simulation_service
from app.api.risk import predict_farm_risk

router = APIRouter(prefix="/simulation", tags=["Climate Stress Simulation Engine"])


class SimulationRunRequest(BaseModel):
    farm_id: int = Field(..., description="ID of the farm to simulate")
    scenario: str = Field(
        ...,
        description="Scenario key: 'heavy_rainfall', 'drought', or 'heatwave'"
    )
    language: str = Field("en", description="Language for generated advisory ('en', 'mr', 'hi', 'kn')")


class SimulationScenarioInfo(BaseModel):
    key: str
    title: str
    description: str
    simulated_inputs: Dict[str, Any]


@router.get(
    "/scenarios",
    response_model=List[SimulationScenarioInfo],
    summary="List Available Climate Stress Scenarios",
    description="Returns pre-calibrated climate stress scenarios (Heavy Rainfall, Drought, Heatwave)."
)
def list_scenarios() -> List[SimulationScenarioInfo]:
    return [
        SimulationScenarioInfo(**s)
        for s in simulation_service.get_available_scenarios()
    ]


@router.post(
    "/run",
    summary="Run Real-Pipeline Climate Simulation",
    description="Feeds scenario parameters through the actual Random Forest ML engine, saves the prediction, updates advisory, and triggers high-risk alerts if applicable."
)
def run_simulation(
    payload: SimulationRunRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        result = simulation_service.run_simulation(
            farm_id=payload.farm_id,
            scenario_key=payload.scenario,
            db=db,
            lang=payload.language
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post(
    "/reset/{farm_id}",
    summary="Reset to Live Telemetry",
    description="Re-runs risk prediction with live microclimate and soil telemetry, clearing active simulation state."
)
async def reset_simulation(
    farm_id: int,
    db: Session = Depends(get_db)
):
    return await predict_farm_risk(farm_id=farm_id, db=db)
