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

    home = await client.get("/home")
    assert home.status_code == 200
    assert "Grammar correction" in home.json()["features"]


@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient) -> None:
    email = "learner@example.com"
    password = "securepass123"

    register_response = await client.post(
        "/register",
        json={
            "name": "Learner",
            "email": email,
            "password": password,
            "phone_number": "9999999999",
            "teacher_voice": "female",
        },
    )
    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["user"]["email"] == email
    assert registered["access_token"]

    login_response = await client.post(
        "/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me_response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["email"] == email
    assert me["name"] == "Learner"

    refresh_response = await client.post(
        "/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200


@pytest.mark.asyncio
async def test_users_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
