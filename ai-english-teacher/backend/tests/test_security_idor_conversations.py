"""IDOR tests for conversation endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.agents.base import AgentOutput
from app.models import Conversation, LearnerProfile


class TestConversationIDOR:
    @pytest.mark.asyncio
    async def test_student_cannot_message_other_learner_conversation(self, client: AsyncClient):
        conv_id = uuid4()
        other_learner_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.tenant_id = client.mock_user.tenant_id
        conv.learner_id = other_learner_id
        conv.messages = []

        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner])

        res = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "Hello"},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_student_cannot_voice_turn_other_learner_conversation(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.tenant_id = client.mock_user.tenant_id
        conv.learner_id = uuid4()
        conv.messages = []

        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner])

        res = await client.post(
            f"/api/v1/conversations/{conv_id}/voice-turn",
            json={"transcript": "Hello"},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_cross_tenant_conversation_denied(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.tenant_id = uuid4()
        conv.learner_id = client.mock_learner.id
        conv.messages = []

        client.mock_db.scalar = AsyncMock(return_value=conv)

        res = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "Hello"},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_teacher_can_access_tenant_learner_conversation(self, teacher_client: AsyncClient):
        conv_id = uuid4()
        learner_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.scenario = "restaurant"
        conv.context = {}
        conv.messages = []
        conv.tenant_id = teacher_client.mock_user.tenant_id
        conv.learner_id = learner_id

        tenant_learner = MagicMock(spec=LearnerProfile)
        tenant_learner.id = learner_id
        tenant_learner.tenant_id = teacher_client.mock_user.tenant_id
        tenant_learner.current_cefr = "B1"

        teacher_client.mock_db.scalar = AsyncMock(side_effect=[conv, tenant_learner])

        mock_output = AgentOutput(data={"response": "Welcome teacher view"})
        with patch("app.api.v1.conversations.run_conversation_turn", return_value=mock_output):
            res = await teacher_client.post(
                f"/api/v1/conversations/{conv_id}/messages",
                json={"content": "Hello from teacher"},
            )
        assert res.status_code == 200
