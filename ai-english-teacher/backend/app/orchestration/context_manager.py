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
    persona_id: str | None = None,
    teaching_instruction: str | None = None,
    teaching_mode: str | None = None,
    voice_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error_texts = list(recent_errors)
    for mem in memories:
        if mem.get("type") == "mistake" and mem.get("text"):
            error_texts.append(str(mem["text"]))
    error_texts = list(dict.fromkeys(error_texts))[:10]

    knowledge_lines = [f"- [{c.get('source', 'curriculum')}] {c.get('text', '')}" for c in rag_chunks[:3]]

    voice_summary = ""
    if voice_analysis:
        voice_summary = (
            f"Fluency {voice_analysis.get('fluency', '—')}, "
            f"Pronunciation {voice_analysis.get('pronunciation', '—')}, "
            f"Grammar {voice_analysis.get('grammar_score', '—')}"
        )

    return {
        "scenario": scenario,
        "cefr_level": cefr_level,
        "message": message,
        "message_history": message_history,
        "recent_errors": error_texts,
        "intent": intent,
        "knowledge_context": "\n".join(knowledge_lines) if knowledge_lines else "",
        "memory_count": len(memories),
        "persona_id": persona_id or "conversation_partner",
        "teaching_instruction": teaching_instruction or "",
        "teaching_mode": teaching_mode or "none",
        "voice_summary": voice_summary,
    }
