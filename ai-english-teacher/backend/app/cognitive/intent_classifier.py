"""Intent classification — what kind of request is this?"""

from __future__ import annotations

import re

from app.cognitive.events import IntentType

GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|how\s+are\s+you|start)[\s!.?]*$",
    re.IGNORECASE,
)

WEB_PATTERNS = [
    r"\b(latest|recent|today'?s?|current)\b.*\b(news|weather|events)\b",
    r"\bwhat is\b.*\b(openai|google|microsoft|chatgpt)\b",
    r"\b(2025|2026)\b.*\b(ielts|exam|topic)\b",
    r"\bcompany\b.*\b(interview|culture|about)\b",
]

TRANSLATION_PATTERNS = [
    r"\btranslate\b",
    r"\bwhat does .+ mean in\b",
    r"\bhow do you say\b",
]

GRAMMAR_EXPLAIN_PATTERNS = [
    r"\bexplain\b.*\b(present perfect|past tense|grammar|article|preposition)\b",
    r"\bwhat is\b.*\b(present perfect|past tense|grammar rule)\b",
    r"\bhow (do|does) (i|we) use\b",
]

HOMEWORK_PATTERNS = [r"\bhomework\b", r"\bassignment\b", r"\bexercises?\b"]
QUIZ_PATTERNS = [r"\bquiz\b", r"\btest me\b", r"\bpractice questions?\b"]
CONTINUE_PATTERNS = [r"\bcontinue\b.*\b(yesterday|last|previous)\b", r"\bpick up where\b"]
UTILITY_PATTERNS = [r"\bwhat time\b", r"\bhow old\b.*\b(earth|universe)\b"]


def classify_intent(message: str, scenario: str = "", event_type: str | None = None) -> IntentType:
    text = message.strip()
    lower = text.lower()

    if not text or GREETING_PATTERN.match(lower) or lower in {"start", "start the conversation."}:
        return IntentType.GREETING

    for pat in CONTINUE_PATTERNS:
        if re.search(pat, lower):
            return IntentType.CONTINUE_LESSON

    for pat in TRANSLATION_PATTERNS:
        if re.search(pat, lower):
            return IntentType.TRANSLATION

    for pat in HOMEWORK_PATTERNS:
        if re.search(pat, lower):
            return IntentType.HOMEWORK

    for pat in QUIZ_PATTERNS:
        if re.search(pat, lower):
            return IntentType.QUIZ

    for pat in GRAMMAR_EXPLAIN_PATTERNS:
        if re.search(pat, lower):
            return IntentType.GRAMMAR_EXPLAIN

    for pat in WEB_PATTERNS:
        if re.search(pat, lower):
            return IntentType.WEB_KNOWLEDGE

    for pat in UTILITY_PATTERNS:
        if re.search(pat, lower):
            return IntentType.UTILITY

    if re.search(r"\b(interview|restaurant|airport|visa|debate)\b", lower) and re.search(
        r"\b(practice|simulate|role.?play)\b", lower
    ):
        return IntentType.SCENARIO_PRACTICE

    if re.search(r"\bpronunciation\b|\bhow (to )?say\b|\bstress\b", lower):
        return IntentType.PRONUNCIATION_PRACTICE

    teaching_keywords = {
        "explain", "teach", "lesson", "grammar", "vocabulary", "example",
        "practice", "correct", "mistake", "why", "how do", "what is", "what are",
    }
    if any(kw in lower for kw in teaching_keywords):
        return IntentType.TEACHING

    if "?" in text and len(lower.split()) > 4:
        return IntentType.TEACHING

    if scenario and scenario not in {"general_conversation", "general", "everyday"}:
        return IntentType.SCENARIO_PRACTICE

    if event_type == "PRONUNCIATION_FAILED":
        return IntentType.PRONUNCIATION_PRACTICE

    return IntentType.CONVERSATION
