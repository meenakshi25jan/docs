"""Whisper transcription service."""

from __future__ import annotations

import base64
import io
import logging

from app.ai.openai_client import ai_client

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_base64: str, mime_type: str = "audio/webm") -> str | None:
    if not audio_base64 or not ai_client.is_configured:
        return None
    if ai_client.provider == "mock":
        return None

    try:
        from app.core.config import get_settings

        settings = get_settings()
        whisper_model = settings.WHISPER_MODEL.strip()
        if not whisper_model:
            base = (settings.OPENAI_BASE_URL or "").lower()
            whisper_model = (
                "whisper-large-v3-turbo"
                if "groq.com" in base or ai_client.provider == "openai"
                else "whisper-1"
            )

        audio_bytes = base64.b64decode(audio_base64)
        client = ai_client._client  # noqa: SLF001
        if not client:
            return None

        ext = "webm" if "webm" in mime_type else "wav" if "wav" in mime_type else "mp3"
        file_obj = io.BytesIO(audio_bytes)
        file_obj.name = f"audio.{ext}"

        response = await client.audio.transcriptions.create(
            model=whisper_model,
            file=file_obj,
        )
        return response.text.strip() if response.text else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("transcription.failed", extra={"error": str(exc)})
        return None
