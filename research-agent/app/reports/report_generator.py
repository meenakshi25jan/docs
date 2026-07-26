"""Generate research reports in Markdown, HTML, JSON, and PDF."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.ai.summarizer import ResearchSummary
from app.utils.helpers import safe_filename, utc_now
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()


class ReportGenerator:
    """Produce multi-format research reports."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(
        self,
        query: str,
        summary: ResearchSummary,
        pages: list[Any],
        job_id: int,
    ) -> dict[str, str]:
        """Generate all report formats and return file paths."""
        timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
        base_name = safe_filename(f"{query}_{job_id}_{timestamp}")

        paths = {
            "markdown": str(self._generate_markdown(base_name, query, summary, pages)),
            "html": str(self._generate_html(base_name, query, summary, pages)),
            "json": str(self._generate_json(base_name, query, summary, pages, job_id)),
            "pdf": str(self._generate_pdf(base_name, query, summary, pages)),
        }
        logger.info("Generated reports for job {}: {}", job_id, paths)
        return paths

    def _generate_markdown(
        self,
        base_name: str,
        query: str,
        summary: ResearchSummary,
        pages: list[Any],
    ) -> Path:
        path = self.settings.reports_dir / f"{base_name}.md"
        lines = [
            f"# Research Report: {query}",
            "",
            f"*Generated: {utc_now().isoformat()}*",
            "",
            "## Executive Summary",
            "",
            summary.executive_summary or "_No summary available._",
            "",
            "## Findings",
            "",
        ]
        lines.extend(f"- {finding}" for finding in summary.findings or ["_No findings._"])

        lines.extend(["", "## Timeline", ""])
        if summary.timeline:
            lines.extend(f"- {event}" for event in summary.timeline)
        else:
            lines.append("_No timeline events identified._")

        lines.extend(["", "## Key Facts", ""])
        lines.extend(f"- {fact}" for fact in summary.key_facts or ["_No key facts._"])

        lines.extend(["", "## Statistics", ""])
        lines.extend(f"- {stat}" for stat in summary.statistics or ["_No statistics found._"])

        lines.extend(["", "## References", ""])
        for ref in summary.references:
            num = ref.get("citation_number", "")
            title = ref.get("title", "Untitled")
            url = ref.get("url", "")
            lines.append(f"- [{num}] [{title}]({url})")

        lines.extend(["", "## Source URLs", ""])
        for url in summary.source_urls or [p.url for p in pages]:
            lines.append(f"- {url}")

        lines.extend(
            [
                "",
                "## Confidence Score",
                "",
                f"**{summary.confidence_score:.2f}** / 1.00",
                "",
                f"## Pages Crawled ({len(pages)})",
                "",
            ]
        )
        for page in pages[:50]:
            title = page.title or page.url
            lines.append(f"- [{title}]({page.url})")

        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _generate_html(
        self,
        base_name: str,
        query: str,
        summary: ResearchSummary,
        pages: list[Any],
    ) -> Path:
        path = self.settings.reports_dir / f"{base_name}.html"

        def list_items(items: list[str], default: str = "None") -> str:
            if not items:
                return f"<li>{default}</li>"
            return "".join(f"<li>{item}</li>" for item in items)

        def ref_items(refs: list[dict[str, Any]]) -> str:
            if not refs:
                return "<li>No references</li>"
            return "".join(
                f'<li>[{r.get("citation_number", "")}] '
                f'<a href="{r.get("url", "")}">{r.get("title", "Untitled")}</a></li>'
                for r in refs
            )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Research Report: {query}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #222; }}
    h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
    h2 {{ color: #444; margin-top: 2rem; }}
    .meta {{ color: #666; font-style: italic; }}
    .confidence {{ font-size: 1.5rem; font-weight: bold; color: #2a7; }}
    a {{ color: #06c; }}
    ul {{ padding-left: 1.5rem; }}
  </style>
</head>
<body>
  <h1>Research Report: {query}</h1>
  <p class="meta">Generated: {utc_now().isoformat()}</p>

  <h2>Executive Summary</h2>
  <p>{summary.executive_summary or "No summary available."}</p>

  <h2>Findings</h2>
  <ul>{list_items(summary.findings)}</ul>

  <h2>Timeline</h2>
  <ul>{list_items(summary.timeline, "No timeline events identified.")}</ul>

  <h2>Key Facts</h2>
  <ul>{list_items(summary.key_facts)}</ul>

  <h2>Statistics</h2>
  <ul>{list_items(summary.statistics)}</ul>

  <h2>References</h2>
  <ul>{ref_items(summary.references)}</ul>

  <h2>Source URLs</h2>
  <ul>{"".join(f'<li><a href="{u}">{u}</a></li>' for u in (summary.source_urls or [p.url for p in pages]))}</ul>

  <h2>Confidence Score</h2>
  <p class="confidence">{summary.confidence_score:.2f} / 1.00</p>

  <h2>Pages Crawled ({len(pages)})</h2>
  <ul>{"".join(f'<li><a href="{p.url}">{p.title or p.url}</a></li>' for p in pages[:50])}</ul>
</body>
</html>"""
        path.write_text(html, encoding="utf-8")
        return path

    def _generate_json(
        self,
        base_name: str,
        query: str,
        summary: ResearchSummary,
        pages: list[Any],
        job_id: int,
    ) -> Path:
        path = self.settings.reports_dir / f"{base_name}.json"
        payload = {
            "job_id": job_id,
            "query": query,
            "generated_at": utc_now().isoformat(),
            "summary": summary.to_dict(),
            "pages": [
                {
                    "url": p.url,
                    "title": p.title,
                    "language": p.language,
                    "depth": p.depth,
                    "paragraph_count": len(p.paragraphs or []),
                    "link_count": len(p.links or []),
                }
                for p in pages
            ],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def _generate_pdf(
        self,
        base_name: str,
        query: str,
        summary: ResearchSummary,
        pages: list[Any],
    ) -> Path:
        path = self.settings.reports_dir / f"{base_name}.pdf"
        doc = SimpleDocTemplate(
            str(path),
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.HexColor("#333333"),
        )
        body_style = styles["BodyText"]

        story: list[Any] = []
        story.append(Paragraph(f"Research Report: {self._escape(query)}", title_style))
        story.append(Paragraph(f"Generated: {utc_now().isoformat()}", body_style))
        story.append(Spacer(1, 12))

        sections = [
            ("Executive Summary", summary.executive_summary),
            ("Confidence Score", f"{summary.confidence_score:.2f} / 1.00"),
        ]
        for heading, content in sections:
            story.append(Paragraph(heading, heading_style))
            story.append(Paragraph(self._escape(content or "N/A"), body_style))
            story.append(Spacer(1, 8))

        for section_name, items in [
            ("Findings", summary.findings),
            ("Key Facts", summary.key_facts),
            ("Statistics", summary.statistics),
        ]:
            story.append(Paragraph(section_name, heading_style))
            for item in (items or ["None"])[:20]:
                story.append(Paragraph(f"• {self._escape(str(item))}", body_style))
            story.append(Spacer(1, 8))

        story.append(Paragraph("Source URLs", heading_style))
        for page in pages[:30]:
            story.append(Paragraph(f"• {self._escape(page.url)}", body_style))

        doc.build(story)
        return path

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
