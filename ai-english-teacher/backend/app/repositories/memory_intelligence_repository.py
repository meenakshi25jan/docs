"""Database access for Memory Intelligence v1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ConversationMessage, LearnerProfile, ProgressSnapshot
from app.models.memory import ErrorTracking, LearnerMemory
from app.models.reports import Report


async def get_recent_conversation_messages(
    db: AsyncSession,
    *,
    conversation_id: UUID,
    limit: int = 12,
) -> list[ConversationMessage]:
    result = await db.scalars(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    rows = list(result.all())
    rows.reverse()
    return rows


async def get_recurring_mistakes_rows(
    db: AsyncSession,
    *,
    learner_id: UUID,
    limit: int = 8,
) -> list[ErrorTracking]:
    result = await db.scalars(
        select(ErrorTracking)
        .where(ErrorTracking.learner_id == learner_id)
        .order_by(ErrorTracking.occurrence_count.desc(), ErrorTracking.last_seen_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_learner_memories_by_type(
    db: AsyncSession,
    *,
    learner_id: UUID,
    memory_type: str,
    limit: int = 5,
) -> list[LearnerMemory]:
    result = await db.scalars(
        select(LearnerMemory)
        .where(
            LearnerMemory.learner_id == learner_id,
            LearnerMemory.memory_type == memory_type,
        )
        .order_by(LearnerMemory.created_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def get_learner_profile(
    db: AsyncSession,
    *,
    learner_id: UUID,
) -> LearnerProfile | None:
    return await db.get(LearnerProfile, learner_id)


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


async def insert_learner_memory(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    memory_type: str,
    content: str,
    weight: float = 0.5,
) -> LearnerMemory:
    row = LearnerMemory(
        tenant_id=tenant_id,
        learner_id=learner_id,
        memory_type=memory_type,
        content=content[:2000],
        weight=weight,
    )
    db.add(row)
    await db.flush()
    return row


async def insert_report(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    report_type: str,
    content: dict,
) -> Report:
    row = Report(
        tenant_id=tenant_id,
        learner_id=learner_id,
        report_type=report_type,
        content=content,
    )
    db.add(row)
    await db.flush()
    return row


async def has_recent_reflection_for_conversation(
    db: AsyncSession,
    *,
    learner_id: UUID,
    conversation_id: str,
    within_minutes: int = 30,
) -> bool:
    """Simple dedupe: skip if a lesson_reflection for this conversation was written recently."""
    rows = await get_learner_memories_by_type(
        db, learner_id=learner_id, memory_type="lesson_reflection", limit=3,
    )
    now = datetime.now(timezone.utc)
    for row in rows:
        try:
            payload = json.loads(row.content)
        except (json.JSONDecodeError, TypeError):
            if conversation_id in row.content:
                return True
            continue
        if payload.get("conversation_id") != conversation_id:
            continue
        created = row.created_at
        if created and (now - created).total_seconds() < within_minutes * 60:
            return True
    return False
