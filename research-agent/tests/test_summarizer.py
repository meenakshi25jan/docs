"""Tests for summarizer fallback."""

from types import SimpleNamespace

from app.ai.summarizer import Summarizer


def _make_page(url: str, title: str, text: str, h1: list[str] | None = None):
    return SimpleNamespace(
        url=url,
        title=title,
        visible_text=text,
        h1=h1 or [title],
        paragraphs=[text[:200]],
    )


def test_fallback_summary_generates_output():
    pages = [
        _make_page("https://a.com", "Page A", "AI is transforming industries with 85% growth."),
        _make_page("https://b.com", "Page B", "Machine learning adoption reached 72% in 2024."),
    ]
    summarizer = Summarizer()
    summary = summarizer._fallback_summary("Artificial Intelligence", pages)

    assert summary.executive_summary
    assert len(summary.findings) > 0
    assert len(summary.source_urls) == 2
    assert 0.0 <= summary.confidence_score <= 1.0


def test_fallback_summary_includes_references():
    pages = [_make_page("https://example.com", "Example", "Some content here for testing.")]
    summarizer = Summarizer()
    summary = summarizer._fallback_summary("test", pages)

    assert len(summary.references) == 1
    assert summary.references[0]["url"] == "https://example.com"
