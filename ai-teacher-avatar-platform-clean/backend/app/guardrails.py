"""
Guardrail layer — wraps every agent call, both input and output.

v1 is intentionally simple (keyword + length + schema checks) so the whole
pipeline is easy to reason about. Swap `check_input` for an LLM-classifier
call later without touching the orchestrator or agents.
"""

from pydantic import BaseModel, ValidationError

MAX_INPUT_CHARS = 2000

# Minimal starter list — expand or replace with a moderation API/classifier.
BLOCKED_TERMS = {
    "kill myself", "suicide", "bomb", "hack into", "credit card number",
}


class GuardrailError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def check_input(text: str) -> str:
    """Raises GuardrailError if input is unsafe/invalid. Returns cleaned text."""
    cleaned = text.strip()
    if not cleaned:
        raise GuardrailError("Empty message.")
    if len(cleaned) > MAX_INPUT_CHARS:
        raise GuardrailError("Message too long.")
    lowered = cleaned.lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            raise GuardrailError(
                "I can't help with that here. If you're going through something "
                "difficult, please reach out to a trusted person or local support line."
            )
    return cleaned


def check_output(data: dict, schema: type[BaseModel]) -> BaseModel:
    """Validates the LLM's structured output against the expected schema.
    Raises GuardrailError if it doesn't conform (caller should retry once, then fail safe).
    """
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise GuardrailError(f"Model output failed validation: {e}")
