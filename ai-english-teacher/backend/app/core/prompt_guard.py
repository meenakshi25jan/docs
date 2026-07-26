import re
from typing import Any

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"disregard\s+(all\s+)?previous",
    r"you\s+are\s+now\s+",
    r"new\s+instructions?:",
    r"system\s+prompt:",
    r"<\|?(system|assistant|user)\|?>",
    r"jailbreak",
    r"DAN\s+mode",
    r"pretend\s+you\s+are",
    r"act\s+as\s+if",
    r"override\s+(your\s+)?instructions",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> list[str]:
    """Return list of matched injection patterns."""
    matches = []
    for pattern in _compiled:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches


def sanitize_user_input(text: str, max_length: int = 10000) -> str:
    """Sanitize and truncate user input before sending to AI."""
    text = text.strip()[:max_length]
    text = re.sub(r"<\|[^|]*\|>", "", text)
    return text


def validate_ai_input(text: str) -> dict[str, Any]:
    """Validate input for AI endpoints. Raises ValueError on injection."""
    injections = detect_prompt_injection(text)
    if injections:
        raise ValueError(f"Potential prompt injection detected: {injections[:3]}")
    return {"sanitized": sanitize_user_input(text), "original_length": len(text)}
