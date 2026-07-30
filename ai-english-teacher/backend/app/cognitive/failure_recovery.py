"""Failure recovery — graceful degradation."""

from __future__ import annotations

import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


async def with_fallback(
    primary: Callable[[], Awaitable[Any]],
    fallback: Callable[[], Awaitable[Any]],
    *,
    label: str,
) -> tuple[Any, bool]:
    try:
        return await primary(), False
    except Exception as exc:  # noqa: BLE001
        logger.warning("cognitive.fallback", extra={"label": label, "error": str(exc)})
        try:
            return await fallback(), True
        except Exception as fb_exc:  # noqa: BLE001
            logger.error("cognitive.fallback_failed", extra={"label": label, "error": str(fb_exc)})
            return {}, True


def mark_assessment_pending(state_patch: dict[str, Any]) -> dict[str, Any]:
    state_patch["assessment_pending"] = True
    return state_patch
