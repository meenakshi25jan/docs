"""Memory router — orchestrator selects which memories to query."""

from __future__ import annotations

from enum import Enum
from typing import Any

from app.cognitive.events import IntentType
from app.cognitive.tool_router import ToolName
from app.orchestration.memory_agent import recall_memories
from app.services.memory_store import get_recurring_mistakes


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
    }

    if MemoryDomain.CONVERSATION in domains or MemoryDomain.LEARNING in domains:
        memories, recent_errors = await recall_memories(
            session_id,
            learner_id,
            tenant_id=tenant_id,
            query=query,
        )
        result["conversation"] = memories
        result["learning_mistakes"] = recent_errors

    if MemoryDomain.LEARNING in domains and tenant_id:
        result["recurring_mistakes"] = await get_recurring_mistakes(learner_id, tenant_id, limit=8)

    if MemoryDomain.STUDENT_PROFILE in domains:
        result["student_profile"] = {
            "cefr_level": student_slice.get("cefr_level"),
            "challenge_level": student_slice.get("challenge_level"),
            "preferences": student_slice.get("preferences", {}),
            "goals": student_slice.get("goals", []),
        }

    return result
