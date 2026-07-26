"""Recursive async web crawler."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse

from tqdm import tqdm

from app.crawler.scraper import Scraper
from app.database.database import (
    create_crawl_job,
    get_session,
    save_page,
    save_search_results,
    update_job_status,
)
from app.database.models import CrawlJob, Page
from app.search.search import SearchService
from app.utils.helpers import deduplicate_urls, normalize_url, utc_now
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()


@dataclass
class CrawlTask:
    """A URL scheduled for crawling."""

    url: str
    depth: int
    parent_url: str | None = None


@dataclass
class CrawlStats:
    """Runtime crawl statistics."""

    pages_crawled: int = 0
    pages_failed: int = 0
    urls_discovered: int = 0
    urls_skipped: int = 0


@dataclass
class CrawlResult:
    """Final crawl output."""

    job_id: int
    query: str
    pages: list[Page] = field(default_factory=list)
    stats: CrawlStats = field(default_factory=CrawlStats)
    seed_urls: list[str] = field(default_factory=list)


class ResearchCrawler:
    """Async recursive crawler with search integration."""

    def __init__(
        self,
        settings: Settings | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.search_service = SearchService(self.settings)
        self.scraper = Scraper()
        self.progress_callback = progress_callback
        self._visited: set[str] = set()
        self._content_hashes: set[str] = set()
        self._state_lock = asyncio.Lock()

    async def close(self) -> None:
        """Release crawler resources."""
        await self.scraper.close()

    async def run(
        self,
        query: str,
        depth: int | None = None,
        max_pages: int | None = None,
        seed_urls: list[str] | None = None,
        job_id: int | None = None,
    ) -> CrawlResult:
        """Execute a full research crawl for a query."""
        depth = depth if depth is not None else self.settings.default_depth
        max_pages = max_pages if max_pages is not None else self.settings.default_max_pages

        async with get_session() as session:
            if job_id is None:
                job = await create_crawl_job(session, query, depth, max_pages)
                job_id = job.id
            else:
                job = await session.get(CrawlJob, job_id)
                if job is None:
                    raise ValueError(f"Job {job_id} not found")

            if seed_urls is None:
                search_results = await self.search_service.search(query, max_results=max_pages)
                await save_search_results(
                    session,
                    job_id,
                    search_results,
                    self.settings.search_provider,
                )
                seed_urls = self.search_service.extract_urls(search_results)

        seed_urls = deduplicate_urls(seed_urls)
        logger.info(
            "Starting crawl job {} for '{}' with {} seed URLs",
            job_id,
            query,
            len(seed_urls),
        )

        stats = CrawlStats(urls_discovered=len(seed_urls))
        pages: list[Page] = []
        work_queue: asyncio.Queue[CrawlTask | None] = asyncio.Queue()
        for url in seed_urls:
            await work_queue.put(CrawlTask(url=url, depth=0))

        worker_count = min(self.settings.max_concurrent_requests, max(1, max_pages))
        progress = tqdm(total=max_pages, desc=f"Crawling: {query[:40]}", unit="page")

        async def worker() -> None:
            while True:
                task = await work_queue.get()
                if task is None:
                    work_queue.task_done()
                    break

                try:
                    await self._process_task(
                        task,
                        work_queue,
                        job_id,
                        depth,
                        max_pages,
                        pages,
                        stats,
                        progress,
                    )
                finally:
                    work_queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(worker_count)]
        await work_queue.join()

        for _ in workers:
            await work_queue.put(None)
        await asyncio.gather(*workers)
        progress.close()

        async with get_session() as session:
            job = await session.get(CrawlJob, job_id)
            if job:
                await update_job_status(
                    session,
                    job,
                    "completed",
                    pages_crawled=stats.pages_crawled,
                )

        return CrawlResult(
            job_id=job_id,
            query=query,
            pages=pages,
            stats=stats,
            seed_urls=seed_urls,
        )

    async def _process_task(
        self,
        task: CrawlTask,
        work_queue: asyncio.Queue[CrawlTask | None],
        job_id: int,
        max_depth: int,
        max_pages: int,
        pages: list[Page],
        stats: CrawlStats,
        progress: tqdm,
    ) -> None:
        url = normalize_url(task.url)
        if not url:
            stats.urls_skipped += 1
            return

        async with self._state_lock:
            if url in self._visited:
                stats.urls_skipped += 1
                return
            if stats.pages_crawled >= max_pages:
                return
            self._visited.add(url)

        parsed, download = await self.scraper.scrape(url)

        async with self._state_lock:
            if stats.pages_crawled >= max_pages:
                return

            if parsed and parsed.content_hash and parsed.content_hash in self._content_hashes:
                stats.urls_skipped += 1
                return
            if parsed and parsed.content_hash:
                self._content_hashes.add(parsed.content_hash)

            page = Page(
                job_id=job_id,
                url=url,
                title=parsed.title if parsed else None,
                meta_description=parsed.meta_description if parsed else None,
                h1=parsed.h1 if parsed else None,
                h2=parsed.h2 if parsed else None,
                paragraphs=parsed.paragraphs if parsed else None,
                lists=parsed.lists if parsed else None,
                tables=parsed.tables if parsed else None,
                images=parsed.images if parsed else None,
                links=parsed.links if parsed else None,
                pdfs=parsed.pdfs if parsed else None,
                visible_text=parsed.visible_text if parsed else None,
                language=parsed.language if parsed else None,
                content_hash=parsed.content_hash if parsed else None,
                depth=task.depth,
                status_code=download.status_code,
                fetch_method=download.method,
                error_message=download.error,
                crawled_at=utc_now(),
            )

        async with get_session() as session:
            await save_page(session, page)

        async with self._state_lock:
            pages.append(page)
            if parsed and parsed.visible_text:
                stats.pages_crawled += 1
                progress.update(1)
                if self.progress_callback:
                    self.progress_callback(stats.pages_crawled, max_pages)
            else:
                stats.pages_failed += 1

            if parsed and task.depth < max_depth and stats.pages_crawled < max_pages:
                await self._enqueue_links(parsed.links, task, work_queue, max_pages, stats)

    async def _enqueue_links(
        self,
        links: list[dict[str, str]],
        parent_task: CrawlTask,
        work_queue: asyncio.Queue[CrawlTask | None],
        max_pages: int,
        stats: CrawlStats,
    ) -> None:
        parent_domain = urlparse(parent_task.url).netloc
        for link in links:
            if stats.urls_discovered >= max_pages * 5:
                break
            url = normalize_url(link["url"])
            if not url or url in self._visited:
                continue
            if urlparse(url).netloc != parent_domain:
                continue
            stats.urls_discovered += 1
            await work_queue.put(
                CrawlTask(url=url, depth=parent_task.depth + 1, parent_url=parent_task.url)
            )
