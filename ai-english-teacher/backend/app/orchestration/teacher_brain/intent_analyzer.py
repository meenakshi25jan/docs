"""Deterministic turn-level intent analysis for Teacher Brain v1."""

from __future__ import annotations

import re

from app.orchestration.teacher_brain.schemas import IntentAnalysis

GREETING_RE = re.compile(r"^\s*(hi|hello|hey|good morning|good afternoon|good evening)\b", re.I)
GRAMMAR_Q_RE = re.compile(
    r"\b(grammar|past tense|present perfect|conditional|why do we use|how do i say|is it correct)\b",
    re.I,
)
VOCAB_Q_RE = re.compile(r"\b(vocabulary|word mean|what does .+ mean|synonym|how to say)\b", re.I)
PRONUNCIATION_RE = re.compile(r"\b(pronunciation|pronounce|how to say|sound right)\b", re.I)
FLUENCY_RE = re.compile(r"\b(fluency|speak faster|speak more naturally|hesitat)\b", re.I)
EXAM_RE = re.compile(r"\b(ielts|pte|toefl|exam|band score|speaking test)\b", re.I)
LESSON_RE = re.compile(r"\b(lesson|teach me|explain|help me learn)\b", re.I)
CORRECTION_RE = re.compile(r"\b(correct me|fix my|was that right|check my sentence)\b", re.I)
MOTIVATION_RE = re.compile(r"\b(nervous|afraid|can't speak|give up|hard for me|discouraged)\b", re.I)
ASSESSMENT_RE = re.compile(r"\b(assessment|placement|my score|my result)\b", re.I)

ROLEPLAY_SCENARIOS = frozenset({
    "job_interview",
    "restaurant",
    "travel",
    "business_meeting",
    "hotel_checkin",
    "everyday",
    "general_conversation",
})

EXAM_PERSONAS = frozenset({"ielts_examiner", "pte_coach", "toefl_trainer"})


def analyze_intent(
    message: str,
    *,
    scenario: str = "general_conversation",
    persona_id: str = "conversation_partner",
    orchestration_intent: str | None = None,
    is_voice_turn: bool = False,
) -> IntentAnalysis:
    text = (message or "").strip()
    lower = text.lower()
    signals: list[str] = []

    if orchestration_intent == "greeting" or (GREETING_RE.search(lower) and len(lower.split()) <= 6):
        signals.append("greeting phrase")
        return IntentAnalysis(intent="greeting", confidence=0.9, signals=signals)

    if CORRECTION_RE.search(lower):
        signals.append("correction request")
        return IntentAnalysis(intent="correction_request", confidence=0.85, signals=signals)

    if GRAMMAR_Q_RE.search(lower):
        signals.append("grammar keyword")
        return IntentAnalysis(intent="grammar_question", confidence=0.82, signals=signals)

    if VOCAB_Q_RE.search(lower):
        signals.append("vocabulary keyword")
        return IntentAnalysis(intent="vocabulary_question", confidence=0.8, signals=signals)

    if PRONUNCIATION_RE.search(lower):
        signals.append("pronunciation keyword")
        return IntentAnalysis(intent="pronunciation_practice", confidence=0.8, signals=signals)

    if FLUENCY_RE.search(lower):
        signals.append("fluency keyword")
        return IntentAnalysis(intent="fluency_practice", confidence=0.78, signals=signals)

    if EXAM_RE.search(lower) or persona_id in EXAM_PERSONAS:
        if persona_id in EXAM_PERSONAS:
            signals.append("exam persona")
        if EXAM_RE.search(lower):
            signals.append("exam keyword")
        return IntentAnalysis(intent="exam_practice", confidence=0.85, signals=signals)

    if LESSON_RE.search(lower):
        signals.append("lesson request")
        return IntentAnalysis(intent="lesson_request", confidence=0.75, signals=signals)

    if MOTIVATION_RE.search(lower):
        signals.append("motivation signal")
        return IntentAnalysis(intent="motivation_support", confidence=0.8, signals=signals)

    if ASSESSMENT_RE.search(lower):
        signals.append("assessment followup")
        return IntentAnalysis(intent="assessment_followup", confidence=0.75, signals=signals)

    if scenario in ROLEPLAY_SCENARIOS and scenario != "general_conversation":
        signals.append("roleplay scenario")
        return IntentAnalysis(intent="roleplay_practice", confidence=0.7, signals=signals)

    if is_voice_turn and text:
        signals.append("voice continuation")
        return IntentAnalysis(intent="practice_continuation", confidence=0.65, signals=signals)

    if text and "?" in text:
        signals.append("question mark")
        return IntentAnalysis(intent="casual_conversation", confidence=0.55, signals=signals)

    if text:
        return IntentAnalysis(intent="practice_continuation", confidence=0.5, signals=signals or ["default continuation"])

    return IntentAnalysis(intent="unknown", confidence=0.3, signals=["empty message"])
