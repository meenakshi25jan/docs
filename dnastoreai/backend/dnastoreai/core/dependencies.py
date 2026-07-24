"""FastAPI dependency injection container."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dnastoreai.core.config import Settings, ensure_directories, get_settings
from dnastoreai.services.pipeline_service import PipelineService
from dnastoreai.services.archive_service import ArchiveService
from dnastoreai.services.experiment_service import ExperimentService
from dnastoreai.services.metrics_service import MetricsService
from dnastoreai.storage.database import Base
from dnastoreai.storage.vector_store import VectorStore


@lru_cache
def get_engine():
    settings = ensure_directories()
    return create_async_engine(settings.effective_database_url, echo=settings.debug)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    return VectorStore(settings)


def get_pipeline_service() -> PipelineService:
    return PipelineService(get_settings())


def get_archive_service() -> ArchiveService:
    return ArchiveService(get_settings())


def get_experiment_service() -> ExperimentService:
    return ExperimentService(get_settings())


def get_metrics_service() -> MetricsService:
    return MetricsService(get_settings())
