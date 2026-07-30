"""Response planning for Teacher Brain v1."""

from __future__ import annotations

from app.orchestration.teacher_brain.schemas import DetectedError, IntentAnalysis, ResponsePlan


def plan_response(
    intent: IntentAnalysis,
    strategy: str,
    errors: list[DetectedError],
    *,
    teaching_mode: str | None = None,
    skill_focus: str | None = None,
    is_voice_turn: bool = False,
) -> ResponsePlan:
    max_sentences = 3 if is_voice_turn else 5
    include_correction = strategy in (
        "immediate_correction",
        "scaffold",
        "delayed_correction",
    ) and bool(errors)
    include_explanation = strategy in ("explanation_first", "scaffold", "immediate_correction")
    include_encouragement = strategy in (
        "encouragement_first",
        "practice_prompt",
        "roleplay_continuation",
        "exam_coaching",
    ) or not errors

    focus = skill_focus or _focus_from_errors(errors) or _focus_from_intent(intent.intent)
    practice_question = _practice_question(intent.intent, focus, errors)
    tone = "supportive" if strategy == "encouragement_first" else "friendly"
    opening = "supportive" if include_encouragement else "direct"

    if strategy == "socratic_questioning":
        include_correction = False
        include_explanation = False
        practice_question = practice_question or "What do you think is the correct form?"

    return ResponsePlan(
        opening_style=opening,
        include_correction=include_correction,
        include_explanation=include_explanation,
        include_encouragement=include_encouragement,
        practice_question=practice_question,
        max_sentences=max_sentences,
        tone=tone,
        next_step=focus,
        skill_focus=focus,
    )


def _focus_from_errors(errors: list[DetectedError]) -> str | None:
    if not errors:
        return None
    types = [e.type for e in errors]
    if "grammar" in types or "sentence_structure" in types:
        return "grammar"
    if "pronunciation" in types:
        return "pronunciation"
    if "vocabulary" in types:
        return "vocabulary"
    if "fluency" in types:
        return "fluency"
    return errors[0].type


def _focus_from_intent(intent: str) -> str | None:
    mapping = {
        "grammar_question": "grammar",
        "vocabulary_question": "vocabulary",
        "pronunciation_practice": "pronunciation",
        "fluency_practice": "fluency",
        "exam_practice": "speaking",
        "roleplay_practice": "speaking",
    }
    return mapping.get(intent)


def _practice_question(intent: str, focus: str | None, errors: list[DetectedError]) -> str | None:
    if intent == "grammar_question":
        return "Can you try another sentence using the correct form?"
    if focus == "grammar" and errors:
        err = errors[0]
        if err.suggested_correction:
            return "Now try one more sentence with the correct past tense."
        return "Can you say that again using past tense?"
    if focus == "vocabulary":
        return "Can you use one new word in a short sentence?"
    if focus == "pronunciation":
        return "Can you repeat that sentence slowly and clearly?"
    if intent == "practice_continuation":
        return "Tell me a little more about that."
    if intent == "greeting":
        return "What would you like to practice today?"
    return None
