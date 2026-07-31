"""Prometheus metrics exposure for production monitoring."""

from __future__ import annotations

import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def mount_prometheus_metrics(app: FastAPI) -> bool:
    """
    Mount /metrics ASGI app (prometheus_client). Returns True if mounted.
    Logs clearly — never silently skip in production.
    """
    try:
        from prometheus_client import make_asgi_app
    except ImportError as exc:
        logger.error(
            "prometheus_metrics: prometheus_client not installed — "
            "add prometheus-client to requirements-render.txt (%s)",
            exc,
        )
        return False

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("prometheus_metrics: mounted /metrics (prometheus_client ASGI app)")
    return True
