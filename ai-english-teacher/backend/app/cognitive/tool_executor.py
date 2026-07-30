"""Tool and agent execution — invoked only via orchestrator."""

from __future__ import annotations

import time
from typing import Any

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.cognitive.agent_planner import AgentName
from app.cognitive.observability import CognitiveTrace
from app.cognitive.tool_router import ToolName
from app.cognitive.web_gateway import fetch_web_knowledge
from app.orchestration.voice.fluency_agent import analyze_fluency
from app.orchestration.voice.pronunciation_agent import analyze_pronunciation
from app.orchestration.voice.speech_quality_agent import analyze_speech_quality
from app.orchestration.voice.accent_agent import analyze_accent
from app.orchestration.voice.teaching_decision import build_teaching_instruction, decide_teaching_mode
from app.orchestration.personas import get_persona
from app.cognitive.state import CognitiveState


async def execute_voice_coaches(
    state: CognitiveState,
    *,
    learner_id: str,
    tenant_id: str | None,
    audio_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    transcript = state.voice.transcript
    duration = state.voice.duration_seconds

    fluency = analyze_fluency(transcript, duration)
    pronunciation = analyze_pronunciation(transcript)
    accent = analyze_accent(transcript)
    speech_quality = analyze_speech_quality(audio_metrics)

    grammar_out = await AGENT_REGISTRY["grammar"].execute(AgentInput(
        learner_id=learner_id,
        tenant_id=tenant_id,
        context={"text": transcript, "cefr_level": state.student.cefr_level},
    ))
    vocab_out = await AGENT_REGISTRY["vocabulary"].execute(AgentInput(
        learner_id=learner_id,
        tenant_id=tenant_id,
        context={"text": transcript, "cefr_level": state.student.cefr_level},
    ))

    grammar_score = float(grammar_out.data.get("score", 70))
    vocabulary_score = float(vocab_out.data.get("score", 70))
    overall = round(
        (fluency["fluency"] * 0.25)
        + (pronunciation["phoneme_score"] * 0.25)
        + (grammar_score * 0.25)
        + (vocabulary_score * 0.25),
        1,
    )

    voice_analysis = {
        "transcript": transcript,
        "overall_score": overall,
        "fluency": fluency["fluency"],
        "pronunciation": pronunciation["phoneme_score"],
        "grammar_score": grammar_score,
        "vocabulary_score": vocabulary_score,
        "details": {
            "fluency": fluency,
            "pronunciation": pronunciation,
            "accent": accent,
            "speech_quality": speech_quality,
            "grammar": grammar_out.data,
            "vocabulary": vocab_out.data,
        },
    }
    state.voice.voice_analysis = voice_analysis

    grammar_errors = grammar_out.data.get("errors", []) if isinstance(grammar_out.data, dict) else []
    persona = get_persona(state.session.persona_id)
    decision = decide_teaching_mode(
        grammar_errors=[e for e in grammar_errors if isinstance(e, dict)],
        fluency_score=float(fluency["fluency"]),
        persona_correction_style=persona.get("correction_style", "delayed"),
        turn_count=state.session.turn_count,
        pending_corrections=state.conversation.pending_corrections,
        student_message_length=len(transcript.split()),
    )
    state.voice.teaching_mode = decision.get("teaching_mode")
    state.voice.teaching_instruction = build_teaching_instruction(decision)
    state.conversation.pending_corrections = list(decision.get("deferred_errors", []))

    return {
        "voice_analysis": voice_analysis,
        "teaching_decision": decision,
        "coach_briefs": {
            "fluency": fluency,
            "pronunciation": pronunciation,
            "grammar": grammar_out.data,
            "vocabulary": vocab_out.data,
            "accent": accent,
            "speech_quality": speech_quality,
        },
    }


async def execute_agents(
    plan_agents: list[AgentName],
    context: dict[str, Any],
    *,
    learner_id: str,
    tenant_id: str | None,
    trace: CognitiveTrace,
) -> dict[str, Any]:
    results: dict[str, Any] = {}

    for agent_name in plan_agents:
        if agent_name == AgentName.TEACHER_BRAIN:
            continue  # handled separately
        if agent_name == AgentName.CONVERSATION:
            continue  # routed via teacher/conversation in brain step

        started = time.perf_counter()
        success = True
        try:
            if agent_name == AgentName.GRAMMAR:
                out = await AGENT_REGISTRY["grammar"].execute(AgentInput(
                    learner_id=learner_id, tenant_id=tenant_id,
                    context={"text": context.get("message", ""), "cefr_level": context.get("cefr_level", "B1")},
                ))
                results["grammar"] = out.data
            elif agent_name == AgentName.VOCABULARY:
                out = await AGENT_REGISTRY["vocabulary"].execute(AgentInput(
                    learner_id=learner_id, tenant_id=tenant_id,
                    context={"text": context.get("message", ""), "cefr_level": context.get("cefr_level", "B1")},
                ))
                results["vocabulary"] = out.data
            elif agent_name == AgentName.ASSESSMENT:
                results["assessment"] = {"status": "deferred_to_voice_coaches"}
            elif agent_name == AgentName.PLANNER:
                out = await AGENT_REGISTRY["planner"].execute(AgentInput(
                    learner_id=learner_id, tenant_id=tenant_id,
                    context={
                        "cefr_level": context.get("cefr_level", "B1"),
                        "duration_weeks": 1,
                        "target_exam": "ielts",
                        "target_score": 7.0,
                        "skill_scores": {},
                        "error_patterns": context.get("recent_errors", []),
                    },
                ))
                results["planner"] = out.data
            elif agent_name == AgentName.WEB_SUMMARIZER:
                web = await fetch_web_knowledge(context.get("message", ""))
                results["web_summary"] = web
            elif agent_name == AgentName.TRANSLATION:
                results["translation"] = {
                    "note": "Translation tool stub — wire lexicon API in production",
                    "query": context.get("message", ""),
                }
        except Exception as exc:  # noqa: BLE001
            success = False
            trace.record_error(agent_name.value, str(exc))

        ms = int((time.perf_counter() - started) * 1000)
        trace.record_agent(agent_name.value, ms, success)

    return results


async def execute_teacher_brain(
    context: dict[str, Any],
    *,
    learner_id: str,
    tenant_id: str | None,
    intent: str,
    trace: CognitiveTrace,
) -> dict[str, Any]:
    from app.orchestration.teacher_brain.teacher_brain_service import TeacherBrainService
    from app.orchestration.teacher_brain.schemas import TeacherBrainInput

    started = time.perf_counter()
    enriched_context = dict(context)
    if not enriched_context.get("memory_bundle"):
        enriched_context["memory_bundle"] = {
            "recurring_mistakes": enriched_context.get("recurring_mistakes", []),
            "learning_mistakes": enriched_context.get("recent_errors", []),
            "lesson_reflections": enriched_context.get("lesson_reflections", []),
            "memory_summary": enriched_context.get("memory_summary", ""),
            "preferences": enriched_context.get("preferences", {}),
            "skill_weaknesses": enriched_context.get("skill_weaknesses", []),
        }
    if enriched_context.get("memory_summary"):
        enriched_context.setdefault("teaching_instruction", "")
        enriched_context["teaching_instruction"] = (
            f"{enriched_context['teaching_instruction']}\n"
            f"Learner memory: {enriched_context['memory_summary'][:800]}"
        ).strip()
    if enriched_context.get("grounding_context"):
        from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService

        enriched_context["teaching_instruction"] = KnowledgeIntelligenceService().inject_teaching_instruction(
            enriched_context.get("teaching_instruction", ""),
            enriched_context["grounding_context"],
        )
    is_voice = bool(enriched_context.get("voice_summary") and enriched_context.get("voice_summary") != "not available")

    tb_input = TeacherBrainInput.from_teacher_context(
        enriched_context,
        learner_id=learner_id,
        tenant_id=tenant_id,
        orchestration_intent=intent,
        is_voice_turn=is_voice,
        session_id=str(enriched_context.get("orchestration_trace_id", "")),
    )

    service = TeacherBrainService()
    try:
        result = await service.process_turn(
            tb_input,
            agent_context=enriched_context,
            learner_id=learner_id,
            tenant_id=tenant_id,
            use_conversation_agent=intent == "greeting",
        )
        trace.record_agent("teacher_brain", int((time.perf_counter() - started) * 1000), True)
        return result.agent_output
    except Exception as exc:  # noqa: BLE001
        trace.record_agent("teacher_brain", int((time.perf_counter() - started) * 1000), False)
        trace.record_error("teacher_brain", str(exc))
        return {"response": "Let's keep going — could you say that again?"}


async def execute_tool(
    tool: ToolName,
    *,
    state: CognitiveState,
    learner_id: str,
    tenant_id: str | None,
    message: str,
    trace: CognitiveTrace,
) -> Any:
    started = time.perf_counter()
    success = True
    result: Any = None
    try:
        if tool == ToolName.WEB_SEARCH:
            result = await fetch_web_knowledge(message)
            state.web_results = result
        elif tool == ToolName.UTILITY:
            result = {"utility": "stub", "message": message}
            state.tool_results["utility"] = result
        else:
            result = {"tool": tool.value, "status": "delegated_to_workflow"}
    except Exception as exc:  # noqa: BLE001
        success = False
        trace.record_error(tool.value, str(exc))
        result = None

    trace.record_tool(tool.value, int((time.perf_counter() - started) * 1000), success)
    return result
