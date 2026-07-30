"""Teaching Decision Engine — when and how to correct the learner."""

from __future__ import annotations

from typing import Any, Literal

TeachingMode = Literal["immediate", "delayed", "socratic", "none"]

SEVERITY_IMMEDIATE = {"high", "critical", "major"}
SEVERITY_DELAY = {"medium", "low", "minor"}


def decide_teaching_mode(
    *,
    grammar_errors: list[dict[str, Any]],
    fluency_score: float,
    persona_correction_style: str,
    turn_count: int,
    pending_corrections: list[dict[str, Any]],
    student_message_length: int,
) -> dict[str, Any]:
    """
    Decide how the teacher should handle detected mistakes this turn.

    Returns teaching_mode, corrections_to_deliver, and deferred items.
    """
    persona_default = persona_correction_style if persona_correction_style in ("immediate", "delayed", "socratic") else "delayed"

    if not grammar_errors and not pending_corrections:
        return {
            "teaching_mode": "none",
            "corrections_now": [],
            "defer_count": 0,
            "reason": "no_errors_detected",
        }

    high_severity = [e for e in grammar_errors if str(e.get("severity", "medium")).lower() in SEVERITY_IMMEDIATE]
    low_severity = [e for e in grammar_errors if str(e.get("severity", "medium")).lower() in SEVERITY_DELAY]

    all_pending = list(pending_corrections) + low_severity
    defer_count = len(all_pending)

    # Long student utterance → preserve flow, batch corrections
    if student_message_length > 40 and persona_default != "immediate":
        return {
            "teaching_mode": "delayed",
            "corrections_now": [],
            "defer_count": defer_count + len(high_severity),
            "deferred_errors": high_severity + all_pending,
            "reason": "extended_speech_batch",
        }

    # Natural pause after several turns with accumulated errors
    if defer_count >= 3 and turn_count >= 2:
        return {
            "teaching_mode": "delayed",
            "corrections_now": _format_corrections(all_pending[:5]),
            "defer_count": 0,
            "deferred_errors": [],
            "reason": "natural_pause_summary",
        }

    if persona_default == "immediate" or high_severity:
        errors_to_fix = high_severity if high_severity else grammar_errors[:2]
        return {
            "teaching_mode": "immediate",
            "corrections_now": _format_corrections(errors_to_fix),
            "defer_count": len(low_severity),
            "deferred_errors": low_severity,
            "reason": "immediate_correction",
        }

    if persona_default == "socratic":
        target = grammar_errors[0] if grammar_errors else pending_corrections[0]
        return {
            "teaching_mode": "socratic",
            "corrections_now": _socratic_prompt(target),
            "defer_count": defer_count,
            "deferred_errors": grammar_errors[1:] + pending_corrections,
            "reason": "socratic_guidance",
        }

    # Default: defer minor errors, fix only blocking ones
    if high_severity:
        return {
            "teaching_mode": "immediate",
            "corrections_now": _format_corrections(high_severity),
            "defer_count": len(low_severity),
            "deferred_errors": low_severity,
            "reason": "blocking_error",
        }

    return {
        "teaching_mode": "delayed",
        "corrections_now": [],
        "defer_count": defer_count + len(grammar_errors),
        "deferred_errors": grammar_errors + pending_corrections,
        "reason": "preserve_flow",
    }


def build_teaching_instruction(decision: dict[str, Any]) -> str:
    """Convert a teaching decision into LLM guidance."""
    mode = decision.get("teaching_mode", "none")
    corrections = decision.get("corrections_now", [])

    if mode == "none":
        return "No corrections needed this turn. Respond naturally and encourage the learner."

    if mode == "immediate" and corrections:
        lines = []
        for c in corrections:
            wrong = c.get("wrong") or c.get("text", "")
            correct = c.get("correct") or c.get("correction", "")
            if wrong and correct:
                lines.append(f'Correct "{wrong}" → "{correct}"')
        return (
            "IMMEDIATE CORRECTION MODE: Gently correct these errors inline in your spoken response, "
            "then continue the conversation. Errors: " + "; ".join(lines)
        )

    if mode == "socratic":
        prompt = corrections[0] if corrections else {}
        question = prompt.get("question", "Can you think about the correct form?")
        return f"SOCRATIC MODE: Do not give the answer directly. Ask: {question}"

    if mode == "delayed" and corrections:
        count = len(corrections)
        return (
            f"DELAYED CORRECTION MODE: The learner spoke well overall. "
            f"Summarize {count} improvement points clearly without interrupting past flow. "
            f"Items: {corrections}"
        )

    if mode == "delayed":
        return "DELAYED MODE: Let the learner continue. Store errors for a later summary."

    return "Respond naturally as an English teacher."


def _format_corrections(errors: list[dict[str, Any]]) -> list[dict[str, str]]:
    result = []
    for err in errors:
        result.append({
            "wrong": str(err.get("text", err.get("wrong", ""))),
            "correct": str(err.get("correction", err.get("correct", ""))),
            "category": str(err.get("category", "grammar")),
            "rule": str(err.get("rule", err.get("tip", ""))),
        })
    return result


def _socratic_prompt(error: dict[str, Any]) -> list[dict[str, str]]:
    wrong = str(error.get("text", error.get("wrong", "")))
    category = str(error.get("category", "grammar"))
    question = "What do you think is the correct way to say that?"
    if category == "tense" or "went" in wrong.lower() or "go" in wrong.lower():
        question = "Think about the time — did it happen in the past, present, or future?"
    elif category == "articles":
        question = "Does this word need 'a', 'an', or 'the' — or no article?"
    return [{"question": question, "wrong": wrong, "category": category}]
