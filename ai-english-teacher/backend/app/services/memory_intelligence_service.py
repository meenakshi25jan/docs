"""Memory Intelligence v1 — unified memory read/write layer."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory, set_tenant_context
from app.orchestration.memory_agent import store_from_teacher_output
from app.orchestration.session_manager import load_session
from app.repositories.memory_intelligence_repository import (
    get_latest_progress_snapshots,
    get_learner_memories_by_type,
    get_learner_profile,
    get_recent_conversation_messages,
    get_recurring_mistakes_rows,
    has_recent_reflection_for_conversation,
    insert_learner_memory,
    insert_report,
)
from app.schemas.memory_intelligence import (
    LearningEventMemory,
    LessonReflection,
    MemoryBundle,
    MemoryBundleMetadata,
    MemoryTurn,
    RecurringMistake,
    TeacherBrainDecisionMemory,
)

logger = logging.getLogger(__name__)

MEMORY_SUMMARY_MAX_CHARS = 1500
MAX_RECENT_TURNS = 12
MAX_RECURRING_MISTAKES = 8
MAX_RECENT_ERRORS = 10
MAX_REFLECTIONS = 3
MAX_DECISIONS = 5
MAX_EVENTS = 5
MAX_SKILL_WEAKNESSES = 2

SKILL_FIELDS = [
    ("grammar", "grammar_score"),
    ("vocabulary", "vocabulary_score"),
    ("speaking", "speaking_score"),
    ("writing", "writing_score"),
    ("reading", "reading_score"),
    ("listening", "listening_score"),
    ("fluency", "confidence_score"),
]


def _empty_bundle(*, used_fallback: bool = True, error: str | None = None) -> MemoryBundle:
    meta = MemoryBundleMetadata(used_fallback=used_fallback)
    if error:
        meta.errors.append(error[:200])
    return MemoryBundle(metadata=meta)


def _parse_json_content(content: str) -> dict[str, Any]:
    try:
        data = json.loads(content)
        return data if isinstance(data, dict) else {"text": content}
    except (json.JSONDecodeError, TypeError):
        return {"text": content}


def _build_memory_summary(
    *,
    recurring: list[RecurringMistake],
    reflections: list[LessonReflection],
    preferences: dict[str, Any],
    weaknesses: list[str],
) -> str:
    parts: list[str] = []

    if weaknesses:
        parts.append(f"Weakest skills: {', '.join(weaknesses[:MAX_SKILL_WEAKNESSES])}.")

    if preferences:
        style = preferences.get("correction_style") or preferences.get("preferred_correction_style")
        goal = preferences.get("daily_goal_minutes")
        exam = preferences.get("target_exam") or preferences.get("exam_target")
        if style:
            parts.append(f"Learner prefers {style} corrections.")
        if goal:
            parts.append(f"Daily goal: {goal} minutes.")
        if exam:
            parts.append(f"Exam target: {exam}.")

    if reflections:
        focus = reflections[0].recommended_focus or reflections[0].content[:120]
        parts.append(f"Last lesson focus: {focus}")

    if recurring:
        mistake_lines = []
        for m in recurring[:3]:
            line = m.error
            if m.correction:
                line = f"{m.error} → {m.correction}"
            if m.count > 1:
                line += f" (×{m.count})"
            mistake_lines.append(line)
        parts.append("Recurring mistakes: " + "; ".join(mistake_lines))

    summary = " ".join(parts).strip()
    if len(summary) > MEMORY_SUMMARY_MAX_CHARS:
        return summary[:MEMORY_SUMMARY_MAX_CHARS - 3] + "..."
    return summary


def _weaknesses_from_snapshot(snapshot) -> list[str]:
    scores: list[tuple[str, float]] = []
    for label, field in SKILL_FIELDS:
        val = getattr(snapshot, field, None)
        if val is not None:
            scores.append((label, float(val)))
    if not scores:
        return []
    scores.sort(key=lambda x: x[1])
    return [s[0] for s in scores[:MAX_SKILL_WEAKNESSES]]


class MemoryIntelligenceService:
    """Deterministic memory bundle builder and writer."""

    async def build_bundle(
        self,
        *,
        learner_id: str,
        tenant_id: str | None,
        session_id: str | None = None,
        conversation_id: str | None = None,
        message_history: list[dict[str, str]] | None = None,
        session_recent_errors: list[str] | None = None,
        same_turn_errors: list[str] | None = None,
        db: AsyncSession | None = None,
    ) -> MemoryBundle:
        try:
            if db is not None:
                return await self._build_bundle_with_session(
                    db,
                    learner_id=learner_id,
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    message_history=message_history,
                    session_recent_errors=session_recent_errors,
                    same_turn_errors=same_turn_errors,
                )
            factory = get_session_factory()
            async with factory() as session:
                if tenant_id:
                    await set_tenant_context(session, str(tenant_id))
                bundle = await self._build_bundle_with_session(
                    session,
                    learner_id=learner_id,
                    tenant_id=tenant_id,
                    conversation_id=conversation_id or session_id,
                    message_history=message_history,
                    session_recent_errors=session_recent_errors,
                    same_turn_errors=same_turn_errors,
                )
                return bundle
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.build_bundle_failed", extra={"error": str(exc)})
            return _empty_bundle(error=str(exc))

    async def _build_bundle_with_session(
        self,
        db: AsyncSession,
        *,
        learner_id: str,
        tenant_id: str | None,
        conversation_id: str | None,
        message_history: list[dict[str, str]] | None,
        session_recent_errors: list[str] | None,
        same_turn_errors: list[str] | None,
    ) -> MemoryBundle:
        lid = UUID(str(learner_id))
        recent_turns: list[MemoryTurn] = []

        conv_uuid = None
        if conversation_id:
            try:
                conv_uuid = UUID(str(conversation_id))
            except (ValueError, TypeError):
                conv_uuid = None

        if conv_uuid:
            messages = await get_recent_conversation_messages(db, conversation_id=conv_uuid, limit=MAX_RECENT_TURNS)
            for msg in messages:
                recent_turns.append(MemoryTurn(
                    role=msg.role,
                    content=msg.content[:500],
                    created_at=msg.created_at,
                ))
        elif message_history:
            for item in message_history[-MAX_RECENT_TURNS:]:
                recent_turns.append(MemoryTurn(
                    role=str(item.get("role", "user")),
                    content=str(item.get("content", ""))[:500],
                ))

        mistake_rows = await get_recurring_mistakes_rows(db, learner_id=lid, limit=MAX_RECURRING_MISTAKES)
        recurring = [
            RecurringMistake(
                error=row.error_text,
                correction=row.correction,
                category=row.error_category or "grammar",
                count=int(row.occurrence_count or 1),
            )
            for row in mistake_rows
        ]

        recent_errors: list[str] = []
        if session_recent_errors:
            recent_errors.extend(session_recent_errors)
        if same_turn_errors:
            recent_errors.extend(same_turn_errors)
        recent_errors = list(dict.fromkeys([e for e in recent_errors if e]))[:MAX_RECENT_ERRORS]

        reflection_rows = await get_learner_memories_by_type(
            db, learner_id=lid, memory_type="lesson_reflection", limit=MAX_REFLECTIONS,
        )
        lesson_reflections: list[LessonReflection] = []
        for row in reflection_rows:
            payload = _parse_json_content(row.content)
            lesson_reflections.append(LessonReflection(
                content=str(payload.get("executive_summary") or payload.get("text") or row.content)[:500],
                conversation_id=payload.get("conversation_id"),
                recommended_focus=payload.get("recommended_next_focus") or payload.get("recommended_focus"),
                created_at=row.created_at,
            ))

        decision_rows = await get_learner_memories_by_type(
            db, learner_id=lid, memory_type="teacher_brain_decision", limit=MAX_DECISIONS,
        )
        decisions: list[TeacherBrainDecisionMemory] = []
        for row in decision_rows:
            payload = _parse_json_content(row.content)
            decisions.append(TeacherBrainDecisionMemory(
                intent=payload.get("intent"),
                teaching_strategy=payload.get("teaching_strategy"),
                skill_focus=payload.get("skill_focus"),
                correction_mode=payload.get("correction_mode"),
                next_prompt=payload.get("next_prompt"),
                conversation_id=payload.get("conversation_id"),
                created_at=row.created_at,
            ))

        event_rows = await get_learner_memories_by_type(
            db, learner_id=lid, memory_type="learning_event", limit=MAX_EVENTS,
        )
        events: list[LearningEventMemory] = []
        for row in event_rows:
            payload = _parse_json_content(row.content)
            events.append(LearningEventMemory(
                event_type=str(payload.get("event_type", "learning_event")),
                content=str(payload.get("text") or row.content)[:300],
                conversation_id=payload.get("conversation_id"),
                created_at=row.created_at,
            ))

        preferences: dict[str, Any] = {}
        profile = await get_learner_profile(db, learner_id=lid)
        if profile and profile.preferences:
            preferences.update(profile.preferences)

        pref_rows = await get_learner_memories_by_type(
            db, learner_id=lid, memory_type="preference", limit=5,
        )
        for row in pref_rows:
            payload = _parse_json_content(row.content)
            key = payload.get("key") or row.memory_type
            preferences[str(key)] = payload.get("value") or payload.get("text") or row.content

        skill_weaknesses: list[str] = []
        snapshots = await get_latest_progress_snapshots(db, learner_id=lid, limit=1)
        if snapshots:
            skill_weaknesses = _weaknesses_from_snapshot(snapshots[0])

        memory_summary = _build_memory_summary(
            recurring=recurring,
            reflections=lesson_reflections,
            preferences=preferences,
            weaknesses=skill_weaknesses,
        )

        counts = {
            "recent_turns": len(recent_turns),
            "recurring_mistakes": len(recurring),
            "recent_errors": len(recent_errors),
            "lesson_reflections": len(lesson_reflections),
            "teacher_brain_decisions": len(decisions),
            "learning_events": len(events),
        }

        return MemoryBundle(
            recent_turns=recent_turns,
            recurring_mistakes=recurring,
            recent_errors=recent_errors,
            lesson_reflections=lesson_reflections,
            teacher_brain_decisions=decisions,
            learning_events=events,
            preferences=preferences,
            skill_weaknesses=skill_weaknesses,
            memory_summary=memory_summary,
            metadata=MemoryBundleMetadata(
                bundle_created_at=datetime.now(timezone.utc),
                source="memory_intelligence_v1",
                counts=counts,
                used_fallback=False,
            ),
        )

    async def build_bundle_with_session_recall(
        self,
        *,
        learner_id: str,
        tenant_id: str | None,
        session_id: str,
        conversation_id: str | None = None,
        message_history: list[dict[str, str]] | None = None,
        query: str | None = None,
    ) -> MemoryBundle:
        """Build bundle including Redis session recent_errors."""
        session = await load_session(session_id)
        session_errors = list(session.get("recent_errors", []))
        bundle = await self.build_bundle(
            learner_id=learner_id,
            tenant_id=tenant_id,
            session_id=session_id,
            conversation_id=conversation_id or session_id,
            message_history=message_history,
            session_recent_errors=session_errors,
        )
        if query and query.strip():
            bundle.recent_errors = list(dict.fromkeys(bundle.recent_errors))[:MAX_RECENT_ERRORS]
        return bundle

    async def write_teacher_brain_decision(
        self,
        *,
        learner_id: str,
        tenant_id: str | None,
        decision: dict[str, Any],
        conversation_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> None:
        if not tenant_id or not decision:
            return
        payload = {
            "intent": decision.get("intent"),
            "teaching_strategy": decision.get("teaching_strategy"),
            "skill_focus": decision.get("skill_focus"),
            "correction_mode": decision.get("correction_mode"),
            "next_prompt": decision.get("next_prompt"),
            "conversation_id": conversation_id,
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
        content = json.dumps(payload)
        try:
            if db is not None:
                await insert_learner_memory(
                    db,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    memory_type="teacher_brain_decision",
                    content=content,
                    weight=0.6,
                )
                return
            factory = get_session_factory()
            async with factory() as session:
                await set_tenant_context(session, str(tenant_id))
                await insert_learner_memory(
                    session,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    memory_type="teacher_brain_decision",
                    content=content,
                    weight=0.6,
                )
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.write_decision_failed", extra={"error": str(exc)})

    async def write_lesson_reflection(
        self,
        *,
        learner_id: str,
        tenant_id: str,
        executive_summary: str,
        recurring_mistakes: list[dict[str, Any]],
        recommended_next_focus: str | None = None,
        practice_recommendations: list[str] | None = None,
        conversation_id: str | None = None,
        report_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> None:
        payload = {
            "executive_summary": executive_summary[:1000],
            "recurring_mistakes_summary": recurring_mistakes[:8],
            "recommended_next_focus": recommended_next_focus,
            "practice_recommendations": (practice_recommendations or [])[:5],
            "conversation_id": conversation_id,
            "report_id": report_id,
        }
        content = json.dumps(payload)

        async def _write(sess: AsyncSession) -> None:
            lid = UUID(str(learner_id))
            if conversation_id and await has_recent_reflection_for_conversation(
                sess, learner_id=lid, conversation_id=conversation_id,
            ):
                return
            await insert_learner_memory(
                sess,
                tenant_id=UUID(str(tenant_id)),
                learner_id=lid,
                memory_type="lesson_reflection",
                content=content,
                weight=0.8,
            )

        try:
            if db is not None:
                await _write(db)
                return
            factory = get_session_factory()
            async with factory() as session:
                await set_tenant_context(session, str(tenant_id))
                await _write(session)
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.write_reflection_failed", extra={"error": str(exc)})

    async def write_learning_event(
        self,
        *,
        learner_id: str,
        tenant_id: str,
        event_type: str,
        detail: str | None = None,
        conversation_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> None:
        payload = {
            "event_type": event_type,
            "text": (detail or event_type)[:300],
            "conversation_id": conversation_id,
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
        content = json.dumps(payload)
        try:
            if db is not None:
                await insert_learner_memory(
                    db,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    memory_type="learning_event",
                    content=content,
                    weight=0.4,
                )
                return
            factory = get_session_factory()
            async with factory() as session:
                await set_tenant_context(session, str(tenant_id))
                await insert_learner_memory(
                    session,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    memory_type="learning_event",
                    content=content,
                    weight=0.4,
                )
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.write_event_failed", extra={"error": str(exc)})

    async def persist_lesson_report(
        self,
        *,
        learner_id: str,
        tenant_id: str,
        report_content: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> str | None:
        try:
            if db is not None:
                row = await insert_report(
                    db,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    report_type="lesson_completion",
                    content=report_content,
                )
                return str(row.id)
            factory = get_session_factory()
            async with factory() as session:
                await set_tenant_context(session, str(tenant_id))
                row = await insert_report(
                    session,
                    tenant_id=UUID(str(tenant_id)),
                    learner_id=UUID(str(learner_id)),
                    report_type="lesson_completion",
                    content=report_content,
                )
                await session.commit()
                return str(row.id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_intelligence.persist_report_failed", extra={"error": str(exc)})
            return None

    async def write_after_teacher_turn(
        self,
        *,
        session_id: str,
        learner_id: str,
        tenant_id: str | None,
        agent_output: dict[str, Any],
        conversation_id: str | None = None,
    ) -> None:
        """Cognitive/LangGraph post-turn write: teacher output + Teacher Brain metadata."""
        if tenant_id:
            await store_from_teacher_output(
                session_id,
                learner_id,
                agent_output,
                tenant_id=tenant_id,
            )
        teacher_brain = agent_output.get("teacher_brain") or {}
        if teacher_brain:
            await self.write_teacher_brain_decision(
                learner_id=learner_id,
                tenant_id=tenant_id,
                decision=teacher_brain,
                conversation_id=conversation_id or session_id,
            )
