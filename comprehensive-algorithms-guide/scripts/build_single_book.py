#!/usr/bin/env python3
"""Merge all chapter markdown files into one complete book."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

BOOK_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = BOOK_ROOT / "SUMMARY.md"
OUTPUT = BOOK_ROOT / "COMPREHENSIVE_ALGORITHMS_GUIDE_COMPLETE.md"


def extract_chapter_paths(summary_text: str) -> list[tuple[str, Path]]:
    """Parse SUMMARY.md links in document order."""
    pattern = re.compile(r"\[([^\]]+)\]\(\./([^)]+)\)")
    entries: list[tuple[str, Path]] = []
    for title, rel_path in pattern.findall(summary_text):
        path = BOOK_ROOT / rel_path
        if path.exists():
            entries.append((title, path))
    return entries


def fix_relative_links(content: str, source_dir: Path) -> str:
    """Adjust relative markdown links to work from book root."""
    # ../../code/... -> code/...
    content = re.sub(r"\]\(\.\./\.\./code/", "](code/", content)
    content = re.sub(r"\]\(\.\./code/", "](code/", content)
    # cross-chapter ../part-xx/... -> part-xx/...
    content = re.sub(r"\]\(\.\./([^)]+)\)", r"](\1)", content)
    content = re.sub(r"\]\(\./([^)]+)\)", r"](\1)", content)
    return content


def build_book() -> None:
    summary_text = SUMMARY.read_text(encoding="utf-8")
    chapters = extract_chapter_paths(summary_text)

    parts: list[str] = [
        "---",
        "title: Comprehensive Algorithms Guide",
        "subtitle: From Beginner to Senior Level",
        "lang: en",
        f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Comprehensive Algorithms Guide",
        "",
        "## From Beginner to Senior Level",
        "",
        "*Classical Algorithms, Artificial Intelligence, Machine Learning, Deep Learning, "
        "Reinforcement Learning, Optimization, Production Engineering, System Design, "
        "and Real-World Applications Using Python*",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for i, (title, _) in enumerate(chapters, start=1):
        anchor = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        parts.append(f"{i}. [{title}](#{anchor})")

    parts.extend(["", "---", ""])

    for title, path in chapters:
        parts.append(f"\n\n<!-- SOURCE: {path.relative_to(BOOK_ROOT)} -->\n")
        parts.append(f"\n\\newpage\n\n" if False else "\n\n---\n\n")
        body = path.read_text(encoding="utf-8").strip()
        body = fix_relative_links(body, path.parent)
        parts.append(body)
        parts.append("\n\n---\n")

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    line_count = OUTPUT.read_text(encoding="utf-8").count("\n") + 1
    print(f"Built: {OUTPUT}")
    print(f"Chapters merged: {len(chapters)}")
    print(f"Lines: {line_count:,}")
    print(f"Size: {OUTPUT.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    build_book()
