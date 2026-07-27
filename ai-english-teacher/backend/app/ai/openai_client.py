"""LLM abstraction — Azure OpenAI, OpenAI, Ollama, or mock."""

import json
import re
from typing import Any

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()


def _extract_teacher_response(data: dict[str, Any]) -> str | None:
    """Get assistant text from LLM JSON or plain-text fallback."""
    if data.get("response"):
        return str(data["response"])
    raw = data.get("raw_response")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


class AIClient:
    def __init__(self):
        provider = settings.AI_PROVIDER.lower().strip()
        self._client: AsyncOpenAI | AsyncAzureOpenAI | None = None
        self._model = "mock"
        self._provider = "mock"

        if provider == "mock":
            return

        if provider == "ollama" or (provider == "auto" and settings.OLLAMA_BASE_URL):
            if provider != "auto" or not (settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT):
                if provider != "auto" or not settings.OPENAI_API_KEY:
                    base = settings.OLLAMA_BASE_URL.rstrip("/")
                    self._client = AsyncOpenAI(base_url=f"{base}/v1", api_key="ollama")
                    self._model = settings.OLLAMA_MODEL
                    self._provider = "ollama"
                    return

        if provider in ("auto", "azure") and settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
            )
            self._model = settings.AZURE_OPENAI_DEPLOYMENT
            self._provider = "azure"
        elif provider in ("auto", "openai") and settings.OPENAI_API_KEY:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = settings.OPENAI_MODEL
            self._provider = "openai"
        elif settings.OLLAMA_BASE_URL:
            base = settings.OLLAMA_BASE_URL.rstrip("/")
            self._client = AsyncOpenAI(base_url=f"{base}/v1", api_key="ollama")
            self._model = settings.OLLAMA_MODEL
            self._provider = "ollama"

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    async def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        response_format: dict | None = None,
        messages: list[dict[str, str]] | None = None,
    ) -> str:
        if not self._client:
            return self._mock_response(system_prompt, user_message)

        chat_messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if messages:
            chat_messages.extend(messages)
        chat_messages.append({"role": "user", "content": user_message})

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": chat_messages,
            "temperature": temperature,
        }
        # Ollama and some models ignore response_format — still works without it
        if response_format and self._provider != "ollama":
            kwargs["response_format"] = response_format

        response = await self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    async def chat_completion_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        messages: list[dict[str, str]] | None = None,
    ) -> dict:
        use_json_format = self._provider not in ("ollama", "mock")
        content = await self.chat_completion(
            system_prompt,
            user_message,
            temperature=temperature,
            response_format={"type": "json_object"} if use_json_format else None,
            messages=messages,
        )
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Ollama often returns plain text — wrap for teacher agent
            if "teacher" in system_prompt.lower() or "role-play" in system_prompt.lower():
                return {"response": content.strip(), "grammar_corrections": [], "raw_response": content}
            return {"raw_response": content}

    async def get_embedding(self, text: str) -> list[float]:
        if not self._client:
            return [0.0] * 1536
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def _mock_teacher_json(self, user_message: str) -> str:
        msg = user_message.lower()
        corrections: list[dict[str, str]] = []

        if "improve english" in msg or "improve my english" in msg:
            corrections.append({
                "text": "improve english",
                "correction": "improve my English",
                "note": "Use possessive 'my' and capitalise 'English'.",
            })
            response = (
                "Great goal! You could say: 'I would like to improve my English.' "
                "Which skill matters most to you right now — speaking, listening, writing, or grammar?"
            )
        elif "correct" in msg:
            response = (
                "Happy to help! One tip: say 'Could you please correct me?' — "
                "using 'could' is more polite. Share a sentence and I'll suggest improvements."
            )
        elif re.search(r"\b(hello|hi|hey)\b", msg):
            response = (
                "Hello! Welcome to our practice session. "
                "Tell me a little about yourself — what do you do, or what brings you here today?"
            )
        else:
            response = (
                f"You said: \"{user_message[:120]}\". "
                "That's a good start. Can you add one more detail or give a specific example?"
            )

        return json.dumps({
            "response": response,
            "grammar_corrections": corrections,
            "vocabulary_introduced": [],
            "difficulty_adjustment": "maintain",
            "encouragement": "Keep going — you're doing well!",
        })

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
            # Extract learner message from formatted prompt
            learner_line = user_message
            if "Learner:" in user_message:
                learner_line = user_message.split("Learner:")[-1].strip()
            elif "Start the conversation" in user_message:
                learner_line = "hello"
            return self._mock_teacher_json(learner_line)
        return json.dumps({"score": 70.0, "feedback": "Mock AI — set OLLAMA_BASE_URL or OPENAI_API_KEY."})


ai_client = AIClient()
extract_teacher_response = _extract_teacher_response
