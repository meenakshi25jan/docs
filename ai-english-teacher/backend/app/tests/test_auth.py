import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(client: AsyncClient) -> None:
    live = await client.get("/health/live")
    assert live.status_code == 200
    assert live.json()["status"] == "alive"

    ready = await client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"

    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient) -> None:
    email = "learner@example.com"
    password = "securepass123"

    register_response = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["email"] == email
    assert registered["is_active"] is True

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    me_response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["email"] == email
    assert me["id"] == registered["id"]

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]


@pytest.mark.asyncio
async def test_users_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
