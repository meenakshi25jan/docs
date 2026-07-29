"""Moderation Agent — input/output safety gate (Wave 6 MVP)."""

from __future__ import annotations

import re
from typing import Any

BLOCKED_PATTERNS = [
    r"\b(kill\s+yourself|kys)\b",
    r"\b(how\s+to\s+make\s+a\s+bomb)\b",
    r"\b(child\s+porn|cp\s+link)\b",
]
_compiled = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


def moderate_text(text: str, direction: str = "input") -> dict[str, Any]:
    for pattern in _compiled:
        if pattern.search(text):
            return {
                "safe": False,
                "action": "block",
                "categories": ["unsafe_content"],
                "direction": direction,
                "message": "I can't help with that. Let's focus on English practice.",
            }
    return {"safe": True, "action": "allow", "categories": [], "direction": direction}
