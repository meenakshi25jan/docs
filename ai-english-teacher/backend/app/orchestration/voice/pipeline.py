"""Voice analysis pipeline — Wave 2 agents orchestration."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import get_session_factory
from app.models.memory import VoiceAnalysis
from app.orchestration.voice.accent_agent import analyze_accent
from app.orchestration.voice.fluency_agent import analyze_fluency
from app.orchestration.voice.pronunciation_agent import analyze_pronunciation
from app.orchestration.voice.speech_quality_agent import analyze_speech_quality
from app.services.memory_store import persist_mistake
from app.services.transcription import transcribe_audio


async def run_voice_analysis(
    *,
    learner_id: str,
    tenant_id: str,
    transcript: str | None = None,
    audio_base64: str | None = None,
    audio_mime_type: str = "audio/webm",
    duration_seconds: float | None = None,
    audio_metrics: dict[str, Any] | None = None,
    conversation_id: str | None = None,
    cefr_level: str = "B1",
) -> dict[str, Any]:
    final_transcript = transcript or ""
    if audio_base64 and not final_transcript:
        transcribed = await transcribe_audio(audio_base64, audio_mime_type)
        if transcribed:
            final_transcript = transcribed

    if not final_transcript.strip():
        return {"error": "No transcript provided and audio transcription failed."}

    speech_quality = analyze_speech_quality(audio_metrics)
    fluency = analyze_fluency(final_transcript, duration_seconds)
    pronunciation = analyze_pronunciation(final_transcript)
    accent = analyze_accent(final_transcript)

    grammar_out = await AGENT_REGISTRY["grammar"].execute(AgentInput(
        learner_id=learner_id,
        tenant_id=tenant_id,
        context={"text": final_transcript, "cefr_level": cefr_level},
    ))
    vocab_out = await AGENT_REGISTRY["vocabulary"].execute(AgentInput(
        learner_id=learner_id,
        tenant_id=tenant_id,
        context={"text": final_transcript, "cefr_level": cefr_level},
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

    for err in grammar_out.data.get("errors", [])[:5]:
        if isinstance(err, dict):
            await persist_mistake(
                learner_id=learner_id,
                tenant_id=tenant_id,
                error_text=str(err.get("text", "")),
                correction=str(err.get("correction", "")),
                category=str(err.get("category", "grammar")),
            )

    details = {
        "fluency": fluency,
        "pronunciation": pronunciation,
        "accent": accent,
        "speech_quality": speech_quality,
        "grammar": grammar_out.data,
        "vocabulary": vocab_out.data,
    }

    try:
        factory = get_session_factory()
        async with factory() as session:
            record = VoiceAnalysis(
                tenant_id=UUID(tenant_id),
                learner_id=UUID(learner_id),
                conversation_id=UUID(conversation_id) if conversation_id else None,
                transcript=final_transcript,
                duration_seconds=duration_seconds,
                pronunciation_score=pronunciation["phoneme_score"],
                fluency_score=fluency["fluency"],
                grammar_score=grammar_score,
                vocabulary_score=vocabulary_score,
                overall_score=overall,
                speech_quality=speech_quality,
                details=details,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            analysis_id = str(record.id)
    except Exception:
        analysis_id = None

    return {
        "analysis_id": analysis_id,
        "transcript": final_transcript,
        "overall_score": overall,
        "fluency": fluency["fluency"],
        "pronunciation": pronunciation["phoneme_score"],
        "grammar_score": grammar_score,
        "vocabulary_score": vocabulary_score,
        "speech_quality": speech_quality,
        "details": details,
    }
