"""Read-mostly operations queries — tenant-scoped."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Assessment, Conversation, ConversationMessage, LearnerProfile, ProgressSnapshot, Tenant, User
from app.models.curriculum import LessonCompletion, RevisionSchedule
from app.models.reports import Report


def since_days(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


async def get_tenant(db: AsyncSession, tenant_id: UUID) -> Tenant | None:
    return await db.get(Tenant, tenant_id)


async def update_tenant_settings_db(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    settings: dict,
) -> Tenant | None:
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        return None
    tenant.settings = settings
    await db.flush()
    return tenant


async def list_users_in_tenant(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    limit: int = 200,
) -> list[User]:
    result = await db.scalars(
        select(User)
        .where(User.tenant_id == tenant_id)
        .order_by(User.created_at.desc())
        .limit(limit)
    )
    return list(result.all())


async def count_users_in_tenant(db: AsyncSession, *, tenant_id: UUID) -> int:
    count = await db.scalar(
        select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
    )
    return int(count or 0)


async def list_learner_profiles_in_tenant(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    limit: int = 100,
) -> list[LearnerProfile]:
    result = await db.scalars(
        select(LearnerProfile)
        .options(selectinload(LearnerProfile.user))
        .where(LearnerProfile.tenant_id == tenant_id)
        .limit(limit)
    )
    return list(result.all())


async def count_learners_in_tenant(db: AsyncSession, *, tenant_id: UUID) -> int:
    count = await db.scalar(
        select(func.count()).select_from(LearnerProfile).where(LearnerProfile.tenant_id == tenant_id)
    )
    return int(count or 0)


async def get_learner_in_tenant(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
) -> LearnerProfile | None:
    return await db.scalar(
        select(LearnerProfile)
        .options(selectinload(LearnerProfile.user))
        .where(LearnerProfile.id == learner_id, LearnerProfile.tenant_id == tenant_id)
    )


async def get_latest_snapshot(
    db: AsyncSession,
    *,
    learner_id: UUID,
) -> ProgressSnapshot | None:
    return await db.scalar(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.learner_id == learner_id)
        .order_by(ProgressSnapshot.snapshot_at.desc())
        .limit(1)
    )


async def count_lesson_completions_since(
    db: AsyncSession,
    *,
    learner_id: UUID,
    since: datetime,
) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(LessonCompletion)
        .where(
            LessonCompletion.learner_id == learner_id,
            LessonCompletion.completed_at >= since,
        )
    )
    return int(count or 0)


async def count_lesson_completions_tenant_since(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    since: datetime,
) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(LessonCompletion)
        .where(
            LessonCompletion.tenant_id == tenant_id,
            LessonCompletion.completed_at >= since,
        )
    )
    return int(count or 0)


async def count_overdue_revisions(db: AsyncSession, *, learner_id: UUID) -> int:
    now = datetime.now(timezone.utc)
    count = await db.scalar(
        select(func.count())
        .select_from(RevisionSchedule)
        .where(
            RevisionSchedule.learner_id == learner_id,
            RevisionSchedule.status.in_(("scheduled", "pending", "due")),
            RevisionSchedule.due_at < now,
        )
    )
    return int(count or 0)


async def get_last_activity_at(db: AsyncSession, *, learner_id: UUID) -> datetime | None:
    latest_completion = await db.scalar(
        select(LessonCompletion.completed_at)
        .where(LessonCompletion.learner_id == learner_id)
        .order_by(LessonCompletion.completed_at.desc())
        .limit(1)
    )
    latest_conv = await db.scalar(
        select(Conversation.started_at)
        .where(Conversation.learner_id == learner_id)
        .order_by(Conversation.started_at.desc())
        .limit(1)
    )
    latest_snap = await db.scalar(
        select(ProgressSnapshot.snapshot_at)
        .where(ProgressSnapshot.learner_id == learner_id)
        .order_by(ProgressSnapshot.snapshot_at.desc())
        .limit(1)
    )
    candidates = [t for t in (latest_completion, latest_conv, latest_snap) if t is not None]
    return max(candidates) if candidates else None


async def _assistant_metadata_rows(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID | None = None,
    since: datetime | None = None,
    limit: int = 500,
) -> list[dict]:
    q = (
        select(ConversationMessage.metadata_)
        .join(Conversation, ConversationMessage.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            ConversationMessage.role == "assistant",
        )
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    if learner_id is not None:
        q = q.where(Conversation.learner_id == learner_id)
    if since is not None:
        q = q.where(ConversationMessage.created_at >= since)
    rows = await db.scalars(q)
    return [dict(m or {}) for m in rows.all()]


def _aggregate_governance(meta_rows: list[dict]) -> dict:
    scores: list[float] = []
    warnings: list[str] = []
    needs_attention = 0
    for meta in meta_rows:
        gov = meta.get("governance")
        if not gov or not isinstance(gov, dict):
            continue
        if gov.get("overall_score") is not None:
            scores.append(float(gov["overall_score"]))
        if gov.get("status") == "needs_attention":
            needs_attention += 1
        for w in gov.get("warnings") or []:
            warnings.append(str(w))
    avg = round(sum(scores) / len(scores), 3) if scores else None
    return {
        "avg_score": avg,
        "evaluation_count": len(scores),
        "warning_count": len(warnings),
        "warnings": warnings,
        "needs_attention_count": needs_attention,
    }


def _aggregate_knowledge_fallback(meta_rows: list[dict]) -> dict:
    grounding_rows = 0
    fallback_count = 0
    for meta in meta_rows:
        kg = meta.get("knowledge_grounding")
        if not kg or not isinstance(kg, dict):
            continue
        grounding_rows += 1
        if kg.get("fallback_used"):
            fallback_count += 1
    rate = round(fallback_count / grounding_rows, 3) if grounding_rows else None
    return {"grounding_count": grounding_rows, "fallback_count": fallback_count, "fallback_rate": rate}


async def get_governance_aggregate_for_learner(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    since: datetime,
) -> dict:
    rows = await _assistant_metadata_rows(
        db, tenant_id=tenant_id, learner_id=learner_id, since=since
    )
    return _aggregate_governance(rows)


async def get_governance_aggregate_for_tenant(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    since: datetime,
) -> dict:
    rows = await _assistant_metadata_rows(db, tenant_id=tenant_id, since=since)
    return _aggregate_governance(rows)


async def get_knowledge_aggregate_for_tenant(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    since: datetime,
) -> dict:
    rows = await _assistant_metadata_rows(db, tenant_id=tenant_id, since=since)
    return _aggregate_knowledge_fallback(rows)


async def count_active_learners_since(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    since: datetime,
) -> int:
    from_lessons = select(LessonCompletion.learner_id).where(
        LessonCompletion.tenant_id == tenant_id,
        LessonCompletion.completed_at >= since,
    )
    from_conv = select(Conversation.learner_id).where(
        Conversation.tenant_id == tenant_id,
        Conversation.started_at >= since,
    )
    lesson_ids = set(await db.scalars(from_lessons))
    conv_ids = set(await db.scalars(from_conv))
    return len(lesson_ids | conv_ids)


async def get_reports_for_learner(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    learner_id: UUID,
    limit: int = 20,
) -> list[Report]:
    result = await db.scalars(
        select(Report)
        .where(Report.tenant_id == tenant_id, Report.learner_id == learner_id)
        .order_by(Report.generated_at.desc())
        .limit(limit)
    )
    return list(result.all())
