"""Chapter 94 — LLMs and RAG reference implementation."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Document:
    doc_id: str
    text: str


@dataclass
class RetrievedChunk:
    doc_id: str
    text: str
    score: float


CORPUS: list[Document] = [
    Document("d1", "Gradient descent minimizes loss by following negative gradients."),
    Document("d2", "RAG combines retrieval with generation for grounded answers."),
    Document("d3", "Transformers use self-attention for sequence modeling."),
    Document("d4", "Vector databases store embeddings for semantic search."),
]


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def retrieve(query: str, k: int = 2) -> list[RetrievedChunk]:
    q_tokens = tokenize(query)
    scored: list[RetrievedChunk] = []
    for doc in CORPUS:
        d_tokens = tokenize(doc.text)
        overlap = len(q_tokens & d_tokens)
        if overlap:
            scored.append(RetrievedChunk(doc.doc_id, doc.text, overlap / max(len(q_tokens), 1)))
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:k]


def generate_answer(query: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I don't have enough context to answer."
    context = " ".join(c.text for c in chunks)
    return f"Based on: {context[:120]}... Answer to '{query}': see retrieved context above."


def rag_pipeline(query: str) -> dict[str, object]:
    chunks = retrieve(query)
    answer = generate_answer(query, chunks)
    confidence = float(chunks[0].score) if chunks else 0.0
    return {"query": query, "chunks": chunks, "answer": answer, "confidence": confidence}


def main() -> float:
    result = rag_pipeline("How does RAG work with retrieval?")
    print(f"Query: {result['query']}")
    for ch in result["chunks"]:  # type: ignore[union-attr]
        print(f"  [{ch.doc_id}] score={ch.score:.2f} {ch.text[:50]}...")
    print(f"Answer: {result['answer']}")
    print("SUCCESS: LLM RAG pipeline completed")
    return float(result["confidence"])


if __name__ == "__main__":
    main()
