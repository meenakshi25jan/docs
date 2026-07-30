"""Teacher learner summary tests."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models import LearnerProfile
from app.services.operations_service import OperationsService


class TestTeacherLearnerSummary:
    @pytest.mark.asyncio
    async def test_summary_works(self):
        tenant_id = uuid4()
        learner_id = uuid4()
        user_id = uuid4()
        profile = MagicMock(spec=LearnerProfile)
        profile.id = learner_id
        profile.user_id = user_id

        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(tenant_id),
            role="teacher",
            email="t@example.com",
        )

        with patch(
            "app.services.operations_service.get_learner_in_tenant",
            new_callable=AsyncMock,
            return_value=profile,
        ), patch(
            "app.services.operations_service.get_summary",
            new_callable=AsyncMock,
            return_value=MagicMock(model_dump=lambda: {"has_data": True}),
        ), patch(
            "app.services.operations_service.get_governance_aggregate_for_learner",
            new_callable=AsyncMock,
            return_value={"warnings": []},
        ), patch(
            "app.services.operations_service.get_reports_for_learner",
            new_callable=AsyncMock,
            return_value=[],
        ):
            service = OperationsService()
            service._analytics.get_overview = AsyncMock(return_value=MagicMock(model_dump=lambda: {}))
            service._analytics.get_insights = AsyncMock(
                return_value=MagicMock(insights=[])
            )
            service._analytics.get_curriculum = AsyncMock(return_value=MagicMock(model_dump=lambda: {}))
            result = await service.get_teacher_learner_summary(AsyncMock(), token, learner_id)

        assert result.learner_id == learner_id

    @pytest.mark.asyncio
    async def test_wrong_learner_not_found(self):
        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(uuid4()),
            role="teacher",
            email="t@example.com",
        )
        with patch(
            "app.services.operations_service.get_learner_in_tenant",
            new_callable=AsyncMock,
            return_value=None,
        ):
            service = OperationsService()
            with pytest.raises(HTTPException) as exc:
                await service.get_teacher_learner_summary(AsyncMock(), token, uuid4())
            assert exc.value.status_code == 404
