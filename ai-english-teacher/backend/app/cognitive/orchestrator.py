"""Cognitive Orchestrator — Layer 1 executive controller."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from app.ai.openai_client import extract_teacher_response
from app.cognitive.agent_planner import plan_agents, AgentName
from app.cognitive.context_builder import build_teacher_context
from app.cognitive.events import CognitiveEvent, EventType, IntentType
from app.cognitive.failure_recovery import with_fallback
from app.cognitive.intent_classifier import classify_intent
from app.cognitive.llm_router import select_model_tier
from app.cognitive.memory_router import route_memories
from app.cognitive.observability import CognitiveTrace, StepTimer
from app.cognitive.policy_engine import evaluate_policy
from app.cognitive.session_lifecycle import handle_lifecycle_event, persist_cognitive_state
from app.cognitive.state import CognitiveState
from app.cognitive.tool_executor import (
    execute_agents,
    execute_teacher_brain,
    execute_tool,
    execute_voice_coaches,
)
from app.cognitive.tool_router import select_tools, tools_to_skip, ToolName
from app.cognitive.web_gateway import needs_external_knowledge
from app.cognitive.workflow_manager import get_workflow, WorkflowStep
from app.orchestration.moderation import moderate_text
from app.orchestration.session_manager import load_session
from app.orchestration.personas import get_persona

logger = logging.getLogger(__name__)


class CognitiveOrchestrator:
    """
    Executive controller — does not teach; coordinates agents, tools, memory, and workflows.
    """

    async def process_event(self, event: CognitiveEvent) -> dict[str, Any]:
        if event.type in (
            EventType.LESSON_STARTED,
            EventType.LESSON_PAUSED,
            EventType.LESSON_RESUMED,
            EventType.LESSON_FINISHED,
            EventType.SESSION_RECONNECT,
            EventType.NETWORK_LOST,
        ):
            session = await handle_lifecycle_event(event.type, event.session_id, event.payload)
            return {"lifecycle": event.type.value, "session": session}

        if event.type == EventType.USER_SPOKE:
            return await self.process_turn(
                session_id=event.session_id,
                learner_id=event.learner_id,
                tenant_id=event.tenant_id,
                message=event.payload.get("message", ""),
                message_history=event.payload.get("message_history", []),
                scenario=event.payload.get("scenario", "general_conversation"),
                cefr_level=event.payload.get("cefr_level", "B1"),
                persona_id=event.payload.get("persona_id", "conversation_partner"),
                voice_payload=event.payload.get("voice"),
            )

        return {"status": "ignored", "event": event.type.value}

    async def process_turn(
        self,
        *,
        session_id: str,
        learner_id: str,
        tenant_id: str | None,
        message: str,
        message_history: list[dict[str, str]],
        scenario: str,
        cefr_level: str,
        persona_id: str = "conversation_partner",
        voice_payload: dict[str, Any] | None = None,
        precomputed_voice_analysis: dict[str, Any] | None = None,
        teaching_instruction: str | None = None,
        teaching_mode: str | None = None,
    ) -> dict[str, Any]:
        trace_id = str(uuid.uuid4())
        trace = CognitiveTrace(trace_id=trace_id)
        started = time.perf_counter()

        session_data = await load_session(session_id)
        state = CognitiveState.from_session_dict(
            session_data,
            scenario=scenario,
            cefr_level=cefr_level,
            persona_id=persona_id,
            message_history=message_history,
        )
        state.trace_id = trace_id
        state.voice.transcript = message

        if voice_payload:
            state.voice.duration_seconds = voice_payload.get("duration_seconds")
        if precomputed_voice_analysis:
            state.voice.voice_analysis = precomputed_voice_analysis
        if teaching_instruction:
            state.voice.teaching_instruction = teaching_instruction
        if teaching_mode:
            state.voice.teaching_mode = teaching_mode

        # --- Moderation ---
        with StepTimer(trace, "moderate_input") as _:
            mod = moderate_text(message, direction="input")
            if not mod["safe"]:
                return self._blocked_response(mod, trace, started)

        # --- Intent ---
        with StepTimer(trace, "intent_classify") as _:
            intent = classify_intent(message, scenario)
            state.conversation.last_intent = intent.value

        has_voice = bool(voice_payload or precomputed_voice_analysis or message)
        workflow = get_workflow(intent, has_voice=bool(precomputed_voice_analysis or voice_payload))

        # --- Tool route ---
        with StepTimer(trace, "tool_route") as _:
            web_needed = needs_external_knowledge(intent, message)
            tools = select_tools(intent, has_voice=bool(precomputed_voice_analysis), web_allowed=web_needed)
            policy = evaluate_policy(tenant_id=tenant_id, tools=tools)
            if not policy.web_search_allowed:
                tools = [t for t in tools if t != ToolName.WEB_SEARCH]
            skipped_tools = tools_to_skip(intent, tools)

        # --- Memory route ---
        memory_bundle: dict[str, Any] = {}
        with StepTimer(trace, "memory_route") as _:
            memory_bundle, used_fallback = await with_fallback(
                lambda: route_memories(
                    tools=tools,
                    session_id=session_id,
                    learner_id=learner_id,
                    tenant_id=tenant_id,
                    query=message,
                    student_slice={
                        "cefr_level": cefr_level,
                        "challenge_level": state.student.challenge_level,
                        "preferences": state.student.preferences,
                        "goals": state.student.goals,
                    },
                    message_history=message_history,
                    conversation_id=session_id,
                ),
                lambda: {"conversation": [], "learning_mistakes": [], "recurring_mistakes": []},
                label="memory_route",
            )
            state.memory_refs = memory_bundle

        # --- Agent plan ---
        with StepTimer(trace, "agent_plan") as _:
            agent_plan = plan_agents(intent, tools)

        coach_briefs: dict[str, Any] = {}

        # --- Workflow steps ---
        for step in workflow.steps:
            if step == WorkflowStep.STT:
                continue  # STT handled upstream (client or voice_turn)

            if step == WorkflowStep.VOICE_COACHES and not precomputed_voice_analysis:
                with StepTimer(trace, "voice_coaches") as _:
                    coach_result, fb = await with_fallback(
                        lambda: execute_voice_coaches(
                            state,
                            learner_id=learner_id,
                            tenant_id=tenant_id,
                            audio_metrics=(voice_payload or {}).get("audio_metrics"),
                        ),
                        lambda: {"coach_briefs": {}, "voice_analysis": None},
                        label="voice_coaches",
                    )
                    coach_briefs = coach_result.get("coach_briefs", {})
                    if coach_result.get("voice_analysis"):
                        state.voice.voice_analysis = coach_result["voice_analysis"]

            if step == WorkflowStep.TEACHING_DECISION and precomputed_voice_analysis:
                coach_briefs = (precomputed_voice_analysis.get("details") or {})

            if step == WorkflowStep.WEB_GATEWAY and web_needed:
                with StepTimer(trace, "web_gateway") as _:
                    await execute_tool(
                        ToolName.WEB_SEARCH,
                        state=state,
                        learner_id=learner_id,
                        tenant_id=tenant_id,
                        message=message,
                        trace=trace,
                    )

            if step == WorkflowStep.EXECUTE_TOOLS:
                with StepTimer(trace, "execute_tools") as _:
                    partial_ctx = {
                        "message": message,
                        "cefr_level": cefr_level,
                        "recent_errors": memory_bundle.get("learning_mistakes", []),
                    }
                    tool_agent_results = await execute_agents(
                        [a for a in agent_plan.agents if a != AgentName.TEACHER_BRAIN],
                        partial_ctx,
                        learner_id=learner_id,
                        tenant_id=tenant_id,
                        trace=trace,
                    )
                    state.tool_results.update(tool_agent_results)

        if precomputed_voice_analysis and not coach_briefs:
            coach_briefs = precomputed_voice_analysis.get("details", {})

        # --- Context build ---
        with StepTimer(trace, "context_build") as _:
            teacher_context = await build_teacher_context(
                state,
                intent=intent,
                agent_plan=agent_plan,
                memory_bundle=memory_bundle,
                tools=tools,
                coach_briefs=coach_briefs,
            )
            model_tier = select_model_tier(intent, agent_plan.agents, message, policy.model_tier)
            teacher_context["model_hint"] = model_tier

        # --- Teacher Brain ---
        with StepTimer(trace, "teacher_brain") as _:
            brain_output = await execute_teacher_brain(
                teacher_context,
                learner_id=learner_id,
                tenant_id=tenant_id,
                intent=intent.value,
                trace=trace,
            )

        response_text = extract_teacher_response(brain_output) or "Could you tell me more about that?"

        # --- Post-turn memory write (Teacher Brain + teacher output) ---
        try:
            from app.services.memory_intelligence_service import MemoryIntelligenceService

            await MemoryIntelligenceService().write_after_teacher_turn(
                session_id=session_id,
                learner_id=learner_id,
                tenant_id=tenant_id,
                agent_output=brain_output,
                conversation_id=session_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.post_turn_write_failed", extra={"error": str(exc)})

        # --- Output moderation ---
        with StepTimer(trace, "moderate_output") as _:
            out_mod = moderate_text(response_text, direction="output")
            if not out_mod["safe"]:
                response_text = "Let me rephrase that in a way that's appropriate for our lesson."

        # --- Apply difficulty adjustment ---
        adj = brain_output.get("difficulty_adjustment")
        if adj == "increase":
            state.student.challenge_level = min(100, state.student.challenge_level + 5)
        elif adj == "decrease":
            state.student.challenge_level = max(0, state.student.challenge_level - 5)

        state.session.turn_count += 1
        await persist_cognitive_state(session_id, state)

        trace.total_latency_ms = int((time.perf_counter() - started) * 1000)

        memory_meta = {
            "recurring_mistakes_count": len(memory_bundle.get("recurring_mistakes", [])),
            "reflections_available": bool(memory_bundle.get("lesson_reflections")),
            "memory_summary_available": bool(memory_bundle.get("memory_summary")),
        }

        return {
            "response": response_text,
            "intent": intent.value,
            "workflow": workflow.name,
            "tools_invoked": [t.value for t in tools],
            "tools_skipped": skipped_tools,
            "agents_invoked": [a.value for a in agent_plan.agents],
            "agents_skipped": agent_plan.skipped,
            "model_tier": model_tier,
            "teaching_mode": state.voice.teaching_mode,
            "voice_analysis": state.voice.voice_analysis,
            "agent_output": brain_output,
            "teacher_brain": brain_output.get("teacher_brain"),
            "memory": memory_meta,
            "cognitive_trace": trace.to_dict(),
            "memory_domains": memory_bundle.get("domains_queried", []),
        }

    def _blocked_response(
        mod: dict[str, Any],
        trace: CognitiveTrace,
        started: float,
    ) -> dict[str, Any]:
        trace.total_latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "response": mod.get("message", "Let's keep our chat appropriate."),
            "blocked": True,
            "cognitive_trace": trace.to_dict(),
        }


_default_orchestrator = CognitiveOrchestrator()


async def process_cognitive_turn(
    *,
    session_id: str,
    learner_id: str,
    tenant_id: str | None,
    message: str,
    message_history: list[dict[str, str]],
    scenario: str,
    cefr_level: str,
    persona_id: str = "conversation_partner",
    voice_payload: dict[str, Any] | None = None,
    precomputed_voice_analysis: dict[str, Any] | None = None,
    teaching_instruction: str | None = None,
    teaching_mode: str | None = None,
) -> dict[str, Any]:
    return await _default_orchestrator.process_turn(
        session_id=session_id,
        learner_id=learner_id,
        tenant_id=tenant_id,
        message=message,
        message_history=message_history,
        scenario=scenario,
        cefr_level=cefr_level,
        persona_id=persona_id,
        voice_payload=voice_payload,
        precomputed_voice_analysis=precomputed_voice_analysis,
        teaching_instruction=teaching_instruction,
        teaching_mode=teaching_mode,
    )
