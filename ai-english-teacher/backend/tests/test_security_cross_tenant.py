"""Cross-tenant isolation tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models import Assessment, Conversation


class TestCrossTenantIsolation:
    @pytest.mark.asyncio
    async def test_conversation_wrong_tenant_returns_404(self, client: AsyncClient):
        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.tenant_id = uuid4()
        conv.learner_id = client.mock_learner.id
        conv.messages = []

        client.mock_db.scalar = AsyncMock(return_value=conv)

        res = await client.get(f"/api/v1/conversations/{conv_id}/lesson-report")
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_assessment_start_wrong_tenant_returns_404(self, client: AsyncClient):
        assessment_id = uuid4()
        assessment = MagicMock(spec=Assessment)
        assessment.id = assessment_id
        assessment.tenant_id = uuid4()
        assessment.learner_id = client.mock_learner.id

        client.mock_db.get = AsyncMock(return_value=assessment)

        res = await client.post(f"/api/v1/assessments/{assessment_id}/start")
        assert res.status_code == 404
