"""Page scraping orchestration."""

from __future__ import annotations

from app.crawler.downloader import Downloader, DownloadResult
from app.crawler.parser import HTMLParser, ParsedPage
from app.utils.logger import get_logger

logger = get_logger()


class Scraper:
    """Coordinate downloading and parsing of individual pages."""

    def __init__(self, downloader: Downloader | None = None) -> None:
        self.downloader = downloader or Downloader()
        self.parser = HTMLParser()

    async def scrape(self, url: str, use_playwright: bool | None = None) -> tuple[ParsedPage | None, DownloadResult]:
        """Download and parse a single URL."""
        download = await self.downloader.download(url, use_playwright=use_playwright)
        if not download.html:
            logger.warning("No HTML content for {}: {}", url, download.error)
            return None, download

        try:
            parsed = self.parser.parse(download.html, url)
            return parsed, download
        except Exception as exc:
            logger.error("Parse error for {}: {}", url, exc)
            download.error = str(exc)
            return None, download

    async def close(self) -> None:
        """Release downloader resources."""
        await self.downloader.close()
