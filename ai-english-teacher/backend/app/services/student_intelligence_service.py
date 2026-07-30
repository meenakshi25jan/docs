"""Student Intelligence v1 — learner state for personalized teaching."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProgressSnapshot
from app.repositories.student_intelligence_repository import (
    get_assessment_skill_scores,
    get_error_tracking_rows,
    get_latest_progress_snapshots,
    get_learner_with_user,
    get_progress_history_count,
    get_voice_analysis_averages,
)
from app.schemas.student_intelligence import (
    LearningPreferencesResponse,
    LearningPreferencesUpdate,
    ProgressSnapshotSummary,
    SkillScoreDetail,
    StudentMistake,
    StudentMistakesResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
    StudentSkillsResponse,
    StudentSummaryResponse,
)
from app.scoring.engine import score_to_cefr

CORE_SKILLS = (
    "speaking",
    "listening",
    "reading",
    "writing",
    "grammar",
    "vocabulary",
    "pronunciation",
    "fluency",
)

FOCUS_RECOMMENDATIONS: dict[str, str] = {
    "pronunciation": "pronunciation practice",
    "fluency": "conversation practice",
    "grammar": "grammar class",
    "vocabulary": "vocabulary practice",
    "speaking": "conversation practice",
    "listening": "listening practice",
    "reading": "reading practice",
    "writing": "writing practice",
}


def _pref(learner_preferences: dict, key: str, default: Any = None) -> Any:
    return learner_preferences.get(key, default)


def _merge_preferences(learner_preferences: dict, updates: dict) -> dict:
    merged = dict(learner_preferences or {})
    for key, value in updates.items():
        if value is not None:
            merged[key] = value
    return merged


def _severity_from_count(count: int) -> str:
    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def _trend_from_delta(delta: float | None) -> str:
    if delta is None:
        return "unknown"
    if delta > 2:
        return "up"
    if delta < -2:
        return "down"
    return "stable"


def _snapshot_skill_value(snapshot: ProgressSnapshot, skill: str) -> float | None:
    mapping = {
        "grammar": snapshot.grammar_score,
        "vocabulary": snapshot.vocabulary_score,
        "writing": snapshot.writing_score,
        "reading": snapshot.reading_score,
        "listening": snapshot.listening_score,
        "speaking": snapshot.speaking_score,
    }
    val = mapping.get(skill)
    return float(val) if val is not None else None


async def _resolve_learner(
    db: AsyncSession,
    user_id: UUID,
) -> tuple[Any, Any]:
    learner, user = await get_learner_with_user(db, user_id=user_id)
    if not learner or not user:
        raise ValueError("Learner profile not found")
    return learner, user


async def get_profile(db: AsyncSession, *, user_id: UUID) -> StudentProfileResponse:
    learner, user = await _resolve_learner(db, user_id)
    snapshots = await get_latest_progress_snapshots(db, learner_id=learner.id, limit=1)
    latest = snapshots[0] if snapshots else None
    prefs = learner.preferences or {}

    name = None
    if user.first_name or user.last_name:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    return StudentProfileResponse(
        user_id=user.id,
        name=name or None,
        cefr_level=learner.current_cefr,
        ielts_estimate=float(learner.ielts_estimate) if learner.ielts_estimate else None,
        pte_estimate=learner.pte_estimate,
        confidence_score=float(latest.confidence_score) if latest and latest.confidence_score else None,
        learning_goal=_pref(prefs, "learning_goal"),
        current_level=learner.current_cefr,
        target_exam=learner.target_exam or _pref(prefs, "target_exam"),
        created_at=learner.created_at,
        updated_at=latest.snapshot_at if latest else learner.created_at,
    )


async def update_profile(
    db: AsyncSession,
    *,
    user_id: UUID,
    updates: StudentProfileUpdate,
) -> StudentProfileResponse:
    learner, _ = await _resolve_learner(db, user_id)
    prefs = dict(learner.preferences or {})
    patch = updates.model_dump(exclude_unset=True)

    if "target_exam" in patch:
        learner.target_exam = patch.pop("target_exam")

    pref_fields = {
        "learning_goal": patch.get("learning_goal"),
        "target_cefr_level": patch.get("target_cefr_level"),
        "preferred_learning_style": patch.get("preferred_learning_style"),
        "daily_goal_minutes": patch.get("daily_goal_minutes"),
    }
    learner.preferences = _merge_preferences(prefs, {k: v for k, v in pref_fields.items() if v is not None})
    await db.flush()
    return await get_profile(db, user_id=user_id)


async def build_skills(db: AsyncSession, *, learner_id: UUID) -> StudentSkillsResponse:
    snapshots = await get_latest_progress_snapshots(db, learner_id=learner_id, limit=2)
    latest = snapshots[0] if snapshots else None
    previous = snapshots[1] if len(snapshots) > 1 else None
    voice_avg = await get_voice_analysis_averages(db, learner_id=learner_id)
    assessment_scores = await get_assessment_skill_scores(db, learner_id=learner_id)

    skills: dict[str, SkillScoreDetail] = {}

    for skill in CORE_SKILLS:
        score: float | None = None
        last_updated: datetime | None = None

        if latest:
            snap_val = _snapshot_skill_value(latest, skill)
            if snap_val is not None:
                score = snap_val
                last_updated = latest.snapshot_at

        if score is None and skill in voice_avg and voice_avg.get(skill) is not None:
            score = float(voice_avg[skill])
            last_updated = voice_avg.get("last_updated") or last_updated

        if score is None and skill in assessment_scores:
            score = assessment_scores[skill]
            last_updated = last_updated

        if score is None:
            skills[skill] = SkillScoreDetail(score=0, level=None, trend="unknown", last_updated=None)
            continue

        prev_score: float | None = None
        if previous:
            prev_score = _snapshot_skill_value(previous, skill)

        delta = (score - prev_score) if prev_score is not None else None
        skills[skill] = SkillScoreDetail(
            score=round(score, 1),
            level=score_to_cefr(score),
            trend=_trend_from_delta(delta),
            last_updated=last_updated,
        )

    return StudentSkillsResponse(**skills)


async def get_mistakes(db: AsyncSession, *, learner_id: UUID, limit: int = 20) -> StudentMistakesResponse:
    rows = await get_error_tracking_rows(db, learner_id=learner_id, limit=limit)
    mistakes = [
        StudentMistake(
            mistake_type=row.error_type,
            original_text=row.error_text,
            corrected_text=row.correction,
            explanation=row.error_category,
            severity=_severity_from_count(row.occurrence_count or 1),
            occurrence_count=row.occurrence_count or 1,
            last_seen_at=row.last_seen_at,
        )
        for row in rows
    ]
    return StudentMistakesResponse(mistakes=mistakes, total=len(mistakes))


async def get_preferences(db: AsyncSession, *, user_id: UUID) -> LearningPreferencesResponse:
    learner, _ = await _resolve_learner(db, user_id)
    prefs = learner.preferences or {}
    return LearningPreferencesResponse(
        learning_goal=_pref(prefs, "learning_goal"),
        target_cefr_level=_pref(prefs, "target_cefr_level"),
        target_exam=learner.target_exam or _pref(prefs, "target_exam"),
        preferred_learning_style=_pref(prefs, "preferred_learning_style"),
        daily_goal_minutes=_pref(prefs, "daily_goal_minutes"),
    )


async def update_preferences(
    db: AsyncSession,
    *,
    user_id: UUID,
    updates: LearningPreferencesUpdate,
) -> LearningPreferencesResponse:
    learner, _ = await _resolve_learner(db, user_id)
    patch = updates.model_dump(exclude_unset=True)
    if "target_exam" in patch:
        learner.target_exam = patch.pop("target_exam")
    learner.preferences = _merge_preferences(learner.preferences or {}, patch)
    await db.flush()
    return await get_preferences(db, user_id=user_id)


def _recommend_focus(skills: StudentSkillsResponse, has_data: bool) -> str:
    if not has_data:
        return "placement assessment"

    scored: dict[str, float] = {}
    for name in CORE_SKILLS:
        detail = getattr(skills, name)
        if detail.score > 0:
            scored[name] = detail.score

    if not scored:
        return "placement assessment"

    weakest = min(scored, key=scored.get)
    return FOCUS_RECOMMENDATIONS.get(weakest, "conversation practice")


async def get_summary(db: AsyncSession, *, user_id: UUID) -> StudentSummaryResponse:
    learner, _ = await _resolve_learner(db, user_id)
    profile = await get_profile(db, user_id=user_id)
    skills = await build_skills(db, learner_id=learner.id)
    mistakes = await get_mistakes(db, learner_id=learner.id, limit=5)
    snapshots = await get_latest_progress_snapshots(db, learner_id=learner.id, limit=1)
    latest = snapshots[0] if snapshots else None
    history_count = await get_progress_history_count(db, learner_id=learner.id)
    voice_avg = await get_voice_analysis_averages(db, learner_id=learner.id)
    assessment_scores = await get_assessment_skill_scores(db, learner_id=learner.id)
    has_data = history_count > 0 or bool(voice_avg) or bool(assessment_scores) or bool(mistakes.mistakes)

    scored = {
        name: detail.score
        for name, detail in [
            ("speaking", skills.speaking),
            ("listening", skills.listening),
            ("reading", skills.reading),
            ("writing", skills.writing),
            ("grammar", skills.grammar),
            ("vocabulary", skills.vocabulary),
            ("pronunciation", skills.pronunciation),
            ("fluency", skills.fluency),
        ]
        if detail.score > 0
    }
    strongest = max(scored, key=scored.get) if scored else None
    weakest = min(scored, key=scored.get) if scored else None

    progress_summary = None
    if latest:
        progress_summary = ProgressSnapshotSummary(
            snapshot_at=latest.snapshot_at,
            cefr_estimate=latest.cefr_estimate,
            ielts_estimate=float(latest.ielts_estimate) if latest.ielts_estimate else None,
            pte_estimate=latest.pte_estimate,
            confidence_score=float(latest.confidence_score) if latest.confidence_score else None,
            speaking_score=float(latest.speaking_score) if latest.speaking_score else None,
            grammar_score=float(latest.grammar_score) if latest.grammar_score else None,
        )

    return StudentSummaryResponse(
        profile=profile,
        skills=skills,
        top_mistakes=mistakes.mistakes[:5],
        latest_progress=progress_summary,
        strongest_skill=strongest,
        weakest_skill=weakest,
        recommended_next_focus=_recommend_focus(skills, has_data),
        has_data=has_data,
    )
