import httpx

from app.core.config import get_settings


class GrokService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.XAI_API_KEY:
            raise ValueError("XAI_API_KEY is missing in environment")
        self.api_key = settings.XAI_API_KEY
        self.model = settings.GROK_MODEL
        self.base_url = settings.GROK_BASE_URL

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
