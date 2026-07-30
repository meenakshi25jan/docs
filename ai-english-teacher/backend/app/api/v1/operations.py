"""Enterprise Operations API — tenant-scoped operations endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user, require_role
from app.schemas.operations import (
    AdminSummaryResponse,
    FeatureFlagResponse,
    OperationsHealthResponse,
    OperationsOverviewResponse,
    OperationsUserResponse,
    ReportSummaryListResponse,
    TeacherLearnerSummaryResponse,
    TeacherRosterResponse,
    TenantSettingsResponse,
    TenantSettingsUpdateRequest,
)
from app.services.operations_service import OperationsService

router = APIRouter(prefix="/operations", tags=["Enterprise Operations"])
_service = OperationsService()


@router.get("/overview", response_model=OperationsOverviewResponse)
async def operations_overview(
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_operations_overview(db, user)


@router.get("/health", response_model=OperationsHealthResponse)
async def operations_health(
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
):
    return await _service.get_operations_health(user)


@router.get("/tenant", response_model=TenantSettingsResponse)
async def operations_tenant(
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_tenant_settings(db, user)


@router.patch("/tenant/settings", response_model=TenantSettingsResponse)
async def operations_tenant_settings(
    request: TenantSettingsUpdateRequest,
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.update_tenant_settings(db, user, request)


@router.get("/feature-flags", response_model=FeatureFlagResponse)
async def operations_feature_flags(
    user: TokenPayload = Depends(require_role("teacher", "admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_feature_flags(db, user)


@router.get("/users", response_model=list[OperationsUserResponse])
async def operations_users(
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.list_users(db, user)


@router.get("/teacher/roster", response_model=TeacherRosterResponse)
async def operations_teacher_roster(
    user: TokenPayload = Depends(require_role("teacher", "admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_teacher_roster(db, user)


@router.get("/teacher/learners/{learner_id}/summary", response_model=TeacherLearnerSummaryResponse)
async def operations_teacher_learner_summary(
    learner_id: UUID,
    user: TokenPayload = Depends(require_role("teacher", "admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_teacher_learner_summary(db, user, learner_id)


@router.get("/admin/summary", response_model=AdminSummaryResponse)
async def operations_admin_summary(
    user: TokenPayload = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_admin_summary(db, user)


@router.get("/reports/learner/{learner_id}", response_model=ReportSummaryListResponse)
async def operations_learner_reports(
    learner_id: UUID,
    user: TokenPayload = Depends(require_role("teacher", "admin", "super_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await _service.get_learner_reports(db, user, learner_id)
