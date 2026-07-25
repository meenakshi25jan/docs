from typing import Any

import httpx

from app.config import Settings


class LLMError(Exception):
    """Raised when the LLM provider returns an error."""


async def chat_completion(
    settings: Settings,
    messages: list[dict[str, str]],
) -> tuple[str, dict[str, Any] | None]:
    if not settings.openai_api_key:
        raise LLMError(
            "OPENAI_API_KEY is not set. Add it to .env or your deployment environment."
        )

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": settings.openai_temperature,
        "max_tokens": settings.openai_max_tokens,
    }

    async with httpx.AsyncClient(timeout=settings.openai_timeout_seconds) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code >= 400:
        detail = response.text[:500]
        raise LLMError(f"LLM API error ({response.status_code}): {detail}")

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Unexpected LLM response shape") from exc

    usage = data.get("usage")
    return content, usage
