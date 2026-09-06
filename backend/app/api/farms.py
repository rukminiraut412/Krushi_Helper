from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.farmer_profile import FarmerProfile
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from app.api.deps import get_current_user, get_current_farmer_profile

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new farm",
    description="Adds a farm for the authenticated farmer. A farmer can register multiple farms."
)
def create_farm(
    payload: FarmCreate,
    farmer_profile: FarmerProfile = Depends(get_current_farmer_profile),
    db: Session = Depends(get_db)
):
    farm = Farm(
        farmer_id=farmer_profile.id,
        farm_name=payload.farm_name,
        area=payload.area,
        crop=payload.crop,
        sowing_date=payload.sowing_date,
        soil_type=payload.soil_type,
        irrigation_available=payload.irrigation_available,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get(
    "",
    response_model=List[FarmResponse],
    summary="List all farms belonging to authenticated farmer",
    description="Returns all farm parcels owned by the currently authenticated farmer."
)
def list_farms(
    farmer_profile: FarmerProfile = Depends(get_current_farmer_profile),
    db: Session = Depends(get_db)
):
    farms = db.query(Farm).filter(Farm.farmer_id == farmer_profile.id).order_by(Farm.created_at.desc()).all()
    return farms


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Get farm details by ID",
    description="Returns full details for a single farm. Only accessible to the farm owner."
)
def get_farm(
    farm_id: int,
    farmer_profile: FarmerProfile = Depends(get_current_farmer_profile),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    if farm.farmer_id != farmer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this farm."
        )
    return farm


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Update farm details",
    description="Updates existing farm attributes. Only the owner can modify their farm."
)
def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    farmer_profile: FarmerProfile = Depends(get_current_farmer_profile),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    if farm.farmer_id != farmer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this farm."
        )

    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(farm, field, val)

    db.commit()
    db.refresh(farm)
    return farm


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a farm",
    description="Deletes a farm parcel permanently. Only the owner can delete their farm."
)
def delete_farm(
    farm_id: int,
    farmer_profile: FarmerProfile = Depends(get_current_farmer_profile),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    if farm.farmer_id != farmer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this farm."
        )

    db.delete(farm)
    db.commit()
    return {
        "status": "success",
        "message": f"Farm '{farm.farm_name}' (ID: {farm_id}) was successfully deleted."
    }
