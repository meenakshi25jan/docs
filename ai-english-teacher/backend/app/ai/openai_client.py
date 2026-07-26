"""OpenAI / Azure OpenAI abstraction layer."""

import json
from typing import Any

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()


class AIClient:
    def __init__(self):
        if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
            )
            self._model = settings.AZURE_OPENAI_DEPLOYMENT
            self._provider = "azure"
        elif settings.OPENAI_API_KEY:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = settings.OPENAI_MODEL
            self._provider = "openai"
        else:
            self._client = None
            self._model = "mock"
            self._provider = "mock"

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    async def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        response_format: dict | None = None,
    ) -> str:
        if not self._client:
            return self._mock_response(system_prompt, user_message)

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    async def chat_completion_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
    ) -> dict:
        content = await self.chat_completion(
            system_prompt,
            user_message,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_response": content}

    async def get_embedding(self, text: str) -> list[float]:
        if not self._client:
            return [0.0] * 1536
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def _mock_response(self, system_prompt: str, user_message: str) -> str:
        if "grammar" in system_prompt.lower():
            return json.dumps({
                "score": 75.0,
                "errors": [],
                "cefr_estimate": "B2",
                "feedback": "Good grammatical range with minor article errors.",
            })
        if "vocabulary" in system_prompt.lower():
            return json.dumps({
                "score": 70.0,
                "range_score": 72,
                "accuracy": 68,
                "recommended_words": ["nevertheless", "furthermore", "consequently"],
            })
        if "teacher" in system_prompt.lower() or "role-play" in system_prompt.lower():
            return "That's a great point! Can you elaborate on your experience with that?"
        return json.dumps({"score": 70.0, "feedback": "Mock AI response — configure Azure OpenAI for production."})


ai_client = AIClient()
