from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IngestedChunk:
    chunk_index: int
    content: str
    skill: str | None = None
    level: str | None = None
    page_number: int | None = None
    section_title: str | None = None
    token_count: int | None = None


@dataclass
class IngestResult:
    title: str
    raw_text: str
    language: str = "en"
    page_count: int | None = None
    chunks: list[IngestedChunk] = field(default_factory=list)


@dataclass
class IngestionInput:
    """Normalized input passed to ingestors by the orchestrator."""

    source_type: str
    title: str
    file_path: Path | None = None
    source_url: str | None = None
    language: str = "en"


class BaseIngestor(ABC):
    """Extract raw text and chunk it into knowledge_chunk-ready segments."""

    @abstractmethod
    async def ingest(self, source: IngestionInput) -> IngestResult:
        """Return document metadata and chunked content (no DB writes)."""
