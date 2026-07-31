"""Chapter 95 — Vector database and embeddings reference."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def embed(text: str, dim: int = 16) -> np.ndarray:
    """Deterministic bag-of-hashes embedding."""
    vec = np.zeros(dim)
    for token in text.lower().split():
        idx = hash(token) % dim
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


class VectorStore:
    def __init__(self) -> None:
        self.ids: list[str] = []
        self.vectors: list[np.ndarray] = []
        self.texts: list[str] = []

    def upsert(self, doc_id: str, text: str) -> None:
        if doc_id in self.ids:
            idx = self.ids.index(doc_id)
            self.vectors[idx] = embed(text)
            self.texts[idx] = text
        else:
            self.ids.append(doc_id)
            self.vectors.append(embed(text))
            self.texts.append(text)

    def search(self, query: str, k: int = 3) -> list[tuple[str, str, float]]:
        q = embed(query)
        scores = [float(np.dot(q, v)) for v in self.vectors]
        ranked = sorted(zip(self.ids, self.texts, scores), key=lambda x: x[2], reverse=True)
        return ranked[:k]


def main() -> float:
    store = VectorStore()
    docs = {
        "a": "neural networks and deep learning",
        "b": "graph algorithms shortest path",
        "c": "vector embeddings semantic search",
    }
    for doc_id, text in docs.items():
        store.upsert(doc_id, text)

    results = store.search("semantic vector retrieval", k=2)
    for doc_id, text, score in results:
        print(f"{doc_id}: score={score:.3f} text={text}")
    print("SUCCESS: Vector database demo completed")
    return results[0][2] if results else 0.0


if __name__ == "__main__":
    main()
