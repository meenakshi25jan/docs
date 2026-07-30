"""Tests for health endpoints and health service."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.health_service import (
    DEFAULT_JWT_SECRET,
    database_url_configured,
    jwt_secret_is_safe,
    probe_database,
    validate_production_jwt_secret,
)


class TestHealthService:
    def test_database_url_configured_with_postgresql(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = "postgresql+asyncpg://localhost/db"
            assert database_url_configured() is True

    def test_database_url_not_configured_when_empty(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = ""
            assert database_url_configured() is False

    @pytest.mark.asyncio
    async def test_probe_database_not_configured(self):
        with patch("app.services.health_service.database_url_configured", return_value=False):
            result = await probe_database()
            assert result["database"] == "not_configured"
            assert result["database_latency_ms"] is None

    @pytest.mark.asyncio
    async def test_probe_database_reachable(self):
        mock_session = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.services.health_service.database_url_configured", return_value=True):
            with patch("app.services.health_service.get_session_factory", return_value=mock_factory):
                result = await probe_database()
                assert result["database"] == "reachable"
                assert result["database_latency_ms"] is not None

    @pytest.mark.asyncio
    async def test_probe_database_unreachable(self):
        mock_factory = MagicMock()
        mock_factory.side_effect = RuntimeError("connection refused")

        with patch("app.services.health_service.database_url_configured", return_value=True):
            with patch("app.services.health_service.get_session_factory", return_value=mock_factory):
                result = await probe_database()
                assert result["database"] == "unreachable"

    def test_jwt_secret_unsafe_with_default(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.JWT_SECRET_KEY = DEFAULT_JWT_SECRET
            assert jwt_secret_is_safe() is False

    def test_jwt_secret_safe_with_custom(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.JWT_SECRET_KEY = "a-unique-production-secret"
            assert jwt_secret_is_safe() is True

    def test_validate_production_jwt_secret_raises_in_production(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.DEBUG = False
            mock_settings.return_value.JWT_SECRET_KEY = DEFAULT_JWT_SECRET
            with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
                validate_production_jwt_secret()

    def test_validate_production_jwt_secret_skips_in_debug(self):
        with patch("app.services.health_service.get_settings") as mock_settings:
            mock_settings.return_value.DEBUG = True
            mock_settings.return_value.JWT_SECRET_KEY = DEFAULT_JWT_SECRET
            validate_production_jwt_secret()


from unittest.mock import MagicMock


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health_reachable(self, public_client: AsyncClient):
        with patch(
            "app.main.probe_database",
            return_value={"database": "reachable", "database_latency_ms": 5},
        ):
            res = await public_client.get("/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "healthy"
            assert data["database"] == "reachable"
            assert data["database_latency_ms"] == 5
            assert "version" in data

    @pytest.mark.asyncio
    async def test_health_not_configured(self, public_client: AsyncClient):
        with patch(
            "app.main.probe_database",
            return_value={"database": "not_configured", "database_latency_ms": None},
        ):
            res = await public_client.get("/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "healthy"
            assert data["database"] == "not_configured"

    @pytest.mark.asyncio
    async def test_health_degraded_when_unreachable(self, public_client: AsyncClient):
        with patch(
            "app.main.probe_database",
            return_value={"database": "unreachable", "database_latency_ms": None},
        ):
            res = await public_client.get("/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "degraded"
            assert data["database"] == "unreachable"

    @pytest.mark.asyncio
    async def test_health_auth_endpoint(self, public_client: AsyncClient):
        res = await public_client.get("/health/auth")
        assert res.status_code == 200
        data = res.json()
        assert data["password_hashing"] == "ok"

    @pytest.mark.asyncio
    async def test_health_live_endpoint(self, public_client: AsyncClient):
        res = await public_client.get("/health/live")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "alive"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_ready_when_reachable(self, public_client: AsyncClient):
        with patch(
            "app.main.probe_database",
            return_value={"database": "reachable", "database_latency_ms": 3},
        ):
            res = await public_client.get("/health/ready")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ready"
            assert data["database"] == "reachable"

    @pytest.mark.asyncio
    async def test_health_ready_not_ready_when_unreachable(self, public_client: AsyncClient):
        with patch(
            "app.main.probe_database",
            return_value={"database": "unreachable", "database_latency_ms": None},
        ):
            res = await public_client.get("/health/ready")
            assert res.status_code == 503
            data = res.json()
            assert data["status"] == "not_ready"

    @pytest.mark.asyncio
    async def test_health_ai_endpoint(self, public_client: AsyncClient):
        res = await public_client.get("/health/ai")
        assert res.status_code == 200
        data = res.json()
        assert "provider" in data
        assert "configured" in data
