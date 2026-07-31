"""Traditional document-chunking RAG (no knowledge graph, no concept metadata)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from common import (
    RetrievedChunk,
    RetrievalResult,
    cosine_similarity,
    term_frequency,
    tokenize,
)


@dataclass
class DocumentChunk:
    id: str
    text: str
    source: str


class TraditionalRAG:
    """Chunk documents, embed with TF-IDF-style vectors, retrieve by similarity."""

    def __init__(self, chunk_size: int = 220, overlap: int = 40):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[DocumentChunk] = []

    def ingest_markdown(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        words = text.split()
        start = 0
        index = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            self.chunks.append(
                DocumentChunk(
                    id=f"{path.stem}-chunk-{index}",
                    text=chunk_text,
                    source=str(path),
                )
            )
            index += 1
            if end == len(words):
                break
            start = max(end - self.overlap, start + 1)

    def retrieve(self, query: str, top_k: int = 3) -> RetrievalResult:
        query_vec = term_frequency(tokenize(query))
        scored: List[RetrievedChunk] = []

        for chunk in self.chunks:
            chunk_vec = term_frequency(tokenize(chunk.text))
            score = cosine_similarity(query_vec, chunk_vec)
            scored.append(
                RetrievedChunk(
                    id=chunk.id,
                    text=chunk.text,
                    score=score,
                    source=chunk.source,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        top = scored[:top_k]

        notes = [
            "Documents were split into fixed-size overlapping chunks.",
            "No metadata filtering or relationship navigation is available.",
            "The model must reconstruct cross-concept context from isolated paragraphs.",
        ]

        return RetrievalResult(
            approach="Traditional RAG (document chunks + vector similarity)",
            query=query,
            chunks=top,
            notes=notes,
        )
