from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Create tables if they don't exist. Fine for dev; use Alembic migrations for prod."""
    from app import models  # noqa: F401  (ensure models are registered)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
