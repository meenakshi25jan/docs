#!/usr/bin/env python3
"""Validate backend imports, OpenAPI surface, and optional service connections."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

REQUIRED_OPENAPI_PATHS = [
    "/health",
    "/health/live",
    "/health/ready",
    "/docs",
    "/openapi.json",
    "/api/v1/grammar/grades",
]

OPTIONAL_CHECKS = os.environ.get("CI_CONNECTION_CHECKS", "true").lower() in (
    "1",
    "true",
    "yes",
)


async def check_database() -> tuple[bool, str]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        return True, "DATABASE_URL not set (skipped)"
    try:
        import asyncpg
        from app.core.db_url import prepare_asyncpg_dsn

        dsn, connect_args = prepare_asyncpg_dsn(url)
        conn = await asyncpg.connect(dsn, timeout=15, **connect_args)
        await conn.execute("SELECT 1")
        await conn.close()
        return True, "database reachable"
    except Exception as exc:
        return False, f"database failed: {exc}"


async def check_redis() -> tuple[bool, str]:
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis.asyncio as redis

        client = redis.from_url(url, decode_responses=True)
        pong = await client.ping()
        await client.aclose()
        return bool(pong), "redis reachable" if pong else "redis ping failed"
    except Exception as exc:
        return False, f"redis failed: {exc}"


def check_openapi() -> tuple[bool, str]:
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    missing: list[str] = []
    for path in REQUIRED_OPENAPI_PATHS:
        res = client.get(path)
        if path == "/health/ready" and res.status_code == 503:
            # Database unreachable in environments without Postgres
            continue
        if res.status_code >= 500:
            missing.append(f"{path} -> HTTP {res.status_code}")

    spec = client.get("/openapi.json")
    if spec.status_code != 200:
        return False, f"openapi.json HTTP {spec.status_code}"

    data = spec.json()
    paths = data.get("paths", {})
    public_api = [p for p in paths if p.startswith("/api/v1")]
    if len(public_api) < 10:
        return False, f"expected >=10 /api/v1 paths, found {len(public_api)}"

    # AI client configuration (no network call)
    from app.ai.openai_client import ai_client

    ai_info = {
        "provider": ai_client.provider,
        "configured": ai_client.is_configured,
        "model": ai_client.model,
    }
    print(f"AI client: {json.dumps(ai_info)}")

    if missing:
        return False, "; ".join(missing)
    return True, f"openapi OK ({len(public_api)} API paths)"


async def async_main() -> int:
    print("Importing app.main...")
    from app.main import app  # noqa: F401

    print(f"App routes: {len(app.routes)}")

    ok, msg = check_openapi()
    print(f"[{'PASS' if ok else 'FAIL'}] openapi: {msg}")
    if not ok:
        return 1

    if not OPTIONAL_CHECKS:
        print("CI_CONNECTION_CHECKS=false — skipping DB/Redis")
        return 0

    db_ok, db_msg = await check_database()
    print(f"[{'PASS' if db_ok else 'FAIL'}] database: {db_msg}")

    redis_ok, redis_msg = await check_redis()
    print(f"[{'PASS' if redis_ok else 'FAIL'}] redis: {redis_msg}")

    if not db_ok or not redis_ok:
        return 1
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
