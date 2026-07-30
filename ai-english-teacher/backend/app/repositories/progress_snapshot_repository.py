"""Database access for learner progress snapshots."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProgressSnapshot


async def create_progress_snapshot(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    grammar_score: float | None = None,
    vocabulary_score: float | None = None,
    writing_score: float | None = None,
    reading_score: float | None = None,
    listening_score: float | None = None,
    speaking_score: float | None = None,
    confidence_score: float | None = None,
    cefr_estimate: str | None = None,
    ielts_estimate: float | None = None,
    pte_estimate: int | None = None,
) -> ProgressSnapshot:
    snapshot = ProgressSnapshot(
        tenant_id=tenant_id,
        learner_id=learner_id,
        grammar_score=grammar_score,
        vocabulary_score=vocabulary_score,
        writing_score=writing_score,
        reading_score=reading_score,
        listening_score=listening_score,
        speaking_score=speaking_score,
        confidence_score=confidence_score,
        cefr_estimate=cefr_estimate,
        ielts_estimate=ielts_estimate,
        pte_estimate=pte_estimate,
    )
    db.add(snapshot)
    await db.flush()
    return snapshot
