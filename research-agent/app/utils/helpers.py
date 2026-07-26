"""Shared helper utilities."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from config import get_settings

_TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "ref",
    "source",
}


def utc_now() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def normalize_url(url: str, base: str | None = None) -> str | None:
    """Normalize and validate a URL."""
    if not url or url.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
        return None

    absolute = urljoin(base, url.strip()) if base else url.strip()
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None

    query = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in query.items() if k.lower() not in _TRACKING_PARAMS}
    normalized_query = urlencode(filtered, doseq=True)
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            normalized_query,
            "",
        )
    )


def is_same_domain(url: str, base_url: str) -> bool:
    """Check whether two URLs share the same registrable domain."""
    return urlparse(url).netloc.lower() == urlparse(base_url).netloc.lower()


def deduplicate_urls(urls: Iterable[str]) -> list[str]:
    """Remove duplicate URLs while preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        normalized = normalize_url(url)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def content_hash(text: str) -> str:
    """Generate SHA-256 hash for content deduplication."""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3].rstrip() + "..."


def pick_user_agent(index: int = 0) -> str:
    """Rotate through configured user agents."""
    agents = get_settings().user_agents
    return agents[index % len(agents)]


def safe_filename(name: str, max_length: int = 120) -> str:
    """Create a filesystem-safe filename."""
    cleaned = re.sub(r"[^\w\s-]", "", name).strip().lower()
    cleaned = re.sub(r"[-\s]+", "-", cleaned)
    return cleaned[:max_length] or "report"


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    if not text:
        return []
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge two dictionaries."""
    merged = base.copy()
    merged.update(override)
    return merged
