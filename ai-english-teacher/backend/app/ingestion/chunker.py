from __future__ import annotations

from app.core.config import get_settings
from app.ingestion.base import IngestedChunk


def estimate_token_count(text: str) -> int:
    """Rough token estimate for MVP (whitespace split)."""
    return len(text.split())


def split_text_into_chunks(
    text: str,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[IngestedChunk]:
    """Split text into overlapping character windows."""
    settings = get_settings()
    size = chunk_size if chunk_size is not None else settings.INGESTION_CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else settings.INGESTION_CHUNK_OVERLAP

    if size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if overlap >= size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[IngestedChunk] = []
    start = 0
    index = 0
    step = size - overlap

    while start < len(normalized):
        end = min(start + size, len(normalized))
        content = normalized[start:end].strip()
        if content:
            chunks.append(
                IngestedChunk(
                    chunk_index=index,
                    content=content,
                    token_count=estimate_token_count(content),
                )
            )
            index += 1
        if end >= len(normalized):
            break
        start += step

    return chunks
