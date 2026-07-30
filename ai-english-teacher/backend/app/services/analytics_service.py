"""Analytics & Insights v1 — deterministic aggregation over existing data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LearnerProfile, ProgressSnapshot
from app.repositories.analytics_repository import (
    default_since_days,
    get_assistant_message_metadata,
    get_completed_assessments,
    get_governance_learning_events,
    get_learner_by_user_id,
    get_lesson_completions,
    get_progress_snapshots,
    get_revision_schedule_rows,
    get_voice_analyses,
)
from app.repositories.student_intelligence_repository import get_error_tracking_rows
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    AnalyticsScorecard,
    CurriculumAnalyticsResponse,
    GovernanceAnalyticsResponse,
    InsightItem,
    KnowledgeAnalyticsResponse,
    LearnerInsightsResponse,
    MetricPoint,
    ProgressAnalyticsResponse,
    SkillTrendPoint,
)
from app.services.governance_service import get_stored_evaluations
from app.services.student_intelligence_service import get_summary

ANALYTICS_VERSION = "analytics_v1"

SNAPSHOT_SKILL_FIELDS = {
    "grammar": "grammar_score",
    "vocabulary": "vocabulary_score",
    "writing": "writing_score",
    "reading": "reading_score",
    "listening": "listening_score",
    "speaking": "speaking_score",
}

VOICE_SKILL_FIELDS = {
    "grammar": "grammar_score",
    "vocabulary": "vocabulary_score",
    "speaking": "overall_score",
    "pronunciation": "pronunciation_score",
    "fluency": "fluency_score",
}

SKILL_LABELS = {
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "writing": "Writing",
    "reading": "Reading",
    "listening": "Listening",
    "speaking": "Speaking",
    "pronunciation": "Pronunciation",
    "fluency": "Fluency",
    "confidence": "Confidence",
}


def _clamp01(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _status_from_score(score: float) -> str:
    if score >= 0.75:
        return "good"
    if score >= 0.5:
        return "fair"
    return "needs_attention"


def _status_from_value(score: float) -> str:
    """Status for 0–100 skill scores."""
    if score >= 75:
        return "good"
    if score >= 50:
        return "fair"
    return "needs_attention"


def trend_from_delta(delta: float | None) -> str:
    if delta is None:
        return "stable"
    if delta > 2:
        return "improving"
    if delta < -2:
        return "declining"
    return "stable"


def _snapshot_value(snapshot: ProgressSnapshot, skill: str) -> float | None:
    field = SNAPSHOT_SKILL_FIELDS.get(skill)
    if not field:
        if skill == "confidence":
            val = snapshot.confidence_score
            return float(val) if val is not None else None
        return None
    val = getattr(snapshot, field, None)
    return float(val) if val is not None else None


def _voice_value(row: Any, skill: str) -> float | None:
    field = VOICE_SKILL_FIELDS.get(skill)
    if not field:
        return None
    val = getattr(row, field, None)
    return float(val) if val is not None else None


def _build_skill_trend_from_values(
    skill: str,
    points: list[tuple[datetime, float]],
) -> SkillTrendPoint:
    label = SKILL_LABELS.get(skill, skill)
    series = [
        {"timestamp": ts.isoformat(), "value": round(v, 2)}
        for ts, v in points
    ]
    current = points[-1][1] if points else None
    previous = points[-2][1] if len(points) >= 2 else None
    delta = round(current - previous, 2) if current is not None and previous is not None else None
    trend = trend_from_delta(delta)
    status = _status_from_value(current) if current is not None else "fair"
    return SkillTrendPoint(
        skill=skill,
        label=label,
        points=series,
        current_value=current,
        previous_value=previous,
        delta=delta,
        trend=trend,
        status=status,
    )


class AnalyticsService:
    async def _resolve_learner(self, db: AsyncSession, user_id: UUID) -> tuple[LearnerProfile | None, UUID | None]:
        learner = await get_learner_by_user_id(db, user_id)
        if not learner:
            return None, None
        return learner, learner.id

    async def get_progress(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> ProgressAnalyticsResponse:
        _, learner_id = await self._resolve_learner(db, user_id)
        if not learner_id:
            return ProgressAnalyticsResponse(has_data=False)

        snapshots = await get_progress_snapshots(db, learner_id=learner_id)
        voice_rows = await get_voice_analyses(db, learner_id=learner_id)

        skill_trends: list[SkillTrendPoint] = []
        for skill in ("grammar", "vocabulary", "speaking", "reading", "writing", "listening"):
            points: list[tuple[datetime, float]] = []
            for snap in snapshots:
                val = _snapshot_value(snap, skill)
                if val is not None:
                    points.append((snap.snapshot_at, val))
            if not points and skill in VOICE_SKILL_FIELDS:
                for row in voice_rows:
                    val = _voice_value(row, skill)
                    if val is not None:
                        points.append((row.created_at, val))
            if points:
                skill_trends.append(_build_skill_trend_from_values(skill, points))

        for skill in ("pronunciation", "fluency"):
            points = []
            for row in voice_rows:
                val = _voice_value(row, skill)
                if val is not None:
                    points.append((row.created_at, val))
            if points:
                skill_trends.append(_build_skill_trend_from_values(skill, points))

        confidence_points: list[tuple[datetime, float]] = []
        for snap in snapshots:
            if snap.confidence_score is not None:
                confidence_points.append((snap.snapshot_at, float(snap.confidence_score) * 100))

        confidence_trend = (
            _build_skill_trend_from_values("confidence", confidence_points)
            if confidence_points
            else None
        )

        cefr_history = [
            {
                "timestamp": snap.snapshot_at.isoformat(),
                "cefr_estimate": snap.cefr_estimate,
                "ielts_estimate": float(snap.ielts_estimate) if snap.ielts_estimate is not None else None,
                "pte_estimate": snap.pte_estimate,
            }
            for snap in snapshots
            if snap.cefr_estimate
        ]

        metrics = [
            MetricPoint(
                label=t.label,
                score=t.current_value,
                current_value=t.current_value,
                previous_value=t.previous_value,
                delta=t.delta,
                trend=t.trend,
                status=t.status,
            )
            for t in skill_trends
        ]

        has_data = bool(skill_trends or cefr_history or confidence_trend)
        return ProgressAnalyticsResponse(
            skill_trends=skill_trends,
            cefr_history=cefr_history,
            confidence_trend=confidence_trend,
            metrics=metrics,
            has_data=has_data,
            metadata={"version": ANALYTICS_VERSION, "snapshot_count": len(snapshots)},
        )

    def _aggregate_governance_from_messages(
        self,
        messages: list[dict],
        learner_id: UUID,
    ) -> GovernanceAnalyticsResponse:
        gov_rows: list[dict] = []
        for meta in messages:
            gov = meta.get("governance")
            if gov and isinstance(gov, dict):
                gov_rows.append(gov)

        stored = get_stored_evaluations(str(learner_id), limit=100)
        for item in stored:
            gov_rows.append(
                {
                    "teacher_response_score": item.teacher_response_score,
                    "grounding_score": item.grounding_score,
                    "curriculum_score": item.curriculum_score,
                    "memory_score": item.memory_score,
                    "overall_score": item.overall_score,
                    "warnings": item.warnings,
                    "status": item.status,
                }
            )

        if not gov_rows:
            return GovernanceAnalyticsResponse(has_data=False)

        n = len(gov_rows)
        warning_freq: dict[str, int] = {}
        status_breakdown: dict[str, int] = {"good": 0, "fair": 0, "needs_attention": 0}

        for row in gov_rows:
            status = row.get("status") or "fair"
            if status in status_breakdown:
                status_breakdown[status] += 1
            else:
                status_breakdown["fair"] += 1
            for w in row.get("warnings") or []:
                warning_freq[w] = warning_freq.get(w, 0) + 1

        def avg(key: str) -> float:
            vals = [float(r.get(key) or 0) for r in gov_rows if r.get(key) is not None]
            return round(sum(vals) / len(vals), 3) if vals else 0.0

        score_trends = [
            MetricPoint(
                label="Teacher response",
                score=avg("teacher_response_score") * 100,
                current_value=avg("teacher_response_score"),
                trend="stable",
                status=_status_from_score(avg("teacher_response_score")),
            ),
            MetricPoint(
                label="Grounding",
                score=avg("grounding_score") * 100,
                current_value=avg("grounding_score"),
                trend="stable",
                status=_status_from_score(avg("grounding_score")),
            ),
            MetricPoint(
                label="Overall",
                score=avg("overall_score") * 100,
                current_value=avg("overall_score"),
                trend="stable",
                status=_status_from_score(avg("overall_score")),
            ),
        ]

        return GovernanceAnalyticsResponse(
            avg_teacher_response_score=avg("teacher_response_score"),
            avg_grounding_score=avg("grounding_score"),
            avg_curriculum_score=avg("curriculum_score"),
            avg_memory_score=avg("memory_score"),
            avg_overall_score=avg("overall_score"),
            evaluation_count=n,
            warning_count=sum(warning_freq.values()),
            warning_frequency=warning_freq,
            status_breakdown=status_breakdown,
            score_trends=score_trends,
            has_data=True,
            metadata={"version": ANALYTICS_VERSION, "source": "messages_and_memory"},
        )

    async def get_governance(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> GovernanceAnalyticsResponse:
        _, learner_id = await self._resolve_learner(db, user_id)
        if not learner_id:
            return GovernanceAnalyticsResponse(has_data=False)

        since = default_since_days(90)
        messages = await get_assistant_message_metadata(
            db, learner_id=learner_id, since=since
        )
        result = self._aggregate_governance_from_messages(messages, learner_id)
        events = await get_governance_learning_events(db, learner_id=learner_id)
        if events and not result.has_data:
            result.has_data = True
            result.metadata["governance_events"] = len(events)
        return result

    async def get_curriculum(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> CurriculumAnalyticsResponse:
        _, learner_id = await self._resolve_learner(db, user_id)
        if not learner_id:
            return CurriculumAnalyticsResponse(has_data=False)

        completions = await get_lesson_completions(db, learner_id=learner_id)
        revisions = await get_revision_schedule_rows(db, learner_id=learner_id)
        since = default_since_days(90)
        messages = await get_assistant_message_metadata(db, learner_id=learner_id, since=since)

        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        lessons_7d = sum(1 for c in completions if c.completed_at >= week_ago)
        lessons_30d = sum(1 for c in completions if c.completed_at >= month_ago)

        skill_dist: dict[str, int] = {}
        for c in completions:
            skill_dist[c.skill_focus] = skill_dist.get(c.skill_focus, 0) + 1

        pending = sum(1 for r in revisions if r.status in ("scheduled", "pending", "due"))
        completed_rev = sum(1 for r in revisions if r.status == "completed")
        overdue = sum(
            1 for r in revisions
            if r.status in ("scheduled", "pending", "due") and r.due_at < now
        )

        rec_count = sum(
            1 for m in messages
            if m.get("curriculum_recommendation")
        )

        most_recent = None
        if completions:
            c = completions[0]
            most_recent = {
                "lesson_id": c.lesson_id,
                "title": c.title,
                "skill_focus": c.skill_focus,
                "score": float(c.score) if c.score is not None else None,
                "completed_at": c.completed_at.isoformat(),
            }

        velocity = None
        if len(completions) >= 2:
            oldest = completions[-1].completed_at
            newest = completions[0].completed_at
            weeks = max((newest - oldest).days / 7.0, 1.0)
            velocity = round(len(completions) / weeks, 2)

        has_data = bool(completions or revisions or rec_count)
        return CurriculumAnalyticsResponse(
            lessons_completed=len(completions),
            lessons_completed_7d=lessons_7d,
            lessons_completed_30d=lessons_30d,
            most_recent_lesson=most_recent,
            revision_pending=pending,
            revision_completed=completed_rev,
            revision_overdue=overdue,
            recommended_lesson_count=rec_count,
            skill_focus_distribution=skill_dist,
            completion_velocity_per_week=velocity,
            has_data=has_data,
            metadata={"version": ANALYTICS_VERSION},
        )

    async def get_knowledge(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> KnowledgeAnalyticsResponse:
        _, learner_id = await self._resolve_learner(db, user_id)
        if not learner_id:
            return KnowledgeAnalyticsResponse(has_data=False)

        since = default_since_days(90)
        messages = await get_assistant_message_metadata(db, learner_id=learner_id, since=since)

        grounding_rows: list[dict] = []
        quality_scores: list[float] = []
        for meta in messages:
            kg = meta.get("knowledge_grounding")
            if kg and isinstance(kg, dict):
                grounding_rows.append(kg)
            gov = meta.get("governance")
            if gov and isinstance(gov, dict) and gov.get("grounding_score") is not None:
                quality_scores.append(float(gov["grounding_score"]))

        if not grounding_rows:
            return KnowledgeAnalyticsResponse(has_data=False)

        chunk_counts = [int(g.get("chunk_count") or 0) for g in grounding_rows]
        fallback_count = sum(1 for g in grounding_rows if g.get("fallback_used"))
        source_dist: dict[str, int] = {}
        for g in grounding_rows:
            for src in g.get("sources") or []:
                source_dist[str(src)] = source_dist.get(str(src), 0) + 1

        with_chunks = sum(1 for c in chunk_counts if c > 0)
        availability = round(with_chunks / len(grounding_rows), 3) if grounding_rows else 0.0

        return KnowledgeAnalyticsResponse(
            grounding_count=len(grounding_rows),
            avg_chunk_count=round(sum(chunk_counts) / len(chunk_counts), 2) if chunk_counts else 0.0,
            fallback_usage_count=fallback_count,
            grounding_availability_rate=availability,
            source_distribution=source_dist,
            avg_grounding_quality_score=(
                round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else None
            ),
            has_data=True,
            metadata={"version": ANALYTICS_VERSION, "message_sample": len(messages)},
        )

    async def get_insights(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> LearnerInsightsResponse:
        learner, learner_id = await self._resolve_learner(db, user_id)
        if not learner_id:
            return LearnerInsightsResponse(has_data=False)

        insights: list[InsightItem] = []

        try:
            summary = await get_summary(db, user_id=user_id)
            weakest = summary.weakest_skill
            if weakest:
                label = SKILL_LABELS.get(weakest, weakest)
                insights.append(
                    InsightItem(
                        type="weakness",
                        severity="warning",
                        title=f"{label} needs attention",
                        description=f"{label} is currently your weakest skill. Continue {label.lower()}-focused practice.",
                        recommended_action=f"Practice {label.lower()}",
                        source="student_intelligence",
                        metadata={"skill": weakest},
                    )
                )

            if summary.has_data:
                progress_resp = await self.get_progress(db, user_id)
                if progress_resp.confidence_trend and progress_resp.confidence_trend.trend == "improving":
                    insights.append(
                        InsightItem(
                            type="progress",
                            severity="info",
                            title="Confidence is improving",
                            description="Your confidence score is improving based on recent progress snapshots.",
                            recommended_action="Keep practicing regularly",
                            source="progress_analytics",
                        )
                    )
        except Exception:  # noqa: BLE001
            pass

        errors = await get_error_tracking_rows(db, learner_id=learner_id, limit=10)
        high_count = sum(1 for e in errors if e.occurrence_count >= 2)
        if high_count >= 2:
            insights.append(
                InsightItem(
                    type="mistake",
                    severity="warning",
                    title="Recurring mistakes detected",
                    description="You have recurring mistakes that should be revised.",
                    recommended_action="Review grammar class or conversation corrections",
                    source="error_tracking",
                    metadata={"recurring_count": high_count},
                )
            )

        gov = await self.get_governance(db, user_id)
        if gov.warning_frequency.get("grounding_fallback_used"):
            insights.append(
                InsightItem(
                    type="governance",
                    severity="info",
                    title="Fallback knowledge grounding used",
                    description="Some lessons used fallback knowledge grounding. Consider reviewing knowledge coverage.",
                    recommended_action="Complete targeted lessons for weak skills",
                    source="governance_analytics",
                )
            )

        curriculum = await self.get_curriculum(db, user_id)
        if curriculum.revision_pending > 0:
            insights.append(
                InsightItem(
                    type="curriculum",
                    severity="warning",
                    title="Pending revisions",
                    description="You have pending revision items.",
                    recommended_action="Complete scheduled revisions",
                    source="curriculum_analytics",
                    metadata={"pending": curriculum.revision_pending},
                )
            )

        if curriculum.lessons_completed_7d >= 3:
            insights.append(
                InsightItem(
                    type="curriculum",
                    severity="info",
                    title="Strong lesson activity",
                    description=f"You completed {curriculum.lessons_completed_7d} lessons in the last 7 days.",
                    recommended_action="Maintain your learning streak",
                    source="curriculum_analytics",
                )
            )

        has_data = bool(insights)
        return LearnerInsightsResponse(
            insights=insights,
            has_data=has_data,
            metadata={"version": ANALYTICS_VERSION, "learner_id": str(learner_id)},
        )

    async def get_overview(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID | None = None,
    ) -> AnalyticsOverviewResponse:
        progress = await self.get_progress(db, user_id, tenant_id)
        governance = await self.get_governance(db, user_id, tenant_id)
        curriculum = await self.get_curriculum(db, user_id, tenant_id)
        knowledge = await self.get_knowledge(db, user_id, tenant_id)

        progress_score = 0.5
        if progress.skill_trends:
            vals = [t.current_value for t in progress.skill_trends if t.current_value is not None]
            if vals:
                progress_score = _clamp01(sum(vals) / len(vals) / 100.0)

        gov_score = governance.avg_overall_score if governance.has_data else 0.5
        curriculum_score = 0.5
        if curriculum.has_data and curriculum.lessons_completed > 0:
            curriculum_score = _clamp01(min(1.0, curriculum.lessons_completed_30d / 10.0))

        knowledge_score = knowledge.grounding_availability_rate if knowledge.has_data else 0.5
        teaching_score = governance.avg_teacher_response_score if governance.has_data else 0.5

        overall = _clamp01(
            progress_score * 0.35
            + gov_score * 0.2
            + curriculum_score * 0.15
            + knowledge_score * 0.15
            + teaching_score * 0.15
        )

        scorecard = AnalyticsScorecard(
            overall_health=overall,
            progress=progress_score,
            governance=gov_score,
            curriculum=curriculum_score,
            knowledge=knowledge_score,
            teaching=teaching_score,
            status=_status_from_score(overall),
            updated_at=datetime.now(timezone.utc),
            metadata={"version": ANALYTICS_VERSION},
        )

        metrics: list[MetricPoint] = []
        metrics.extend(progress.metrics[:4])
        if governance.has_data:
            metrics.extend(governance.score_trends)
        if curriculum.has_data:
            metrics.append(
                MetricPoint(
                    label="Lessons completed (30d)",
                    current_value=float(curriculum.lessons_completed_30d),
                    trend="stable",
                    status="good" if curriculum.lessons_completed_30d >= 2 else "fair",
                )
            )
        if knowledge.has_data:
            metrics.append(
                MetricPoint(
                    label="Grounding availability",
                    score=knowledge.grounding_availability_rate * 100,
                    current_value=knowledge.grounding_availability_rate,
                    trend="stable",
                    status=_status_from_score(knowledge.grounding_availability_rate),
                )
            )

        has_data = any(
            [
                progress.has_data,
                governance.has_data,
                curriculum.has_data,
                knowledge.has_data,
            ]
        )

        return AnalyticsOverviewResponse(
            scorecard=scorecard,
            metrics=metrics,
            period="30d",
            has_data=has_data,
            metadata={"version": ANALYTICS_VERSION},
        )
