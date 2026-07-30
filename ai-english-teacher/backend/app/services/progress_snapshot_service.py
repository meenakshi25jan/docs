"""Record learner progress snapshots after lessons and assessments."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.progress_snapshot_repository import create_progress_snapshot
from app.scoring.engine import ProficiencyEstimate


async def record_from_skill_map(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    skill_scores: dict[str, float],
    estimate: ProficiencyEstimate | None = None,
    confidence_score: float | None = None,
) -> None:
    """Persist a progress snapshot from per-skill scores."""
    cefr = estimate.cefr if estimate else None
    ielts = estimate.ielts if estimate else None
    pte = estimate.pte if estimate else None
    confidence = confidence_score if confidence_score is not None else (
        estimate.confidence if estimate else None
    )

    await create_progress_snapshot(
        db,
        tenant_id=tenant_id,
        learner_id=learner_id,
        grammar_score=skill_scores.get("grammar"),
        vocabulary_score=skill_scores.get("vocabulary"),
        writing_score=skill_scores.get("writing"),
        reading_score=skill_scores.get("reading"),
        listening_score=skill_scores.get("listening"),
        speaking_score=skill_scores.get("speaking") or skill_scores.get("fluency"),
        confidence_score=confidence,
        cefr_estimate=cefr,
        ielts_estimate=ielts,
        pte_estimate=pte,
    )


async def record_from_lesson_scores(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    scores: dict[str, float],
    estimate: ProficiencyEstimate,
) -> None:
    """Snapshot after a voice lesson report (speaking-focused)."""
    skill_map = {
        "grammar": scores.get("grammar"),
        "vocabulary": scores.get("vocabulary"),
        "speaking": scores.get("overall_speaking") or scores.get("speaking"),
        "fluency": scores.get("fluency"),
        "pronunciation": scores.get("pronunciation"),
    }
    # Use communication effectiveness as confidence proxy when available
    confidence = scores.get("communication_effectiveness")
    await record_from_skill_map(
        db,
        tenant_id=tenant_id,
        learner_id=learner_id,
        skill_scores={k: v for k, v in skill_map.items() if v is not None},
        estimate=estimate,
        confidence_score=confidence,
    )


async def record_from_assessment(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    skill_scores: dict[str, float],
    estimate: ProficiencyEstimate,
) -> None:
    """Snapshot after formal assessment submission."""
    await record_from_skill_map(
        db,
        tenant_id=tenant_id,
        learner_id=learner_id,
        skill_scores=skill_scores,
        estimate=estimate,
    )
