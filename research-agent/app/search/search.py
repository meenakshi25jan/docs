"""Unified search interface."""

from __future__ import annotations

from typing import Any, Literal

from app.search.bing import search_bing
from app.search.duckduckgo import search_duckduckgo
from app.search.google import search_google
from app.utils.helpers import deduplicate_urls
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()

SearchProvider = Literal["duckduckgo", "google", "bing"]


class SearchService:
    """Coordinate web search across configured providers."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def search(
        self,
        query: str,
        max_results: int | None = None,
        provider: SearchProvider | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a web search and return deduplicated results."""
        provider = provider or self.settings.search_provider  # type: ignore[assignment]
        max_results = max_results or self.settings.search_max_results
        logger.info("Searching '{}' via {} (max={})", query, provider, max_results)

        if provider == "google":
            results = await search_google(query, max_results=max_results)
            if not results:
                logger.info("Falling back to DuckDuckGo")
                results = await search_duckduckgo(query, max_results=max_results)
        elif provider == "bing":
            results = await search_bing(query, max_results=max_results)
            if not results:
                logger.info("Falling back to DuckDuckGo")
                results = await search_duckduckgo(query, max_results=max_results)
        else:
            results = await search_duckduckgo(query, max_results=max_results)

        deduped_urls = deduplicate_urls(item["url"] for item in results)
        url_set = set(deduped_urls)
        unique_results = [item for item in results if item["url"] in url_set]
        logger.info("Found {} unique URLs for query '{}'", len(unique_results), query)
        return unique_results[:max_results]

    def extract_urls(self, results: list[dict[str, Any]]) -> list[str]:
        """Extract URL list from search results."""
        return deduplicate_urls(item["url"] for item in results)
