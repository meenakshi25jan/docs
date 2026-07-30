"""LangGraph conversation pipeline — Wave 1 foundation orchestration."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.base import AgentInput, AgentOutput
from app.agents import AGENT_REGISTRY
from app.ai.openai_client import extract_teacher_response
from app.orchestration.context_manager import build_enriched_context
from app.orchestration.conversation_agent import ConversationAgent
from app.orchestration.cost_router import select_model_hint
from app.orchestration.moderation import moderate_text
from app.orchestration.orchestrator import classify_intent
from app.orchestration.rag_agent import retrieve
from app.orchestration.session_manager import merge_session
from app.orchestration.state import ConversationState

logger = logging.getLogger(__name__)

_conversation_agent = ConversationAgent()


def _append_path(state: ConversationState, agent: str) -> list[str]:
    path = list(state.get("agent_path", []))
    path.append(agent)
    return path


async def node_moderate_input(state: ConversationState) -> dict[str, Any]:
    result = moderate_text(state.get("message", ""), direction="input")
    if not result["safe"]:
        return {
            "blocked": True,
            "block_reason": result.get("message"),
            "agent_output": {"response": result.get("message", "Let's keep our chat appropriate.")},
            "agent_path": _append_path(state, "ModerationAgent"),
            "next_agent": "blocked",
        }
    return {"blocked": False, "agent_path": _append_path(state, "ModerationAgent")}


async def node_orchestrate(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    intent, next_agent = classify_intent(state.get("message", ""), state.get("scenario", ""))
    model_hint = select_model_hint(intent, state.get("message", ""))
    return {
        "intent": intent,
        "next_agent": next_agent,
        "model_hint": model_hint,
        "agent_path": _append_path(state, "OrchestratorAgent"),
    }


async def node_recall_memory(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    from app.services.memory_intelligence_service import MemoryIntelligenceService

    service = MemoryIntelligenceService()
    bundle = await service.build_bundle_with_session_recall(
        learner_id=state["learner_id"],
        tenant_id=state.get("tenant_id"),
        session_id=state["session_id"],
        conversation_id=state["session_id"],
        message_history=state.get("message_history", []),
        query=state.get("message"),
    )
    router_dict = bundle.to_router_dict()
    return {
        "memories": router_dict.get("conversation", []),
        "recent_errors": router_dict.get("recent_errors", []),
        "recurring_mistakes": router_dict.get("recurring_mistakes", []),
        "lesson_reflections": router_dict.get("lesson_reflections", []),
        "memory_summary": router_dict.get("memory_summary", ""),
        "memory_bundle": router_dict,
        "agent_path": _append_path(state, "MemoryAgent"),
    }


async def node_rag(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService

    ki = KnowledgeIntelligenceService()
    recurring = state.get("recurring_mistakes", [])
    grounding = await ki.build_grounding_context(
        message=state.get("message", ""),
        scenario=state.get("scenario", ""),
        cefr_level=state.get("cefr_level", "B1"),
        recurring_mistakes=recurring,
        tenant_id=state.get("tenant_id"),
        retrieve=True,
    )
    chunks = []
    for i, expl in enumerate(grounding.explanations[:3]):
        src = grounding.sources[i] if i < len(grounding.sources) else "curriculum"
        chunks.append(
            {
                "text": expl,
                "source": src,
                "topic": grounding.lesson_id or "",
                "score": 1.0,
                "method": grounding.validation.retrieval_method,
            }
        )
    if not chunks and state.get("message"):
        from app.orchestration.rag_agent import retrieve

        chunks = await retrieve(
            state.get("message", ""),
            scenario=state.get("scenario", ""),
            top_k=3,
            tenant_id=state.get("tenant_id"),
        )
    return {
        "rag_chunks": chunks,
        "grounding_context": grounding.compact_text,
        "knowledge_grounding": ki.to_metadata(grounding).model_dump(),
        "agent_path": _append_path(state, "RAGAgent"),
    }


async def node_build_context(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    enriched = build_enriched_context(
        scenario=state.get("scenario", "general_conversation"),
        cefr_level=state.get("cefr_level", "B1"),
        message=state.get("message", ""),
        message_history=state.get("message_history", []),
        recent_errors=state.get("recent_errors", []),
        memories=state.get("memories", []),
        rag_chunks=state.get("rag_chunks", []),
        intent=state.get("intent", "conversation"),
        persona_id=state.get("persona_id"),
        teaching_instruction=state.get("teaching_instruction"),
        teaching_mode=state.get("teaching_mode"),
        voice_analysis=state.get("voice_analysis"),
    )
    enriched["recurring_mistakes"] = state.get("recurring_mistakes", [])
    enriched["lesson_reflections"] = state.get("lesson_reflections", [])
    enriched["memory_summary"] = state.get("memory_summary", "")
    enriched["memory_bundle"] = state.get("memory_bundle", {})
    enriched["grounding_context"] = state.get("grounding_context", "")
    enriched["knowledge_grounding"] = state.get("knowledge_grounding", {})
    if enriched.get("grounding_context"):
        from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService

        enriched["teaching_instruction"] = KnowledgeIntelligenceService().inject_teaching_instruction(
            enriched.get("teaching_instruction", ""), enriched["grounding_context"]
        )
    if enriched.get("memory_summary"):
        enriched["teaching_instruction"] = (
            f"{enriched.get('teaching_instruction', '')}\n"
            f"Learner memory: {enriched['memory_summary'][:800]}"
        ).strip()
    from app.orchestration.teacher_brain.teacher_brain_service import TeacherBrainService

    service = TeacherBrainService()
    enriched = await service.enrich_context_for_langgraph(
        enriched,
        learner_id=state.get("learner_id", ""),
        tenant_id=state.get("tenant_id"),
        message=state.get("message", ""),
        scenario=state.get("scenario", "general_conversation"),
        persona_id=state.get("persona_id") or "conversation_partner",
        intent=state.get("intent", "conversation"),
        is_voice_turn=bool(state.get("voice_analysis")),
        teaching_mode=state.get("teaching_mode"),
        voice_analysis=state.get("voice_analysis"),
    )
    return {"enriched_context": enriched, "agent_path": _append_path(state, "ContextManagerAgent")}


async def _run_agent(agent_key: str, state: ConversationState) -> AgentOutput:
    ctx = dict(state.get("enriched_context", {}))
    agent_input = AgentInput(
        learner_id=state.get("learner_id"),
        tenant_id=state.get("tenant_id"),
        context=ctx,
    )
    if agent_key == "ConversationAgent":
        return await _conversation_agent.execute(agent_input)
    if agent_key == "TeacherAgent":
        return await AGENT_REGISTRY["teacher"].execute(agent_input)
    return await AGENT_REGISTRY["teacher"].execute(agent_input)


async def node_execute_agent(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    next_agent = state.get("next_agent", "TeacherAgent")
    started = time.perf_counter()
    output = await _run_agent(next_agent, state)
    latency_ms = int((time.perf_counter() - started) * 1000)
    data = dict(output.data)
    data.setdefault("response", extract_teacher_response(data))
    teacher_brain = state.get("enriched_context", {}).get("teacher_brain")
    metadata = {
        "agent": next_agent,
        "intent": state.get("intent"),
        "model_hint": state.get("model_hint"),
        "latency_ms": latency_ms,
        "rag_chunk_count": len(state.get("rag_chunks", [])),
    }
    if teacher_brain:
        data["teacher_brain"] = teacher_brain
        metadata["teacher_brain"] = teacher_brain
    return {
        "agent_output": data,
        "agent_path": _append_path(state, next_agent),
        "metadata": metadata,
    }


async def node_store_memory(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    output = state.get("agent_output", {})
    from app.services.memory_intelligence_service import MemoryIntelligenceService

    await MemoryIntelligenceService().write_after_teacher_turn(
        session_id=state["session_id"],
        learner_id=state["learner_id"],
        tenant_id=state.get("tenant_id"),
        agent_output=output,
        conversation_id=state["session_id"],
    )
    session = await merge_session(state["session_id"], {})
    await merge_session(state["session_id"], {
        "last_intent": state.get("intent"),
        "last_agent": state.get("next_agent"),
        "turn_count": session.get("turn_count", 0) + 1,
    })
    return {"agent_path": _append_path(state, "MemoryAgent:store")}


async def node_moderate_output(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    response = extract_teacher_response(state.get("agent_output", {})) or ""
    result = moderate_text(response, direction="output")
    if not result["safe"]:
        return {
            "agent_output": {"response": "Let me rephrase that in a way that's appropriate for our lesson."},
            "agent_path": _append_path(state, "ModerationAgent:output"),
        }
    return {"agent_path": _append_path(state, "ModerationAgent:output")}


def _route_after_input(state: ConversationState) -> str:
    if state.get("blocked"):
        return "end"
    return "orchestrate"


def build_conversation_graph():
    graph = StateGraph(ConversationState)
    graph.add_node("moderate_input", node_moderate_input)
    graph.add_node("orchestrate", node_orchestrate)
    graph.add_node("recall_memory", node_recall_memory)
    graph.add_node("rag", node_rag)
    graph.add_node("build_context", node_build_context)
    graph.add_node("execute_agent", node_execute_agent)
    graph.add_node("store_memory", node_store_memory)
    graph.add_node("moderate_output", node_moderate_output)

    graph.set_entry_point("moderate_input")
    graph.add_conditional_edges("moderate_input", _route_after_input, {"orchestrate": "orchestrate", "end": END})
    graph.add_edge("orchestrate", "recall_memory")
    graph.add_edge("recall_memory", "rag")
    graph.add_edge("rag", "build_context")
    graph.add_edge("build_context", "execute_agent")
    graph.add_edge("execute_agent", "store_memory")
    graph.add_edge("store_memory", "moderate_output")
    graph.add_edge("moderate_output", END)
    return graph.compile()


_compiled_graph = None


def get_conversation_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_conversation_graph()
    return _compiled_graph


async def invoke_conversation_graph(
    *,
    session_id: str,
    learner_id: str,
    tenant_id: str | None,
    scenario: str,
    cefr_level: str,
    message: str,
    message_history: list[dict[str, str]],
    persona_id: str | None = None,
    teaching_instruction: str | None = None,
    teaching_mode: str | None = None,
    voice_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trace_id = str(uuid.uuid4())
    initial: ConversationState = {
        "session_id": session_id,
        "learner_id": learner_id,
        "tenant_id": tenant_id,
        "scenario": scenario,
        "cefr_level": cefr_level,
        "message": message,
        "message_history": message_history,
        "agent_path": [],
        "trace_id": trace_id,
        "blocked": False,
        "persona_id": persona_id,
        "teaching_instruction": teaching_instruction,
        "teaching_mode": teaching_mode,
        "voice_analysis": voice_analysis,
    }
    graph = get_conversation_graph()
    final = await graph.ainvoke(initial)
    logger.info(
        "orchestration.complete",
        extra={
            "trace_id": trace_id,
            "agent_path": final.get("agent_path", []),
            "intent": final.get("intent"),
        },
    )
    return final
