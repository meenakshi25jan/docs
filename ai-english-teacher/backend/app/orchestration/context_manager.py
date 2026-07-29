"""Context Manager Agent — merge history, profile, memory, and RAG into agent context."""

from __future__ import annotations

from typing import Any


def build_enriched_context(
    *,
    scenario: str,
    cefr_level: str,
    message: str,
    message_history: list[dict[str, str]],
    recent_errors: list[str],
    memories: list[dict[str, Any]],
    rag_chunks: list[dict[str, Any]],
    intent: str,
) -> dict[str, Any]:
    error_texts = list(recent_errors)
    for mem in memories:
        if mem.get("type") == "mistake" and mem.get("text"):
            error_texts.append(str(mem["text"]))
    error_texts = list(dict.fromkeys(error_texts))[:10]

    knowledge_lines = [f"- [{c.get('source', 'curriculum')}] {c.get('text', '')}" for c in rag_chunks[:3]]

    return {
        "scenario": scenario,
        "cefr_level": cefr_level,
        "message": message,
        "message_history": message_history,
        "recent_errors": error_texts,
        "intent": intent,
        "knowledge_context": "\n".join(knowledge_lines) if knowledge_lines else "",
        "memory_count": len(memories),
    }
