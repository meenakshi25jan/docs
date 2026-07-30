"""Production readiness APIs — admin deployment verification (read-only)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, require_role
from app.schemas.production_readiness import (
    EnvironmentVerificationResponse,
    MigrationVerificationResponse,
    ProductionReadinessSummary,
    SecurityVerificationResponse,
)
from app.services.production_readiness_service import (
    build_readiness_summary,
    verify_environment,
    verify_migrations,
    verify_security_status,
)

router = APIRouter(prefix="/production", tags=["Production Readiness"])


@router.get("/readiness", response_model=ProductionReadinessSummary)
async def production_readiness(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await build_readiness_summary(db, user)


@router.get("/migrations", response_model=MigrationVerificationResponse)
async def production_migrations(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await verify_migrations(db)


@router.get("/security", response_model=SecurityVerificationResponse)
async def production_security(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await verify_security_status(db, user)


@router.get("/environment", response_model=EnvironmentVerificationResponse)
async def production_environment(
    user: TokenPayload = Depends(require_role("admin")),
):
    return verify_environment()
