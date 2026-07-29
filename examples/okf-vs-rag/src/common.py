"""Shared utilities for the OKF vs RAG comparison demo."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def tokenize(text: str) -> List[str]:
    return TOKEN_PATTERN.findall(text.lower())


def term_frequency(tokens: Iterable[str]) -> Counter:
    return Counter(tokens)


def cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    shared = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def split_frontmatter(content: str) -> Tuple[Dict[str, object], str]:
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1].strip()
    body = parts[2].lstrip("\n")
    metadata: Dict[str, object] = {}

    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            metadata[key] = [item.strip() for item in inner.split(",") if item.strip()]
        else:
            metadata[key] = value.strip("\"'")

    return metadata, body


@dataclass
class RetrievedChunk:
    id: str
    text: str
    score: float
    source: str
    metadata: Dict[str, object] = field(default_factory=dict)
    related: List[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    approach: str
    query: str
    chunks: List[RetrievedChunk]
    notes: List[str] = field(default_factory=list)

    def top_text(self, limit: int = 3) -> str:
        return "\n\n---\n\n".join(chunk.text[:500] for chunk in self.chunks[:limit])


def extract_links(markdown: str) -> Set[str]:
    return {match.group(2) for match in LINK_PATTERN.finditer(markdown)}


def resolve_link(bundle_root: Path, current_file: Path, link: str) -> Optional[Path]:
    if link.startswith("http://") or link.startswith("https://"):
        return None

    normalized = link.split("#", 1)[0]
    candidates = [
        Path(normalized.lstrip("/")),
        bundle_root.parent / normalized.lstrip("/"),
        current_file.parent / normalized,
        bundle_root / Path(normalized).name,
        bundle_root / normalized,
    ]

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.suffix == ".md":
            return resolved
    return None
