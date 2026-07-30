"""Request ID middleware tests."""

import pytest
from httpx import AsyncClient

from app.core.middleware import REQUEST_ID_HEADER


@pytest.mark.asyncio
async def test_request_id_generated(public_client: AsyncClient):
    res = await public_client.get("/health")
    assert res.status_code == 200
    rid = res.headers.get(REQUEST_ID_HEADER)
    assert rid
    assert len(rid) >= 8


@pytest.mark.asyncio
async def test_request_id_propagated(public_client: AsyncClient):
    custom = "test-correlation-id-abc123"
    res = await public_client.get("/health", headers={REQUEST_ID_HEADER: custom})
    assert res.status_code == 200
    assert res.headers.get(REQUEST_ID_HEADER) == custom


@pytest.mark.asyncio
async def test_request_id_on_api_route(public_client: AsyncClient):
    res = await public_client.get("/")
    assert res.status_code == 200
    assert res.headers.get(REQUEST_ID_HEADER)
