"""Admin summary operations tests."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.services.operations_service import OperationsService


class TestAdminSummary:
    @pytest.mark.asyncio
    async def test_admin_summary_tenant_scoped(self):
        tenant_id = uuid4()
        tenant = MagicMock()
        tenant.id = tenant_id
        tenant.plan_tier = "pro"
        tenant.is_active = True

        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(tenant_id),
            role="admin",
            email="admin@example.com",
        )

        with patch(
            "app.services.operations_service.get_tenant",
            new_callable=AsyncMock,
            return_value=tenant,
        ), patch(
            "app.services.operations_service.count_users_in_tenant",
            new_callable=AsyncMock,
            return_value=5,
        ), patch(
            "app.services.operations_service.count_learners_in_tenant",
            new_callable=AsyncMock,
            return_value=4,
        ), patch(
            "app.services.operations_service.count_active_learners_since",
            new_callable=AsyncMock,
            return_value=2,
        ), patch(
            "app.services.operations_service.count_lesson_completions_tenant_since",
            new_callable=AsyncMock,
            return_value=10,
        ), patch(
            "app.services.operations_service.get_governance_aggregate_for_tenant",
            new_callable=AsyncMock,
            return_value={"avg_score": 0.75, "warning_count": 3},
        ), patch(
            "app.services.operations_service.get_knowledge_aggregate_for_tenant",
            new_callable=AsyncMock,
            return_value={"fallback_rate": 0.1},
        ):
            service = OperationsService()
            result = await service.get_admin_summary(AsyncMock(), token)

        assert result.tenant_id == tenant_id
        assert result.user_count == 5
        assert result.learner_count == 4
        assert result.lessons_completed_30d == 10
        assert result.plan_tier == "pro"
