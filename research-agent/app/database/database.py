"""Async database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.models import Base, CrawlJob, Page, SearchResult
from app.utils.helpers import utc_now
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create or return the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = settings or get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    """Create or return the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(settings),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(settings: Settings | None = None) -> None:
    """Initialize database schema."""
    settings = settings or get_settings()
    settings.ensure_directories()
    engine = get_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized at {}", settings.database_url)


async def create_crawl_job(
    session: AsyncSession,
    query: str,
    depth: int,
    max_pages: int,
) -> CrawlJob:
    """Create a new crawl job record."""
    job = CrawlJob(query=query, depth=depth, max_pages=max_pages, status="running")
    session.add(job)
    await session.flush()
    return job


async def update_job_status(
    session: AsyncSession,
    job: CrawlJob,
    status: str,
    *,
    pages_crawled: int | None = None,
    summary: str | None = None,
    confidence_score: float | None = None,
    report_paths: dict[str, str] | None = None,
    error_message: str | None = None,
) -> CrawlJob:
    """Update crawl job status and metadata."""
    job.status = status
    job.updated_at = utc_now()
    if pages_crawled is not None:
        job.pages_crawled = pages_crawled
    if summary is not None:
        job.summary = summary
    if confidence_score is not None:
        job.confidence_score = confidence_score
    if report_paths is not None:
        job.report_paths = report_paths
    if error_message is not None:
        job.error_message = error_message
    if status in {"completed", "failed"}:
        job.completed_at = utc_now()
    await session.flush()
    return job


async def save_page(session: AsyncSession, page: Page) -> Page:
    """Persist a crawled page."""
    session.add(page)
    await session.flush()
    return page


async def save_search_results(
    session: AsyncSession,
    job_id: int,
    results: list[dict[str, str | int | None]],
    provider: str,
) -> None:
    """Persist search engine results."""
    for item in results:
        session.add(
            SearchResult(
                job_id=job_id,
                title=item.get("title"),
                url=str(item["url"]),
                snippet=item.get("snippet"),
                rank=int(item.get("rank", 0)),
                provider=provider,
            )
        )
    await session.flush()


async def get_job_by_id(session: AsyncSession, job_id: int) -> CrawlJob | None:
    """Fetch a crawl job by ID."""
    return await session.get(CrawlJob, job_id)


async def get_job_pages(session: AsyncSession, job_id: int) -> list[Page]:
    """Fetch all pages for a job."""
    from sqlalchemy import select

    result = await session.execute(select(Page).where(Page.job_id == job_id))
    return list(result.scalars().all())
