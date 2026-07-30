"""Analytics API tests."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CurriculumAnalyticsResponse,
    GovernanceAnalyticsResponse,
    KnowledgeAnalyticsResponse,
    LearnerInsightsResponse,
    ProgressAnalyticsResponse,
)


class TestAnalyticsAPI:
    @pytest.mark.asyncio
    async def test_overview(self, client: AsyncClient):
        mock = AnalyticsOverviewResponse(has_data=True)
        with patch(
            "app.api.v1.analytics._service.get_overview",
            new_callable=AsyncMock,
            return_value=mock,
        ):
            res = await client.get("/api/v1/analytics/overview")
        assert res.status_code == 200
        assert res.json()["has_data"] is True

    @pytest.mark.asyncio
    async def test_progress(self, client: AsyncClient):
        with patch(
            "app.api.v1.analytics._service.get_progress",
            new_callable=AsyncMock,
            return_value=ProgressAnalyticsResponse(has_data=False),
        ):
            res = await client.get("/api/v1/analytics/progress")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_governance(self, client: AsyncClient):
        with patch(
            "app.api.v1.analytics._service.get_governance",
            new_callable=AsyncMock,
            return_value=GovernanceAnalyticsResponse(has_data=False),
        ):
            res = await client.get("/api/v1/analytics/governance")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_curriculum(self, client: AsyncClient):
        with patch(
            "app.api.v1.analytics._service.get_curriculum",
            new_callable=AsyncMock,
            return_value=CurriculumAnalyticsResponse(has_data=False),
        ):
            res = await client.get("/api/v1/analytics/curriculum")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_knowledge(self, client: AsyncClient):
        with patch(
            "app.api.v1.analytics._service.get_knowledge",
            new_callable=AsyncMock,
            return_value=KnowledgeAnalyticsResponse(has_data=False),
        ):
            res = await client.get("/api/v1/analytics/knowledge")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_insights(self, client: AsyncClient):
        with patch(
            "app.api.v1.analytics._service.get_insights",
            new_callable=AsyncMock,
            return_value=LearnerInsightsResponse(has_data=False),
        ):
            res = await client.get("/api/v1/analytics/insights")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_required(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/analytics/overview")
        assert res.status_code in (401, 403)
