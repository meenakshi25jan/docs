"""Lesson completion report — post-session summary for voice lessons."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.models.memory import VoiceAnalysis
from app.scoring.engine import aggregate_scores
from app.services.memory_store import get_recurring_mistakes
from app.services.memory_intelligence_service import MemoryIntelligenceService
from app.services.progress_snapshot_service import record_from_lesson_scores


async def generate_lesson_report(
    *,
    db: AsyncSession,
    learner_id: UUID,
    tenant_id: UUID,
    conversation_id: UUID | None = None,
    persona_id: str | None = None,
    scenario: str | None = None,
) -> dict[str, Any]:
    """Build a lesson completion report from voice analyses and learner memory."""
    query = select(VoiceAnalysis).where(
        VoiceAnalysis.learner_id == learner_id,
        VoiceAnalysis.tenant_id == tenant_id,
    )
    if conversation_id:
        query = query.where(VoiceAnalysis.conversation_id == conversation_id)
    query = query.order_by(VoiceAnalysis.created_at.desc()).limit(50)

    analyses = list(await db.scalars(query))
    if not analyses:
        return {"error": "No voice data found for this lesson."}

    avg_overall = round(sum(a.overall_score or 0 for a in analyses) / len(analyses), 1)
    avg_fluency = round(sum(a.fluency_score or 0 for a in analyses) / len(analyses), 1)
    avg_pronunciation = round(sum(a.pronunciation_score or 0 for a in analyses) / len(analyses), 1)
    avg_grammar = round(sum(a.grammar_score or 0 for a in analyses) / len(analyses), 1)
    avg_vocab = round(sum(a.vocabulary_score or 0 for a in analyses) / len(analyses), 1)

    skill_scores = {
        "grammar": avg_grammar,
        "vocabulary": avg_vocab,
        "speaking": avg_overall,
        "fluency": avg_fluency,
        "pronunciation": avg_pronunciation,
    }
    estimate = aggregate_scores(skill_scores)

    recurring = await get_recurring_mistakes(str(learner_id), str(tenant_id), limit=10)
    new_vocab: list[str] = []
    for a in analyses[:10]:
        details = a.details or {}
        vocab = details.get("vocabulary", {})
        if isinstance(vocab, dict):
            for w in vocab.get("recommended_words", [])[:3]:
                if w and w not in new_vocab:
                    new_vocab.append(str(w))

    report_context = {
        "turn_count": len(analyses),
        "skill_scores": skill_scores,
        "recurring_mistakes": recurring,
        "scenario": scenario or "general",
        "persona": persona_id or "conversation_partner",
    }
    agent_out = await AGENT_REGISTRY["report"].execute(AgentInput(
        learner_id=str(learner_id),
        tenant_id=str(tenant_id),
        context={
            "report_type": "lesson_completion",
            "progress_data": report_context,
        },
    ))
    ai_report = agent_out.data

    scores = {
        "overall_speaking": avg_overall,
        "fluency": avg_fluency,
        "pronunciation": avg_pronunciation,
        "grammar": avg_grammar,
        "vocabulary": avg_vocab,
        "communication_effectiveness": round((avg_overall + avg_fluency) / 2, 1),
    }

    await record_from_lesson_scores(
        db,
        tenant_id=tenant_id,
        learner_id=learner_id,
        scores=scores,
        estimate=estimate,
    )

    executive_summary = ai_report.get("executive_summary", "")
    recommendations = ai_report.get("recommendations", [])
    suggested_practice = ai_report.get("next_steps", [])
    recommended_focus = None
    if isinstance(ai_report.get("skill_breakdown"), dict):
        recommended_focus = ai_report["skill_breakdown"].get("focus") or ai_report["skill_breakdown"].get("weakest")
    if not recommended_focus and recurring:
        recommended_focus = recurring[0].get("category", "grammar")

    report_payload = {
        "lesson_summary": {
            "turn_count": len(analyses),
            "scenario": scenario,
            "persona_id": persona_id,
            "conversation_id": str(conversation_id) if conversation_id else None,
        },
        "scores": scores,
        "estimates": {
            "cefr_level": estimate.cefr,
            "ielts_speaking_estimate": estimate.ielts,
            "pte_speaking_estimate": estimate.pte,
            "label": "estimate — not an official exam score",
            "confidence": estimate.confidence,
        },
        "recurring_mistakes": recurring,
        "new_vocabulary": new_vocab[:15],
        "executive_summary": executive_summary,
        "recommendations": recommendations,
        "suggested_practice": suggested_practice,
        "personalized_next_lesson": ai_report.get("skill_breakdown", {}),
    }

    mi = MemoryIntelligenceService()
    conv_id_str = str(conversation_id) if conversation_id else None
    report_id = await mi.persist_lesson_report(
        learner_id=str(learner_id),
        tenant_id=str(tenant_id),
        report_content=report_payload,
        db=db,
    )
    await mi.write_lesson_reflection(
        learner_id=str(learner_id),
        tenant_id=str(tenant_id),
        executive_summary=executive_summary or "Lesson completed.",
        recurring_mistakes=recurring,
        recommended_next_focus=str(recommended_focus) if recommended_focus else None,
        practice_recommendations=suggested_practice if isinstance(suggested_practice, list) else [],
        conversation_id=conv_id_str,
        report_id=report_id,
        db=db,
    )
    await mi.write_learning_event(
        learner_id=str(learner_id),
        tenant_id=str(tenant_id),
        event_type="lesson_report_generated",
        detail=f"Lesson report for conversation {conv_id_str or 'session'}",
        conversation_id=conv_id_str,
        db=db,
    )

    return report_payload
