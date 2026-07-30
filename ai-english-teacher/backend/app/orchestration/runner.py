"""High-level API for conversation orchestration."""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentInput, AgentOutput
from app.ai.openai_client import extract_teacher_response
from app.agents import AGENT_REGISTRY
from app.core.config import get_settings
from app.orchestration.graph import invoke_conversation_graph


async def run_conversation_turn(
    *,
    session_id: str,
    learner_id: str,
    tenant_id: str | None,
    scenario: str,
    cefr_level: str,
    message: str,
    message_history: list[dict[str, str]],
    use_orchestration: bool | None = None,
    persona_id: str | None = None,
    teaching_instruction: str | None = None,
    teaching_mode: str | None = None,
    voice_analysis: dict[str, Any] | None = None,
) -> AgentOutput:
    settings = get_settings()
    enabled = use_orchestration if use_orchestration is not None else True
    cognitive = getattr(settings, "COGNITIVE_ORCHESTRATION_ENABLED", True)

    if not enabled:
        output = await AGENT_REGISTRY["teacher"].execute(AgentInput(
            learner_id=learner_id,
            tenant_id=tenant_id,
            context={
                "scenario": scenario,
                "cefr_level": cefr_level,
                "message": message,
                "message_history": message_history,
            },
        ))
        return output

    if cognitive:
        from app.cognitive.orchestrator import process_cognitive_turn

        result = await process_cognitive_turn(
            session_id=session_id,
            learner_id=learner_id,
            tenant_id=tenant_id,
            message=message,
            message_history=message_history,
            scenario=scenario,
            cefr_level=cefr_level,
            persona_id=persona_id or "conversation_partner",
            precomputed_voice_analysis=voice_analysis,
            teaching_instruction=teaching_instruction,
            teaching_mode=teaching_mode,
        )
        data: dict[str, Any] = dict(result.get("agent_output", {}))
        if not data.get("response"):
            data["response"] = result.get("response") or extract_teacher_response(data) or "Could you tell me more?"

        metadata = {
            "trace_id": result.get("cognitive_trace", {}).get("trace_id"),
            "intent": result.get("intent"),
            "workflow": result.get("workflow"),
            "tools_invoked": result.get("tools_invoked"),
            "tools_skipped": result.get("tools_skipped"),
            "agents_invoked": result.get("agents_invoked"),
            "agents_skipped": result.get("agents_skipped"),
            "model_tier": result.get("model_tier"),
            "teaching_mode": result.get("teaching_mode"),
            "teacher_brain": result.get("teacher_brain"),
            "memory": result.get("memory"),
            "knowledge_grounding": result.get("knowledge_grounding"),
            "governance": result.get("governance"),
            "cognitive_trace": result.get("cognitive_trace"),
            "orchestration": "cognitive",
        }
        return AgentOutput(data=data, metadata=metadata)

    final = await invoke_conversation_graph(
        session_id=session_id,
        learner_id=learner_id,
        tenant_id=tenant_id,
        scenario=scenario,
        cefr_level=cefr_level,
        message=message,
        message_history=message_history,
        persona_id=persona_id,
        teaching_instruction=teaching_instruction,
        teaching_mode=teaching_mode,
        voice_analysis=voice_analysis,
    )
    data = dict(final.get("agent_output", {}))
    if not data.get("response"):
        data["response"] = extract_teacher_response(data) or "Could you tell me more about that?"

    metadata = dict(final.get("metadata", {}))
    memory_bundle = final.get("memory_bundle", {})
    metadata.update({
        "trace_id": final.get("trace_id"),
        "agent_path": final.get("agent_path", []),
        "intent": final.get("intent"),
        "next_agent": final.get("next_agent"),
        "rag_chunks": final.get("rag_chunks", []),
        "orchestration": "langgraph",
        "memory": {
            "recurring_mistakes_count": len(memory_bundle.get("recurring_mistakes", [])),
            "reflections_available": bool(memory_bundle.get("lesson_reflections")),
            "memory_summary_available": bool(memory_bundle.get("memory_summary")),
        },
        "knowledge_grounding": final.get("knowledge_grounding", {}),
    })
    try:
        from app.services.governance_service import GovernanceService

        enriched = final.get("enriched_context", {}) or {}
        gov = await GovernanceService().evaluate_turn_safe(
            learner_id=learner_id,
            tenant_id=tenant_id,
            trace_id=final.get("trace_id"),
            conversation_id=session_id,
            response=data.get("response") or extract_teacher_response(data) or "",
            intent=final.get("intent"),
            teacher_brain=enriched.get("teacher_brain") or data.get("teacher_brain"),
            agent_output=data,
            teaching_mode=final.get("teaching_mode"),
            teaching_instruction=enriched.get("teaching_instruction"),
            memory_meta=metadata.get("memory"),
            knowledge_grounding=metadata.get("knowledge_grounding"),
            tools_invoked=None,
        )
        if gov:
            metadata["governance"] = GovernanceService().to_api_metadata(gov)
    except Exception:  # noqa: BLE001
        pass
    return AgentOutput(data=data, metadata=metadata)
