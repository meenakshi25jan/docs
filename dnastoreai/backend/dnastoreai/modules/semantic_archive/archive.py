"""Semantic DNA archive with vector search capability."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class DocumentEntry:
    """A document stored in the semantic archive."""

    document_id: str
    content: str
    embedding: list[float] = field(default_factory=list)
    dna_sequence: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Semantic search result."""

    document_id: str
    score: float
    content: str
    dna_sequence: str
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStoreBackend(Protocol):
    """Protocol for vector database backends."""

    def add(self, id: str, embedding: list[float], metadata: dict[str, Any]) -> None: ...
    def query(self, embedding: list[float], top_k: int) -> list[tuple[str, float, dict[str, Any]]]: ...


class SimpleVectorBackend:
    """In-memory vector store for testing and fallback."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def add(self, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        self._store[id] = (embedding, metadata)

    def query(self, embedding: list[float], top_k: int) -> list[tuple[str, float, dict[str, Any]]]:
        results = []
        for doc_id, (emb, meta) in self._store.items():
            score = _cosine_similarity(embedding, emb)
            results.append((doc_id, score, meta))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _simple_embedding(text: str, dim: int = 128) -> list[float]:
    """Generate a simple deterministic embedding from text."""
    embedding = [0.0] * dim
    for i, char in enumerate(text):
        embedding[i % dim] += ord(char) / 256.0
    norm = sum(x * x for x in embedding) ** 0.5
    return [x / norm for x in embedding] if norm > 0 else embedding


class SemanticDNAArchive:
    """Semantic DNA archive with vector search."""

    def __init__(self, backend: VectorStoreBackend | None = None, embedding_dim: int = 128) -> None:
        self.backend = backend or SimpleVectorBackend()
        self.embedding_dim = embedding_dim
        self._entries: dict[str, DocumentEntry] = {}

    def store_document(
        self,
        document_id: str,
        content: str,
        dna_sequence: str,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentEntry:
        """Store a document with embedding and DNA encoding."""
        embedding = _simple_embedding(content, self.embedding_dim)
        entry = DocumentEntry(
            document_id=document_id,
            content=content,
            embedding=embedding,
            dna_sequence=dna_sequence,
            metadata=metadata or {},
        )
        self._entries[document_id] = entry
        self.backend.add(document_id, embedding, {"content": content, "dna": dna_sequence, **(metadata or {})})
        return entry

    def semantic_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search for semantically similar documents."""
        query_embedding = _simple_embedding(query, self.embedding_dim)
        results = self.backend.query(query_embedding, top_k)
        return [
            SearchResult(
                document_id=doc_id,
                score=score,
                content=meta.get("content", ""),
                dna_sequence=meta.get("dna", ""),
                metadata=meta,
            )
            for doc_id, score, meta in results
        ]

    def similar_documents(self, document_id: str, top_k: int = 5) -> list[SearchResult]:
        """Find documents similar to a given document."""
        entry = self._entries.get(document_id)
        if not entry:
            return []
        results = self.backend.query(entry.embedding, top_k + 1)
        return [
            SearchResult(
                document_id=doc_id,
                score=score,
                content=meta.get("content", ""),
                dna_sequence=meta.get("dna", ""),
                metadata=meta,
            )
            for doc_id, score, meta in results
            if doc_id != document_id
        ][:top_k]
