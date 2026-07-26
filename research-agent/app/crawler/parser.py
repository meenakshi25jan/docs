"""HTML parsing and content extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment, Tag
from langdetect import DetectorFactory, LangDetectException, detect

from app.utils.helpers import content_hash, normalize_url
from app.utils.logger import get_logger

DetectorFactory.seed = 0
logger = get_logger()

_AD_PATTERNS = re.compile(
    r"(ad|ads|advert|banner|sponsor|promo|popup|newsletter|cookie|sidebar|"
    r"social-share|related-posts|comment|footer|header|nav|menu|breadcrumb)",
    re.IGNORECASE,
)

_REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "canvas",
    "form",
    "button",
    "input",
    "select",
    "textarea",
}


@dataclass
class ParsedPage:
    """Structured content extracted from HTML."""

    url: str
    title: str | None = None
    meta_description: str | None = None
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    lists: list[list[str]] = field(default_factory=list)
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    links: list[dict[str, str]] = field(default_factory=list)
    pdfs: list[str] = field(default_factory=list)
    visible_text: str = ""
    language: str | None = None
    content_hash: str | None = None


class HTMLParser:
    """Parse and clean HTML documents."""

    def __init__(self, parser: str = "lxml") -> None:
        self.parser = parser

    def parse(self, html: str, url: str) -> ParsedPage:
        """Parse HTML and extract structured content."""
        soup = BeautifulSoup(html, self.parser)
        self._remove_noise(soup)
        cleaned_soup = self._clean_html(soup)

        title = self._extract_title(soup)
        meta_description = self._extract_meta_description(soup)
        h1 = self._extract_headings(cleaned_soup, "h1")
        h2 = self._extract_headings(cleaned_soup, "h2")
        paragraphs = self._extract_paragraphs(cleaned_soup)
        lists = self._extract_lists(cleaned_soup)
        tables = self._extract_tables(cleaned_soup)
        images = self._extract_images(cleaned_soup, url)
        links = self._extract_links(cleaned_soup, url)
        pdfs = self._extract_pdfs(links)
        visible_text = self._extract_visible_text(cleaned_soup)
        language = self._detect_language(visible_text, soup)

        return ParsedPage(
            url=url,
            title=title,
            meta_description=meta_description,
            h1=h1,
            h2=h2,
            paragraphs=paragraphs,
            lists=lists,
            tables=tables,
            images=images,
            links=links,
            pdfs=pdfs,
            visible_text=visible_text,
            language=language,
            content_hash=content_hash(visible_text) if visible_text else None,
        )

    def _remove_noise(self, soup: BeautifulSoup) -> None:
        """Remove scripts, ads, navigation, and comments."""
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        for tag_name in _REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        for tag in soup.find_all(["nav", "header", "footer", "aside"]):
            tag.decompose()

        for tag in soup.find_all(True):
            if not isinstance(tag, Tag):
                continue
            classes = " ".join(tag.get("class", []))
            tag_id = tag.get("id", "")
            role = tag.get("role", "")
            identifier = f"{classes} {tag_id} {role}"
            if _AD_PATTERNS.search(identifier):
                tag.decompose()

    def _clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Return a cleaned copy of the document body."""
        body = soup.find("body")
        if body is None:
            return soup
        return BeautifulSoup(str(body), self.parser)

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            return str(og["content"]).strip()
        return None

    def _extract_meta_description(self, soup: BeautifulSoup) -> str | None:
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return str(meta["content"]).strip()
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            return str(og["content"]).strip()
        return None

    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> list[str]:
        return [
            el.get_text(strip=True)
            for el in soup.find_all(tag)
            if el.get_text(strip=True)
        ]

    def _extract_paragraphs(self, soup: BeautifulSoup) -> list[str]:
        paragraphs: list[str] = []
        for p in soup.find_all("p"):
            text = p.get_text(" ", strip=True)
            if len(text) > 30:
                paragraphs.append(text)
        return paragraphs

    def _extract_lists(self, soup: BeautifulSoup) -> list[list[str]]:
        result: list[list[str]] = []
        for list_tag in soup.find_all(["ul", "ol"]):
            items = [
                li.get_text(" ", strip=True)
                for li in list_tag.find_all("li", recursive=False)
                if li.get_text(strip=True)
            ]
            if items:
                result.append(items)
        return result

    def _extract_tables(self, soup: BeautifulSoup) -> list[list[list[str]]]:
        tables: list[list[list[str]]] = []
        for table in soup.find_all("table"):
            rows: list[list[str]] = []
            for tr in table.find_all("tr"):
                cells = [
                    cell.get_text(" ", strip=True)
                    for cell in tr.find_all(["th", "td"])
                ]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        return tables

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list[dict[str, str]]:
        images: list[dict[str, str]] = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue
            absolute = normalize_url(src, base_url)
            if absolute:
                images.append(
                    {
                        "src": absolute,
                        "alt": img.get("alt", ""),
                        "title": img.get("title", ""),
                    }
                )
        return images

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[dict[str, str]]:
        links: list[dict[str, str]] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = normalize_url(anchor["href"], base_url)
            if not href or href in seen:
                continue
            seen.add(href)
            links.append({"url": href, "text": anchor.get_text(strip=True)})
        return links

    def _extract_pdfs(self, links: list[dict[str, str]]) -> list[str]:
        return [
            link["url"]
            for link in links
            if link["url"].lower().endswith(".pdf")
        ]

    def _extract_visible_text(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _detect_language(self, text: str, soup: BeautifulSoup) -> str | None:
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            return str(html_tag["lang"])[:16]

        sample = text[:2000] if text else ""
        if len(sample) < 20:
            return None
        try:
            return detect(sample)
        except LangDetectException:
            return None


def parsed_page_to_dict(parsed: ParsedPage) -> dict[str, Any]:
    """Convert ParsedPage to a serializable dictionary."""
    return {
        "url": parsed.url,
        "title": parsed.title,
        "meta_description": parsed.meta_description,
        "h1": parsed.h1,
        "h2": parsed.h2,
        "paragraphs": parsed.paragraphs,
        "lists": parsed.lists,
        "tables": parsed.tables,
        "images": parsed.images,
        "links": parsed.links,
        "pdfs": parsed.pdfs,
        "visible_text": parsed.visible_text,
        "language": parsed.language,
        "content_hash": parsed.content_hash,
    }
