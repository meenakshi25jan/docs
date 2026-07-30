"""Production readiness verification — deployment, migrations, environment, health."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.openai_client import ai_client
from app.core.config import get_settings
from app.core.security import TokenPayload
from app.schemas.production_readiness import (
    DeploymentCheck,
    EnvironmentCheck,
    EnvironmentVerificationResponse,
    MigrationCheck,
    MigrationVerificationResponse,
    ProductionReadinessSummary,
    ReadinessStatus,
    ReadinessWarning,
    SecurityCheck,
    SecurityVerificationResponse,
)
from app.services.health_service import database_url_configured, jwt_secret_is_safe, probe_database
from app.services.security_service import (
    get_auth_diagnostics,
    get_authorization_diagnostics,
    get_rls_diagnostics,
)

PRODUCTION_READINESS_VERSION = "production_readiness_v1"

EXPECTED_MIGRATIONS: tuple[str, ...] = (
    "001_initial_schema.sql",
    "002_pgvector.sql",
    "003_auth_rls.sql",
    "004_fix_rls_policies.sql",
    "005_knowledge_and_voice.sql",
    "006_curriculum_intelligence.sql",
    "007_security_rls_hardening.sql",
)


def _migrations_dir() -> Path:
    backend_root = Path(__file__).resolve().parents[2]
    candidates = [
        backend_root / "migrations",
        backend_root.parent / "database" / "migrations",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[0]


def _overall_status(statuses: list[ReadinessStatus]) -> ReadinessStatus:
    if "critical" in statuses:
        return "critical"
    if "warning" in statuses:
        return "warning"
    if all(s == "ok" for s in statuses):
        return "ok"
    return "unknown"


async def verify_migrations(db: AsyncSession) -> MigrationVerificationResponse:
    warnings: list[ReadinessWarning] = []
    applied: list[str] = []
    missing: list[str] = []
    unexpected: list[str] = []
    checks: list[MigrationCheck] = []

    try:
        rows = await db.execute(text("SELECT filename FROM schema_migrations ORDER BY filename"))
        applied = [row.filename for row in rows]
        unexpected = [f for f in applied if f not in EXPECTED_MIGRATIONS]
        missing = [f for f in EXPECTED_MIGRATIONS if f not in applied]

        for filename in EXPECTED_MIGRATIONS:
            is_applied = filename in applied
            status: ReadinessStatus = "ok" if is_applied else "critical"
            checks.append(
                MigrationCheck(
                    filename=filename,
                    applied=is_applied,
                    status=status,
                    detail="applied" if is_applied else "missing",
                )
            )
    except Exception as exc:
        warnings.append(
            ReadinessWarning(
                code="migration_catalog_unavailable",
                message=f"Could not read schema_migrations: {type(exc).__name__}",
                severity="warning",
            )
        )
        migrations_dir = _migrations_dir()
        if migrations_dir.exists():
            on_disk = sorted(p.name for p in migrations_dir.glob("*.sql"))
            missing = [f for f in EXPECTED_MIGRATIONS if f not in on_disk]
            for filename in EXPECTED_MIGRATIONS:
                on_disk_present = filename in on_disk
                checks.append(
                    MigrationCheck(
                        filename=filename,
                        applied=False,
                        status="unknown",
                        detail="on_disk" if on_disk_present else "file_missing",
                    )
                )
        else:
            missing = list(EXPECTED_MIGRATIONS)

    status: ReadinessStatus = "ok"
    if missing:
        status = "critical"
    elif unexpected or warnings:
        status = "warning"

    return MigrationVerificationResponse(
        status=status,
        applied=applied,
        missing=missing,
        unexpected=unexpected,
        checks=checks,
        warnings=warnings,
        metadata={
            "expected_count": len(EXPECTED_MIGRATIONS),
            "applied_count": len([c for c in checks if c.applied]),
            "migrations_dir": str(_migrations_dir()),
        },
    )


def verify_environment() -> EnvironmentVerificationResponse:
    settings = get_settings()
    checks: list[EnvironmentCheck] = []
    warnings: list[ReadinessWarning] = []
    errors: list[str] = []

    db_ok = database_url_configured()
    checks.append(
        EnvironmentCheck(
            name="database_url",
            passed=db_ok,
            status="ok" if db_ok else "critical",
            detail="configured" if db_ok else "missing_or_invalid",
        )
    )
    if not db_ok:
        errors.append("DATABASE_URL is not configured")

    jwt_ok = jwt_secret_is_safe()
    checks.append(
        EnvironmentCheck(
            name="jwt_secret",
            passed=jwt_ok,
            status="ok" if jwt_ok else "critical",
            detail="safe" if jwt_ok else "default_secret_in_use",
        )
    )
    if not jwt_ok:
        errors.append("JWT_SECRET_KEY uses unsafe default")

    cors_ok = len(settings.CORS_ORIGINS) > 0
    checks.append(
        EnvironmentCheck(
            name="cors_origins",
            passed=cors_ok,
            status="ok" if cors_ok else "warning",
            detail=f"{len(settings.CORS_ORIGINS)} origin(s)",
        )
    )

    ai_configured = ai_client.is_configured
    ai_status: ReadinessStatus = "ok" if ai_configured else "warning"
    checks.append(
        EnvironmentCheck(
            name="ai_provider",
            passed=ai_configured or settings.AI_PROVIDER == "mock",
            status=ai_status,
            detail=f"provider={ai_client.provider}, configured={ai_configured}",
        )
    )
    if not ai_configured and settings.AI_PROVIDER != "mock":
        warnings.append(
            ReadinessWarning(
                code="ai_not_configured",
                message="AI provider keys not configured; mock mode may be active",
                severity="warning",
            )
        )

    skip_migrations = os.environ.get("SKIP_MIGRATIONS", "false").lower() == "true"
    checks.append(
        EnvironmentCheck(
            name="skip_migrations",
            passed=not skip_migrations,
            status="warning" if skip_migrations else "ok",
            detail="true" if skip_migrations else "false",
        )
    )
    if skip_migrations:
        warnings.append(
            ReadinessWarning(
                code="skip_migrations",
                message="SKIP_MIGRATIONS=true — migrations must be applied manually",
                severity="warning",
            )
        )

    if settings.DEBUG:
        warnings.append(
            ReadinessWarning(
                code="debug_enabled",
                message="DEBUG=true is not recommended for production",
                severity="warning",
            )
        )
        checks.append(
            EnvironmentCheck(
                name="debug_mode",
                passed=False,
                status="warning",
                detail="DEBUG=true",
            )
        )

    status = _overall_status([c.status for c in checks])
    passed = not errors and status != "critical"

    return EnvironmentVerificationResponse(
        status=status,
        passed=passed,
        checks=checks,
        warnings=warnings,
        errors=errors,
        metadata={
            "app_version": settings.APP_VERSION,
            "ai_provider_setting": settings.AI_PROVIDER,
        },
    )


async def verify_health_endpoints() -> tuple[ReadinessStatus, list[DeploymentCheck], list[str]]:
    checks: list[DeploymentCheck] = []
    errors: list[str] = []

    db_probe = await probe_database()
    db_status = db_probe.get("database", "not_configured")
    db_ok = db_status in ("reachable", "not_configured")
    checks.append(
        DeploymentCheck(
            name="database_probe",
            passed=db_ok,
            status="ok" if db_status == "reachable" else ("warning" if db_status == "not_configured" else "critical"),
            detail=str(db_status),
        )
    )
    if db_status == "unreachable":
        errors.append("database unreachable")

    auth_ok = False
    try:
        from app.core.security import hash_password, verify_password

        hashed = hash_password("readiness-check")
        auth_ok = verify_password("readiness-check", hashed)
    except Exception:
        auth_ok = False
    checks.append(
        DeploymentCheck(
            name="auth_hashing",
            passed=auth_ok,
            status="ok" if auth_ok else "critical",
            detail="ok" if auth_ok else "failed",
        )
    )
    if not auth_ok:
        errors.append("auth hashing check failed")

    ai_ok = ai_client.provider in ("mock", "copilot", "azure", "openai", "ollama")
    checks.append(
        DeploymentCheck(
            name="ai_health",
            passed=ai_ok,
            status="ok" if ai_ok else "warning",
            detail=f"provider={ai_client.provider}",
        )
    )

    status = _overall_status([c.status for c in checks])
    return status, checks, errors


async def verify_security_status(
    db: AsyncSession,
    current_user: TokenPayload,
) -> SecurityVerificationResponse:
    checks: list[SecurityCheck] = []
    warnings: list[ReadinessWarning] = []

    auth = get_auth_diagnostics(db, current_user)
    checks.append(
        SecurityCheck(
            name="db_backed_jwt",
            passed=auth.db_backed_user_validation,
            status=auth.status,
            detail="enabled",
        )
    )
    checks.append(
        SecurityCheck(
            name="active_user_enforcement",
            passed=auth.active_user_enforced,
            status="ok" if auth.active_user_enforced else "critical",
            detail="enabled" if auth.active_user_enforced else "disabled",
        )
    )
    checks.append(
        SecurityCheck(
            name="jwt_secret_safe",
            passed=auth.jwt_secret_safe,
            status="ok" if auth.jwt_secret_safe else "critical",
            detail="safe" if auth.jwt_secret_safe else "default",
        )
    )

    authz = get_authorization_diagnostics(db, current_user)
    checks.append(
        SecurityCheck(
            name="ownership_checks",
            passed=authz.ownership_checks_enabled,
            status=authz.status,
            detail="enabled",
        )
    )
    checks.append(
        SecurityCheck(
            name="role_gates",
            passed=authz.role_gated_routes_count >= 10,
            status="ok" if authz.role_gated_routes_count >= 10 else "warning",
            detail=f"{authz.role_gated_routes_count} role-gated routes",
        )
    )

    rls = await get_rls_diagnostics(db, current_user)
    critical_rls = sum(1 for t in rls.tables if t.status == "critical")
    checks.append(
        SecurityCheck(
            name="rls_coverage",
            passed=critical_rls == 0,
            status=rls.status,
            detail=f"{len(rls.tables)} tables inspected, {critical_rls} critical",
        )
    )
    warnings.extend(
        ReadinessWarning(code=w.code, message=w.message, severity=w.severity)
        for w in rls.warnings
    )

    status = _overall_status([c.status for c in checks])
    passed = status != "critical"

    return SecurityVerificationResponse(
        status=status,
        passed=passed,
        checks=checks,
        warnings=warnings,
        metadata={
            "known_gaps": authz.known_gaps,
            "protected_routes": authz.protected_routes_count,
        },
    )


async def build_readiness_summary(
    db: AsyncSession,
    current_user: TokenPayload,
) -> ProductionReadinessSummary:
    env = verify_environment()
    migrations = await verify_migrations(db)
    security = await verify_security_status(db, current_user)
    health_status, health_checks, health_errors = await verify_health_endpoints()

    checks: list[DeploymentCheck] = list(health_checks)
    checks.append(
        DeploymentCheck(
            name="migrations",
            passed=migrations.status == "ok",
            status=migrations.status,
            detail=f"missing={len(migrations.missing)}",
        )
    )
    checks.append(
        DeploymentCheck(
            name="environment",
            passed=env.passed,
            status=env.status,
            detail=f"errors={len(env.errors)}",
        )
    )
    checks.append(
        DeploymentCheck(
            name="security",
            passed=security.passed,
            status=security.status,
            detail=f"checks={len(security.checks)}",
        )
    )

    warnings = list(env.warnings) + list(migrations.warnings) + list(security.warnings)
    errors = list(env.errors) + list(health_errors)
    if migrations.missing:
        errors.append(f"missing_migrations:{','.join(migrations.missing)}")

    statuses = [
        migrations.status,
        env.status,
        security.status,
        health_status,
    ]
    overall = _overall_status(statuses)
    passed = overall == "ok" and not errors

    return ProductionReadinessSummary(
        status=overall,
        passed=passed,
        warnings=warnings,
        errors=errors,
        checks=checks,
        migration_status=migrations.status,
        environment_status=env.status,
        security_status=security.status,
        health_status=health_status,
        metadata={
            "version": PRODUCTION_READINESS_VERSION,
            "tenant_id": str(current_user.tenant_id),
            "expected_migrations": list(EXPECTED_MIGRATIONS),
        },
    )
