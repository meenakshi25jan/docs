"""Reliability API integration tests."""

import pytest
from httpx import AsyncClient

from app.schemas.production_readiness import ProductionReadinessSummary


class TestReliabilityAPI:
    @pytest.mark.asyncio
    async def test_student_forbidden_status(self, client: AsyncClient):
        res = await client.get("/api/v1/reliability/status")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_status(self, admin_client: AsyncClient):
        from unittest.mock import AsyncMock, patch

        summary = ProductionReadinessSummary(status="ok", passed=True)
        with patch(
            "app.services.reliability_service.build_readiness_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ), patch(
            "app.services.reliability_service.probe_database",
            new_callable=AsyncMock,
            return_value={"database": "not_configured"},
        ):
            res = await admin_client.get("/api/v1/reliability/status")
        assert res.status_code == 200
        data = res.json()
        assert "observability" in data
        assert "logging" in data
        assert "backup" in data
        assert "performance" in data

    @pytest.mark.asyncio
    async def test_admin_logging(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/reliability/logging")
        assert res.status_code == 200
        data = res.json()
        assert data["logging_enabled"]
        assert data["request_id_enabled"]

    @pytest.mark.asyncio
    async def test_admin_backup(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/reliability/backup")
        assert res.status_code == 200
        assert "backup_verified" in res.json()

    @pytest.mark.asyncio
    async def test_admin_performance(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/reliability/performance")
        assert res.status_code == 200
        data = res.json()
        assert data["load_smoke_available"]

    @pytest.mark.asyncio
    async def test_student_forbidden_logging(self, client: AsyncClient):
        res = await client.get("/api/v1/reliability/logging")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_existing_health_unchanged(self, public_client: AsyncClient):
        res = await public_client.get("/health")
        assert res.status_code == 200
        assert "status" in res.json()
