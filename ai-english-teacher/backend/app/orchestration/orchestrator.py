"""Orchestrator Agent — intent routing and agent selection."""

from __future__ import annotations

import re

TEACHING_KEYWORDS = {
    "explain", "teach", "lesson", "grammar", "vocabulary", "example",
    "practice", "correct", "mistake", "why", "how do", "what is", "what are",
}
GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|how\s+are\s+you|start)[\s!.?]*$",
    re.IGNORECASE,
)


def classify_intent(message: str, scenario: str = "") -> tuple[str, str]:
    text = message.strip()
    lower = text.lower()

    if not text or GREETING_PATTERN.match(lower) or lower in {"start", "start the conversation."}:
        return "greeting", "ConversationAgent"

    if any(kw in lower for kw in TEACHING_KEYWORDS):
        return "teaching", "TeacherAgent"

    if "?" in text and len(lower.split()) > 4:
        return "teaching", "TeacherAgent"

    if scenario and scenario not in {"general_conversation", "general"}:
        return "teaching", "TeacherAgent"

    return "conversation", "ConversationAgent"
