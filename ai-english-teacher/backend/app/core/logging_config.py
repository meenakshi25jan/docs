"""Centralized logging — Render-safe, optional JSON, request_id binding."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from logging import LogRecord

from app.core.request_context import get_request_id

_configured = False


class RequestIdFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        rid = get_request_id()
        record.request_id = rid if rid else "-"
        return True


class JsonLogFormatter(logging.Formatter):
    def format(self, record: LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if hasattr(record, "route"):
            payload["route"] = record.route
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    _configured = True

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    json_enabled = os.environ.get("LOG_JSON_FORMAT", "false").lower() in ("1", "true", "yes")

    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())

    if json_enabled:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"
            )
        )

    root.handlers.clear()
    root.addHandler(handler)

    logging.getLogger("uvicorn.access").addFilter(RequestIdFilter())


def logging_is_json_enabled() -> bool:
    return os.environ.get("LOG_JSON_FORMAT", "false").lower() in ("1", "true", "yes")
