"""Operations API integration tests."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.schemas.operations import (
    AdminSummaryResponse,
    FeatureFlagResponse,
    OperationsHealthResponse,
    OperationsOverviewResponse,
    ReportSummaryListResponse,
    TeacherLearnerSummaryResponse,
    TeacherRosterResponse,
    TenantSettingsResponse,
)


class TestApiOperations:
    @pytest.mark.asyncio
    async def test_health_admin(self, admin_client: AsyncClient):
        with patch(
            "app.api.v1.operations._service.get_operations_health",
            new_callable=AsyncMock,
            return_value=OperationsHealthResponse(status="healthy"),
        ):
            res = await admin_client.get("/api/v1/operations/health")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_overview_admin(self, admin_client: AsyncClient):
        with patch(
            "app.api.v1.operations._service.get_operations_overview",
            new_callable=AsyncMock,
            return_value=OperationsOverviewResponse(tenant_id=uuid4()),
        ):
            res = await admin_client.get("/api/v1/operations/overview")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_feature_flags_teacher(self, teacher_client: AsyncClient):
        with patch(
            "app.api.v1.operations._service.get_feature_flags",
            new_callable=AsyncMock,
            return_value=FeatureFlagResponse(),
        ):
            res = await teacher_client.get("/api/v1/operations/feature-flags")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_teacher_roster_api(self, teacher_client: AsyncClient):
        with patch(
            "app.api.v1.operations._service.get_teacher_roster",
            new_callable=AsyncMock,
            return_value=TeacherRosterResponse(),
        ):
            res = await teacher_client.get("/api/v1/operations/teacher/roster")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_learner_summary_api(self, teacher_client: AsyncClient, learner_id):
        with patch(
            "app.api.v1.operations._service.get_teacher_learner_summary",
            new_callable=AsyncMock,
            return_value=TeacherLearnerSummaryResponse(learner_id=learner_id),
        ):
            res = await teacher_client.get(
                f"/api/v1/operations/teacher/learners/{learner_id}/summary"
            )
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_learner_reports_api(self, teacher_client: AsyncClient, learner_id):
        with patch(
            "app.api.v1.operations._service.get_learner_reports",
            new_callable=AsyncMock,
            return_value=ReportSummaryListResponse(),
        ):
            res = await teacher_client.get(f"/api/v1/operations/reports/learner/{learner_id}")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_tenant_get_admin(self, admin_client: AsyncClient):
        with patch(
            "app.api.v1.operations._service.get_tenant_settings",
            new_callable=AsyncMock,
            return_value=TenantSettingsResponse(
                tenant_id=uuid4(),
                name="Test",
                slug="test",
            ),
        ):
            res = await admin_client.get("/api/v1/operations/tenant")
        assert res.status_code == 200
