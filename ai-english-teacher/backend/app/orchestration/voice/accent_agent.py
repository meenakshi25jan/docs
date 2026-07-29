"""Accent Agent — intelligibility-focused accent notes (MVP)."""

from __future__ import annotations

from typing import Any


def analyze_accent(transcript: str) -> dict[str, Any]:
    text = transcript.strip()
    word_count = len(text.split())

    # MVP: intelligibility proxy from sentence completeness
    intelligibility = 88 if word_count >= 8 else 72 if word_count >= 4 else 60

    return {
        "accent_profile": "general_english_learner",
        "intelligibility": intelligibility,
        "drills": ["th sound practice", "word stress in multi-syllable words"],
        "feedback": "Focus on clear consonants at the end of words for better intelligibility.",
    }
