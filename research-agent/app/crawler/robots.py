"""robots.txt parsing and compliance."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

from app.utils.logger import get_logger

logger = get_logger()


@dataclass
class RobotsCache:
    """Cache robots.txt rules per domain."""

    _parsers: dict[str, RobotFileParser] = field(default_factory=dict)
    _failed: set[str] = field(default_factory=set)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def _fetch_robots(self, domain: str) -> RobotFileParser | None:
        robots_url = f"https://{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    robots_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"User-Agent": "ResearchAgent/1.0"},
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        parser.parse(content.splitlines())
                        return parser
                    if response.status in {403, 404}:
                        parser.parse([])
                        return parser
        except Exception as exc:
            logger.debug("Failed to fetch robots.txt for {}: {}", domain, exc)

        return None

    async def get_parser(self, url: str) -> RobotFileParser | None:
        """Get or fetch robots parser for a URL's domain."""
        domain = urlparse(url).netloc.lower()
        if not domain:
            return None

        async with self._lock:
            if domain in self._parsers:
                return self._parsers[domain]
            if domain in self._failed:
                return None

        parser = await self._fetch_robots(domain)
        async with self._lock:
            if parser is not None:
                self._parsers[domain] = parser
            else:
                self._failed.add(domain)
        return parser

    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Check if fetching the URL is allowed by robots.txt."""
        parser = await self.get_parser(url)
        if parser is None:
            return True
        return parser.can_fetch(user_agent, url)

    async def crawl_delay(self, url: str, user_agent: str = "*") -> float | None:
        """Return crawl-delay if specified in robots.txt."""
        parser = await self.get_parser(url)
        if parser is None:
            return None
        delay = parser.crawl_delay(user_agent)
        return float(delay) if delay else None


_robots_cache = RobotsCache()


def get_robots_cache() -> RobotsCache:
    """Return shared robots cache instance."""
    return _robots_cache


def is_allowed_by_robots(parser: RobotFileParser | None, url: str, user_agent: str) -> bool:
    """Synchronous robots.txt check."""
    if parser is None:
        return True
    return parser.can_fetch(user_agent, url)


def resolve_robots_url(base_url: str) -> str:
    """Resolve robots.txt URL for a given page."""
    return urljoin(base_url, "/robots.txt")
