"""IDOR tests for assessment endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.agents.base import AgentOutput
from app.models import Assessment, LearnerProfile


class TestAssessmentIDOR:
    @pytest.mark.asyncio
    async def test_student_cannot_submit_other_learner_assessment(self, client: AsyncClient):
        assessment_id = uuid4()
        assessment = MagicMock(spec=Assessment)
        assessment.id = assessment_id
        assessment.tenant_id = client.mock_user.tenant_id
        assessment.learner_id = uuid4()
        assessment.status = "in_progress"

        client.mock_db.get = AsyncMock(return_value=assessment)
        client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)

        res = await client.post(
            f"/api/v1/assessments/{assessment_id}/submit",
            json={"answers": [{"skill": "grammar", "question_id": "q1", "response": "test"}]},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_submit_updates_assessment_owner_learner(self, client: AsyncClient):
        assessment_id = uuid4()
        owner_id = client.mock_learner.id
        assessment = MagicMock(spec=Assessment)
        assessment.id = assessment_id
        assessment.tenant_id = client.mock_user.tenant_id
        assessment.learner_id = owner_id
        assessment.status = "in_progress"

        owner = client.mock_learner
        owner.current_cefr = "A2"
        owner.ielts_estimate = 5.0
        owner.pte_estimate = 40

        client.mock_db.get = AsyncMock(return_value=assessment)
        client.mock_db.scalar = AsyncMock(side_effect=[owner, owner])

        mock_output = AgentOutput(data={"score": 85.0, "confidence": 0.9})
        mock_agent = MagicMock()
        mock_agent.execute = AsyncMock(return_value=mock_output)
        with patch.dict(
            "app.api.v1.assessments.AGENT_REGISTRY",
            {"assessment": mock_agent, "grammar": mock_agent},
        ), patch(
            "app.services.progress_snapshot_service.record_from_assessment",
            new_callable=AsyncMock,
        ):
            res = await client.post(
                f"/api/v1/assessments/{assessment_id}/submit",
                json={"answers": [{"skill": "grammar", "question_id": "q1", "response": "I have been studying."}]},
            )
        assert res.status_code == 200
        assert owner.current_cefr is not None

    @pytest.mark.asyncio
    async def test_cross_tenant_assessment_denied(self, client: AsyncClient):
        assessment_id = uuid4()
        assessment = MagicMock(spec=Assessment)
        assessment.id = assessment_id
        assessment.tenant_id = uuid4()
        assessment.learner_id = client.mock_learner.id

        client.mock_db.get = AsyncMock(return_value=assessment)

        res = await client.get(f"/api/v1/assessments/{assessment_id}/results")
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_teacher_can_read_tenant_assessment_results(self, teacher_client: AsyncClient):
        assessment_id = uuid4()
        learner_id = uuid4()
        assessment = MagicMock(spec=Assessment)
        assessment.id = assessment_id
        assessment.tenant_id = teacher_client.mock_user.tenant_id
        assessment.learner_id = learner_id
        assessment.status = "completed"
        assessment.results = []

        teacher_client.mock_db.scalar = AsyncMock(return_value=assessment)

        res = await teacher_client.get(f"/api/v1/assessments/{assessment_id}/results")
        assert res.status_code == 200
