from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User, UserRole
from app.models.farmer_profile import FarmerProfile
from app.schemas.auth import (
    FarmerRegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileDTO
)
from app.utils.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer",
    description="Registers a farmer, creates their profile, securely hashes their password, and returns an initial JWT token."
)
def register_farmer(
    payload: FarmerRegisterRequest,
    db: Session = Depends(get_db)
):
    # 1. Check for duplicate mobile number
    existing = db.query(User).filter(User.mobile == payload.mobile).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this mobile number is already registered."
        )

    # 2. Hash password securely (never store plain-text)
    pw_hash = hash_password(payload.password)

    # 3. Create User record
    user = User(
        name=payload.name,
        mobile=payload.mobile,
        password_hash=pw_hash,
        role=UserRole.FARMER,
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.flush()  # Populates user.id

    # 4. Create FarmerProfile record
    profile = FarmerProfile(
        user_id=user.id,
        village=payload.village,
        district=payload.district,
        state=payload.state,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)

    # 5. Generate JWT Access Token
    token_payload = {
        "user_id": user.id,
        "mobile": user.mobile,
        "name": user.name,
        "role": user.role.value,
    }
    token = create_access_token(data=token_payload)

    user_dto = UserProfileDTO(
        id=user.id,
        name=user.name,
        mobile=user.mobile,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        village=profile.village,
        district=profile.district,
        state=profile.state,
        latitude=profile.latitude,
        longitude=profile.longitude,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user=user_dto
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with mobile and password",
    description="Authenticates a user via mobile and password, returning a JWT token containing their role."
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password."
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password."
        )

    # Fetch farmer profile if available
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user.id).first()

    token_payload = {
        "user_id": user.id,
        "mobile": user.mobile,
        "name": user.name,
        "role": user.role.value,
    }
    token = create_access_token(data=token_payload)

    user_dto = UserProfileDTO(
        id=user.id,
        name=user.name,
        mobile=user.mobile,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        village=profile.village if profile else None,
        district=profile.district if profile else None,
        state=profile.state if profile else None,
        latitude=profile.latitude if profile else None,
        longitude=profile.longitude if profile else None,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user=user_dto
    )


@router.get(
    "/me",
    response_model=UserProfileDTO,
    summary="Get current user profile",
    description="Protected endpoint: returns authenticated user details."
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    return UserProfileDTO(
        id=current_user.id,
        name=current_user.name,
        mobile=current_user.mobile,
        role=current_user.role,
        preferred_language=current_user.preferred_language,
        created_at=current_user.created_at,
        village=profile.village if profile else None,
        district=profile.district if profile else None,
        state=profile.state if profile else None,
        latitude=profile.latitude if profile else None,
        longitude=profile.longitude if profile else None,
    )


@router.get(
    "/admin-check",
    summary="Admin-only test endpoint",
    description="Protected endpoint: accessible ONLY to ADMIN role users."
)
def admin_check(admin: User = Depends(require_admin)):
    return {
        "status": "authorized",
        "message": f"Welcome Admin {admin.name} ({admin.mobile})",
        "role": admin.role.value
    }
