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
from app.orchestration.memory_agent import recall_memories, store_from_teacher_output
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
    memories, recent_errors = await recall_memories(
        state["session_id"],
        state["learner_id"],
        tenant_id=state.get("tenant_id"),
        query=state.get("message"),
    )
    return {
        "memories": memories,
        "recent_errors": recent_errors,
        "agent_path": _append_path(state, "MemoryAgent"),
    }


async def node_rag(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    chunks = await retrieve(
        state.get("message", ""),
        scenario=state.get("scenario", ""),
        top_k=3,
        tenant_id=state.get("tenant_id"),
    )
    return {"rag_chunks": chunks, "agent_path": _append_path(state, "RAGAgent")}


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
    return {
        "agent_output": data,
        "agent_path": _append_path(state, next_agent),
        "metadata": {
            "agent": next_agent,
            "intent": state.get("intent"),
            "model_hint": state.get("model_hint"),
            "latency_ms": latency_ms,
            "rag_chunk_count": len(state.get("rag_chunks", [])),
        },
    }


async def node_store_memory(state: ConversationState) -> dict[str, Any]:
    if state.get("blocked"):
        return {}
    output = state.get("agent_output", {})
    await store_from_teacher_output(
        state["session_id"],
        state["learner_id"],
        output,
        tenant_id=state.get("tenant_id"),
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
