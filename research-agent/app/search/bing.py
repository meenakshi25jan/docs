"""Bing Search API integration."""

from __future__ import annotations

from typing import Any

import aiohttp

from app.utils.helpers import deduplicate_urls, normalize_url
from app.utils.logger import get_logger
from config import get_settings

logger = get_logger()


async def search_bing(
    query: str,
    max_results: int = 50,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Search using Bing Web Search API v7."""
    settings = get_settings()
    api_key = api_key or settings.bing_api_key

    if not api_key:
        logger.warning("Bing API key not configured")
        return []

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": min(max_results, 50), "offset": 0}
    results: list[dict[str, Any]] = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error("Bing search error {}: {}", response.status, text)
                    return []
                data = await response.json()
    except Exception as exc:
        logger.error("Bing search request failed: {}", exc)
        return []

    for rank, item in enumerate(data.get("webPages", {}).get("value", []), start=1):
        url = normalize_url(item.get("url", ""))
        if not url:
            continue
        results.append(
            {
                "title": item.get("name", ""),
                "url": url,
                "snippet": item.get("snippet", ""),
                "rank": rank,
                "provider": "bing",
            }
        )

    urls = deduplicate_urls(item["url"] for item in results)
    url_set = set(urls)
    return [item for item in results if item["url"] in url_set][:max_results]
