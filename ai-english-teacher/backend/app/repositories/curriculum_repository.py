"""Database access for Curriculum Intelligence v1."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assessment
from app.models.curriculum import LessonCompletion, RevisionSchedule


async def has_completed_assessment(db: AsyncSession, *, learner_id: UUID) -> bool:
    row = await db.scalar(
        select(Assessment.id)
        .where(Assessment.learner_id == learner_id, Assessment.status == "completed")
        .limit(1)
    )
    return row is not None


async def get_completed_lessons(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 50,
) -> list[LessonCompletion]:
    result = await db.scalars(
        select(LessonCompletion)
        .where(LessonCompletion.learner_id == learner_id)
        .order_by(LessonCompletion.completed_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_completion_by_lesson(
    db: AsyncSession,
    *,
    learner_id: UUID,
    lesson_id: str,
) -> LessonCompletion | None:
    return await db.scalar(
        select(LessonCompletion)
        .where(
            LessonCompletion.learner_id == learner_id,
            LessonCompletion.lesson_id == lesson_id,
        )
        .order_by(LessonCompletion.completed_at.desc())
        .limit(1)
    )


async def mark_lesson_complete(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    lesson_id: str,
    title: str,
    skill_focus: str,
    route: str,
    score: float | None = None,
    metadata: dict | None = None,
) -> LessonCompletion:
    row = LessonCompletion(
        tenant_id=tenant_id,
        learner_id=learner_id,
        lesson_id=lesson_id,
        title=title,
        skill_focus=skill_focus,
        route=route,
        score=score,
        metadata_=metadata or {},
        completed_at=datetime.now(timezone.utc),
    )
    db.add(row)
    await db.flush()
    return row


async def create_revision_item(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    lesson_id: str,
    source_type: str,
    source_ref: str | None,
    title: str,
    skill_focus: str,
    route: str,
    due_at: datetime,
    priority: int = 5,
    metadata: dict | None = None,
) -> RevisionSchedule:
    existing = await db.scalar(
        select(RevisionSchedule)
        .where(
            RevisionSchedule.learner_id == learner_id,
            RevisionSchedule.lesson_id == lesson_id,
            RevisionSchedule.status == "scheduled",
            RevisionSchedule.source_ref == source_ref,
        )
        .limit(1)
    )
    if existing:
        existing.due_at = due_at
        existing.priority = priority
        existing.title = title
        existing.route = route
        await db.flush()
        return existing

    row = RevisionSchedule(
        tenant_id=tenant_id,
        learner_id=learner_id,
        lesson_id=lesson_id,
        source_type=source_type,
        source_ref=source_ref,
        title=title,
        skill_focus=skill_focus,
        route=route,
        due_at=due_at,
        status="scheduled",
        priority=priority,
        metadata_=metadata or {},
    )
    db.add(row)
    await db.flush()
    return row


async def update_revision_item(
    db: AsyncSession,
    *,
    revision_id: UUID,
    status: str | None = None,
    due_at: datetime | None = None,
) -> RevisionSchedule | None:
    row = await db.get(RevisionSchedule, revision_id)
    if not row:
        return None
    if status:
        row.status = status
    if due_at:
        row.due_at = due_at
    await db.flush()
    return row


async def get_revision_schedule(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 20,
) -> list[RevisionSchedule]:
    result = await db.scalars(
        select(RevisionSchedule)
        .where(RevisionSchedule.learner_id == learner_id)
        .order_by(RevisionSchedule.due_at.asc())
        .limit(limit)
    )
    return list(result.all())


async def get_due_revision_items(
    db: AsyncSession,
    *,
    learner_id: UUID,
    as_of: datetime | None = None,
    limit: int = 5,
) -> list[RevisionSchedule]:
    now = as_of or datetime.now(timezone.utc)
    result = await db.scalars(
        select(RevisionSchedule)
        .where(
            RevisionSchedule.learner_id == learner_id,
            RevisionSchedule.status == "scheduled",
            RevisionSchedule.due_at <= now,
        )
        .order_by(RevisionSchedule.priority.asc(), RevisionSchedule.due_at.asc())
        .limit(limit)
    )
    return list(result.all())
