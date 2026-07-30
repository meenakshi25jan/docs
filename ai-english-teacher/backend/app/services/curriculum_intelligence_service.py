"""Curriculum Intelligence v1 — recommendations, paths, and revision scheduling."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.curriculum_repository import (
    create_revision_item,
    get_completed_lessons,
    get_due_revision_items,
    get_revision_schedule,
    has_completed_assessment,
    mark_lesson_complete,
)
from app.repositories.student_intelligence_repository import get_error_tracking_rows
from app.schemas.curriculum_intelligence import (
    CurriculumLessonResponse,
    CurriculumRecommendationBundle,
    CurriculumSkillResponse,
    CurriculumTopicResponse,
    LearningPathResponse,
    LessonCompletionResponse,
    LessonRecommendationResponse,
    RevisionItemResponse,
)
from app.schemas.memory_intelligence import MemoryBundle
from app.schemas.student_intelligence import StudentSummaryResponse
from app.services.curriculum_registry import (
    CurriculumLesson,
    get_lesson,
    get_lessons,
    get_next_cefr_lesson,
    get_path,
    get_paths,
    get_skills,
    get_topics,
    get_grammar_lesson_for_mistake,
)
from app.services.student_intelligence_service import get_summary

logger = logging.getLogger(__name__)

EXAM_PERSONA_MAP = {
    "ielts": "exam-ielts-examiner",
    "pte": "exam-pte-coach",
    "toefl": "exam-toefl-trainer",
}


def _lesson_to_response(lesson: CurriculumLesson) -> CurriculumLessonResponse:
    return CurriculumLessonResponse(
        lesson_id=lesson.lesson_id,
        title=lesson.title,
        topic_id=lesson.topic_id,
        skill_id=lesson.skill_id,
        skill_focus=lesson.skill_focus,
        route=lesson.route,
        cefr_level=lesson.cefr_level,
        description=lesson.description,
        exam_tag=lesson.exam_tag,
        metadata=dict(lesson.metadata),
    )


def _recommendation_from_lesson(
    lesson: CurriculumLesson,
    reason: str,
    priority: int = 5,
) -> LessonRecommendationResponse:
    return LessonRecommendationResponse(
        lesson_id=lesson.lesson_id,
        title=lesson.title,
        reason=reason,
        route=lesson.route,
        skill_focus=lesson.skill_focus,
        priority=priority,
    )


def _revision_to_recommendation(item, reason: str) -> LessonRecommendationResponse:
    return LessonRecommendationResponse(
        lesson_id=item.lesson_id,
        title=item.title,
        reason=reason,
        route=item.route,
        skill_focus=item.skill_focus,
        priority=item.priority,
    )


class CurriculumIntelligenceService:
    """Deterministic curriculum recommendations and scheduling."""

    def list_topics(self) -> list[CurriculumTopicResponse]:
        return [CurriculumTopicResponse(id=t.id, title=t.title, description=t.description) for t in get_topics()]

    def list_skills(self, topic_id: str | None = None) -> list[CurriculumSkillResponse]:
        return [
            CurriculumSkillResponse(id=s.id, topic_id=s.topic_id, title=s.title, description=s.description)
            for s in get_skills(topic_id)
        ]

    def list_lessons(
        self,
        *,
        topic_id: str | None = None,
        skill_focus: str | None = None,
        cefr_level: str | None = None,
    ) -> list[CurriculumLessonResponse]:
        return [
            _lesson_to_response(l)
            for l in get_lessons(topic_id=topic_id, skill_focus=skill_focus, cefr_level=cefr_level)
        ]

    async def build_recommendations(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        memory_bundle: MemoryBundle | None = None,
    ) -> CurriculumRecommendationBundle:
        try:
            summary = await get_summary(db, user_id=user_id)
        except ValueError:
            placement = get_lesson("placement-assessment")
            if placement:
                primary = _recommendation_from_lesson(
                    placement,
                    "Complete a placement assessment to personalize your learning path.",
                    priority=1,
                )
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=[],
                    metadata={"rule": "placement_fallback", "has_assessment": False},
                )
            raise

        from app.repositories.student_intelligence_repository import get_learner_with_user

        learner, _ = await get_learner_with_user(db, user_id=user_id)
        if not learner:
            raise ValueError("Learner not found")

        return await self._build_recommendations_for_learner(
            db,
            learner_id=learner.id,
            tenant_id=learner.tenant_id,
            summary=summary,
            memory_bundle=memory_bundle,
        )

    async def _build_recommendations_for_learner(
        self,
        db: AsyncSession,
        *,
        learner_id: UUID,
        tenant_id: UUID,
        summary: StudentSummaryResponse,
        memory_bundle: MemoryBundle | None = None,
    ) -> CurriculumRecommendationBundle:
        completed = await get_completed_lessons(db, learner_id=learner_id)
        completed_ids = {c.lesson_id for c in completed}
        cefr = summary.profile.cefr_level or summary.profile.current_level or "B1"
        target_exam = (summary.profile.target_exam or "").lower()
        confidence = summary.profile.confidence_score or 0.5
        weakest = summary.weakest_skill or "grammar"

        alternates: list[LessonRecommendationResponse] = []
        rule_applied = "default_cefr_path"

        # RULE 1: No completed assessment
        if not await has_completed_assessment(db, learner_id=learner_id):
            placement = get_lesson("placement-assessment")
            if placement:
                primary = _recommendation_from_lesson(
                    placement,
                    "Start with a placement assessment so your teacher can personalize lessons.",
                    priority=1,
                )
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=placement.lesson_id),
                    metadata={"rule": "placement_assessment", "has_assessment": False},
                )

        # RULE 2: Due revision
        due_items = await get_due_revision_items(db, learner_id=learner_id, limit=1)
        if due_items:
            item = due_items[0]
            primary = _revision_to_recommendation(
                item,
                "A scheduled revision item is due — let's strengthen this before moving on.",
            )
            rule_applied = "revision_due"
            return CurriculumRecommendationBundle(
                primary=primary,
                alternates=self._skill_alternates(weakest, cefr, completed_ids, exclude=item.lesson_id),
                metadata={"rule": rule_applied, "revision_id": str(item.id)},
            )

        # RULE 3: Recurring mistake occurrence_count >= 3
        mistakes = await get_error_tracking_rows(db, learner_id=learner_id, limit=10)
        top_mistake = next((m for m in mistakes if (m.occurrence_count or 0) >= 3), None)
        if memory_bundle and memory_bundle.recurring_mistakes:
            rm = memory_bundle.recurring_mistakes[0]
            if rm.count >= 3:
                lesson = get_grammar_lesson_for_mistake(rm.category, cefr)
                if lesson:
                    primary = _recommendation_from_lesson(
                        lesson,
                        f"You've repeated this mistake ({rm.error}) — let's practice the related lesson.",
                        priority=2,
                    )
                    rule_applied = "recurring_mistake"
                    return CurriculumRecommendationBundle(
                        primary=primary,
                        alternates=self._skill_alternates(weakest, cefr, completed_ids, exclude=lesson.lesson_id),
                        metadata={"rule": rule_applied, "mistake": rm.error},
                    )
        if top_mistake and (top_mistake.occurrence_count or 0) >= 3:
            lesson = get_grammar_lesson_for_mistake(top_mistake.error_category or "grammar", cefr)
            if lesson:
                primary = _recommendation_from_lesson(
                    lesson,
                    f"Recurring mistake detected ({top_mistake.error_text}) — targeted practice recommended.",
                    priority=2,
                )
                rule_applied = "recurring_mistake_db"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._skill_alternates(weakest, cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied},
                )

        # RULE 4-6: weakest skill
        if weakest == "grammar":
            lesson = get_next_cefr_lesson(cefr, completed_ids)
            if lesson:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Your weakest skill is grammar — let's build accuracy with a focused lesson.",
                    priority=3,
                )
                rule_applied = "weak_grammar"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "weakest_skill": weakest},
                )

        if weakest == "pronunciation":
            lesson = get_lesson("pronunciation-practice")
            if lesson:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Pronunciation is your weakest area — practice clear sounds in conversation.",
                    priority=3,
                )
                rule_applied = "weak_pronunciation"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "weakest_skill": weakest},
                )

        if weakest in ("fluency", "speaking"):
            lesson = get_lesson("fluency-conversation") or get_lesson("speaking-everyday")
            if lesson:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Build fluency through guided conversation practice.",
                    priority=3,
                )
                rule_applied = "weak_fluency_speaking"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "weakest_skill": weakest},
                )

        # RULE 7: IELTS
        if "ielts" in target_exam:
            lesson = get_lesson(EXAM_PERSONA_MAP["ielts"])
            if lesson and lesson.lesson_id not in completed_ids:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Your target exam is IELTS — practice examiner-style speaking.",
                    priority=4,
                )
                rule_applied = "exam_ielts"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "target_exam": target_exam},
                )

        # RULE 8: PTE
        if "pte" in target_exam:
            lesson = get_lesson(EXAM_PERSONA_MAP["pte"])
            if lesson and lesson.lesson_id not in completed_ids:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Your target exam is PTE — practice timed speaking tasks.",
                    priority=4,
                )
                rule_applied = "exam_pte"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "target_exam": target_exam},
                )

        # RULE 9: Low confidence
        if confidence < 0.5:
            lesson = get_lesson("confidence-friendly-beginner")
            if lesson:
                primary = _recommendation_from_lesson(
                    lesson,
                    "Let's build confidence with a friendly, low-pressure conversation.",
                    priority=5,
                )
                rule_applied = "low_confidence"
                return CurriculumRecommendationBundle(
                    primary=primary,
                    alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                    metadata={"rule": rule_applied, "confidence_score": confidence},
                )

        # RULE 10: Next CEFR lesson
        lesson = get_next_cefr_lesson(cefr, completed_ids)
        if lesson:
            primary = _recommendation_from_lesson(
                lesson,
                f"Continue your {cefr} learning path with the next recommended lesson.",
                priority=6,
            )
            return CurriculumRecommendationBundle(
                primary=primary,
                alternates=self._default_alternates(cefr, completed_ids, exclude=lesson.lesson_id),
                metadata={"rule": "cefr_path", "cefr_level": cefr},
            )

        fallback = get_lesson("speaking-everyday")
        primary = _recommendation_from_lesson(
            fallback or CurriculumLesson(
                lesson_id="speaking-everyday",
                title="Everyday Conversation",
                topic_id="speaking",
                skill_id="speaking",
                skill_focus="speaking",
                route="/conversation?scenario=everyday",
            ),
            "Keep practicing with everyday conversation.",
            priority=10,
        )
        return CurriculumRecommendationBundle(
            primary=primary,
            alternates=[],
            metadata={"rule": "fallback"},
        )

    def _default_alternates(
        self,
        cefr: str,
        completed_ids: set[str],
        exclude: str | None = None,
        limit: int = 2,
    ) -> list[LessonRecommendationResponse]:
        alts: list[LessonRecommendationResponse] = []
        for lid in ("speaking-everyday", "vocabulary-daily", "fluency-conversation"):
            if lid == exclude or lid in completed_ids:
                continue
            lesson = get_lesson(lid)
            if lesson:
                alts.append(_recommendation_from_lesson(lesson, "Alternate practice option.", priority=8))
            if len(alts) >= limit:
                break
        if len(alts) < limit:
            next_lesson = get_next_cefr_lesson(cefr, completed_ids | {exclude or ""})
            if next_lesson and next_lesson.lesson_id != exclude:
                alts.append(_recommendation_from_lesson(next_lesson, "Continue on your learning path.", priority=7))
        return alts[:limit]

    def _skill_alternates(
        self,
        weakest: str,
        cefr: str,
        completed_ids: set[str],
        exclude: str | None = None,
    ) -> list[LessonRecommendationResponse]:
        return self._default_alternates(cefr, completed_ids, exclude=exclude)

    async def build_learning_path(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        path_type: str,
    ) -> LearningPathResponse:
        template = get_path(path_type)
        if not template:
            template = get_path("daily")
        if not template:
            return LearningPathResponse(path_id="daily", title="Daily Path", description="", items=[])

        from app.repositories.student_intelligence_repository import get_learner_with_user

        learner, _ = await get_learner_with_user(db, user_id=user_id)
        bundle = await self.build_recommendations(db, user_id=user_id) if learner else None

        items: list[LessonRecommendationResponse] = []

        if path_type == "daily":
            due = await get_due_revision_items(db, learner_id=learner.id, limit=1) if learner else []
            if due:
                items.append(_revision_to_recommendation(due[0], "Today's revision item."))
            elif bundle:
                items.append(bundle.primary)

            weak_lesson = None
            if bundle and bundle.metadata.get("weakest_skill") == "grammar":
                weak_lesson = get_next_cefr_lesson(
                    bundle.metadata.get("cefr_level", "B1"),
                    set(),
                )
            if not weak_lesson and learner:
                try:
                    summary = await get_summary(db, user_id=user_id)
                    weak_lesson = get_next_cefr_lesson(
                        summary.profile.cefr_level or "B1",
                        set(),
                    )
                except ValueError:
                    pass
            if weak_lesson:
                items.append(_recommendation_from_lesson(weak_lesson, "Weak skill focus for today.", priority=4))

            speaking = get_lesson("speaking-everyday")
            if speaking:
                items.append(_recommendation_from_lesson(speaking, "Daily speaking practice.", priority=5))

        elif path_type == "weekly":
            for lid in template.lesson_ids[:3]:
                lesson = get_lesson(lid)
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, "Weekly curriculum step.", priority=5))
            for lid in ("speaking-restaurant", "speaking-travel"):
                lesson = get_lesson(lid)
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, "Weekly speaking scenario.", priority=6))
            rev = await get_due_revision_items(db, learner_id=learner.id, limit=1) if learner else []
            if rev:
                items.append(_revision_to_recommendation(rev[0], "Scheduled revision this week."))
            placement = get_lesson("placement-assessment")
            if placement and learner and not await has_completed_assessment(db, learner_id=learner.id):
                items.append(_recommendation_from_lesson(placement, "Assessment checkpoint.", priority=2))

        elif path_type == "exam":
            for lid in template.lesson_ids:
                lesson = get_lesson(lid)
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, "Exam preparation step.", priority=3))

        elif path_type == "repair":
            if learner:
                summary = await get_summary(db, user_id=user_id)
                weakest = summary.weakest_skill or "grammar"
                if weakest == "pronunciation":
                    lesson = get_lesson("pronunciation-practice")
                elif weakest == "grammar":
                    lesson = get_next_cefr_lesson(summary.profile.cefr_level or "B1", set())
                else:
                    lesson = get_lesson("fluency-conversation")
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, f"Repair path for {weakest}.", priority=2))

        elif path_type == "confidence":
            for lid in template.lesson_ids:
                lesson = get_lesson(lid)
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, "Confidence-building activity.", priority=4))

        else:
            for lid in template.lesson_ids:
                lesson = get_lesson(lid)
                if lesson:
                    items.append(_recommendation_from_lesson(lesson, "Path lesson.", priority=5))

        return LearningPathResponse(
            path_id=template.path_id,
            title=template.title,
            description=template.description,
            items=items[:8],
        )

    async def schedule_revisions_from_signals(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        learner_id: UUID,
        memory_bundle: MemoryBundle | None = None,
    ) -> int:
        """Generate revision items from errors, completions, and reflections."""
        created = 0
        now = datetime.now(timezone.utc)

        mistakes = await get_error_tracking_rows(db, learner_id=learner_id, limit=15)
        for err in mistakes:
            count = err.occurrence_count or 1
            if count < 2:
                continue
            days = 1 if count >= 5 else 3
            lesson = get_grammar_lesson_for_mistake(err.error_category or "grammar")
            if not lesson:
                continue
            await create_revision_item(
                db,
                tenant_id=tenant_id,
                learner_id=learner_id,
                lesson_id=lesson.lesson_id,
                source_type="error_tracking",
                source_ref=err.error_text[:200],
                title=f"Revision: {lesson.title}",
                skill_focus=lesson.skill_focus,
                route=lesson.route,
                due_at=now + timedelta(days=days),
                priority=2 if count >= 5 else 4,
                metadata={"occurrence_count": count, "error": err.error_text},
            )
            created += 1

        completions = await get_completed_lessons(db, learner_id=learner_id, limit=10)
        for comp in completions:
            score = float(comp.score or 0)
            if score < 70:
                continue
            days = 30 if score >= 90 else 7
            await create_revision_item(
                db,
                tenant_id=tenant_id,
                learner_id=learner_id,
                lesson_id=comp.lesson_id,
                source_type="lesson_completion",
                source_ref=str(comp.id),
                title=f"Review: {comp.title}",
                skill_focus=comp.skill_focus,
                route=comp.route,
                due_at=comp.completed_at + timedelta(days=days),
                priority=5,
                metadata={"score": score},
            )
            created += 1

        if memory_bundle and memory_bundle.lesson_reflections:
            ref = memory_bundle.lesson_reflections[0]
            focus = ref.recommended_focus or "grammar"
            lesson = get_grammar_lesson_for_mistake(focus)
            if lesson:
                await create_revision_item(
                    db,
                    tenant_id=tenant_id,
                    learner_id=learner_id,
                    lesson_id=lesson.lesson_id,
                    source_type="lesson_reflection",
                    source_ref=ref.conversation_id,
                    title=f"Review focus: {lesson.title}",
                    skill_focus=lesson.skill_focus,
                    route=lesson.route,
                    due_at=now + timedelta(days=3),
                    priority=3,
                    metadata={"reflection": ref.content[:200]},
                )
                created += 1

        return created

    async def complete_lesson(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        learner_id: UUID,
        lesson_id: str,
        title: str | None = None,
        skill_focus: str | None = None,
        route: str | None = None,
        score: float | None = None,
        metadata: dict | None = None,
    ) -> LessonCompletionResponse:
        lesson = get_lesson(lesson_id)
        row = await mark_lesson_complete(
            db,
            tenant_id=tenant_id,
            learner_id=learner_id,
            lesson_id=lesson_id,
            title=title or (lesson.title if lesson else lesson_id),
            skill_focus=skill_focus or (lesson.skill_focus if lesson else "general"),
            route=route or (lesson.route if lesson else "/conversation"),
            score=score,
            metadata=metadata,
        )
        await self.schedule_revisions_from_signals(db, tenant_id=tenant_id, learner_id=learner_id)
        return LessonCompletionResponse(
            id=str(row.id),
            lesson_id=row.lesson_id,
            title=row.title,
            skill_focus=row.skill_focus,
            route=row.route,
            score=float(row.score) if row.score is not None else None,
            completed_at=row.completed_at,
        )

    async def list_revision_schedule(
        self,
        db: AsyncSession,
        *,
        learner_id: UUID,
    ) -> list[RevisionItemResponse]:
        rows = await get_revision_schedule(db, learner_id=learner_id)
        return [
            RevisionItemResponse(
                id=str(r.id),
                lesson_id=r.lesson_id,
                title=r.title,
                reason=f"Scheduled revision ({r.source_type}).",
                route=r.route,
                skill_focus=r.skill_focus,
                due_at=r.due_at,
                status=r.status,
                priority=r.priority,
                source_type=r.source_type,
            )
            for r in rows
        ]

    def get_primary_recommendation_metadata(
        self,
        bundle: CurriculumRecommendationBundle,
    ) -> dict[str, Any]:
        primary = bundle.primary
        return {
            "lesson_id": primary.lesson_id,
            "title": primary.title,
            "reason": primary.reason,
            "route": primary.route,
            "skill_focus": primary.skill_focus,
        }
