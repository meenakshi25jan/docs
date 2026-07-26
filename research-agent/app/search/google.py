"""Google Custom Search API integration."""

from __future__ import annotations

from typing import Any

import aiohttp

from app.utils.helpers import deduplicate_urls, normalize_url
from app.utils.logger import get_logger
from config import get_settings

logger = get_logger()


async def search_google(
    query: str,
    max_results: int = 50,
    api_key: str | None = None,
    cse_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search using Google Custom Search JSON API."""
    settings = get_settings()
    api_key = api_key or settings.google_api_key
    cse_id = cse_id or settings.google_cse_id

    if not api_key or not cse_id:
        logger.warning("Google Custom Search credentials not configured")
        return []

    results: list[dict[str, Any]] = []
    start = 1
    per_page = 10

    async with aiohttp.ClientSession() as session:
        while len(results) < max_results:
            params = {
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "start": start,
                "num": min(per_page, max_results - len(results)),
            }
            try:
                async with session.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error("Google search error {}: {}", response.status, text)
                        break
                    data = await response.json()
            except Exception as exc:
                logger.error("Google search request failed: {}", exc)
                break

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                url = normalize_url(item.get("link", ""))
                if not url:
                    continue
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("snippet", ""),
                        "rank": len(results) + 1,
                        "provider": "google",
                    }
                )

            start += per_page
            if "nextPage" not in data.get("queries", {}):
                break

    urls = deduplicate_urls(item["url"] for item in results)
    url_set = set(urls)
    return [item for item in results if item["url"] in url_set][:max_results]
