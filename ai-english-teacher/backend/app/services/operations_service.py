"""Enterprise Operations v1 — tenant-scoped operations and dashboards."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import TokenPayload
from app.repositories.operations_repository import (
    count_active_learners_since,
    count_learners_in_tenant,
    count_lesson_completions_since,
    count_lesson_completions_tenant_since,
    count_overdue_revisions,
    count_users_in_tenant,
    get_governance_aggregate_for_learner,
    get_governance_aggregate_for_tenant,
    get_knowledge_aggregate_for_tenant,
    get_last_activity_at,
    get_latest_snapshot,
    get_learner_in_tenant,
    get_reports_for_learner,
    get_tenant,
    list_learner_profiles_in_tenant,
    list_users_in_tenant,
    since_days,
    update_tenant_settings_db,
)
from app.schemas.operations import (
    AdminSummaryResponse,
    FeatureFlagResponse,
    OperationsHealthCheck,
    OperationsHealthResponse,
    OperationsOverviewResponse,
    OperationsUserResponse,
    ReportSummaryListResponse,
    ReportSummaryResponse,
    TeacherLearnerSummaryResponse,
    TeacherRosterEntry,
    TeacherRosterResponse,
    TenantSettingsResponse,
    TenantSettingsUpdateRequest,
)
from app.services.analytics_service import AnalyticsService
from app.services.health_service import jwt_secret_is_safe, probe_database
from app.services.student_intelligence_service import get_summary

OPERATIONS_VERSION = "operations_v1"

ALLOWED_FEATURE_KEYS = frozenset(
    {
        "voice_enabled",
        "governance_metadata",
        "curriculum_recommendations",
        "knowledge_grounding",
        "analytics_dashboard",
    }
)
ALLOWED_LIMIT_KEYS = frozenset({"max_learners"})

DEFAULT_FEATURES: dict[str, bool] = {
    "voice_enabled": True,
    "governance_metadata": True,
    "curriculum_recommendations": True,
    "knowledge_grounding": True,
    "analytics_dashboard": True,
}
DEFAULT_LIMITS: dict[str, Any] = {"max_learners": 100}

SNAPSHOT_SKILLS = {
    "grammar": "grammar_score",
    "vocabulary": "vocabulary_score",
    "writing": "writing_score",
    "reading": "reading_score",
    "listening": "listening_score",
    "speaking": "speaking_score",
}


def _merge_settings(raw: dict | None) -> dict:
    base = dict(raw or {})
    features = {**DEFAULT_FEATURES, **(base.get("features") or {})}
    limits = {**DEFAULT_LIMITS, **(base.get("limits") or {})}
    return {"features": features, "limits": limits}


def _limit_warnings(learner_count: int, limits: dict) -> list[str]:
    warnings: list[str] = []
    max_learners = limits.get("max_learners")
    if isinstance(max_learners, int) and learner_count > max_learners:
        warnings.append(f"learner_count_exceeds_limit:{learner_count}>{max_learners}")
    return warnings


def _skills_from_snapshot(snapshot) -> tuple[str | None, str | None, float | None]:
    if not snapshot:
        return None, None, None
    scores: dict[str, float] = {}
    for skill, field in SNAPSHOT_SKILLS.items():
        val = getattr(snapshot, field, None)
        if val is not None:
            scores[skill] = float(val)
    if not scores:
        return None, None, None
    weakest = min(scores, key=scores.get)
    strongest = max(scores, key=scores.get)
    weakest_score = scores[weakest]
    return weakest, strongest, weakest_score


def _report_to_summary(report) -> ReportSummaryResponse:
    content = report.content or {}
    title = content.get("lesson_summary") or content.get("title") or report.report_type
    summary = content.get("executive_summary") or content.get("lesson_summary")
    recommendations = content.get("recommendations") or content.get("suggested_practice")
    preview = None
    if isinstance(recommendations, list) and recommendations:
        preview = str(recommendations[0])
    elif isinstance(recommendations, str):
        preview = recommendations
    scores = content.get("scores") or {}
    return ReportSummaryResponse(
        id=report.id,
        report_type=report.report_type,
        generated_at=report.generated_at,
        learner_id=report.learner_id,
        title=str(title) if title else None,
        summary=str(summary) if summary else None,
        key_metrics=scores if isinstance(scores, dict) else {},
        recommendation_preview=preview,
    )


class OperationsService:
    def __init__(self) -> None:
        self._analytics = AnalyticsService()

    async def get_operations_health(self, _user: TokenPayload) -> OperationsHealthResponse:
        settings = get_settings()
        db_probe = await probe_database()
        db_status = db_probe.get("database", "not_configured")
        overall = "healthy" if db_status in ("reachable", "not_configured") else "degraded"

        auth_status = "ok"
        try:
            from app.core.security import hash_password, verify_password

            hashed = hash_password("health-check")
            if not verify_password("health-check", hashed):
                auth_status = "failed"
                overall = "degraded"
        except Exception:  # noqa: BLE001
            auth_status = "error"
            overall = "degraded"

        from app.ai.openai_client import ai_client

        checks = [
            OperationsHealthCheck(name="database", status=db_status),
            OperationsHealthCheck(
                name="ai_provider",
                status="configured" if ai_client.is_configured else "mock",
                detail=ai_client.provider,
            ),
            OperationsHealthCheck(name="auth_hashing", status=auth_status),
            OperationsHealthCheck(
                name="jwt_secret",
                status="ok" if jwt_secret_is_safe() or settings.DEBUG else "unsafe",
            ),
        ]

        return OperationsHealthResponse(
            status=overall,
            database=db_status,
            database_latency_ms=db_probe.get("database_latency_ms"),
            ai_provider=ai_client.provider,
            ai_configured=ai_client.is_configured,
            auth_hashing=auth_status,
            version=settings.APP_VERSION,
            checks=checks,
        )

    async def get_tenant_settings(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> TenantSettingsResponse:
        tenant = await get_tenant(db, user.tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        merged = _merge_settings(tenant.settings)
        learner_count = await count_learners_in_tenant(db, tenant_id=user.tenant_id)
        return TenantSettingsResponse(
            tenant_id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            plan_tier=tenant.plan_tier or "free",
            is_active=tenant.is_active,
            settings=merged,
            feature_flags=merged["features"],
            limits=merged["limits"],
            limit_warnings=_limit_warnings(learner_count, merged["limits"]),
        )

    async def update_tenant_settings(
        self,
        db: AsyncSession,
        user: TokenPayload,
        request: TenantSettingsUpdateRequest,
    ) -> TenantSettingsResponse:
        tenant = await get_tenant(db, user.tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        current = _merge_settings(tenant.settings)
        incoming = request.settings or {}

        if "features" in incoming and isinstance(incoming["features"], dict):
            for key, val in incoming["features"].items():
                if key not in ALLOWED_FEATURE_KEYS:
                    raise HTTPException(status_code=400, detail=f"Unknown feature key: {key}")
                if not isinstance(val, bool):
                    raise HTTPException(status_code=400, detail=f"Feature {key} must be boolean")
                current["features"][key] = val

        if "limits" in incoming and isinstance(incoming["limits"], dict):
            for key, val in incoming["limits"].items():
                if key not in ALLOWED_LIMIT_KEYS:
                    raise HTTPException(status_code=400, detail=f"Unknown limit key: {key}")
                if not isinstance(val, int) or val < 1:
                    raise HTTPException(status_code=400, detail=f"Limit {key} must be a positive integer")
                current["limits"][key] = val

        updated = await update_tenant_settings_db(db, tenant_id=user.tenant_id, settings=current)
        if not updated:
            raise HTTPException(status_code=404, detail="Tenant not found")
        await db.commit()

        return await self.get_tenant_settings(db, user)

    async def get_feature_flags(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> FeatureFlagResponse:
        tenant_resp = await self.get_tenant_settings(db, user)
        return FeatureFlagResponse(
            feature_flags=tenant_resp.feature_flags,
            limits=tenant_resp.limits,
            limit_warnings=tenant_resp.limit_warnings,
        )

    async def list_users(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> list[OperationsUserResponse]:
        rows = await list_users_in_tenant(db, tenant_id=user.tenant_id)
        return [
            OperationsUserResponse(
                id=u.id,
                email=u.email,
                role=u.role,
                first_name=u.first_name,
                last_name=u.last_name,
                is_active=u.is_active,
            )
            for u in rows
        ]

    async def get_teacher_roster(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> TeacherRosterResponse:
        since_30d = since_days(30)
        since_7d = since_days(7)
        profiles = await list_learner_profiles_in_tenant(db, tenant_id=user.tenant_id)
        entries: list[TeacherRosterEntry] = []
        active_count = 0
        needs_attention_count = 0

        for profile in profiles:
            learner_id = profile.id
            u = profile.user
            name = None
            email = None
            if u:
                name = " ".join(filter(None, [u.first_name, u.last_name])).strip() or None
                email = u.email

            snapshot = await get_latest_snapshot(db, learner_id=learner_id)
            weakest, strongest, weakest_score = _skills_from_snapshot(snapshot)
            cefr = profile.current_cefr or (snapshot.cefr_estimate if snapshot else None)

            lessons_30d = await count_lesson_completions_since(db, learner_id=learner_id, since=since_30d)
            last_activity = await get_last_activity_at(db, learner_id=learner_id)
            gov = await get_governance_aggregate_for_learner(
                db, tenant_id=user.tenant_id, learner_id=learner_id, since=since_30d
            )
            overdue = await count_overdue_revisions(db, learner_id=learner_id)

            needs_attention = False
            if weakest_score is not None and weakest_score < 50:
                needs_attention = True
            if gov.get("needs_attention_count", 0) > 0:
                needs_attention = True
            if overdue > 0:
                needs_attention = True
            if last_activity and last_activity < since_days(14):
                needs_attention = True
            elif last_activity is None and lessons_30d == 0:
                needs_attention = True

            if last_activity and last_activity >= since_7d:
                active_count += 1

            if needs_attention:
                needs_attention_count += 1

            status = "needs_attention" if needs_attention else "active"

            entries.append(
                TeacherRosterEntry(
                    learner_id=learner_id,
                    user_id=profile.user_id,
                    name=name,
                    email=email,
                    cefr_level=cefr,
                    weakest_skill=weakest,
                    strongest_skill=strongest,
                    last_activity_at=last_activity,
                    lessons_completed_30d=lessons_30d,
                    governance_avg_score=gov.get("avg_score"),
                    status=status,
                    needs_attention=needs_attention,
                )
            )

        return TeacherRosterResponse(
            learners=entries,
            total=len(entries),
            needs_attention_count=needs_attention_count,
            active_learners=active_count,
        )

    async def get_teacher_learner_summary(
        self,
        db: AsyncSession,
        user: TokenPayload,
        learner_id: UUID,
    ) -> TeacherLearnerSummaryResponse:
        profile = await get_learner_in_tenant(db, tenant_id=user.tenant_id, learner_id=learner_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Learner not found")

        learner_user_id = profile.user_id
        profile_summary: dict[str, Any] = {}
        insights_list: list[dict[str, Any]] = []
        analytics_overview: dict[str, Any] = {}
        curriculum_activity: dict[str, Any] = {}

        try:
            summary = await get_summary(db, user_id=learner_user_id)
            profile_summary = summary.model_dump()
        except Exception:  # noqa: BLE001
            profile_summary = {"learner_id": str(learner_id), "has_data": False}

        try:
            overview = await self._analytics.get_overview(db, learner_user_id, user.tenant_id)
            analytics_overview = overview.model_dump()
        except Exception:  # noqa: BLE001
            analytics_overview = {}

        try:
            insights_resp = await self._analytics.get_insights(db, learner_user_id, user.tenant_id)
            insights_list = [i.model_dump() for i in insights_resp.insights]
        except Exception:  # noqa: BLE001
            insights_list = []

        try:
            curriculum = await self._analytics.get_curriculum(db, learner_user_id, user.tenant_id)
            curriculum_activity = curriculum.model_dump()
        except Exception:  # noqa: BLE001
            curriculum_activity = {}

        since_30d = since_days(30)
        gov = await get_governance_aggregate_for_learner(
            db, tenant_id=user.tenant_id, learner_id=learner_id, since=since_30d
        )
        recent_warnings = list(dict.fromkeys(gov.get("warnings") or []))[:10]

        reports = await get_reports_for_learner(
            db, tenant_id=user.tenant_id, learner_id=learner_id, limit=5
        )
        recent_reports = [_report_to_summary(r).model_dump() for r in reports]

        return TeacherLearnerSummaryResponse(
            learner_id=learner_id,
            profile_summary=profile_summary,
            analytics_overview=analytics_overview,
            insights=insights_list,
            recent_reports=recent_reports,
            recent_warnings=recent_warnings,
            curriculum_activity=curriculum_activity,
            metadata={"version": OPERATIONS_VERSION},
        )

    async def get_admin_summary(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> AdminSummaryResponse:
        tenant = await get_tenant(db, user.tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        since_7d = since_days(7)
        since_30d = since_days(30)

        user_count = await count_users_in_tenant(db, tenant_id=user.tenant_id)
        learner_count = await count_learners_in_tenant(db, tenant_id=user.tenant_id)
        active_7d = await count_active_learners_since(db, tenant_id=user.tenant_id, since=since_7d)
        lessons_30d = await count_lesson_completions_tenant_since(
            db, tenant_id=user.tenant_id, since=since_30d
        )
        gov = await get_governance_aggregate_for_tenant(db, tenant_id=user.tenant_id, since=since_30d)
        knowledge = await get_knowledge_aggregate_for_tenant(db, tenant_id=user.tenant_id, since=since_30d)

        return AdminSummaryResponse(
            tenant_id=user.tenant_id,
            user_count=user_count,
            learner_count=learner_count,
            active_learners_7d=active_7d,
            lessons_completed_30d=lessons_30d,
            avg_governance_score=gov.get("avg_score"),
            warning_count_30d=gov.get("warning_count", 0),
            grounding_fallback_rate=knowledge.get("fallback_rate"),
            plan_tier=tenant.plan_tier or "free",
            is_active=tenant.is_active,
            metadata={"version": OPERATIONS_VERSION},
        )

    async def get_operations_overview(
        self,
        db: AsyncSession,
        user: TokenPayload,
    ) -> OperationsOverviewResponse:
        admin_summary = await self.get_admin_summary(db, user)
        health = await self.get_operations_health(user)
        return OperationsOverviewResponse(
            tenant_id=user.tenant_id,
            admin_summary=admin_summary.model_dump(),
            health=health,
            metadata={"version": OPERATIONS_VERSION},
        )

    async def get_learner_reports(
        self,
        db: AsyncSession,
        user: TokenPayload,
        learner_id: UUID,
    ) -> ReportSummaryListResponse:
        profile = await get_learner_in_tenant(db, tenant_id=user.tenant_id, learner_id=learner_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Learner not found")

        reports = await get_reports_for_learner(
            db, tenant_id=user.tenant_id, learner_id=learner_id
        )
        summaries = [_report_to_summary(r) for r in reports]
        return ReportSummaryListResponse(reports=summaries, total=len(summaries))
