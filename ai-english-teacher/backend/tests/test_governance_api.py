"""Governance API tests."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.governance_service import GovernanceService


class TestGovernanceAPI:
    @pytest.mark.asyncio
    async def test_governance_summary(self, client: AsyncClient, learner_id):
        GovernanceService().evaluate_turn(
            learner_id=str(client.mock_learner.id),
            response="Good work! Try past simple.",
            teacher_brain={"next_prompt": "What did you do?"},
            intent="teaching",
            store=True,
        )
        with patch(
            "app.services.student_intelligence_service.get_summary",
            new_callable=AsyncMock,
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.get("/api/v1/governance/summary")
        assert res.status_code == 200
        data = res.json()
        assert "avg_overall_score" in data
        assert data["evaluation_count"] >= 1

    @pytest.mark.asyncio
    async def test_governance_evaluations(self, client: AsyncClient, learner_id):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
        res = await client.get("/api/v1/governance/evaluations")
        assert res.status_code == 200
        assert "evaluations" in res.json()

    @pytest.mark.asyncio
    async def test_governance_quality(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
        res = await client.get("/api/v1/governance/quality")
        assert res.status_code == 200
        data = res.json()
        assert "avg_teacher_response_score" in data

    @pytest.mark.asyncio
    async def test_governance_grounding_endpoint(self, client: AsyncClient):
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
        res = await client.get("/api/v1/governance/grounding")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_governance_requires_auth(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/governance/summary")
        assert res.status_code in (401, 403)
