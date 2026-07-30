"""Shared fixtures for API integration tests — no production DB or real AI."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.main import app
from app.models import LearnerProfile, Tenant, User


@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def learner_id():
    return uuid4()


@pytest.fixture
def mock_user(tenant_id, user_id):
    return TokenPayload(
        sub=str(user_id),
        tenant_id=str(tenant_id),
        role="student",
        email="student@example.com",
    )


@pytest.fixture
def mock_learner(tenant_id, user_id, learner_id):
    profile = MagicMock(spec=LearnerProfile)
    profile.id = learner_id
    profile.user_id = user_id
    profile.tenant_id = tenant_id
    profile.current_cefr = "B1"
    return profile


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def flush_assign_ids():
        for call in session.add.call_args_list:
            obj = call.args[0] if call.args else None
            if obj is not None:
                if getattr(obj, "id", None) is None:
                    try:
                        obj.id = uuid4()
                    except AttributeError:
                        pass
                if hasattr(obj, "status") and obj.status is None:
                    obj.status = "active"

    session.flush = AsyncMock(side_effect=flush_assign_ids)
    session.add = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.scalar = AsyncMock(return_value=None)
    session.scalars = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
async def client(mock_db_session, mock_user, mock_learner):
    async def override_get_db() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    async def override_get_current_user() -> TokenPayload:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.mock_db = mock_db_session
        ac.mock_user = mock_user
        ac.mock_learner = mock_learner
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def public_client():
    """Client without auth overrides — for public endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
