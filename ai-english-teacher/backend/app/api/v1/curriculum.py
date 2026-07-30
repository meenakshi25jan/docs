"""Curriculum Intelligence API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.schemas.curriculum_intelligence import (
    CurriculumLessonResponse,
    CurriculumRecommendationBundle,
    CurriculumSkillResponse,
    CurriculumTopicResponse,
    LearningPathResponse,
    LessonCompletionRequest,
    LessonCompletionResponse,
    RevisionItemResponse,
)
from app.services.curriculum_intelligence_service import CurriculumIntelligenceService
from app.services.memory_intelligence_service import MemoryIntelligenceService

router = APIRouter(prefix="/curriculum", tags=["Curriculum Intelligence"])
_service = CurriculumIntelligenceService()


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.get("/topics", response_model=list[CurriculumTopicResponse])
async def list_topics():
    return _service.list_topics()


@router.get("/skills", response_model=list[CurriculumSkillResponse])
async def list_skills(topic_id: str | None = Query(None)):
    return _service.list_skills(topic_id)


@router.get("/lessons", response_model=list[CurriculumLessonResponse])
async def list_lessons(
    topic_id: str | None = Query(None),
    skill_focus: str | None = Query(None),
    cefr_level: str | None = Query(None),
):
    return _service.list_lessons(topic_id=topic_id, skill_focus=skill_focus, cefr_level=cefr_level)


@router.get("/recommended", response_model=CurriculumRecommendationBundle)
async def get_recommended(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    memory_bundle = None
    try:
        memory_bundle = await MemoryIntelligenceService().build_bundle(
            learner_id=str(learner.id),
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            db=db,
        )
    except Exception:  # noqa: BLE001
        memory_bundle = None
    try:
        return await _service.build_recommendations(db, user_id=user.user_id, memory_bundle=memory_bundle)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/learning-path", response_model=LearningPathResponse)
async def get_learning_path(
    type: str = Query("daily", alias="type"),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.build_learning_path(db, user_id=user.user_id, path_type=type)


@router.post("/lesson-complete", response_model=LessonCompletionResponse)
async def post_lesson_complete(
    req: LessonCompletionRequest,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    return await _service.complete_lesson(
        db,
        tenant_id=learner.tenant_id,
        learner_id=learner.id,
        lesson_id=req.lesson_id,
        title=req.title,
        skill_focus=req.skill_focus,
        route=req.route,
        score=req.score,
        metadata=req.metadata,
    )


@router.get("/revision-schedule", response_model=list[RevisionItemResponse])
async def get_revision_schedule(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    return await _service.list_revision_schedule(db, learner_id=learner.id)
