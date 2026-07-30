"""Student Intelligence API — learner state for personalized teaching."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.schemas.student_intelligence import (
    LearningPreferencesResponse,
    LearningPreferencesUpdate,
    StudentMistakesResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
    StudentSkillsResponse,
    StudentSummaryResponse,
)
from app.services.student_intelligence_service import (
    build_skills,
    get_mistakes,
    get_preferences,
    get_profile,
    get_summary,
    update_preferences,
    update_profile,
)

router = APIRouter(prefix="/student-intelligence", tags=["Student Intelligence"])


async def _learner_id_from_user(db: AsyncSession, user: TokenPayload):
    from sqlalchemy import select
    from app.models import LearnerProfile

    learner = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not learner:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return learner.id


@router.get("/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_profile(db, user_id=user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/profile", response_model=StudentProfileResponse)
async def patch_student_profile(
    body: StudentProfileUpdate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_profile(db, user_id=user.user_id, updates=body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/skills", response_model=StudentSkillsResponse)
async def get_student_skills(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner_id = await _learner_id_from_user(db, user)
    return await build_skills(db, learner_id=learner_id)


@router.get("/mistakes", response_model=StudentMistakesResponse)
async def get_student_mistakes(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner_id = await _learner_id_from_user(db, user)
    return await get_mistakes(db, learner_id=learner_id)


@router.get("/preferences", response_model=LearningPreferencesResponse)
async def get_student_preferences(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_preferences(db, user_id=user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/preferences", response_model=LearningPreferencesResponse)
async def patch_student_preferences(
    body: LearningPreferencesUpdate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_preferences(db, user_id=user.user_id, updates=body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/summary", response_model=StudentSummaryResponse)
async def get_student_summary(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_summary(db, user_id=user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
