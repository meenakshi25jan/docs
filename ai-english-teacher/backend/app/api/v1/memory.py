"""Memory Intelligence API — read-only memory summary for authenticated learners."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.schemas.memory_intelligence import MemoryReflectionsResponse, MemorySummaryResponse
from app.services.memory_intelligence_service import MemoryIntelligenceService

router = APIRouter(prefix="/memory", tags=["Memory Intelligence"])


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.get("/summary", response_model=MemorySummaryResponse)
async def get_memory_summary(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    service = MemoryIntelligenceService()
    bundle = await service.build_bundle(
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        db=db,
    )
    return MemorySummaryResponse(
        memory_summary=bundle.memory_summary,
        recurring_mistakes_count=len(bundle.recurring_mistakes),
        reflections_count=len(bundle.lesson_reflections),
        skill_weaknesses=bundle.skill_weaknesses,
        preferences=bundle.preferences,
        metadata=bundle.metadata.model_dump(),
    )


@router.get("/reflections", response_model=MemoryReflectionsResponse)
async def get_memory_reflections(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    service = MemoryIntelligenceService()
    bundle = await service.build_bundle(
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        db=db,
    )
    return MemoryReflectionsResponse(reflections=bundle.lesson_reflections)
