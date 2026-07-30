"""PostgreSQL-backed long-term memory for Memory Agent."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, text

from app.core.database import get_session_factory
from app.models.memory import ErrorTracking, LearnerMemory
from app.services.embeddings import embed_text, embedding_to_pgvector

logger = logging.getLogger(__name__)


async def recall_learner_memories(
    learner_id: str,
    *,
    tenant_id: str | None = None,
    query: str | None = None,
    limit: int = 10,
) -> tuple[list[dict[str, Any]], list[str]]:
    memories: list[dict[str, Any]] = []
    recent_errors: list[str] = []

    try:
        factory = get_session_factory()
        async with factory() as session:
            lid = UUID(learner_id)

            if query and await embed_text(query):
                embedding = await embed_text(query)
                if embedding:
                    vec = embedding_to_pgvector(embedding)
                    result = await session.execute(
                        text("""
                            SELECT error_text, correction, error_category,
                                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                            FROM error_tracking
                            WHERE learner_id = :learner_id AND embedding IS NOT NULL
                            ORDER BY embedding <=> CAST(:embedding AS vector)
                            LIMIT :limit
                        """),
                        {"embedding": vec, "learner_id": lid, "limit": limit},
                    )
                    for row in result.fetchall():
                        text_val = row.correction or row.error_text
                        memories.append({
                            "type": "mistake",
                            "text": text_val,
                            "category": row.error_category,
                            "weight": float(row.similarity),
                        })
                        recent_errors.append(text_val)

            if not memories:
                result = await session.scalars(
                    select(ErrorTracking)
                    .where(ErrorTracking.learner_id == lid)
                    .order_by(ErrorTracking.last_seen_at.desc())
                    .limit(limit)
                )
                for err in result.all():
                    text_val = err.correction or err.error_text
                    memories.append({
                        "type": "mistake",
                        "text": text_val,
                        "category": err.error_category,
                        "weight": 0.7,
                    })
                    recent_errors.append(text_val)

            pref_result = await session.scalars(
                select(LearnerMemory)
                .where(LearnerMemory.learner_id == lid)
                .order_by(LearnerMemory.updated_at.desc())
                .limit(5)
            )
            for pref in pref_result.all():
                memories.append({
                    "type": pref.memory_type,
                    "text": pref.content,
                    "weight": float(pref.weight or 0.5),
                })
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_store.recall_failed", extra={"error": str(exc)})

    recent_errors = list(dict.fromkeys(recent_errors))[:10]
    return memories[:limit], recent_errors


async def persist_mistake(
    *,
    learner_id: str,
    tenant_id: str,
    error_text: str,
    correction: str | None = None,
    category: str = "grammar",
) -> None:
    if not error_text.strip():
        return

    embedding = await embed_text(f"{error_text} {correction or ''}")

    try:
        factory = get_session_factory()
        async with factory() as session:
            lid = UUID(learner_id)
            tid = UUID(tenant_id)
            existing = await session.scalar(
                select(ErrorTracking).where(
                    ErrorTracking.learner_id == lid,
                    ErrorTracking.error_text == error_text[:500],
                )
            )
            if existing:
                existing.occurrence_count += 1
                if correction:
                    existing.correction = correction[:500]
            else:
                err = ErrorTracking(
                    tenant_id=tid,
                    learner_id=lid,
                    error_category=category,
                    error_type=category,
                    error_text=error_text[:500],
                    correction=(correction or error_text)[:500],
                )
                session.add(err)
                await session.flush()
                if embedding:
                    vec = embedding_to_pgvector(embedding)
                    await session.execute(
                        text("UPDATE error_tracking SET embedding = CAST(:vec AS vector) WHERE id = :id"),
                        {"vec": vec, "id": err.id},
                    )
            await session.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_store.persist_failed", extra={"error": str(exc)})


async def get_recurring_mistakes(
    learner_id: str,
    tenant_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return frequently repeated mistakes for lesson reports."""
    try:
        factory = get_session_factory()
        async with factory() as session:
            lid = UUID(learner_id)
            result = await session.scalars(
                select(ErrorTracking)
                .where(ErrorTracking.learner_id == lid)
                .order_by(ErrorTracking.occurrence_count.desc(), ErrorTracking.last_seen_at.desc())
                .limit(limit)
            )
            return [
                {
                    "error": err.error_text,
                    "correction": err.correction,
                    "category": err.error_category,
                    "count": err.occurrence_count,
                }
                for err in result.all()
            ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_store.recurring_failed", extra={"error": str(exc)})
        return []


async def persist_preference(
    *,
    learner_id: str,
    tenant_id: str,
    memory_type: str,
    content: str,
    weight: float = 0.5,
) -> None:
    if not content.strip():
        return
    try:
        factory = get_session_factory()
        async with factory() as session:
            session.add(LearnerMemory(
                tenant_id=UUID(tenant_id),
                learner_id=UUID(learner_id),
                memory_type=memory_type,
                content=content[:500],
                weight=weight,
            ))
            await session.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_store.preference_failed", extra={"error": str(exc)})
