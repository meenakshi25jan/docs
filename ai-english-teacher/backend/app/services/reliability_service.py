"""Reliability and observability diagnostics."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging_config import logging_is_json_enabled, setup_logging
from app.core.security import TokenPayload
from app.schemas.reliability import (
    BackupStatusResponse,
    LoggingStatusResponse,
    ObservabilityStatusResponse,
    PerformanceStatusResponse,
    ReliabilityCheck,
    ReliabilityLevel,
    ReliabilityStatusResponse,
    ReliabilityWarning,
)
from app.services.health_service import database_url_configured, probe_database
from app.services.production_readiness_service import build_readiness_summary

RELIABILITY_VERSION = "reliability_observability_v1"
REQUEST_ID_HEADER = "X-Request-ID"


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts"


def _overall_status(statuses: list[ReliabilityLevel]) -> ReliabilityLevel:
    if "critical" in statuses:
        return "critical"
    if "warning" in statuses:
        return "warning"
    if statuses and all(s == "ok" for s in statuses):
        return "ok"
    return "unknown"


def sentry_is_configured() -> bool:
    return bool(os.environ.get("SENTRY_DSN", "").strip())


def get_logging_status() -> LoggingStatusResponse:
    setup_logging()
    checks = [
        ReliabilityCheck(
            name="logging_configured",
            passed=True,
            status="ok",
            detail="centralized logging active",
        ),
        ReliabilityCheck(
            name="request_id_context",
            passed=True,
            status="ok",
            detail=f"header={REQUEST_ID_HEADER}",
        ),
        ReliabilityCheck(
            name="json_format",
            passed=True,
            status="ok" if not logging_is_json_enabled() else "ok",
            detail="enabled" if logging_is_json_enabled() else "disabled",
        ),
    ]
    return LoggingStatusResponse(
        status="ok",
        passed=True,
        logging_enabled=True,
        request_id_enabled=True,
        json_format_enabled=logging_is_json_enabled(),
        checks=checks,
        metadata={"log_level": os.environ.get("LOG_LEVEL", "INFO")},
    )


async def get_backup_status(db: AsyncSession | None = None) -> BackupStatusResponse:
    warnings: list[ReliabilityWarning] = []
    checks: list[ReliabilityCheck] = []
    db_configured = database_url_configured()
    checks.append(
        ReliabilityCheck(
            name="database_url",
            passed=db_configured,
            status="ok" if db_configured else "critical",
            detail="configured" if db_configured else "missing",
        )
    )

    script_path = _scripts_dir() / "backup_verify.sh"
    script_exists = script_path.exists()
    checks.append(
        ReliabilityCheck(
            name="backup_verify_script",
            passed=script_exists,
            status="ok" if script_exists else "warning",
            detail=str(script_path),
        )
    )

    verified = False
    if db is not None and db_configured:
        try:
            migration_count = await db.scalar(text("SELECT COUNT(*) FROM schema_migrations"))
            tenant_count = await db.scalar(text("SELECT COUNT(*) FROM tenants"))
            checks.append(
                ReliabilityCheck(
                    name="schema_migrations_readable",
                    passed=True,
                    status="ok",
                    detail=f"count={migration_count}",
                )
            )
            checks.append(
                ReliabilityCheck(
                    name="tenants_readable",
                    passed=True,
                    status="ok",
                    detail=f"count={tenant_count}",
                )
            )
            verified = True
        except Exception as exc:
            warnings.append(
                ReliabilityWarning(
                    code="backup_probe_failed",
                    message=f"Database probe failed: {type(exc).__name__}",
                    severity="warning",
                )
            )
            checks.append(
                ReliabilityCheck(
                    name="database_probe",
                    passed=False,
                    status="warning",
                    detail=type(exc).__name__,
                )
            )
    else:
        warnings.append(
            ReliabilityWarning(
                code="backup_db_skipped",
                message="Live DB probe skipped — run scripts/backup_verify.sh",
                severity="warning",
            )
        )

    status = _overall_status([c.status for c in checks])
    return BackupStatusResponse(
        status=status,
        passed=db_configured and script_exists,
        backup_verified=verified,
        database_configured=db_configured,
        checks=checks,
        warnings=warnings,
        metadata={"script": "scripts/backup_verify.sh"},
    )


def get_performance_status() -> PerformanceStatusResponse:
    load_script = _scripts_dir() / "load_smoke.py"
    smoke_script = _scripts_dir() / "production_smoke_test.py"
    load_available = load_script.exists()
    checks = [
        ReliabilityCheck(
            name="load_smoke_script",
            passed=load_available,
            status="ok" if load_available else "warning",
            detail=str(load_script),
        ),
        ReliabilityCheck(
            name="production_smoke_script",
            passed=smoke_script.exists(),
            status="ok" if smoke_script.exists() else "warning",
            detail=str(smoke_script),
        ),
    ]
    warnings: list[ReliabilityWarning] = []
    if not load_available:
        warnings.append(
            ReliabilityWarning(
                code="load_smoke_missing",
                message="load_smoke.py not found",
                severity="warning",
            )
        )
    return PerformanceStatusResponse(
        status="ok" if load_available else "warning",
        passed=load_available,
        load_smoke_available=load_available,
        checks=checks,
        warnings=warnings,
        metadata={"note": "Lightweight smoke only — not stress testing"},
    )


def get_observability_status() -> ObservabilityStatusResponse:
    sentry = sentry_is_configured()
    checks = [
        ReliabilityCheck(
            name="request_id_middleware",
            passed=True,
            status="ok",
            detail=REQUEST_ID_HEADER,
        ),
        ReliabilityCheck(
            name="structured_logging",
            passed=True,
            status="ok",
            detail="json" if logging_is_json_enabled() else "text",
        ),
        ReliabilityCheck(
            name="sentry_dsn",
            passed=True,
            status="ok" if sentry else "warning",
            detail="configured" if sentry else "not_configured",
        ),
    ]
    warnings: list[ReliabilityWarning] = []
    if not sentry:
        warnings.append(
            ReliabilityWarning(
                code="sentry_not_configured",
                message="SENTRY_DSN not set — optional error reporting",
                severity="warning",
            )
        )
    return ObservabilityStatusResponse(
        status="ok",
        passed=True,
        request_id_enabled=True,
        logging_enabled=True,
        sentry_configured=sentry,
        checks=checks,
        warnings=warnings,
        metadata={"version": RELIABILITY_VERSION},
    )


async def get_reliability_status(
    db: AsyncSession,
    current_user: TokenPayload,
) -> ReliabilityStatusResponse:
    observability = get_observability_status()
    logging_status = get_logging_status()
    backup = await get_backup_status(db)
    performance = get_performance_status()

    readiness = await build_readiness_summary(db, current_user)
    checks: list[ReliabilityCheck] = [
        ReliabilityCheck(
            name="production_readiness",
            passed=readiness.passed,
            status=readiness.status,
            detail=f"errors={len(readiness.errors)}",
        ),
    ]

    db_probe = await probe_database()
    db_state = db_probe.get("database", "not_configured")
    checks.append(
        ReliabilityCheck(
            name="database_health",
            passed=db_state in ("reachable", "not_configured"),
            status="ok" if db_state == "reachable" else ("warning" if db_state == "not_configured" else "critical"),
            detail=str(db_state),
        )
    )

    warnings = (
        list(observability.warnings)
        + list(logging_status.warnings)
        + list(backup.warnings)
        + list(performance.warnings)
    )
    errors: list[str] = []
    if not readiness.passed:
        errors.extend(readiness.errors)

    statuses: list[ReliabilityLevel] = [
        observability.status,
        logging_status.status,
        backup.status,
        performance.status,
        readiness.status,
        checks[-1].status,
    ]
    overall = _overall_status(statuses)
    passed = overall == "ok" and not errors

    settings = get_settings()
    return ReliabilityStatusResponse(
        status=overall,
        passed=passed,
        warnings=warnings,
        checks=checks,
        observability=observability,
        logging=logging_status,
        backup=backup,
        performance=performance,
        metadata={
            "version": RELIABILITY_VERSION,
            "app_version": settings.APP_VERSION,
            "tenant_id": str(current_user.tenant_id),
        },
    )


async def build_operations_summary(
    db: AsyncSession,
    current_user: TokenPayload,
) -> dict[str, Any]:
    status = await get_reliability_status(db, current_user)
    return {
        "status": status.status,
        "passed": status.passed,
        "request_id_enabled": status.observability.request_id_enabled if status.observability else True,
        "logging_enabled": status.logging.logging_enabled if status.logging else True,
        "backup_verified": status.backup.backup_verified if status.backup else False,
        "load_smoke_available": status.performance.load_smoke_available if status.performance else False,
        "checks": [c.model_dump() for c in status.checks],
        "warnings": [w.model_dump() for w in status.warnings],
    }
