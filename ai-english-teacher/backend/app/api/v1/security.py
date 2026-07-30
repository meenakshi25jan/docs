"""Security diagnostics — admin read-only probes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, require_role
from app.schemas.security_diagnostics import (
    AuthSecurityResponse,
    AuthorizationSecurityResponse,
    RLSCoverageResponse,
    SecuritySummaryResponse,
)
from app.services.security_service import (
    get_auth_diagnostics,
    get_authorization_diagnostics,
    get_rls_diagnostics,
    get_security_summary,
)

router = APIRouter(prefix="/security", tags=["Security"])


@router.get("/summary", response_model=SecuritySummaryResponse)
async def security_summary(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await get_security_summary(db, user)


@router.get("/rls", response_model=RLSCoverageResponse)
async def security_rls(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await get_rls_diagnostics(db, user)


@router.get("/auth", response_model=AuthSecurityResponse)
async def security_auth(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return get_auth_diagnostics(db, user)


@router.get("/authorization", response_model=AuthorizationSecurityResponse)
async def security_authorization(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return get_authorization_diagnostics(db, user)
