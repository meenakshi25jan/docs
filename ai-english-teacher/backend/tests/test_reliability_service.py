"""Reliability service unit tests."""

from unittest.mock import AsyncMock, patch

import pytest

from uuid import uuid4

from app.core.security import TokenPayload
from app.schemas.production_readiness import ProductionReadinessSummary
from app.services.reliability_service import (
    get_backup_status,
    get_logging_status,
    get_performance_status,
    get_observability_status,
    get_reliability_status,
    sentry_is_configured,
)


@pytest.fixture
def admin_user():
    uid = uuid4()
    tid = uuid4()
    return TokenPayload(
        sub=str(uid),
        tenant_id=str(tid),
        role="admin",
        email="admin@example.com",
    )


class TestLoggingStatus:
    def test_logging_status_ok(self):
        status = get_logging_status()
        assert status.logging_enabled
        assert status.request_id_enabled
        assert status.passed

    def test_observability_without_sentry(self, monkeypatch):
        monkeypatch.delenv("SENTRY_DSN", raising=False)
        status = get_observability_status()
        assert status.request_id_enabled
        assert not status.sentry_configured
        assert any(w.code == "sentry_not_configured" for w in status.warnings)

    def test_sentry_detection(self, monkeypatch):
        monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
        assert sentry_is_configured()
        status = get_observability_status()
        assert status.sentry_configured


class TestBackupStatus:
    @pytest.mark.asyncio
    async def test_backup_without_db(self):
        with patch(
            "app.services.reliability_service.database_url_configured",
            return_value=False,
        ):
            status = await get_backup_status(None)
        assert status.database_configured is False
        assert not status.backup_verified
        assert any(w.code == "backup_db_skipped" for w in status.warnings)

    @pytest.mark.asyncio
    async def test_backup_with_db_mock(self, mock_db_session):
        mock_db_session.scalar = AsyncMock(side_effect=[7, 2])
        with patch(
            "app.services.reliability_service.database_url_configured",
            return_value=True,
        ):
            status = await get_backup_status(mock_db_session)
        assert status.backup_verified
        assert status.passed


class TestPerformanceStatus:
    def test_performance_load_smoke_available(self):
        status = get_performance_status()
        assert status.load_smoke_available
        assert status.passed


class TestReliabilityStatus:
    @pytest.mark.asyncio
    async def test_reliability_aggregate(self, mock_db_session, admin_user):
        mock_db_session.scalar = AsyncMock(side_effect=[5, 1])
        summary = ProductionReadinessSummary(status="ok", passed=True)
        with patch(
            "app.services.reliability_service.build_readiness_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ), patch(
            "app.services.reliability_service.probe_database",
            new_callable=AsyncMock,
            return_value={"database": "reachable"},
        ):
            status = await get_reliability_status(mock_db_session, admin_user)
        assert status.observability is not None
        assert status.logging is not None
        assert status.backup is not None
        assert status.performance is not None
        assert status.metadata.get("version") == "reliability_observability_v1"
