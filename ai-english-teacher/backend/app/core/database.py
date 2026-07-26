from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    url = get_settings().DATABASE_URL.strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add your Neon connection string in Render → Environment."
        )
    return url


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            _database_url(),
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.DEBUG,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            await session.execute(
                __import__("sqlalchemy").text(
                    f"SET LOCAL app.tenant_id = '{__import__('contextvars').ContextVar('tenant_id', default='00000000-0000-0000-0000-000000000000').get()}'"
                )
            )
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
