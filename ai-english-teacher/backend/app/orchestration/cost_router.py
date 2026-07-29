"""Cost Optimization Agent — route intents to appropriate model tiers."""

from __future__ import annotations

GREETING_KEYWORDS = {"hi", "hello", "hey", "good morning", "good evening", "how are you", "start"}


def select_model_hint(intent: str, message: str) -> str:
    lower = message.lower().strip()
    if intent == "greeting" or any(kw in lower for kw in GREETING_KEYWORDS):
        return "mini"
    if intent == "conversation" and len(lower.split()) < 8:
        return "mini"
    return "full"
