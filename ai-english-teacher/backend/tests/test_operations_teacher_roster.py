"""Teacher roster operations tests."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models import LearnerProfile
from app.services.operations_service import OperationsService


class TestTeacherRoster:
    @pytest.mark.asyncio
    async def test_roster_returns_tenant_learners(self):
        tenant_id = uuid4()
        learner_id = uuid4()
        user_id = uuid4()
        profile = MagicMock(spec=LearnerProfile)
        profile.id = learner_id
        profile.user_id = user_id
        profile.tenant_id = tenant_id
        profile.current_cefr = "B1"
        user = MagicMock()
        user.first_name = "Jane"
        user.last_name = "Doe"
        user.email = "jane@example.com"
        profile.user = user

        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(tenant_id),
            role="teacher",
            email="teacher@example.com",
        )

        with patch(
            "app.services.operations_service.list_learner_profiles_in_tenant",
            new_callable=AsyncMock,
            return_value=[profile],
        ), patch(
            "app.services.operations_service.get_latest_snapshot",
            new_callable=AsyncMock,
            return_value=None,
        ), patch(
            "app.services.operations_service.count_lesson_completions_since",
            new_callable=AsyncMock,
            return_value=2,
        ), patch(
            "app.services.operations_service.get_last_activity_at",
            new_callable=AsyncMock,
            return_value=datetime.now(timezone.utc),
        ), patch(
            "app.services.operations_service.get_governance_aggregate_for_learner",
            new_callable=AsyncMock,
            return_value={"avg_score": 0.8, "needs_attention_count": 0, "warnings": []},
        ), patch(
            "app.services.operations_service.count_overdue_revisions",
            new_callable=AsyncMock,
            return_value=0,
        ):
            service = OperationsService()
            result = await service.get_teacher_roster(AsyncMock(), token)

        assert result.total == 1
        assert result.learners[0].learner_id == learner_id
        assert result.learners[0].email == "jane@example.com"

    @pytest.mark.asyncio
    async def test_empty_roster_safe(self):
        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(uuid4()),
            role="teacher",
            email="t@example.com",
        )
        with patch(
            "app.services.operations_service.list_learner_profiles_in_tenant",
            new_callable=AsyncMock,
            return_value=[],
        ):
            service = OperationsService()
            result = await service.get_teacher_roster(AsyncMock(), token)
        assert result.total == 0
        assert result.learners == []
