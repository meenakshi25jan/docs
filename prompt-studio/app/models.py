from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class StudioMode(str, Enum):
    AUTO = "auto"
    BEGINNER = "beginner"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class GenerateRequest(BaseModel):
    user_request: str = Field(
        ...,
        min_length=3,
        max_length=32000,
        description="Raw idea or requirements for the prompt to generate.",
    )
    mode: StudioMode = Field(
        default=StudioMode.AUTO,
        description="beginner | professional | expert | auto",
    )
    target_model: str | None = Field(
        default=None,
        max_length=128,
        description="Optional target LLM family for deployment notes.",
    )
    output_format: OutputFormat = Field(default=OutputFormat.MARKDOWN)
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list,
        description="Optional prior turns: [{role: user|assistant, content: ...}]",
    )

    @field_validator("conversation_history")
    @classmethod
    def validate_history(cls, value: list[dict[str, str]]) -> list[dict[str, str]]:
        cleaned: list[dict[str, str]] = []
        for item in value[-20:]:
            role = item.get("role", "").strip().lower()
            content = item.get("content", "").strip()
            if role in {"user", "assistant"} and content:
                cleaned.append({"role": role, "content": content})
        return cleaned


class GenerateResponse(BaseModel):
    output: str
    mode_used: str
    model: str
    usage: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_configured: bool
    model: str
