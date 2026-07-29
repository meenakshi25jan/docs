"""pgvector-backed knowledge retrieval for RAG Agent."""

from __future__ import annotations

import logging
import re
from typing import Any
from uuid import UUID

from sqlalchemy import text

from app.core.database import get_session_factory
from app.services.curriculum_data import CURRICULUM_SNIPPETS, tokenize
from app.services.embeddings import embed_text, embedding_to_pgvector

logger = logging.getLogger(__name__)


async def _keyword_fallback(query: str, scenario: str, top_k: int) -> list[dict[str, Any]]:
    query_tokens = tokenize(query)
    if scenario:
        query_tokens |= tokenize(scenario.replace("_", " "))
    scored: list[tuple[float, dict[str, str]]] = []
    for snippet in CURRICULUM_SNIPPETS:
        topic_tokens = tokenize(snippet["topic"])
        text_tokens = tokenize(snippet["text"])
        overlap = len(query_tokens & (topic_tokens | text_tokens))
        if overlap > 0:
            scored.append((overlap / max(len(query_tokens), 1), snippet))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"text": s["text"], "source": s["source"], "topic": s["topic"], "score": round(score, 2), "method": "keyword"}
        for score, s in scored[:top_k]
    ]


async def retrieve_knowledge(
    query: str,
    *,
    scenario: str = "",
    tenant_id: str | None = None,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    if not query.strip():
        return []

    embedding = await embed_text(query)
    if not embedding:
        return await _keyword_fallback(query, scenario, top_k)

    try:
        factory = get_session_factory()
        async with factory() as session:
            vec = embedding_to_pgvector(embedding)
            tid = UUID(tenant_id) if tenant_id else None
            result = await session.execute(
                text("""
                    SELECT topic, source, content,
                           1 - (embedding <=> CAST(:embedding AS vector)) AS score
                    FROM knowledge_chunks
                    WHERE embedding IS NOT NULL
                      AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT :limit
                """),
                {"embedding": vec, "tenant_id": tid, "limit": top_k},
            )
            rows = result.fetchall()
            if rows:
                return [
                    {
                        "text": row.content,
                        "source": row.source,
                        "topic": row.topic,
                        "score": round(float(row.score), 3),
                        "method": "pgvector",
                    }
                    for row in rows
                ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("knowledge_store.vector_search_failed", extra={"error": str(exc)})

    return await _keyword_fallback(query, scenario, top_k)
