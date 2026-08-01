import io

import pytest
from httpx import AsyncClient

from app.api.conversation import get_orchestrator, get_stt_service, get_tts_service
from app.main import app

MOCK_GRAMMAR_RESULT = {
    "original_text": "I goes to school yesterday",
    "corrected_text": "I went to school yesterday",
    "explanation": "Use past tense for yesterday.",
    "mistakes": ["verb tense"],
    "score": 70,
    "teacher_response": "Good try! Say: I went to school yesterday.",
}


class MockOrchestrator:
    async def handle(self, mode: str, text: str) -> dict:
        if mode == "conversation":
            return {
                "original_text": text,
                "corrected_text": "",
                "explanation": "",
                "mistakes": [],
                "score": 0,
                "teacher_response": "Nice! What did you learn at school?",
            }
        return {**MOCK_GRAMMAR_RESULT, "original_text": text}


class MockSTTService:
    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        return "I goes to school yesterday"


class MockTTSService:
    async def speak(self, text: str, voice: str = "female") -> dict:
        return {
            "voice": voice,
            "voice_name": "en-US-JennyNeural",
            "text": text,
            "audio_base64": "dGVzdA==",
            "audio_mime_type": "audio/mpeg",
        }


@pytest.fixture
def mock_conversation_services():
    app.dependency_overrides[get_orchestrator] = lambda: MockOrchestrator()
    app.dependency_overrides[get_stt_service] = lambda: MockSTTService()
    app.dependency_overrides[get_tts_service] = lambda: MockTTSService()
    yield
    app.dependency_overrides.pop(get_orchestrator, None)
    app.dependency_overrides.pop(get_stt_service, None)
    app.dependency_overrides.pop(get_tts_service, None)


async def _register_and_login(client: AsyncClient) -> str:
    email = "conversation@example.com"
    password = "securepass123"
    await client.post(
        "/register",
        json={
            "name": "Conversation User",
            "email": email,
            "password": password,
            "teacher_voice": "female",
        },
    )
    login = await client.post("/login", json={"email": email, "password": password})
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_conversation_flow(client: AsyncClient, mock_conversation_services) -> None:
    token = await _register_and_login(client)

    response = await client.post(
        "/conversation",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "I goes to school yesterday", "mode": "grammar"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["input_type"] == "text"
    assert body["result"]["corrected_text"] == "I went to school yesterday"
    assert body["voice_output"]["audio_base64"]
    assert body["feedback_id"]

    feedback = await client.get("/feedback", headers={"Authorization": f"Bearer {token}"})
    assert feedback.status_code == 200
    assert feedback.json()["count"] == 1


@pytest.mark.asyncio
async def test_grammar_check(client: AsyncClient, mock_conversation_services) -> None:
    token = await _register_and_login(client)
    response = await client.post(
        "/grammar-check",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "I goes to school yesterday", "mode": "grammar"},
    )
    assert response.status_code == 200
    assert response.json()["score"] == 70


@pytest.mark.asyncio
async def test_band_score(client: AsyncClient, mock_conversation_services) -> None:
    token = await _register_and_login(client)
    response = await client.post(
        "/band-score",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "I goes to school yesterday", "mode": "grammar"},
    )
    assert response.status_code == 200
    assert response.json()["estimated_cefr"] == "B1"


@pytest.mark.asyncio
async def test_audio_conversation(client: AsyncClient, mock_conversation_services) -> None:
    token = await _register_and_login(client)
    audio_file = io.BytesIO(b"fake-audio-bytes")
    response = await client.post(
        "/audio-conversation",
        headers={"Authorization": f"Bearer {token}"},
        data={"mode": "grammar"},
        files={"audio": ("sample.wav", audio_file, "audio/wav")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["input_type"] == "audio"
    assert body["transcribed_text"] == "I goes to school yesterday"
    assert body["voice_output"]["audio_base64"]


@pytest.mark.asyncio
async def test_conversation_requires_auth(client: AsyncClient, mock_conversation_services) -> None:
    response = await client.post(
        "/conversation",
        json={"text": "Hello", "mode": "grammar"},
    )
    assert response.status_code == 401
