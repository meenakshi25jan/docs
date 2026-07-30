"""Web intelligence gateway — classify external knowledge needs."""

from __future__ import annotations

import re
from typing import Any

from app.cognitive.events import IntentType

NEEDS_WEB = {
    IntentType.WEB_KNOWLEDGE,
}

WEB_QUERY_PATTERNS = [
    r"\b(latest|recent|today|current|news|weather)\b",
    r"\b(2025|2026)\b",
    r"\bwhat is\b.*\b(openai|google|microsoft)\b",
]

NO_WEB_INTENTS = {
    IntentType.GRAMMAR_EXPLAIN,
    IntentType.PRONUNCIATION_PRACTICE,
    IntentType.QUIZ,
    IntentType.HOMEWORK,
}


def needs_external_knowledge(intent: IntentType, message: str) -> bool:
    if intent in NO_WEB_INTENTS:
        return False
    if intent in NEEDS_WEB:
        return True
    lower = message.lower()
    return any(re.search(p, lower) for p in WEB_QUERY_PATTERNS)


async def fetch_web_knowledge(
    query: str,
    *,
    cache: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Web search stub — returns structured placeholder until search API is wired.
    Orchestrator falls back to knowledge base on empty results.
    """
    cache = cache or {}
    cached = cache.get(query)
    if cached:
        return cached

    # Production: integrate Bing/Google Search API here
    return [
        {
            "title": "Curriculum fallback",
            "snippet": (
                f"I don't have live web access in this environment. "
                f"For '{query[:80]}', I'll use curriculum knowledge and general teaching guidance."
            ),
            "source": "web_gateway_stub",
            "confidence": 0.3,
        },
    ]
