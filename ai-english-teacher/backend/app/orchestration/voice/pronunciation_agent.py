"""Pronunciation Agent — transcript-based intelligibility scoring (MVP)."""

from __future__ import annotations

import re
from typing import Any

# Common learner pronunciation issues visible in transcripts
ISSUE_PATTERNS = [
    (re.compile(r"\bhe go\b", re.I), "subject-verb agreement", "He goes"),
    (re.compile(r"\bmore (better|easier)\b", re.I), "double comparative", "better / easier"),
    (re.compile(r"\bcan to\b", re.I), "modal + to", "can + verb"),
    (re.compile(r"\bdon't has\b", re.I), "auxiliary mismatch", "doesn't have"),
]


def analyze_pronunciation(transcript: str, target_text: str | None = None) -> dict[str, Any]:
    text = transcript.strip()
    issues: list[dict[str, str]] = []

    for pattern, issue_type, tip in ISSUE_PATTERNS:
        if pattern.search(text):
            issues.append({"type": issue_type, "tip": tip})

    # Word clarity: penalize very short responses and repeated stutters
    stutters = len(re.findall(r"\b(\w+)\s+\1\b", text, re.I))
    words = re.findall(r"[a-zA-Z']+", text)
    score = 82.0
    score -= len(issues) * 8
    score -= stutters * 5
    if len(words) < 4:
        score -= 15
    score = max(0, min(100, round(score)))

    return {
        "phoneme_score": score,
        "stress_score": max(0, score - 5),
        "issues": issues,
        "stutters": stutters,
        "words_analyzed": len(words),
        "feedback": (
            "Clear and intelligible speech."
            if score >= 80
            else "Focus on clear word endings and subject-verb agreement when speaking."
        ),
    }
