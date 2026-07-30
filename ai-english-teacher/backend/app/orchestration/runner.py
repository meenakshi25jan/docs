"""High-level API for conversation orchestration."""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentInput, AgentOutput
from app.ai.openai_client import extract_teacher_response
from app.orchestration.graph import invoke_conversation_graph
from app.agents import AGENT_REGISTRY


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
    enabled = use_orchestration if use_orchestration is not None else True

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
    data: dict[str, Any] = dict(final.get("agent_output", {}))
    if not data.get("response"):
        data["response"] = extract_teacher_response(data) or "Could you tell me more about that?"

    metadata = dict(final.get("metadata", {}))
    metadata.update({
        "trace_id": final.get("trace_id"),
        "agent_path": final.get("agent_path", []),
        "intent": final.get("intent"),
        "next_agent": final.get("next_agent"),
        "rag_chunks": final.get("rag_chunks", []),
        "orchestration": True,
    })
    return AgentOutput(data=data, metadata=metadata)
