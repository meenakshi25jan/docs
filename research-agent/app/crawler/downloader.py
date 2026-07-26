"""Async HTTP downloader with retries, rate limiting, and Playwright fallback."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import aiohttp
from playwright.async_api import Browser, async_playwright

from app.crawler.robots import get_robots_cache
from app.utils.helpers import pick_user_agent
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()


@dataclass
class DownloadResult:
    """Result of a page download attempt."""

    url: str
    html: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    method: str = "aiohttp"
    error: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


class RateLimiter:
    """Token-bucket style async rate limiter per domain."""

    def __init__(self, delay: float) -> None:
        self.delay = delay
        self._last_request: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def wait(self, domain: str, extra_delay: float = 0.0) -> None:
        """Wait before making the next request to a domain."""
        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            last = self._last_request.get(domain, 0.0)
            wait_time = max(0.0, self.delay + extra_delay - (now - last))
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_request[domain] = loop.time()


class Downloader:
    """Download web pages using aiohttp with optional Playwright."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.rate_limiter = RateLimiter(self.settings.rate_limit_delay)
        self.robots = get_robots_cache()
        self._session: aiohttp.ClientSession | None = None
        self._browser: Browser | None = None
        self._playwright = None
        self._ua_index = 0
        self._playwright_semaphore = asyncio.Semaphore(self.settings.max_concurrent_playwright)

    def _next_user_agent(self) -> str:
        agent = pick_user_agent(self._ua_index)
        self._ua_index += 1
        return agent

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.settings.request_timeout)
            connector = aiohttp.TCPConnector(limit=self.settings.max_concurrent_requests)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                trust_env=True,
            )
        return self._session

    async def _get_browser(self) -> Browser:
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser

    async def close(self) -> None:
        """Release HTTP and browser resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._session = None
        self._browser = None
        self._playwright = None

    async def download(self, url: str, use_playwright: bool | None = None) -> DownloadResult:
        """Download a URL with retries and robots.txt compliance."""
        from urllib.parse import urlparse

        domain = urlparse(url).netloc
        user_agent = self._next_user_agent()

        if self.settings.respect_robots_txt:
            allowed = await self.robots.can_fetch(url, user_agent)
            if not allowed:
                logger.info("Blocked by robots.txt: {}", url)
                return DownloadResult(url=url, error="Blocked by robots.txt", status_code=403)

        extra_delay = 0.0
        if self.settings.respect_robots_txt:
            crawl_delay = await self.robots.crawl_delay(url, user_agent)
            if crawl_delay:
                extra_delay = crawl_delay

        await self.rate_limiter.wait(domain, extra_delay)

        last_error: str | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                result = await self._download_aiohttp(url, user_agent)
                if result.html and len(result.html.strip()) > 100:
                    return result
                if use_playwright is False:
                    return result
                if self.settings.use_playwright and attempt == self.settings.max_retries:
                    return await self._download_playwright(url, user_agent)
                if result.error:
                    last_error = result.error
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Download attempt {}/{} failed for {}: {}",
                    attempt,
                    self.settings.max_retries,
                    url,
                    exc,
                )
            if attempt < self.settings.max_retries:
                await asyncio.sleep(self.settings.retry_backoff ** attempt)

        return DownloadResult(url=url, error=last_error or "Download failed")

    async def _download_aiohttp(self, url: str, user_agent: str) -> DownloadResult:
        session = await self._get_session()
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        max_bytes = self.settings.max_content_size_mb * 1024 * 1024

        async with session.get(
            url,
            headers=headers,
            allow_redirects=self.settings.follow_redirects,
        ) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return DownloadResult(
                    url=url,
                    status_code=response.status,
                    content_type=content_type,
                    error=f"Unsupported content type: {content_type}",
                    method="aiohttp",
                )

            raw = await response.content.read(max_bytes + 1)
            if len(raw) > max_bytes:
                return DownloadResult(
                    url=url,
                    status_code=response.status,
                    error="Content exceeds maximum size",
                    method="aiohttp",
                )

            encoding = response.charset or "utf-8"
            html = raw.decode(encoding, errors="replace")
            return DownloadResult(
                url=url,
                html=html,
                status_code=response.status,
                content_type=content_type,
                method="aiohttp",
                headers=dict(response.headers),
            )

    async def _download_playwright(self, url: str, user_agent: str) -> DownloadResult:
        async with self._playwright_semaphore:
            try:
                browser = await self._get_browser()
                context = await browser.new_context(user_agent=user_agent)
                page = await context.new_page()
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=int(self.settings.request_timeout * 1000),
                )
                html = await page.content()
                status = response.status if response else None
                await context.close()
                return DownloadResult(
                    url=url,
                    html=html,
                    status_code=status,
                    content_type="text/html",
                    method="playwright",
                )
            except Exception as exc:
                logger.error("Playwright download failed for {}: {}", url, exc)
                return DownloadResult(url=url, error=str(exc), method="playwright")

    async def download_pdf(self, url: str) -> bytes | None:
        """Download binary PDF content."""
        session = await self._get_session()
        user_agent = self._next_user_agent()
        try:
            async with session.get(url, headers={"User-Agent": user_agent}) as response:
                if response.status == 200:
                    return await response.read()
        except Exception as exc:
            logger.error("PDF download failed for {}: {}", url, exc)
        return None
