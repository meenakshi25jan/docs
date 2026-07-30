"""Knowledge Intelligence API."""

from fastapi import APIRouter, Depends, Query

from app.core.security import TokenPayload, get_current_user
from app.schemas.knowledge_intelligence import (
    KnowledgeSearchResponse,
    LessonContextResponse,
    MistakeContextResponse,
)
from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Intelligence"])
_service = KnowledgeIntelligenceService()


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=500),
    skill_focus: str | None = Query(None),
    lesson_id: str | None = Query(None),
    cefr_level: str | None = Query(None),
    target_exam: str | None = Query(None),
    user: TokenPayload = Depends(get_current_user),
):
    tenant_id = str(user.tenant_id) if user.tenant_id else None
    return await _service.search(
        q,
        skill_focus=skill_focus,
        lesson_id=lesson_id,
        cefr_level=cefr_level,
        target_exam=target_exam,
        tenant_id=tenant_id,
        top_k=5,
    )


@router.get("/lesson-context", response_model=LessonContextResponse)
async def get_lesson_context(
    lesson_id: str = Query(..., min_length=1, max_length=120),
    cefr_level: str | None = Query(None),
    target_exam: str | None = Query(None),
    user: TokenPayload = Depends(get_current_user),
):
    tenant_id = str(user.tenant_id) if user.tenant_id else None
    return await _service.build_lesson_context(
        lesson_id,
        cefr_level=cefr_level,
        target_exam=target_exam,
        tenant_id=tenant_id,
    )


@router.get("/mistake-context", response_model=MistakeContextResponse)
async def get_mistake_context(
    error_category: str = Query(..., min_length=1, max_length=100),
    error_type: str | None = Query(None),
    error_text: str | None = Query(None),
    cefr_level: str | None = Query(None),
    user: TokenPayload = Depends(get_current_user),
):
    tenant_id = str(user.tenant_id) if user.tenant_id else None
    return await _service.build_mistake_context(
        error_category,
        error_type=error_type,
        error_text=error_text,
        cefr_level=cefr_level,
        tenant_id=tenant_id,
    )
