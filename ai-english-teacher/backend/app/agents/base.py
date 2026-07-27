"""Base agent class and shared types."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from app.ai.openai_client import ai_client
from app.core.prompt_guard import validate_ai_input


class AgentInput(BaseModel):
    learner_id: str | None = None
    tenant_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    success: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    name: str = "base"
    system_prompt_template: str = ""

    def build_system_prompt(self, **kwargs: Any) -> str:
        return self.system_prompt_template.format(**kwargs)

    def sanitize(self, text: str) -> str:
        result = validate_ai_input(text)
        return result["sanitized"]

    async def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        messages: list[dict[str, str]] | None = None,
    ) -> dict:
        return await ai_client.chat_completion_json(
            system_prompt, user_message, messages=messages
        )

    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ...
