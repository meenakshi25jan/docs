"""
Single choke point for all LLM calls. If you swap providers later
(or add a fallback provider), this is the only file that changes.
"""

import json

import httpx

from app.config import settings


class LLMClient:
    def __init__(self):
        self.base_url = settings.grok_api_base
        self.api_key = settings.grok_api_key
        self.model = settings.grok_model

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        json_mode: bool = False,
        temperature: float = 0.4,
    ) -> str:
        """Calls Grok's OpenAI-compatible chat completions endpoint.
        Returns the raw text content of the reply.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            if resp.status_code >= 400:
                try:
                    error_body = resp.json()
                except ValueError:
                    error_body = resp.text
                raise RuntimeError(
                    f"xAI API error {resp.status_code} (model={self.model}): {error_body}"
                )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_json(self, system_prompt: str, user_message: str) -> dict:
        raw = await self.chat(system_prompt, user_message, json_mode=True)
        return json.loads(raw)


llm_client = LLMClient()
