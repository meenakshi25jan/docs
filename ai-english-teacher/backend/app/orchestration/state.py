"""Shared state for the conversation LangGraph."""

from typing import Any, TypedDict


class ConversationState(TypedDict, total=False):
    session_id: str
    learner_id: str
    tenant_id: str | None
    scenario: str
    cefr_level: str
    message: str
    message_history: list[dict[str, str]]
    intent: str
    next_agent: str
    recent_errors: list[str]
    memories: list[dict[str, Any]]
    rag_chunks: list[dict[str, Any]]
    enriched_context: dict[str, Any]
    agent_output: dict[str, Any]
    agent_path: list[str]
    trace_id: str
    blocked: bool
    block_reason: str | None
    model_hint: str | None
    metadata: dict[str, Any]
    persona_id: str | None
    teaching_instruction: str | None
    teaching_mode: str | None
    voice_analysis: dict[str, Any] | None
