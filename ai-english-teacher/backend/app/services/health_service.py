"""Health checks — database connectivity without exposing credentials."""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import get_session_factory


DEFAULT_JWT_SECRET = "change-me-in-production-use-rs256-key-pair"


def database_url_configured() -> bool:
    settings = get_settings()
    url = settings.DATABASE_URL.strip()
    if not url:
        return False
    return url.startswith("postgresql")


async def probe_database() -> dict[str, Any]:
    """
    Lightweight connectivity probe.
    Returns database: not_configured | reachable | unreachable
    """
    if not database_url_configured():
        return {"database": "not_configured", "database_latency_ms": None}

    started = time.perf_counter()
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {"database": "reachable", "database_latency_ms": latency_ms}
    except Exception:
        return {"database": "unreachable", "database_latency_ms": None}


def jwt_secret_is_safe() -> bool:
    settings = get_settings()
    return settings.JWT_SECRET_KEY.strip() != DEFAULT_JWT_SECRET


def validate_production_jwt_secret() -> None:
    """Fail fast in production when default JWT secret is still in use."""
    settings = get_settings()
    if settings.DEBUG:
        return
    if settings.JWT_SECRET_KEY.strip() == DEFAULT_JWT_SECRET:
        raise RuntimeError(
            "JWT_SECRET_KEY is using the unsafe default. "
            "Set a strong random secret in environment variables before running in production."
        )
