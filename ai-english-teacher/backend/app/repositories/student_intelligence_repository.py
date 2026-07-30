"""Database access for Student Intelligence v1."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Assessment, AssessmentResult, LearnerProfile, ProgressSnapshot, User
from app.models.memory import ErrorTracking, VoiceAnalysis
from app.repositories.optional_tables import query_optional_table


async def get_learner_with_user(
    db: AsyncSession,
    *,
    user_id: UUID,
) -> tuple[LearnerProfile | None, User | None]:
    learner = await db.scalar(
        select(LearnerProfile)
        .options(selectinload(LearnerProfile.user))
        .where(LearnerProfile.user_id == user_id)
    )
    if not learner:
        return None, None
    user = learner.user
    if user is None:
        user = await db.get(User, user_id)
    return learner, user


async def get_latest_progress_snapshots(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 2,
) -> list[ProgressSnapshot]:
    result = await db.scalars(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.learner_id == learner_id)
        .order_by(ProgressSnapshot.snapshot_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_voice_analysis_averages(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 20,
) -> dict[str, float | None]:
    async def _run() -> dict[str, float | None]:
        rows = list(
            await db.scalars(
                select(VoiceAnalysis)
                .where(VoiceAnalysis.learner_id == learner_id)
                .order_by(VoiceAnalysis.created_at.desc())
                .limit(limit)
            )
        )
        if not rows:
            return {}

        def avg(field: str) -> float | None:
            values = [float(getattr(r, field) or 0) for r in rows if getattr(r, field) is not None]
            if not values:
                return None
            return round(sum(values) / len(values), 1)

        latest_at = rows[0].created_at
        return {
            "speaking": avg("overall_score"),
            "pronunciation": avg("pronunciation_score"),
            "fluency": avg("fluency_score"),
            "grammar": avg("grammar_score"),
            "vocabulary": avg("vocabulary_score"),
            "last_updated": latest_at,
        }

    return await query_optional_table(db, _run, {})


async def get_assessment_skill_scores(
    db: AsyncSession,
    *,
    learner_id: UUID,
) -> dict[str, float]:
    """Latest completed assessment results keyed by skill."""
    assessment = await db.scalar(
        select(Assessment)
        .options(selectinload(Assessment.results))
        .where(Assessment.learner_id == learner_id, Assessment.status == "completed")
        .order_by(Assessment.completed_at.desc())
        .limit(1)
    )
    if not assessment or not assessment.results:
        return {}

    return {r.skill: float(r.score) for r in assessment.results}


async def get_error_tracking_rows(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 20,
) -> list[ErrorTracking]:
    result = await db.scalars(
        select(ErrorTracking)
        .where(ErrorTracking.learner_id == learner_id)
        .order_by(ErrorTracking.occurrence_count.desc(), ErrorTracking.last_seen_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_progress_history_count(db: AsyncSession, *, learner_id: UUID) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(ProgressSnapshot)
        .where(ProgressSnapshot.learner_id == learner_id)
    )
    return int(count or 0)
