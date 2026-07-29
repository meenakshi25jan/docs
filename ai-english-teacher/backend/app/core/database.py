from uuid import UUID

from collections.abc import AsyncGenerator
from contextvars import ContextVar

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.db_url import is_neon_database_url, prepare_asyncpg_url

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
tenant_id_ctx: ContextVar[str] = ContextVar(
    "tenant_id", default="00000000-0000-0000-0000-000000000000"
)
_optional_bearer = HTTPBearer(auto_error=False)


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    url = get_settings().DATABASE_URL.strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add your Neon connection string in Render → Environment."
        )
    return url


def _engine_pool_kwargs(settings, database_url: str) -> dict[str, int]:
    """Neon scale-to-zero + Render cold starts need small pools and recycling."""
    pool_size = settings.DATABASE_POOL_SIZE
    max_overflow = settings.DATABASE_MAX_OVERFLOW
    if is_neon_database_url(database_url):
        pool_size = min(pool_size, 5)
        max_overflow = min(max_overflow, 5)
    return {"pool_size": pool_size, "max_overflow": max_overflow}


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        database_url = _database_url()
        url, connect_args = prepare_asyncpg_url(database_url)
        pool_kwargs = _engine_pool_kwargs(settings, database_url)
        _engine = create_async_engine(
            url,
            connect_args=connect_args,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            echo=settings.DEBUG,
            **pool_kwargs,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def set_tenant_context(db: AsyncSession, tenant_id: str) -> None:
    # SET LOCAL does not accept bound parameters in PostgreSQL.
    safe_tenant_id = str(UUID(tenant_id))
    tenant_id_ctx.set(safe_tenant_id)
    await db.execute(text(f"SET LOCAL app.tenant_id = '{safe_tenant_id}'"))


async def enable_auth_lookup(db: AsyncSession) -> None:
    await db.execute(text("SET LOCAL app.auth_lookup = 'on'"))


async def disable_auth_lookup(db: AsyncSession) -> None:
    await db.execute(text("SET LOCAL app.auth_lookup = 'off'"))


async def get_db(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
) -> AsyncGenerator[AsyncSession, None]:
    if credentials:
        try:
            from app.core.security import decode_token

            payload = decode_token(credentials.credentials)
            if payload.get("tenant_id"):
                tenant_id_ctx.set(str(payload["tenant_id"]))
        except Exception:
            pass

    factory = get_session_factory()
    async with factory() as session:
        try:
            tid = tenant_id_ctx.get()
            if tid != "00000000-0000-0000-0000-000000000000":
                await set_tenant_context(session, tid)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
