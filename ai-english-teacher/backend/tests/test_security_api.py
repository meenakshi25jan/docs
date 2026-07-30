"""Security diagnostics API tests."""

import pytest
from httpx import AsyncClient

from app.schemas.security_diagnostics import SecuritySummaryResponse


class TestSecurityAPI:
    @pytest.mark.asyncio
    async def test_student_forbidden_security_summary(self, client: AsyncClient):
        res = await client.get("/api/v1/security/summary")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_security_summary(self, admin_client: AsyncClient):
        from unittest.mock import AsyncMock, patch

        summary = SecuritySummaryResponse(status="ok")
        with patch(
            "app.api.v1.security.get_security_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ):
            res = await admin_client.get("/api/v1/security/summary")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_admin_rls_diagnostics(self, admin_client: AsyncClient):
        from app.services.security_service import get_rls_diagnostics

        result = await get_rls_diagnostics(admin_client.mock_db, admin_client.mock_user)
        assert len(result.tables) >= 10

    @pytest.mark.asyncio
    async def test_admin_auth_diagnostics(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/security/auth")
        assert res.status_code == 200
        data = res.json()
        assert data["db_backed_user_validation"] is True
        assert data["active_user_enforced"] is True

    @pytest.mark.asyncio
    async def test_admin_authorization_diagnostics(self, admin_client: AsyncClient):
        res = await admin_client.get("/api/v1/security/authorization")
        assert res.status_code == 200
        data = res.json()
        assert data["ownership_checks_enabled"] is True
