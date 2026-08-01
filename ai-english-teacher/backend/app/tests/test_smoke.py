"""Production smoke tests — run against a live deployment URL.

Set SMOKE_BASE_URL (e.g. https://ai-english-teacher-api.onrender.com).
Optional: SMOKE_EXPECT_COMMIT to verify the deployed commit SHA matches.
"""

from __future__ import annotations

import os
import time
import uuid

import httpx
import pytest

SMOKE_BASE_URL = os.getenv("SMOKE_BASE_URL", "").rstrip("/")
SMOKE_EXPECT_COMMIT = os.getenv("SMOKE_EXPECT_COMMIT", "")
TIMEOUT = float(os.getenv("SMOKE_TIMEOUT_SECONDS", "30"))


pytestmark = pytest.mark.skipif(not SMOKE_BASE_URL, reason="SMOKE_BASE_URL not set")


def _fail(check_name: str, detail: str) -> None:
    pytest.fail(f"SMOKE TEST FAILED [{check_name}]: {detail}")


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    with httpx.Client(base_url=SMOKE_BASE_URL, timeout=TIMEOUT) as http_client:
        yield http_client


def test_health_returns_200_and_commit(client: httpx.Client) -> None:
    response = client.get("/health")
    if response.status_code != 200:
        _fail("health_status", f"expected 200, got {response.status_code}: {response.text[:200]}")
    payload = response.json()
    if payload.get("status") not in {"healthy", "degraded"}:
        _fail("health_body", f"unexpected status field: {payload}")
    build = payload.get("build") or {}
    commit = build.get("commit")
    if not commit or commit == "unknown":
        _fail("health_commit", "build.commit missing from /health")
    if SMOKE_EXPECT_COMMIT and commit != SMOKE_EXPECT_COMMIT:
        _fail(
            "health_commit_match",
            f"expected commit {SMOKE_EXPECT_COMMIT}, got {commit}",
        )


def test_register_login_and_core_endpoint(client: httpx.Client) -> None:
    email = f"smoke_{int(time.time())}_{uuid.uuid4().hex[:6]}@example.com"
    password = "SmokeTestPass1!"

    register = client.post(
        "/register",
        json={
            "name": "Smoke Tester",
            "email": email,
            "password": password,
            "teacher_voice": "female",
        },
    )
    if register.status_code not in (200, 201):
        _fail("register", f"HTTP {register.status_code}: {register.text[:200]}")

    login = client.post("/login", json={"email": email, "password": password})
    if login.status_code != 200:
        _fail("login", f"HTTP {login.status_code}: {login.text[:200]}")
    token = login.json().get("access_token")
    if not token:
        _fail("login_token", "access_token missing")

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    if me.status_code != 200:
        _fail("users_me", f"HTTP {me.status_code}: {me.text[:200]}")

    home = client.get("/home")
    if home.status_code != 200:
        _fail("home", f"HTTP {home.status_code}: {home.text[:200]}")
