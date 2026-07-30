"""Unified voice conversation turn — STT, coaches, teaching decision, teacher response."""

from __future__ import annotations

import time
from typing import Any

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.ai.openai_client import extract_teacher_response
from app.orchestration.personas import get_persona
from app.orchestration.runner import run_conversation_turn
from app.orchestration.session_manager import load_session, merge_session
from app.orchestration.voice.pipeline import run_voice_analysis
from app.orchestration.voice.teaching_decision import build_teaching_instruction, decide_teaching_mode
from app.scoring.engine import aggregate_scores


async def run_voice_turn(
    *,
    session_id: str,
    learner_id: str,
    tenant_id: str | None,
    scenario: str,
    cefr_level: str,
    message_history: list[dict[str, str]],
    transcript: str | None = None,
    audio_base64: str | None = None,
    audio_mime_type: str = "audio/webm",
    duration_seconds: float | None = None,
    audio_metrics: dict[str, Any] | None = None,
    persona_id: str = "conversation_partner",
    conversation_id: str | None = None,
) -> dict[str, Any]:
    """
    Single voice turn: analyze speech → coach agents → teaching decision → teacher response.
    """
    started = time.perf_counter()

    voice_result = await run_voice_analysis(
        learner_id=learner_id,
        tenant_id=tenant_id or "",
        transcript=transcript,
        audio_base64=audio_base64,
        audio_mime_type=audio_mime_type,
        duration_seconds=duration_seconds,
        audio_metrics=audio_metrics,
        conversation_id=conversation_id,
        cefr_level=cefr_level,
    )
    if voice_result.get("error"):
        return {"error": voice_result["error"]}

    final_transcript = voice_result["transcript"]
    session = await load_session(session_id)
    persona = get_persona(persona_id)
    turn_count = int(session.get("turn_count", 0))
    pending = list(session.get("pending_corrections", []))

    grammar_details = voice_result.get("details", {}).get("grammar", {})
    grammar_errors = grammar_details.get("errors", []) if isinstance(grammar_details, dict) else []

    decision = decide_teaching_mode(
        grammar_errors=[e for e in grammar_errors if isinstance(e, dict)],
        fluency_score=float(voice_result.get("fluency", 70)),
        persona_correction_style=persona.get("correction_style", "delayed"),
        turn_count=turn_count,
        pending_corrections=pending,
        student_message_length=len(final_transcript.split()),
    )

    teaching_instruction = build_teaching_instruction(decision)
    deferred = decision.get("deferred_errors", [])

    enriched_history = list(message_history)
    output = await run_conversation_turn(
        session_id=session_id,
        learner_id=learner_id,
        tenant_id=tenant_id,
        scenario=scenario,
        cefr_level=cefr_level,
        message=final_transcript,
        message_history=enriched_history,
        use_orchestration=True,
        persona_id=persona_id,
        teaching_instruction=teaching_instruction,
        teaching_mode=decision.get("teaching_mode"),
        voice_analysis=voice_result,
    )

    response_text = extract_teacher_response(output.data) or "Could you tell me more about that?"
    skill_scores = {
        "grammar": float(voice_result.get("grammar_score", 70)),
        "vocabulary": float(voice_result.get("vocabulary_score", 70)),
        "speaking": float(voice_result.get("overall_score", 70)),
        "fluency": float(voice_result.get("fluency", 70)),
        "pronunciation": float(voice_result.get("pronunciation", 70)),
    }
    estimate = aggregate_scores(skill_scores)

    await merge_session(session_id, {
        "turn_count": turn_count + 1,
        "pending_corrections": deferred,
        "last_voice_scores": skill_scores,
        "persona_id": persona_id,
    })

    latency_ms = int((time.perf_counter() - started) * 1000)
    teacher_brain_meta = output.data.get("teacher_brain") or (output.metadata or {}).get("teacher_brain")
    memory_meta = (output.metadata or {}).get("memory")

    if not memory_meta:
        try:
            from app.services.memory_intelligence_service import MemoryIntelligenceService

            bundle = await MemoryIntelligenceService().build_bundle_with_session_recall(
                learner_id=learner_id,
                tenant_id=tenant_id,
                session_id=session_id,
                conversation_id=conversation_id or session_id,
                message_history=enriched_history,
            )
            memory_meta = bundle.to_api_metadata()
        except Exception:  # noqa: BLE001
            memory_meta = {
                "recurring_mistakes_count": 0,
                "reflections_available": False,
                "memory_summary_available": False,
            }

    curriculum_meta = None
    try:
        from uuid import UUID

        from sqlalchemy import select

        from app.core.database import get_session_factory, set_tenant_context
        from app.models import LearnerProfile
        from app.services.curriculum_intelligence_service import CurriculumIntelligenceService
        from app.services.memory_intelligence_service import MemoryIntelligenceService

        factory = get_session_factory()
        async with factory() as session:
            if tenant_id:
                await set_tenant_context(session, str(tenant_id))
            profile = await session.scalar(
                select(LearnerProfile).where(LearnerProfile.id == UUID(str(learner_id)))
            )
            if profile:
                mem = await MemoryIntelligenceService().build_bundle(
                    learner_id=str(profile.id),
                    tenant_id=tenant_id,
                    db=session,
                )
                rec = await CurriculumIntelligenceService().build_recommendations(
                    session,
                    user_id=profile.user_id,
                    memory_bundle=mem,
                )
                curriculum_meta = CurriculumIntelligenceService().get_primary_recommendation_metadata(rec)
    except Exception:  # noqa: BLE001
        curriculum_meta = None

    return {
        "transcript": final_transcript,
        "response": response_text,
        "teaching_mode": decision.get("teaching_mode"),
        "teaching_reason": decision.get("reason"),
        "corrections": decision.get("corrections_now", []),
        "voice_scores": {
            "overall": voice_result.get("overall_score"),
            "fluency": voice_result.get("fluency"),
            "pronunciation": voice_result.get("pronunciation"),
            "grammar": voice_result.get("grammar_score"),
            "vocabulary": voice_result.get("vocabulary_score"),
        },
        "estimates": {
            "cefr": estimate.cefr,
            "ielts_speaking_estimate": estimate.ielts,
            "pte_speaking_estimate": estimate.pte,
            "confidence": estimate.confidence,
            "label": "estimate",
        },
        "analysis_id": voice_result.get("analysis_id"),
        "teacher_brain": teacher_brain_meta,
        "memory": memory_meta,
        "curriculum_recommendation": curriculum_meta,
        "agent_output": output.data,
        "metadata": {
            **(output.metadata or {}),
            "latency_ms": latency_ms,
            "persona_id": persona_id,
            "voice_pipeline": True,
        },
    }
