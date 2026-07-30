"""API integration tests for conversation endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.agents.base import AgentOutput
from app.models import Conversation


class TestConversations:
    @pytest.mark.asyncio
    async def test_start_conversation(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)

        mock_output = AgentOutput(
            data={"response": "Welcome! Let's practice English today."},
        )
        with patch("app.api.v1.conversations.run_conversation_turn", return_value=mock_output):
            res = await client.post(
                "/api/v1/conversations",
                json={"scenario": "job_interview"},
            )
            assert res.status_code == 201
            data = res.json()
            assert data["scenario"] == "job_interview"
            assert "initial_message" in data

    @pytest.mark.asyncio
    async def test_voice_turn_in_conversation(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.scenario = "job_interview"
        conv.context = {"persona_id": "conversation_partner"}
        conv.messages = []
        conv.tenant_id = client.mock_user.tenant_id
        conv.learner_id = client.mock_learner.id

        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner, client.mock_learner])

        mock_voice_result = {
            "transcript": "I have five years experience",
            "response": "That's excellent experience!",
            "teaching_mode": "delayed",
            "corrections": [{"text": "experience", "correction": "of experience"}],
            "voice_scores": {"overall": 82},
            "estimates": {"cefr": "B2"},
            "agent_output": {},
            "metadata": {},
        }
        with patch(
            "app.api.v1.conversations.run_voice_turn",
            return_value=mock_voice_result,
        ):
            res = await client.post(
                f"/api/v1/conversations/{conv_id}/voice-turn",
                json={"transcript": "I have five years experience"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["transcript"] == "I have five years experience"
            assert data["response"] == "That's excellent experience!"

    @pytest.mark.asyncio
    async def test_voice_turn_conversation_not_found(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=None)

        res = await client.post(
            f"/api/v1/conversations/{uuid4()}/voice-turn",
            json={"transcript": "Hello"},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_lesson_report(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.scenario = "restaurant"
        conv.context = {"persona_id": "conversation_partner"}
        conv.tenant_id = client.mock_user.tenant_id
        conv.learner_id = client.mock_learner.id

        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner, client.mock_learner])

        mock_report = {
            "lesson_summary": {"turn_count": 3},
            "scores": {"overall_speaking": 80},
            "estimates": {"cefr_level": "B1"},
        }
        with patch(
            "app.api.v1.conversations.generate_lesson_report",
            return_value=mock_report,
        ):
            res = await client.get(f"/api/v1/conversations/{conv_id}/lesson-report")
            assert res.status_code == 200
            data = res.json()
            assert data["scores"]["overall_speaking"] == 80

    @pytest.mark.asyncio
    async def test_lesson_report_no_data(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.scenario = "general"
        conv.context = {}
        conv.tenant_id = client.mock_user.tenant_id
        conv.learner_id = client.mock_learner.id

        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner, client.mock_learner])

        with patch(
            "app.api.v1.conversations.generate_lesson_report",
            return_value={"error": "No voice data found for this lesson."},
        ):
            res = await client.get(f"/api/v1/conversations/{conv_id}/lesson-report")
            assert res.status_code == 404
