"""Production readiness API tests."""

import pytest
from httpx import AsyncClient

from app.schemas.production_readiness import ProductionReadinessSummary


class TestProductionAPI:
    @pytest.mark.asyncio
    async def test_student_forbidden_readiness(self, client: AsyncClient):
        res = await client.get("/api/v1/production/readiness")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_readiness(self, admin_client: AsyncClient):
        from unittest.mock import AsyncMock, patch

        summary = ProductionReadinessSummary(status="ok", passed=True)
        with patch(
            "app.api.v1.production.build_readiness_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ):
            res = await admin_client.get("/api/v1/production/readiness")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_admin_migrations_endpoint(self, admin_client: AsyncClient):
        from app.schemas.production_readiness import MigrationVerificationResponse

        from unittest.mock import AsyncMock, patch

        payload = MigrationVerificationResponse(status="ok")
        with patch(
            "app.api.v1.production.verify_migrations",
            new_callable=AsyncMock,
            return_value=payload,
        ):
            res = await admin_client.get("/api/v1/production/migrations")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_environment_endpoint(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/production/environment")
        assert res.status_code == 200
        data = res.json()
        assert "checks" in data

    @pytest.mark.asyncio
    async def test_admin_security_endpoint(self, admin_client: AsyncClient):
        from unittest.mock import AsyncMock, patch
        from app.schemas.production_readiness import SecurityVerificationResponse

        with patch(
            "app.api.v1.production.verify_security_status",
            new_callable=AsyncMock,
            return_value=SecurityVerificationResponse(status="ok", passed=True),
        ):
            res = await admin_client.get("/api/v1/production/security")
        assert res.status_code == 200
