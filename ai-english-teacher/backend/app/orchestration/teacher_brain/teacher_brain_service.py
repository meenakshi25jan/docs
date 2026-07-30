"""Teacher Brain v1 service — plan, enrich, delegate to TeacherAgent."""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.ai.openai_client import extract_teacher_response
from app.core.database import get_session_factory, set_tenant_context
from app.models import LearnerProfile
from app.orchestration.teacher_brain.error_detector import detect_errors
from app.orchestration.teacher_brain.intent_analyzer import analyze_intent
from app.orchestration.teacher_brain.prompt_templates import (
    build_error_summary_for_agent,
    build_teacher_brain_instruction,
)
from app.orchestration.teacher_brain.response_planner import plan_response
from app.orchestration.teacher_brain.schemas import (
    DetectedError,
    ResponsePlan,
    TeacherBrainInput,
    TeacherBrainOutput,
)
from app.orchestration.teacher_brain.teaching_strategy_selector import select_teaching_strategy
from app.schemas.student_intelligence import StudentSummaryResponse
from app.services.student_intelligence_service import get_summary

logger = logging.getLogger(__name__)


class TeacherBrainService:
    """Planning layer that enriches context and delegates response generation."""

    async def process_turn(
        self,
        input_data: TeacherBrainInput,
        *,
        agent_context: dict[str, Any],
        learner_id: str,
        tenant_id: str | None,
        use_conversation_agent: bool = False,
    ) -> TeacherBrainOutput:
        started = time.perf_counter()
        si_available = False
        si_summary = input_data.student_intelligence_summary

        if si_summary is None and input_data.learner_id:
            si_summary = await self._try_fetch_si_summary(
                input_data.learner_id,
                tenant_id=tenant_id,
            )
        if si_summary is not None:
            si_available = True

        message = (input_data.message or input_data.transcript or "").strip()
        intent = analyze_intent(
            message,
            scenario=input_data.scenario,
            persona_id=input_data.persona_id,
            orchestration_intent=input_data.orchestration_intent,
            is_voice_turn=input_data.is_voice_turn,
        )

        memory_bundle = input_data.memory_bundle or agent_context.get("memory_bundle")
        errors = detect_errors(
            message,
            voice_analysis=input_data.voice_analysis or agent_context.get("voice_analysis"),
            student_intelligence_summary=si_summary,
            memory_bundle=memory_bundle,
        )

        skill_focus = None
        si_weakest = None
        si_recommended = None
        if si_summary:
            si_weakest = si_summary.weakest_skill
            si_recommended = si_summary.recommended_next_focus
            skill_focus = si_weakest

        strategy = select_teaching_strategy(
            intent,
            errors,
            teaching_mode=input_data.teaching_mode,
            persona_id=input_data.persona_id,
            scenario=input_data.scenario,
            student_intelligence_summary=si_summary,
        )

        plan = plan_response(
            intent,
            strategy,
            errors,
            teaching_mode=input_data.teaching_mode,
            skill_focus=skill_focus,
            is_voice_turn=input_data.is_voice_turn,
        )

        correction_mode = input_data.teaching_mode or "none"

        enriched = dict(agent_context)
        brain_instruction = build_teacher_brain_instruction(
            plan,
            strategy,
            si_focus=si_recommended,
            si_weakest=si_weakest,
        )
        existing_instruction = enriched.get("teaching_instruction", "") or input_data.teaching_instruction or ""
        enriched["teaching_instruction"] = f"{existing_instruction}\n{brain_instruction}".strip()
        enriched["teacher_brain_skill_focus"] = plan.skill_focus
        enriched["teacher_brain_strategy"] = strategy
        enriched["recent_errors"] = list(dict.fromkeys(
            enriched.get("recent_errors", []) + build_error_summary_for_agent(errors).split("; ")
        ))[:10]
        if errors:
            enriched["error_summary"] = build_error_summary_for_agent(errors)

        used_fallback = False
        agent_output: dict[str, Any] = {}
        teacher_response = ""

        try:
            from app.orchestration.conversation_agent import ConversationAgent

            if use_conversation_agent:
                out = await ConversationAgent().execute(AgentInput(
                    learner_id=learner_id,
                    tenant_id=tenant_id,
                    context=enriched,
                ))
            else:
                out = await AGENT_REGISTRY["teacher"].execute(AgentInput(
                    learner_id=learner_id,
                    tenant_id=tenant_id,
                    context=enriched,
                ))
            agent_output = dict(out.data)
            teacher_response = extract_teacher_response(agent_output) or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("TeacherBrain agent failed: %s", exc)
            used_fallback = True
            teacher_response = self._deterministic_fallback(message, errors, plan)
            agent_output = {"response": teacher_response, "grammar_corrections": []}

        if not teacher_response:
            used_fallback = True
            teacher_response = self._deterministic_fallback(message, errors, plan)
            agent_output.setdefault("response", teacher_response)

        planning_ms = int((time.perf_counter() - started) * 1000)

        output = TeacherBrainOutput(
            intent=intent.intent,
            detected_errors=errors,
            teaching_strategy=strategy,
            response_plan=plan,
            teacher_response=teacher_response,
            correction_mode=correction_mode,
            next_prompt=plan.practice_question,
            skill_focus=plan.skill_focus,
            agent_output=agent_output,
            metadata={
                "si_available": si_available,
                "used_fallback": used_fallback,
                "planning_latency_ms": planning_ms,
                "source": "teacher_brain_v1",
                "intent_confidence": intent.confidence,
                "intent_signals": intent.signals,
            },
        )
        output.agent_output["teacher_brain"] = output.to_api_metadata()
        output.agent_output["response"] = teacher_response
        return output

    async def enrich_context_for_langgraph(
        self,
        context: dict[str, Any],
        *,
        learner_id: str,
        tenant_id: str | None,
        message: str,
        scenario: str,
        persona_id: str,
        intent: str,
        is_voice_turn: bool = False,
        teaching_mode: str | None = None,
        voice_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Lightweight planning enrichment for LangGraph path."""
        learner_uuid = None
        if learner_id:
            try:
                learner_uuid = UUID(str(learner_id))
            except (ValueError, TypeError):
                pass
        intent_result = analyze_intent(
            message,
            scenario=scenario,
            persona_id=persona_id,
            orchestration_intent=intent,
            is_voice_turn=is_voice_turn,
        )
        errors = detect_errors(message, voice_analysis=voice_analysis)
        strategy = select_teaching_strategy(
            intent_result,
            errors,
            teaching_mode=teaching_mode,
            persona_id=persona_id,
            scenario=scenario,
        )
        plan = plan_response(
            intent_result,
            strategy,
            errors,
            teaching_mode=teaching_mode,
            is_voice_turn=is_voice_turn,
        )
        enriched = dict(context)
        enriched["teaching_instruction"] = (
            f"{context.get('teaching_instruction', '')}\n"
            f"{build_teacher_brain_instruction(plan, strategy)}"
        ).strip()
        enriched["teacher_brain"] = {
            "intent": intent_result.intent,
            "teaching_strategy": strategy,
            "skill_focus": plan.skill_focus,
            "correction_mode": teaching_mode or "none",
            "next_prompt": plan.practice_question,
        }
        return enriched

    async def _try_fetch_si_summary(
        self,
        learner_id: UUID,
        *,
        tenant_id: str | None,
    ) -> StudentSummaryResponse | None:
        try:
            factory = get_session_factory()
            async with factory() as session:
                if tenant_id:
                    await set_tenant_context(session, str(tenant_id))
                profile = await session.scalar(
                    select(LearnerProfile).where(LearnerProfile.id == learner_id)
                )
                if not profile:
                    return None
                return await get_summary(session, user_id=profile.user_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Student Intelligence fetch failed: %s", exc)
            return None

    def _deterministic_fallback(
        self,
        message: str,
        errors: list[DetectedError],
        plan: ResponsePlan,
    ) -> str:
        for err in errors:
            if err.type == "grammar" and err.suggested_correction:
                return (
                    f"Good try. A better sentence is: '{err.suggested_correction}'. "
                    f"We use the correct form because of the grammar rule. "
                    f"{plan.practice_question or 'Now try another sentence.'}"
                )
            if err.type == "grammar" and "go" in message.lower() and "yesterday" in message.lower():
                return (
                    "Good try. A better sentence is: 'I went to the market yesterday.' "
                    "We use 'went' because it happened in the past. "
                    "Now try another sentence about what you did yesterday."
                )

        if plan.practice_question:
            return f"Good effort! {plan.practice_question}"
        if message:
            return (
                f"You said: \"{message[:80]}\". That's a good start. "
                "Can you add one more detail?"
            )
        return "Let's keep going — could you say that again?"
