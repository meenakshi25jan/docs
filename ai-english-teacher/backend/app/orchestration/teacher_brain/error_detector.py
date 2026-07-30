"""Lightweight error detection for Teacher Brain v1."""

from __future__ import annotations

import re
from typing import Any

from app.orchestration.teacher_brain.schemas import DetectedError
from app.schemas.student_intelligence import StudentSummaryResponse

TENSE_HEURISTIC = re.compile(
    r"\b(am|is|are)\s+(go|went|going)\b|\bgo to\b.*\b(yesterday|last week)\b",
    re.I,
)


def _severity_from_string(value: str | None) -> str:
    s = (value or "medium").lower()
    if s in ("high", "critical", "major"):
        return "high"
    if s in ("low", "minor"):
        return "low"
    return "medium"


def _error_from_grammar_dict(err: dict[str, Any]) -> DetectedError | None:
    original = str(err.get("text", err.get("wrong", ""))).strip()
    if not original:
        return None
    correction = err.get("correction", err.get("correct"))
    return DetectedError(
        type=str(err.get("category", "grammar")),
        original_text=original,
        suggested_correction=str(correction) if correction else None,
        explanation=str(err.get("rule", err.get("tip", ""))) or None,
        severity=_severity_from_string(err.get("severity")),
        source="voice_analysis",
    )


def detect_errors(
    message: str,
    *,
    voice_analysis: dict[str, Any] | None = None,
    student_intelligence_summary: StudentSummaryResponse | None = None,
    memory_bundle: dict[str, Any] | None = None,
) -> list[DetectedError]:
    if not (message or "").strip() and not voice_analysis:
        return []

    errors: list[DetectedError] = []
    seen: set[str] = set()

    def add(err: DetectedError) -> None:
        key = (err.type, err.original_text.lower())
        if key in seen:
            return
        seen.add(key)
        errors.append(err)

    if voice_analysis:
        details = voice_analysis.get("details") or {}
        grammar = details.get("grammar") if isinstance(details.get("grammar"), dict) else {}
        for raw in grammar.get("errors", []) if isinstance(grammar.get("errors"), list) else []:
            if isinstance(raw, dict):
                parsed = _error_from_grammar_dict(raw)
                if parsed:
                    add(parsed)

        pron = details.get("pronunciation") if isinstance(details.get("pronunciation"), dict) else {}
        if pron.get("issues"):
            for issue in pron.get("issues", [])[:3]:
                if isinstance(issue, str) and issue.strip():
                    add(DetectedError(
                        type="pronunciation",
                        original_text=issue.strip(),
                        severity="medium",
                        source="voice_analysis",
                    ))

    if student_intelligence_summary:
        for m in student_intelligence_summary.top_mistakes[:5]:
            add(DetectedError(
                type=m.mistake_type or "grammar",
                original_text=m.original_text,
                suggested_correction=m.corrected_text,
                explanation=m.explanation,
                severity=m.severity,
                source="student_intelligence",
            ))

    if memory_bundle:
        for m in memory_bundle.get("recurring_mistakes", [])[:5]:
            if not isinstance(m, dict):
                continue
            original = str(m.get("error", m.get("text", ""))).strip()
            if not original:
                continue
            add(DetectedError(
                type=str(m.get("category", "grammar")),
                original_text=original,
                suggested_correction=str(m.get("correction", "")) or None,
                explanation="recurring mistake",
                severity="medium",
                source="memory",
            ))

    text = (message or "").strip()
    if text and TENSE_HEURISTIC.search(text) and not errors:
        add(DetectedError(
            type="grammar",
            original_text=text[:120],
            suggested_correction=None,
            explanation="Possible past tense issue",
            severity="medium",
            source="heuristic",
        ))

    return errors[:10]
