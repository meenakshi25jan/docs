"""Embedding helpers for pgvector RAG and memory."""

from __future__ import annotations

from app.ai.openai_client import ai_client


async def embed_text(text: str) -> list[float] | None:
    text = text.strip()
    if not text or not ai_client.is_configured:
        return None
    try:
        return await ai_client.get_embedding(text[:8000])
    except Exception:  # noqa: BLE001
        return None


def embedding_to_pgvector(values: list[float]) -> str:
    return "[" + ",".join(str(v) for v in values) + "]"
