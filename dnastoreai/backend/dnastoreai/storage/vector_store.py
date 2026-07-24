"""ChromaDB vector store abstraction layer."""

from __future__ import annotations

from typing import Any

from dnastoreai.core.config import Settings


class VectorStore:
    """Vector database abstraction with ChromaDB backend."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Any = None
        self._collection: Any = None
        self._fallback: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        if not self.settings.vector_db_enabled:
            return
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.settings.chroma_persist_dir))
            self._collection = self._client.get_or_create_collection(
                name="dnastoreai_semantic",
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self._client = None

    def add(self, doc_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        self._ensure_client()
        if self._collection is not None:
            self._collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[{k: str(v) for k, v in metadata.items()}],
            )
        else:
            self._fallback[doc_id] = (embedding, metadata)

    def query(self, embedding: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        self._ensure_client()
        if self._collection is not None:
            results = self._collection.query(query_embeddings=[embedding], n_results=top_k)
            output = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    score = 1.0 - (results["distances"][0][i] if results["distances"] else 0.0)
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    output.append((doc_id, score, meta))
            return output

        # Fallback in-memory search
        scored = []
        for doc_id, (emb, meta) in self._fallback.items():
            score = _cosine_similarity(embedding, emb)
            scored.append((doc_id, score, meta))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
