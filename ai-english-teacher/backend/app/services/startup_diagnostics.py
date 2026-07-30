"""Startup diagnostics — logged once at API boot (no secrets)."""

from __future__ import annotations

import logging
import os
from typing import Any

from app.core.config import get_settings
from app.services.health_service import database_url_configured, jwt_secret_is_safe

logger = logging.getLogger(__name__)


def collect_startup_diagnostics() -> dict[str, Any]:
    settings = get_settings()
    skip = os.environ.get("SKIP_MIGRATIONS", "false").lower() == "true"
    return {
        "app_version": settings.APP_VERSION,
        "environment": os.environ.get("ENVIRONMENT", "unknown"),
        "debug": settings.DEBUG,
        "database_configured": database_url_configured(),
        "jwt_secret_safe": jwt_secret_is_safe(),
        "skip_migrations": skip,
        "ai_provider": settings.AI_PROVIDER,
        "redis_url_set": bool(settings.REDIS_URL),
        "render_git_commit": os.environ.get("RENDER_GIT_COMMIT", "not_set"),
        "render_service_name": os.environ.get("RENDER_SERVICE_NAME", "not_set"),
    }


def log_startup_diagnostics() -> None:
    diag = collect_startup_diagnostics()
    if diag["skip_migrations"] and diag["environment"] == "production":
        logger.error("startup_diagnostics: SKIP_MIGRATIONS=true in production is forbidden")
    logger.info("startup_diagnostics %s", diag)
