"""Memory router — orchestrator selects which memories to query."""

from __future__ import annotations

from enum import Enum
from typing import Any

from app.cognitive.events import IntentType
from app.cognitive.tool_router import ToolName
from app.services.memory_intelligence_service import MemoryIntelligenceService


class MemoryDomain(str, Enum):
    CONVERSATION = "conversation_memory"
    LEARNING = "learning_memory"
    STUDENT_PROFILE = "student_profile"
    CURRICULUM = "curriculum_memory"
    KNOWLEDGE_BASE = "knowledge_base"
    WEB = "web_cache"


MEMORY_FOR_TOOL: dict[ToolName, list[MemoryDomain]] = {
    ToolName.CONVERSATION_MEMORY: [MemoryDomain.CONVERSATION],
    ToolName.LEARNING_MEMORY: [MemoryDomain.LEARNING],
    ToolName.STUDENT_PROFILE: [MemoryDomain.STUDENT_PROFILE],
    ToolName.CURRICULUM_KB: [MemoryDomain.KNOWLEDGE_BASE, MemoryDomain.CURRICULUM],
    ToolName.RAG_SCENARIO: [MemoryDomain.KNOWLEDGE_BASE],
    ToolName.WEB_SEARCH: [MemoryDomain.WEB],
}


async def route_memories(
    *,
    tools: list[ToolName],
    session_id: str,
    learner_id: str,
    tenant_id: str | None,
    query: str | None,
    student_slice: dict[str, Any],
    message_history: list[dict[str, str]] | None = None,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    domains: set[MemoryDomain] = set()
    for tool in tools:
        for domain in MEMORY_FOR_TOOL.get(tool, []):
            domains.add(domain)

    result: dict[str, Any] = {
        "domains_queried": [d.value for d in domains],
        "conversation": [],
        "learning_mistakes": [],
        "recurring_mistakes": [],
        "student_profile": {},
        "knowledge": [],
        "lesson_reflections": [],
        "teacher_brain_decisions": [],
        "learning_events": [],
        "recent_turns": [],
        "preferences": {},
        "skill_weaknesses": [],
        "memory_summary": "",
        "metadata": {},
    }

    needs_memory = (
        MemoryDomain.CONVERSATION in domains
        or MemoryDomain.LEARNING in domains
        or MemoryDomain.STUDENT_PROFILE in domains
    )

    if needs_memory:
        service = MemoryIntelligenceService()
        bundle = await service.build_bundle_with_session_recall(
            learner_id=learner_id,
            tenant_id=tenant_id,
            session_id=session_id,
            conversation_id=conversation_id or session_id,
            message_history=message_history,
            query=query,
        )
        router_dict = bundle.to_router_dict()
        result.update(router_dict)

    if MemoryDomain.STUDENT_PROFILE in domains:
        profile_prefs = result.get("preferences") or {}
        result["student_profile"] = {
            "cefr_level": student_slice.get("cefr_level"),
            "challenge_level": student_slice.get("challenge_level"),
            "preferences": profile_prefs or student_slice.get("preferences", {}),
            "goals": student_slice.get("goals", []),
            "skill_weaknesses": result.get("skill_weaknesses", []),
        }

    return result
