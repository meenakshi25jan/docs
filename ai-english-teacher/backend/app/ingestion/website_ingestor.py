from __future__ import annotations

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from readability import Document

from app.ingestion.base import BaseIngestor, IngestionInput, IngestResult
from app.ingestion.chunker import split_text_into_chunks

DEFAULT_USER_AGENT = "AI-English-Teacher-Ingestor/1.0 (+https://github.com/meenakshi25jan/docs)"


class WebsiteIngestor(BaseIngestor):
    """Fetch a URL, respect robots.txt, and extract readable article text."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 30.0) -> None:
        self.user_agent = user_agent
        self.timeout = timeout

    async def ingest(self, source: IngestionInput) -> IngestResult:
        if not source.source_url:
            raise ValueError("source_url is required for website ingestion")

        await self._ensure_robots_allowed(source.source_url)

        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
        ) as client:
            response = await client.get(source.source_url)
            response.raise_for_status()
            html = response.text

        document = Document(html)
        title = document.title() or source.title
        summary_html = document.summary()
        soup = BeautifulSoup(summary_html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        raw_text = soup.get_text(separator="\n", strip=True)

        chunks = split_text_into_chunks(raw_text)
        for chunk in chunks:
            chunk.section_title = title

        return IngestResult(
            title=title,
            raw_text=raw_text,
            language=source.language,
            page_count=None,
            chunks=chunks,
        )

    async def _ensure_robots_allowed(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        async with httpx.AsyncClient(
            timeout=self.timeout, headers={"User-Agent": self.user_agent}
        ) as client:
            try:
                response = await client.get(robots_url)
                if response.status_code == 404:
                    return
                response.raise_for_status()
                parser.parse(response.text.splitlines())
            except httpx.HTTPError as exc:
                raise PermissionError(
                    f"Unable to fetch robots.txt from {robots_url}: {exc}"
                ) from exc

        if not parser.can_fetch(self.user_agent, url):
            raise PermissionError(
                f"robots.txt disallows fetching {url} for user-agent {self.user_agent}"
            )
