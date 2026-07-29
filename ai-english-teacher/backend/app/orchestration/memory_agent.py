"""Memory Agent — Redis session + PostgreSQL long-term memory."""

from __future__ import annotations

from typing import Any

from app.orchestration.session_manager import load_session, merge_session
from app.services.memory_store import persist_mistake, persist_preference, recall_learner_memories

MAX_MEMORIES = 50


async def recall_memories(
    session_id: str,
    learner_id: str,
    *,
    tenant_id: str | None = None,
    query: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    pg_memories, pg_errors = await recall_learner_memories(
        learner_id,
        tenant_id=tenant_id,
        query=query,
    )

    session = await load_session(session_id)
    session_memories: list[dict[str, Any]] = list(session.get("memories", []))
    session_errors: list[str] = list(session.get("recent_errors", []))

    merged_memories = {m.get("text", ""): m for m in pg_memories + session_memories if m.get("text")}
    memories = list(merged_memories.values())[-10:]
    recent_errors = list(dict.fromkeys(pg_errors + session_errors))[:10]
    return memories, recent_errors


async def store_memory(
    session_id: str,
    learner_id: str,
    memory_type: str,
    text: str,
    weight: float = 0.8,
    *,
    tenant_id: str | None = None,
    correction: str | None = None,
) -> None:
    if not text.strip():
        return

    session = await load_session(session_id)
    memories: list[dict[str, Any]] = list(session.get("memories", []))
    memories.append({
        "type": memory_type,
        "text": text[:500],
        "weight": weight,
        "learner_id": learner_id,
    })
    if len(memories) > MAX_MEMORIES:
        memories = memories[-MAX_MEMORIES:]
    recent_errors = list(session.get("recent_errors", []))
    if memory_type == "mistake" and text not in recent_errors:
        recent_errors.append(text[:200])
        recent_errors = recent_errors[-10:]
    await merge_session(session_id, {"memories": memories, "recent_errors": recent_errors})

    if tenant_id:
        if memory_type == "mistake":
            await persist_mistake(
                learner_id=learner_id,
                tenant_id=tenant_id,
                error_text=text,
                correction=correction or text,
                category="grammar",
            )
        else:
            await persist_preference(
                learner_id=learner_id,
                tenant_id=tenant_id,
                memory_type=memory_type,
                content=text,
                weight=weight,
            )


async def store_from_teacher_output(
    session_id: str,
    learner_id: str,
    output: dict[str, Any],
    *,
    tenant_id: str | None = None,
) -> None:
    for correction in output.get("grammar_corrections", [])[:5]:
        if isinstance(correction, dict):
            text = correction.get("text") or correction.get("original") or ""
            fix = correction.get("correction") or correction.get("text") or ""
        else:
            text = str(correction)
            fix = text
        await store_memory(
            session_id, learner_id, "mistake", fix or text,
            tenant_id=tenant_id, correction=fix,
        )
    for word in output.get("vocabulary_introduced", [])[:3]:
        await store_memory(session_id, learner_id, "vocabulary", str(word), weight=0.5, tenant_id=tenant_id)
