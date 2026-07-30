"""Read-only analytics queries over existing tables."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Assessment, Conversation, ConversationMessage, LearnerProfile, ProgressSnapshot
from app.models.curriculum import LessonCompletion, RevisionSchedule
from app.models.memory import LearnerMemory, VoiceAnalysis
from app.models.reports import Report


async def get_learner_by_user_id(db: AsyncSession, user_id: UUID) -> LearnerProfile | None:
    return await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user_id))


async def get_progress_snapshots(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 90,
) -> list[ProgressSnapshot]:
    result = await db.scalars(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.learner_id == learner_id)
        .order_by(ProgressSnapshot.snapshot_at.asc())
        .limit(limit)
    )
    return list(result.all())


async def get_completed_assessments(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 20,
) -> list[Assessment]:
    result = await db.scalars(
        select(Assessment)
        .options(selectinload(Assessment.results))
        .where(Assessment.learner_id == learner_id, Assessment.status == "completed")
        .order_by(Assessment.completed_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_lesson_completions(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 100,
) -> list[LessonCompletion]:
    result = await db.scalars(
        select(LessonCompletion)
        .where(LessonCompletion.learner_id == learner_id)
        .order_by(LessonCompletion.completed_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_revision_schedule_rows(
    db: AsyncSession,
    *,
    learner_id: UUID,
) -> list[RevisionSchedule]:
    result = await db.scalars(
        select(RevisionSchedule)
        .where(RevisionSchedule.learner_id == learner_id)
        .order_by(RevisionSchedule.due_at.asc())
    )
    return list(result.all())


async def get_voice_analyses(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 90,
) -> list[VoiceAnalysis]:
    result = await db.scalars(
        select(VoiceAnalysis)
        .where(VoiceAnalysis.learner_id == learner_id)
        .order_by(VoiceAnalysis.created_at.asc())
        .limit(limit)
    )
    return list(result.all())


async def get_assistant_message_metadata(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 200,
    since: datetime | None = None,
) -> list[dict]:
    q = (
        select(ConversationMessage.metadata_, ConversationMessage.created_at)
        .join(Conversation, ConversationMessage.conversation_id == Conversation.id)
        .where(
            Conversation.learner_id == learner_id,
            ConversationMessage.role == "assistant",
        )
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    if since is not None:
        q = q.where(ConversationMessage.created_at >= since)
    rows = await db.execute(q)
    out: list[dict] = []
    for meta, created_at in rows.all():
        payload = dict(meta or {})
        payload["_created_at"] = created_at
        out.append(payload)
    return out


async def get_governance_learning_events(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 50,
) -> list[LearnerMemory]:
    result = await db.scalars(
        select(LearnerMemory)
        .where(
            LearnerMemory.learner_id == learner_id,
            LearnerMemory.memory_type == "learning_event",
        )
        .order_by(LearnerMemory.created_at.desc())
        .limit(limit)
    )
    rows = list(result.all())
    return [r for r in rows if "governance" in (r.content or "").lower()]


async def get_reports(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 20,
) -> list[Report]:
    result = await db.scalars(
        select(Report)
        .where(Report.learner_id == learner_id)
        .order_by(Report.generated_at.desc())
        .limit(limit)
    )
    return list(result.all())


def default_since_days(days: int = 90) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)
