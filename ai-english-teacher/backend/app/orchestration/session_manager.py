"""Session Manager Agent — Redis-backed session state with in-memory fallback."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_memory_store: dict[str, dict[str, Any]] = {}
_redis_client = None
_redis_checked = False


async def _get_redis():
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    settings = get_settings()
    if not settings.REDIS_URL:
        return None
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        _redis_client = client
        logger.info("session_manager.redis_connected")
    except Exception as exc:  # noqa: BLE001
        logger.warning("session_manager.redis_unavailable", extra={"error": str(exc)})
        _redis_client = None
    return _redis_client


def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


async def load_session(session_id: str) -> dict[str, Any]:
    client = await _get_redis()
    if client:
        try:
            raw = await client.get(_session_key(session_id))
            if raw:
                return json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            logger.warning("session_manager.load_failed", extra={"error": str(exc)})
    return dict(_memory_store.get(session_id, {}))


async def save_session(session_id: str, data: dict[str, Any], ttl_seconds: int = 86400) -> None:
    client = await _get_redis()
    payload = json.dumps(data)
    if client:
        try:
            await client.set(_session_key(session_id), payload, ex=ttl_seconds)
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("session_manager.save_failed", extra={"error": str(exc)})
    _memory_store[session_id] = data


async def merge_session(session_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    current = await load_session(session_id)
    current.update(patch)
    await save_session(session_id, current)
    return current
