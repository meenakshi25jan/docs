"""Rule-based teaching strategy selection for Teacher Brain v1."""

from __future__ import annotations

from app.orchestration.teacher_brain.schemas import DetectedError, IntentAnalysis
from app.schemas.student_intelligence import StudentSummaryResponse

EXAM_PERSONAS = frozenset({"ielts_examiner", "pte_coach", "toefl_trainer"})

TEACHING_MODE_TO_STRATEGY = {
    "immediate": "immediate_correction",
    "delayed": "delayed_correction",
    "socratic": "socratic_questioning",
    "none": "practice_prompt",
}


def select_teaching_strategy(
    intent: IntentAnalysis,
    errors: list[DetectedError],
    *,
    teaching_mode: str | None = None,
    persona_id: str = "conversation_partner",
    scenario: str = "general_conversation",
    student_intelligence_summary: StudentSummaryResponse | None = None,
) -> str:
    confidence = None
    weakest_skill = None
    if student_intelligence_summary:
        confidence = student_intelligence_summary.profile.confidence_score
        weakest_skill = student_intelligence_summary.weakest_skill

    high_errors = [e for e in errors if e.severity == "high"]
    grammar_errors = [e for e in errors if e.type in ("grammar", "sentence_structure")]

    if confidence is not None and confidence < 0.5:
        return "encouragement_first"

    if intent.intent == "correction_request":
        return "immediate_correction"

    if intent.intent == "grammar_question":
        return "explanation_first"

    if intent.intent == "motivation_support":
        return "encouragement_first"

    if intent.intent == "exam_practice" or persona_id in EXAM_PERSONAS:
        return "exam_coaching"

    if intent.intent == "roleplay_practice":
        return "roleplay_continuation"

    if teaching_mode == "socratic":
        return "socratic_questioning"

    if teaching_mode == "immediate" or high_errors:
        return "immediate_correction"

    if len(grammar_errors) >= 2:
        return "scaffold"

    if teaching_mode == "delayed":
        return "delayed_correction"

    if weakest_skill in ("grammar", "vocabulary"):
        return "scaffold"

    if weakest_skill in ("fluency", "speaking", "pronunciation"):
        return "practice_prompt"

    if intent.intent == "practice_continuation" and not errors:
        return "practice_prompt"

    if errors:
        return TEACHING_MODE_TO_STRATEGY.get(teaching_mode or "delayed", "delayed_correction")

    return TEACHING_MODE_TO_STRATEGY.get(teaching_mode or "none", "practice_prompt")
