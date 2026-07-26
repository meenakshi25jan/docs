"""DuckDuckGo search integration."""

from __future__ import annotations

import asyncio
from typing import Any

from duckduckgo_search import DDGS

from app.utils.helpers import deduplicate_urls, normalize_url
from app.utils.logger import get_logger

logger = get_logger()


async def search_duckduckgo(query: str, max_results: int = 50) -> list[dict[str, Any]]:
    """Search DuckDuckGo and return normalized results."""

    def _search() -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        with DDGS() as ddgs:
            for rank, item in enumerate(ddgs.text(query, max_results=max_results), start=1):
                url = normalize_url(item.get("href", ""))
                if not url:
                    continue
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("body", ""),
                        "rank": rank,
                        "provider": "duckduckgo",
                    }
                )
        return results

    try:
        results = await asyncio.to_thread(_search)
        urls = deduplicate_urls(item["url"] for item in results)
        url_set = set(urls)
        return [item for item in results if item["url"] in url_set]
    except Exception as exc:
        logger.error("DuckDuckGo search failed: {}", exc)
        return []
