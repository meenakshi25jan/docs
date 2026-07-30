"""Reliability and observability APIs — admin read-only."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, require_role
from app.schemas.reliability import (
    BackupStatusResponse,
    LoggingStatusResponse,
    PerformanceStatusResponse,
    ReliabilityStatusResponse,
)
from app.services.reliability_service import (
    get_backup_status,
    get_logging_status,
    get_performance_status,
    get_reliability_status,
)

router = APIRouter(prefix="/reliability", tags=["Reliability"])


@router.get("/status", response_model=ReliabilityStatusResponse)
async def reliability_status(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await get_reliability_status(db, user)


@router.get("/logging", response_model=LoggingStatusResponse)
async def reliability_logging(
    user: TokenPayload = Depends(require_role("admin")),
):
    return get_logging_status()


@router.get("/backup", response_model=BackupStatusResponse)
async def reliability_backup(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await get_backup_status(db)


@router.get("/performance", response_model=PerformanceStatusResponse)
async def reliability_performance(
    user: TokenPayload = Depends(require_role("admin")),
):
    return get_performance_status()
