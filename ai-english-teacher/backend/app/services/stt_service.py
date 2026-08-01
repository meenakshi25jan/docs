import httpx

from app.core.config import get_settings


class STTService:
    """Speech-to-text using OpenAI Whisper API."""

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for speech-to-text (Whisper)")

        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        files = {"file": (filename, audio_bytes, "application/octet-stream")}
        data = {"model": settings.WHISPER_MODEL}

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                settings.WHISPER_BASE_URL,
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()
            text = payload.get("text", "").strip()
            if not text:
                raise ValueError("Whisper returned empty transcription")
            return text
