from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import StudentProfile, User
from app.schemas import StudentProfileRequest, StudentProfileResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


async def _get_or_create(db: AsyncSession, user: User) -> StudentProfile:
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile:
        return profile
    profile = StudentProfile(user_id=user.id)
    db.add(profile)
    await db.flush()
    return profile


@router.get("", response_model=StudentProfileResponse)
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create(db, user)
    await db.commit()
    return StudentProfileResponse(
        level=profile.level,
        target_band=profile.target_band,
        native_language=profile.native_language,
        weaknesses=profile.weaknesses or [],
    )


@router.put("", response_model=StudentProfileResponse)
async def set_profile(
    req: StudentProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create(db, user)
    profile.level = req.level
    profile.target_band = req.target_band
    profile.native_language = req.native_language
    profile.weaknesses = req.weaknesses
    await db.commit()
    return StudentProfileResponse(
        level=profile.level,
        target_band=profile.target_band,
        native_language=profile.native_language,
        weaknesses=profile.weaknesses or [],
    )
