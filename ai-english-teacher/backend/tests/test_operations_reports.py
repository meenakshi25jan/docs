"""Operations report summary tests."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.reports import Report
from app.services.operations_service import OperationsService


class TestOperationsReports:
    @pytest.mark.asyncio
    async def test_learner_reports_returned(self):
        tenant_id = uuid4()
        learner_id = uuid4()
        profile = MagicMock()
        profile.user_id = uuid4()

        report = MagicMock(spec=Report)
        report.id = uuid4()
        report.report_type = "lesson_completion"
        report.generated_at = datetime.now(timezone.utc)
        report.learner_id = learner_id
        report.content = {
            "lesson_summary": "Great session",
            "scores": {"grammar": 80},
            "recommendations": ["Practice past tense"],
        }

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
            "app.services.operations_service.get_reports_for_learner",
            new_callable=AsyncMock,
            return_value=[report],
        ):
            service = OperationsService()
            result = await service.get_learner_reports(AsyncMock(), token, learner_id)

        assert result.total == 1
        assert result.reports[0].report_type == "lesson_completion"
