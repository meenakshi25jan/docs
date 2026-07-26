"""Tests for helper utilities."""

from app.utils.helpers import (
    content_hash,
    deduplicate_urls,
    normalize_url,
    truncate_text,
)


def test_normalize_url_removes_fragment():
    assert normalize_url("https://example.com/page#section") == "https://example.com/page"


def test_normalize_url_removes_tracking_params():
    url = "https://example.com/page?utm_source=test&id=1"
    assert normalize_url(url) == "https://example.com/page?id=1"


def test_normalize_url_rejects_invalid():
    assert normalize_url("javascript:alert(1)") is None
    assert normalize_url("") is None


def test_deduplicate_urls():
    urls = [
        "https://example.com/a",
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert deduplicate_urls(urls) == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_content_hash_deterministic():
    assert content_hash("hello") == content_hash("hello")
    assert content_hash("hello") != content_hash("world")


def test_truncate_text():
    long_text = "a" * 100
    result = truncate_text(long_text, max_length=50)
    assert len(result) == 50
    assert result.endswith("...")
