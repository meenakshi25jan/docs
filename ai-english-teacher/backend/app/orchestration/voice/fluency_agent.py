"""Fluency Agent — pauses, fillers, speaking speed."""

from __future__ import annotations

import re
from typing import Any

FILLER_PATTERN = re.compile(r"\b(um+|uh+|er+|ah+|like|you know|i mean)\b", re.IGNORECASE)


def analyze_fluency(transcript: str, duration_seconds: float | None = None) -> dict[str, Any]:
    text = transcript.strip()
    words = re.findall(r"[a-zA-Z']+", text)
    word_count = len(words)
    fillers = FILLER_PATTERN.findall(text)
    filler_count = len(fillers)

    wpm = None
    if duration_seconds and duration_seconds > 0:
        wpm = round((word_count / duration_seconds) * 60)

    # Heuristic fluency score 0-100
    score = 85.0
    if filler_count > 0:
        score -= min(filler_count * 4, 25)
    if wpm:
        if wpm < 80:
            score -= 15
        elif wpm > 180:
            score -= 10
        elif 110 <= wpm <= 150:
            score += 5
    if word_count < 5:
        score -= 20

    score = max(0, min(100, round(score)))

    confidence = "high" if score >= 75 else "medium" if score >= 55 else "low"
    return {
        "fluency": score,
        "wpm": wpm,
        "fillers": filler_count,
        "filler_words": fillers[:10],
        "word_count": word_count,
        "confidence": confidence,
        "feedback": _fluency_feedback(score, filler_count, wpm),
    }


def _fluency_feedback(score: float, fillers: int, wpm: int | None) -> str:
    if score >= 80:
        return "Smooth flow with good pacing. Keep practicing!"
    if fillers > 3:
        return "Try pausing briefly instead of using filler words like 'um' or 'like'."
    if wpm and wpm < 90:
        return "Speak a little faster — short phrases help build fluency."
    return "Good effort. Practice speaking in full sentences without long hesitations."
