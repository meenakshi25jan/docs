"""Enterprise Operations v1 schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TenantSettingsResponse(BaseModel):
    tenant_id: UUID
    name: str
    slug: str
    plan_tier: str = "free"
    is_active: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    limits: dict[str, Any] = Field(default_factory=dict)
    limit_warnings: list[str] = Field(default_factory=list)


class TenantSettingsUpdateRequest(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)


class FeatureFlagResponse(BaseModel):
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    limits: dict[str, Any] = Field(default_factory=dict)
    limit_warnings: list[str] = Field(default_factory=list)


class OperationsHealthCheck(BaseModel):
    name: str
    status: str
    detail: str | None = None


class OperationsHealthResponse(BaseModel):
    status: str = "healthy"
    database: str = "not_configured"
    database_latency_ms: int | None = None
    ai_provider: str = "mock"
    ai_configured: bool = False
    auth_hashing: str = "unknown"
    version: str = ""
    checks: list[OperationsHealthCheck] = Field(default_factory=list)


class OperationsOverviewResponse(BaseModel):
    tenant_id: UUID | None = None
    admin_summary: dict[str, Any] = Field(default_factory=dict)
    health: OperationsHealthResponse | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperationsUserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True


class TeacherRosterEntry(BaseModel):
    learner_id: UUID
    user_id: UUID
    name: str | None = None
    email: str | None = None
    cefr_level: str | None = None
    weakest_skill: str | None = None
    strongest_skill: str | None = None
    last_activity_at: datetime | None = None
    lessons_completed_30d: int = 0
    governance_avg_score: float | None = None
    status: str = "active"
    needs_attention: bool = False


class TeacherRosterResponse(BaseModel):
    learners: list[TeacherRosterEntry] = Field(default_factory=list)
    total: int = 0
    needs_attention_count: int = 0
    active_learners: int = 0


class TeacherLearnerSummaryResponse(BaseModel):
    learner_id: UUID
    profile_summary: dict[str, Any] = Field(default_factory=dict)
    analytics_overview: dict[str, Any] = Field(default_factory=dict)
    insights: list[dict[str, Any]] = Field(default_factory=list)
    recent_reports: list[dict[str, Any]] = Field(default_factory=list)
    recent_warnings: list[str] = Field(default_factory=list)
    curriculum_activity: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdminSummaryResponse(BaseModel):
    tenant_id: UUID
    user_count: int = 0
    learner_count: int = 0
    active_learners_7d: int = 0
    lessons_completed_30d: int = 0
    avg_governance_score: float | None = None
    warning_count_30d: int = 0
    grounding_fallback_rate: float | None = None
    plan_tier: str = "free"
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportSummaryResponse(BaseModel):
    id: UUID
    report_type: str
    generated_at: datetime
    learner_id: UUID
    title: str | None = None
    summary: str | None = None
    key_metrics: dict[str, Any] = Field(default_factory=dict)
    recommendation_preview: str | None = None


class ReportSummaryListResponse(BaseModel):
    reports: list[ReportSummaryResponse] = Field(default_factory=list)
    total: int = 0
