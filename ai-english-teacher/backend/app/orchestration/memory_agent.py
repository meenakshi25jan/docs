"""Memory Agent — store and recall learner mistakes, preferences, and weak areas."""

from __future__ import annotations

from typing import Any

from app.orchestration.session_manager import load_session, merge_session

MAX_MEMORIES = 50


async def recall_memories(session_id: str, learner_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    session = await load_session(session_id)
    memories: list[dict[str, Any]] = list(session.get("memories", []))
    recent_errors: list[str] = list(session.get("recent_errors", []))
    for mem in memories:
        if mem.get("type") == "mistake" and mem.get("text"):
            text = str(mem["text"])
            if text not in recent_errors:
                recent_errors.append(text)
    return memories[-10:], recent_errors[-10:]


async def store_memory(
    session_id: str,
    learner_id: str,
    memory_type: str,
    text: str,
    weight: float = 0.8,
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


async def store_from_teacher_output(
    session_id: str,
    learner_id: str,
    output: dict[str, Any],
) -> None:
    for correction in output.get("grammar_corrections", [])[:5]:
        if isinstance(correction, dict):
            text = correction.get("correction") or correction.get("text") or ""
        else:
            text = str(correction)
        await store_memory(session_id, learner_id, "mistake", text)
    for word in output.get("vocabulary_introduced", [])[:3]:
        await store_memory(session_id, learner_id, "vocabulary", str(word), weight=0.5)
