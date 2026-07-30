"""API integration tests for voice endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestVoicePersonas:
    @pytest.mark.asyncio
    async def test_get_personas_public(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/voice/personas")
        assert res.status_code == 200
        data = res.json()
        assert "personas" in data
        assert "scenarios" in data
        assert len(data["personas"]) > 0


class TestVoiceTurn:
    @pytest.mark.asyncio
    async def test_voice_turn_requires_input(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)

        res = await client.post("/api/v1/voice/turn", json={})
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_voice_turn_success(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)

        mock_result = {
            "transcript": "Hello teacher",
            "response": "Great job! Let's continue.",
            "teaching_mode": "immediate",
            "corrections": [],
            "voice_scores": {"overall": 85},
            "estimates": {"cefr": "B1"},
        }
        with patch("app.api.v1.voice.run_voice_turn", return_value=mock_result):
            res = await client.post(
                "/api/v1/voice/turn",
                json={"transcript": "Hello teacher", "scenario": "general_conversation"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["transcript"] == "Hello teacher"
            assert data["response"] == "Great job! Let's continue."

    @pytest.mark.asyncio
    async def test_voice_analyze_success(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)

        mock_result = {
            "transcript": "I went to school",
            "overall_score": 78,
            "fluency": 80,
            "pronunciation": 75,
        }
        with patch("app.api.v1.voice.run_voice_analysis", return_value=mock_result):
            res = await client.post(
                "/api/v1/voice/analyze",
                json={"transcript": "I went to school"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["overall_score"] == 78
