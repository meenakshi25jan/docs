"""Tests for report generation."""

from pathlib import Path
from types import SimpleNamespace

from app.ai.summarizer import ResearchSummary
from app.reports.report_generator import ReportGenerator
from config import Settings


def test_generate_all_report_formats(tmp_path):
    settings = Settings(reports_dir=tmp_path, data_dir=tmp_path / "data")
    settings.ensure_directories()

    summary = ResearchSummary(
        executive_summary="Test executive summary for the report.",
        findings=["Finding one", "Finding two"],
        key_facts=["Fact A"],
        statistics=["85%"],
        references=[{"title": "Source", "url": "https://example.com", "citation_number": 1}],
        confidence_score=0.75,
        source_urls=["https://example.com"],
    )
    pages = [
        SimpleNamespace(
            url="https://example.com",
            title="Example",
            language="en",
            depth=0,
            paragraphs=["p1"],
            links=[{"url": "https://example.com/other"}],
        )
    ]

    generator = ReportGenerator(settings)
    paths = generator.generate_all("Test Query", summary, pages, job_id=1)

    assert "markdown" in paths
    assert "html" in paths
    assert "json" in paths
    assert "pdf" in paths

    for path_str in paths.values():
        assert Path(path_str).exists()
