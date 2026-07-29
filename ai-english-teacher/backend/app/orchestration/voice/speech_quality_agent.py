"""Speech Quality Agent — audio signal checks."""

from __future__ import annotations

from typing import Any


def analyze_speech_quality(audio_metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    metrics = audio_metrics or {}
    snr = metrics.get("snr_db")
    issues: list[str] = []

    if snr is not None:
        if snr < 10:
            issues.append("background_noise")
            quality = "poor"
        elif snr < 18:
            issues.append("moderate_noise")
            quality = "fair"
        else:
            quality = "good"
    else:
        quality = "unknown"

    if metrics.get("clipping"):
        issues.append("clipping")
        quality = "poor"

    guidance = "Audio quality looks good."
    if "background_noise" in issues:
        guidance = "Try recording in a quieter room or move closer to the microphone."
    elif "clipping" in issues:
        guidance = "Lower your microphone volume to avoid distortion."

    return {
        "quality": quality,
        "snr_db": snr,
        "issues": issues,
        "guidance": guidance,
    }
