"""Analytics & Insights API — read-only learner analytics."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CurriculumAnalyticsResponse,
    GovernanceAnalyticsResponse,
    KnowledgeAnalyticsResponse,
    LearnerInsightsResponse,
    ProgressAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
_service = AnalyticsService()


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def analytics_overview(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_overview(db, user_id=user.user_id, tenant_id=user.tenant_id)


@router.get("/progress", response_model=ProgressAnalyticsResponse)
async def analytics_progress(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_progress(db, user_id=user.user_id, tenant_id=user.tenant_id)


@router.get("/governance", response_model=GovernanceAnalyticsResponse)
async def analytics_governance(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_governance(db, user_id=user.user_id, tenant_id=user.tenant_id)


@router.get("/curriculum", response_model=CurriculumAnalyticsResponse)
async def analytics_curriculum(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_curriculum(db, user_id=user.user_id, tenant_id=user.tenant_id)


@router.get("/knowledge", response_model=KnowledgeAnalyticsResponse)
async def analytics_knowledge(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_knowledge(db, user_id=user.user_id, tenant_id=user.tenant_id)


@router.get("/insights", response_model=LearnerInsightsResponse)
async def analytics_insights(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_insights(db, user_id=user.user_id, tenant_id=user.tenant_id)
