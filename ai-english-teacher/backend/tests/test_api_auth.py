"""API integration tests for authentication endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Tenant, User


@pytest.fixture
async def auth_client():
    """Client with real get_db override but mocked session — no production DB."""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    async def flush_assign_ids():
        for call in mock_session.add.call_args_list:
            obj = call.args[0] if call.args else None
            if obj is not None and getattr(obj, "id", None) is None:
                try:
                    obj.id = uuid4()
                except AttributeError:
                    pass
            if hasattr(obj, "is_active") and obj.is_active is None:
                obj.is_active = True

    mock_session.flush = AsyncMock(side_effect=flush_assign_ids)
    mock_session.add = MagicMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.mock_session = mock_session
        yield ac

    app.dependency_overrides.clear()


class TestAuthRegister:
    @pytest.mark.asyncio
    async def test_register_creates_user(self, auth_client: AsyncClient):
        tenant = Tenant(id=uuid4(), name="Default", slug="default")
        auth_client.mock_session.scalar = AsyncMock(side_effect=[tenant, None])

        res = await auth_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert "access_token" in data["tokens"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_client: AsyncClient):
        tenant = Tenant(id=uuid4(), name="Default", slug="default")
        existing = User(id=uuid4(), tenant_id=tenant.id, email="dup@example.com")
        auth_client.mock_session.scalar = AsyncMock(side_effect=[tenant, existing])

        res = await auth_client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "password": "securepass123",
                "first_name": "Dup",
                "last_name": "User",
            },
        )
        assert res.status_code == 409


class TestAuthLogin:
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_client: AsyncClient):
        auth_client.mock_session.scalar = AsyncMock(return_value=None)

        res = await auth_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrongpassword"},
        )
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_login_success(self, auth_client: AsyncClient):
        from app.core.security import hash_password

        tenant_id = uuid4()
        user = User(
            id=uuid4(),
            tenant_id=tenant_id,
            email="login@example.com",
            password_hash=hash_password("correctpass"),
            role="student",
        )
        auth_client.mock_session.scalar = AsyncMock(return_value=user)

        res = await auth_client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "correctpass"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["email"] == "login@example.com"
        assert "access_token" in data["tokens"]


class TestAuthRefresh:
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not-a-valid-token"},
        )
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_success(self, auth_client: AsyncClient):
        from app.core.security import create_refresh_token

        tenant_id = uuid4()
        user_id = uuid4()
        user = User(
            id=user_id,
            tenant_id=tenant_id,
            email="refresh@example.com",
            role="student",
            is_active=True,
        )
        refresh = create_refresh_token({"sub": str(user_id)})
        auth_client.mock_session.get = AsyncMock(return_value=user)

        res = await auth_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
