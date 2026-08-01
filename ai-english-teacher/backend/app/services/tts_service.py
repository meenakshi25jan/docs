import base64

import edge_tts

from app.core.config import get_settings


class TTSService:
    """Text-to-speech using Microsoft Edge TTS (no API key required)."""

    def _resolve_voice(self, voice: str) -> str:
        settings = get_settings()
        if voice == "male":
            return settings.TTS_VOICE_MALE
        return settings.TTS_VOICE_FEMALE

    async def speak(self, text: str, voice: str = "female") -> dict:
        voice_name = self._resolve_voice(voice)
        communicate = edge_tts.Communicate(text=text, voice=voice_name)
        audio_chunks: list[bytes] = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        audio_bytes = b"".join(audio_chunks)
        audio_base64 = base64.b64encode(audio_bytes).decode("ascii") if audio_bytes else None

        return {
            "voice": voice,
            "voice_name": voice_name,
            "text": text,
            "audio_base64": audio_base64,
            "audio_mime_type": "audio/mpeg" if audio_bytes else None,
        }
