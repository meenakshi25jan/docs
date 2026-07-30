"""Prompt fragments for Teacher Brain v1 — keep outside route handlers."""

from __future__ import annotations

from app.orchestration.teacher_brain.schemas import DetectedError, ResponsePlan


def build_teacher_brain_instruction(
    plan: ResponsePlan,
    strategy: str,
    *,
    si_focus: str | None = None,
    si_weakest: str | None = None,
) -> str:
    parts: list[str] = [
        f"TEACHER BRAIN PLAN: strategy={strategy}; tone={plan.tone}; max_sentences={plan.max_sentences}.",
    ]
    if plan.skill_focus:
        parts.append(f"Skill focus this turn: {plan.skill_focus}.")
    if si_weakest:
        parts.append(f"Learner's weakest skill (from progress data): {si_weakest}.")
    if si_focus:
        parts.append(f"Recommended practice focus: {si_focus}.")
    if plan.include_correction:
        parts.append("Include a gentle correction in your spoken response.")
    if plan.include_explanation:
        parts.append("Give a brief explanation the learner can understand.")
    if plan.include_encouragement:
        parts.append("Start with brief encouragement.")
    if plan.practice_question:
        parts.append(f"End with this practice prompt: {plan.practice_question}")
    parts.append("Keep sentences short and natural for speech.")
    return " ".join(parts)


def build_error_summary_for_agent(errors: list[DetectedError]) -> str:
    if not errors:
        return "none"
    lines = []
    for e in errors[:5]:
        if e.suggested_correction:
            lines.append(f"{e.original_text} → {e.suggested_correction}")
        else:
            lines.append(e.original_text)
    return "; ".join(lines) if lines else "none"
