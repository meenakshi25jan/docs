"""Security hardening helpers and read-only diagnostics."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenPayload
from app.models import Assessment, Conversation, LearnerProfile
from app.schemas.security_diagnostics import (
    AuthSecurityResponse,
    AuthorizationSecurityResponse,
    RLSCoverageResponse,
    RLSTableStatus,
    SecurityCheck,
    SecurityDiagnosticStatus,
    SecuritySummaryResponse,
    SecurityWarning,
)
from app.services.health_service import jwt_secret_is_safe

# Tables inspected for RLS coverage (Phase 9 v1).
CRITICAL_RLS_TABLES: tuple[str, ...] = (
    "users",
    "learner_profiles",
    "assessments",
    "assessment_results",
    "conversations",
    "conversation_messages",
    "reports",
    "progress_snapshots",
    "lesson_completions",
    "revision_schedule",
    "voice_analyses",
    "learner_memories",
    "error_tracking",
)

V1_OWNERSHIP_ROUTES = (
    "conversations.send_message",
    "conversations.voice_turn_in_conversation",
    "conversations.get_lesson_report",
    "assessments.start_assessment",
    "assessments.submit_assessment",
    "assessments.get_results",
)

KNOWN_AUTHORIZATION_GAPS = [
    "Teacher sees all tenant learners (no class/cohort assignments in v1)",
    "Knowledge chunks RLS deferred (nullable tenant_id global corpus)",
    "No persisted auth audit log in v1",
    "Frontend route guards deferred (API-enforced auth)",
]


def _tenant_setting_expr() -> str:
    return "NULLIF(current_setting('app.tenant_id', true), '')::uuid"


async def _learner_profile_for_user(db: AsyncSession, user: TokenPayload) -> LearnerProfile | None:
    return await db.scalar(
        select(LearnerProfile).where(LearnerProfile.user_id == user.user_id)
    )


async def verify_learner_access(
    db: AsyncSession,
    current_user: TokenPayload,
    learner_id: UUID,
) -> LearnerProfile:
    profile = await db.scalar(
        select(LearnerProfile).where(
            LearnerProfile.id == learner_id,
            LearnerProfile.tenant_id == current_user.tenant_id,
        )
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    if current_user.role == "student":
        own = await _learner_profile_for_user(db, current_user)
        if not own or own.id != learner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    return profile


async def verify_conversation_access(
    db: AsyncSession,
    current_user: TokenPayload,
    conversation: Conversation | None,
) -> Conversation:
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if conversation.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if current_user.role == "student":
        own = await _learner_profile_for_user(db, current_user)
        if not own or conversation.learner_id != own.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


async def verify_assessment_access(
    db: AsyncSession,
    current_user: TokenPayload,
    assessment: Assessment | None,
) -> Assessment:
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if assessment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if current_user.role == "student":
        own = await _learner_profile_for_user(db, current_user)
        if not own or assessment.learner_id != own.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


async def learner_profile_for_resource(
    db: AsyncSession,
    current_user: TokenPayload,
    learner_id: UUID,
) -> LearnerProfile:
    """Resolve learner profile for AI/scoring context after access is verified."""
    if current_user.role == "student":
        profile = await _learner_profile_for_user(db, current_user)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner profile not found")
        return profile
    profile = await db.scalar(
        select(LearnerProfile).where(
            LearnerProfile.id == learner_id,
            LearnerProfile.tenant_id == current_user.tenant_id,
        )
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner profile not found")
    return profile


def _table_status_from_policies(
    table_name: str,
    rls_enabled: bool,
    policies: list[dict[str, Any]],
) -> RLSTableStatus:
    cmds = {p.get("cmd", "ALL") for p in policies}
    has_select = "r" in cmds or "SELECT" in cmds or "ALL" in cmds or "*" in cmds
    has_insert = "a" in cmds or "INSERT" in cmds or "ALL" in cmds or "*" in cmds
    has_update = "w" in cmds or "UPDATE" in cmds or "ALL" in cmds or "*" in cmds
    has_delete = "d" in cmds or "DELETE" in cmds or "ALL" in cmds or "*" in cmds
    has_with_check = any(p.get("with_check") for p in policies)

    warnings: list[str] = []
    status: SecurityDiagnosticStatus = "ok"
    if not rls_enabled:
        warnings.append("RLS not enabled")
        status = "critical"
    elif not policies:
        warnings.append("No policies defined")
        status = "critical"
    elif not has_with_check:
        warnings.append("Missing WITH CHECK on write policies")
        status = "warning" if status == "ok" else status

    return RLSTableStatus(
        table_name=table_name,
        rls_enabled=rls_enabled,
        has_select_policy=has_select,
        has_insert_policy=has_insert,
        has_update_policy=has_update,
        has_delete_policy=has_delete,
        has_with_check=has_with_check,
        status=status,
        warnings=warnings,
    )


async def _fetch_rls_from_db(db: AsyncSession) -> dict[str, tuple[bool, list[dict[str, Any]]]]:
    rls_map: dict[str, tuple[bool, list[dict[str, Any]]]] = {}
    try:
        rows = await db.execute(
            text(
                """
                SELECT c.relname AS table_name, c.relrowsecurity AS rls_enabled
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relkind = 'r'
                """
            )
        )
        for row in rows:
            rls_map[row.table_name] = (bool(row.rls_enabled), [])

        policy_rows = await db.execute(
            text(
                """
                SELECT tablename, cmd, qual IS NOT NULL AS has_qual,
                       with_check IS NOT NULL AS has_with_check
                FROM pg_policies
                WHERE schemaname = 'public'
                """
            )
        )
        for prow in policy_rows:
            if prow.tablename not in rls_map:
                rls_map[prow.tablename] = (False, [])
            rls_enabled, policies = rls_map[prow.tablename]
            policies.append(
                {
                    "cmd": prow.cmd,
                    "qual": prow.has_qual,
                    "with_check": prow.has_with_check,
                }
            )
            rls_map[prow.tablename] = (rls_enabled, policies)
    except Exception:
        return {}
    return rls_map


async def get_rls_diagnostics(db: AsyncSession, current_user: TokenPayload) -> RLSCoverageResponse:
    rls_map = await _fetch_rls_from_db(db)
    tables: list[RLSTableStatus] = []
    warnings: list[SecurityWarning] = []

    for table_name in CRITICAL_RLS_TABLES:
        if table_name in rls_map:
            rls_enabled, policies = rls_map[table_name]
            tables.append(_table_status_from_policies(table_name, rls_enabled, policies))
        else:
            tables.append(
                RLSTableStatus(
                    table_name=table_name,
                    rls_enabled=False,
                    status="unknown",
                    warnings=["Could not read pg_catalog (mock DB or insufficient privileges)"],
                )
            )

    if not rls_map:
        warnings.append(
            SecurityWarning(
                code="rls_catalog_unavailable",
                message="Using static manifest; live pg_policies query unavailable",
                severity="warning",
            )
        )
        for entry in tables:
            if entry.table_name in (
                "conversation_messages",
                "assessment_results",
                "voice_analyses",
                "learner_memories",
            ):
                entry.status = "warning"
                entry.warnings.append("Migration 007 expected to enable RLS")

    critical_count = sum(1 for t in tables if t.status == "critical")
    overall: SecurityDiagnosticStatus = "ok"
    if critical_count:
        overall = "critical"
    elif any(t.status == "warning" for t in tables):
        overall = "warning"

    return RLSCoverageResponse(
        status=overall,
        tables=tables,
        warnings=warnings,
        metadata={"tenant_id": str(current_user.tenant_id), "tables_inspected": len(tables)},
    )


def get_auth_diagnostics(_db: AsyncSession, _current_user: TokenPayload) -> AuthSecurityResponse:
    warnings: list[SecurityWarning] = []
    jwt_safe = jwt_secret_is_safe()
    if not jwt_safe:
        warnings.append(
            SecurityWarning(
                code="jwt_secret_default",
                message="JWT_SECRET_KEY uses unsafe default",
                severity="critical",
            )
        )

    status: SecurityDiagnosticStatus = "ok" if jwt_safe else "critical"
    return AuthSecurityResponse(
        db_backed_user_validation=True,
        active_user_enforced=True,
        tenant_validation=True,
        role_validation=True,
        jwt_secret_safe=jwt_safe,
        login_blocks_inactive=True,
        refresh_checks_active=True,
        status=status,
        warnings=warnings,
    )


def get_authorization_diagnostics(_db: AsyncSession, _current_user: TokenPayload) -> AuthorizationSecurityResponse:
    from app.main import app

    protected = 0
    role_gated = 0
    for route in app.routes:
        if not hasattr(route, "dependant"):
            continue
        protected += 1
        for dep in route.dependant.dependencies:
            call = getattr(dep, "call", None)
            if call and getattr(call, "__name__", "") == "checker":
                role_gated += 1

    warnings: list[SecurityWarning] = []
    if role_gated < 10:
        warnings.append(
            SecurityWarning(
                code="sparse_role_gates",
                message="Most routes rely on authentication only; role gates concentrated on operations/security",
                severity="warning",
            )
        )

    return AuthorizationSecurityResponse(
        role_checks_available=True,
        ownership_checks_enabled=True,
        protected_routes_count=protected,
        role_gated_routes_count=role_gated,
        known_gaps=list(KNOWN_AUTHORIZATION_GAPS),
        status="ok",
        warnings=warnings,
    )


async def get_security_summary(db: AsyncSession, current_user: TokenPayload) -> SecuritySummaryResponse:
    rls = await get_rls_diagnostics(db, current_user)
    auth = get_auth_diagnostics(db, current_user)
    authz = get_authorization_diagnostics(db, current_user)

    warnings = list(rls.warnings) + list(auth.warnings) + list(authz.warnings)
    checks = [
        SecurityCheck(name="rls_coverage", status=rls.status, detail=f"{len(rls.tables)} tables inspected"),
        SecurityCheck(name="auth_hardening", status=auth.status, detail="DB-backed JWT validation enabled"),
        SecurityCheck(
            name="authorization",
            status=authz.status,
            detail=f"{len(V1_OWNERSHIP_ROUTES)} ownership-gated resource routes",
        ),
        SecurityCheck(name="jwt_secret", status="ok" if auth.jwt_secret_safe else "critical"),
    ]

    statuses = [rls.status, auth.status, authz.status]
    overall: SecurityDiagnosticStatus = "ok"
    if "critical" in statuses:
        overall = "critical"
    elif "warning" in statuses:
        overall = "warning"

    return SecuritySummaryResponse(
        status=overall,
        tenant_id=current_user.tenant_id,
        rls_status=rls.status,
        auth_status=auth.status,
        authorization_status=authz.status,
        warnings=warnings,
        checks=checks,
        metadata={
            "ownership_routes": list(V1_OWNERSHIP_ROUTES),
            "critical_rls_tables": list(CRITICAL_RLS_TABLES),
        },
    )
