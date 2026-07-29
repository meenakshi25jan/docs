"""RAG Agent — pgvector retrieval with keyword fallback."""

from __future__ import annotations

from typing import Any

from app.services.knowledge_store import retrieve_knowledge


async def retrieve(
    query: str,
    scenario: str = "",
    top_k: int = 3,
    tenant_id: str | None = None,
) -> list[dict[str, Any]]:
    return await retrieve_knowledge(
        query,
        scenario=scenario,
        tenant_id=tenant_id,
        top_k=top_k,
    )
