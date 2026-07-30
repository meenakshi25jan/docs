"""Production readiness service tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.security import TokenPayload
from app.services.production_readiness_service import (
    EXPECTED_MIGRATIONS,
    build_readiness_summary,
    verify_environment,
    verify_health_endpoints,
    verify_migrations,
)


@pytest.fixture
def admin_user(tenant_id, user_id):
    return TokenPayload(
        sub=str(user_id),
        tenant_id=str(tenant_id),
        role="admin",
        email="admin@example.com",
    )


class TestVerifyEnvironment:
    def test_verify_environment_reports_checks(self):
        with patch("app.services.production_readiness_service.database_url_configured", return_value=True):
            with patch("app.services.production_readiness_service.jwt_secret_is_safe", return_value=True):
                result = verify_environment()
        assert len(result.checks) >= 4
        assert any(c.name == "database_url" for c in result.checks)

    def test_verify_environment_flags_default_jwt(self):
        with patch("app.services.production_readiness_service.database_url_configured", return_value=True):
            with patch("app.services.production_readiness_service.jwt_secret_is_safe", return_value=False):
                result = verify_environment()
        assert result.status == "critical"
        assert not result.passed


class TestVerifyMigrations:
    @pytest.mark.asyncio
    async def test_verify_migrations_all_applied(self):
        db = AsyncMock()
        row = MagicMock()
        row.filename = EXPECTED_MIGRATIONS[0]
        rows = [MagicMock(filename=f) for f in EXPECTED_MIGRATIONS]
        db.execute = AsyncMock(return_value=rows)
        result = await verify_migrations(db)
        assert result.status == "ok"
        assert result.missing == []

    @pytest.mark.asyncio
    async def test_verify_migrations_detects_missing(self):
        db = AsyncMock()
        db.execute = AsyncMock(return_value=[])
        result = await verify_migrations(db)
        assert result.status == "critical"
        assert len(result.missing) == len(EXPECTED_MIGRATIONS)

    @pytest.mark.asyncio
    async def test_verify_migrations_safe_failure(self):
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=RuntimeError("no table"))
        result = await verify_migrations(db)
        assert result.warnings
        assert result.status in ("critical", "warning", "unknown")


class TestVerifyHealthEndpoints:
    @pytest.mark.asyncio
    async def test_verify_health_endpoints(self):
        with patch(
            "app.services.production_readiness_service.probe_database",
            return_value={"database": "reachable", "database_latency_ms": 5},
        ):
            status, checks, errors = await verify_health_endpoints()
        assert status in ("ok", "warning")
        assert any(c.name == "database_probe" for c in checks)


class TestBuildReadinessSummary:
    @pytest.mark.asyncio
    async def test_build_readiness_summary(self, admin_user, tenant_id, user_id):
        db = AsyncMock()
        rows = [MagicMock(filename=f) for f in EXPECTED_MIGRATIONS]
        db.execute = AsyncMock(return_value=rows)

        with patch(
            "app.services.production_readiness_service.probe_database",
            return_value={"database": "reachable", "database_latency_ms": 3},
        ):
            with patch("app.services.production_readiness_service.database_url_configured", return_value=True):
                with patch("app.services.production_readiness_service.jwt_secret_is_safe", return_value=True):
                    with patch(
                        "app.services.production_readiness_service.get_rls_diagnostics",
                        new_callable=AsyncMock,
                    ) as mock_rls:
                        from app.schemas.security_diagnostics import RLSCoverageResponse

                        mock_rls.return_value = RLSCoverageResponse(status="ok")
                        summary = await build_readiness_summary(db, admin_user)

        assert summary.metadata["version"] == "production_readiness_v1"
        assert len(summary.checks) >= 4
