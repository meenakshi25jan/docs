"""Analytics & Insights v1 schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    label: str
    score: float | None = None
    current_value: float | None = None
    previous_value: float | None = None
    delta: float | None = None
    trend: str = "stable"
    status: str = "fair"
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillTrendPoint(BaseModel):
    skill: str
    label: str
    points: list[dict[str, Any]] = Field(default_factory=list)
    current_value: float | None = None
    previous_value: float | None = None
    delta: float | None = None
    trend: str = "stable"
    status: str = "fair"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsScorecard(BaseModel):
    overall_health: float = 0.5
    progress: float = 0.5
    governance: float = 0.5
    curriculum: float = 0.5
    knowledge: float = 0.5
    teaching: float = 0.5
    status: str = "fair"
    updated_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InsightItem(BaseModel):
    type: str
    severity: str = "info"
    title: str
    description: str
    recommended_action: str | None = None
    source: str = "analytics_v1"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsOverviewResponse(BaseModel):
    scorecard: AnalyticsScorecard = Field(default_factory=AnalyticsScorecard)
    metrics: list[MetricPoint] = Field(default_factory=list)
    period: str = "30d"
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProgressAnalyticsResponse(BaseModel):
    skill_trends: list[SkillTrendPoint] = Field(default_factory=list)
    cefr_history: list[dict[str, Any]] = Field(default_factory=list)
    confidence_trend: SkillTrendPoint | None = None
    metrics: list[MetricPoint] = Field(default_factory=list)
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceAnalyticsResponse(BaseModel):
    avg_teacher_response_score: float = 0.0
    avg_grounding_score: float = 0.0
    avg_curriculum_score: float = 0.0
    avg_memory_score: float = 0.0
    avg_overall_score: float = 0.0
    evaluation_count: int = 0
    warning_count: int = 0
    warning_frequency: dict[str, int] = Field(default_factory=dict)
    status_breakdown: dict[str, int] = Field(default_factory=dict)
    score_trends: list[MetricPoint] = Field(default_factory=list)
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CurriculumAnalyticsResponse(BaseModel):
    lessons_completed: int = 0
    lessons_completed_7d: int = 0
    lessons_completed_30d: int = 0
    most_recent_lesson: dict[str, Any] | None = None
    revision_pending: int = 0
    revision_completed: int = 0
    revision_overdue: int = 0
    recommended_lesson_count: int = 0
    skill_focus_distribution: dict[str, int] = Field(default_factory=dict)
    completion_velocity_per_week: float | None = None
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeAnalyticsResponse(BaseModel):
    grounding_count: int = 0
    avg_chunk_count: float = 0.0
    fallback_usage_count: int = 0
    grounding_availability_rate: float = 0.0
    source_distribution: dict[str, int] = Field(default_factory=dict)
    avg_grounding_quality_score: float | None = None
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearnerInsightsResponse(BaseModel):
    insights: list[InsightItem] = Field(default_factory=list)
    has_data: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
