import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.db.base import Base
from app.main import app

INTEGRATION_DATABASE_URL = os.getenv(
    "INTEGRATION_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
)


@pytest.fixture(scope="module")
async def integration_engine():
    if not INTEGRATION_DATABASE_URL.startswith("postgresql"):
        pytest.skip("INTEGRATION_DATABASE_URL must be PostgreSQL")
    engine = create_async_engine(INTEGRATION_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def integration_client(integration_engine):
    session_factory = async_sessionmaker(integration_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_persists_to_postgres(integration_client: AsyncClient, integration_engine):
    email = f"integration_{uuid.uuid4().hex[:8]}@example.com"
    response = await integration_client.post(
        "/register",
        json={
            "name": "Integration User",
            "email": email,
            "password": "IntegrationTest1!",
            "teacher_voice": "female",
        },
    )
    assert response.status_code == 201

    session_factory = async_sessionmaker(integration_engine, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": email},
        )
        row = result.first()
        assert row is not None
        assert row[0] == email


@pytest.mark.asyncio
async def test_alembic_schema_compatible(integration_engine):
    session_factory = async_sessionmaker(integration_engine, expire_on_commit=False)
    async with session_factory() as session:
        tables = await session.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name IN ('users', 'grammar_feedback')"
            )
        )
        names = {row[0] for row in tables}
        assert "users" in names
