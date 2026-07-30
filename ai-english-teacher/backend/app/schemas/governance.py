"""AI Governance v1 schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluationSignals(BaseModel):
    items: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TeacherResponseEvaluation(BaseModel):
    score: float = 0.0
    status: str = "unknown"
    correction_quality: float = 0.0
    explanation_quality: float = 0.0
    encouragement_quality: float = 0.0
    practice_prompt_quality: float = 0.0
    length_compliance: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    signals: EvaluationSignals = Field(default_factory=EvaluationSignals)


class CurriculumEvaluation(BaseModel):
    score: float = 0.0
    status: str = "unknown"
    weakest_skill_match: float = 0.0
    lesson_relevance: float = 0.0
    revision_relevance: float = 0.0
    path_consistency: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    signals: EvaluationSignals = Field(default_factory=EvaluationSignals)


class GroundingEvaluation(BaseModel):
    score: float = 0.0
    status: str = "unknown"
    grounding_present: float = 0.0
    source_count_score: float = 0.0
    fallback_penalty: float = 0.0
    lesson_match: float = 0.0
    knowledge_quality: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    signals: EvaluationSignals = Field(default_factory=EvaluationSignals)


class MemoryEvaluation(BaseModel):
    score: float = 0.0
    status: str = "unknown"
    recurring_mistakes_used: float = 0.0
    reflections_used: float = 0.0
    summary_available: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    signals: EvaluationSignals = Field(default_factory=EvaluationSignals)


class StudentOutcomeEvaluation(BaseModel):
    score: float = 0.0
    status: str = "unknown"
    progress_trend: float = 0.0
    confidence_trend: float = 0.0
    lesson_activity: float = 0.0
    assessment_improvement: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    signals: EvaluationSignals = Field(default_factory=EvaluationSignals)


class GovernanceAuditEvent(BaseModel):
    event_type: str
    learner_id: str | None = None
    tenant_id: str | None = None
    trace_id: str | None = None
    conversation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GovernanceMetadata(BaseModel):
    teacher_response_score: float = 0.0
    curriculum_score: float = 0.0
    grounding_score: float = 0.0
    memory_score: float = 0.0
    student_outcome_score: float | None = None
    overall_score: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    status: str = "ok"
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TurnGovernanceEvaluation(BaseModel):
    teacher: TeacherResponseEvaluation
    curriculum: CurriculumEvaluation
    grounding: GroundingEvaluation
    memory: MemoryEvaluation
    governance: GovernanceMetadata
    audit_event: GovernanceAuditEvent | None = None


class GovernanceSummary(BaseModel):
    learner_id: str | None = None
    evaluation_count: int = 0
    avg_teacher_response_score: float = 0.0
    avg_curriculum_score: float = 0.0
    avg_grounding_score: float = 0.0
    avg_memory_score: float = 0.0
    avg_overall_score: float = 0.0
    student_outcome: StudentOutcomeEvaluation | None = None
    recent_warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceEvaluationsResponse(BaseModel):
    evaluations: list[GovernanceMetadata] = Field(default_factory=list)
    total: int = 0


class GovernanceQualityResponse(BaseModel):
    avg_teacher_response_score: float = 0.0
    avg_grounding_score: float = 0.0
    avg_curriculum_score: float = 0.0
    avg_memory_score: float = 0.0
    avg_overall_score: float = 0.0
    evaluation_count: int = 0
    warning_count: int = 0


class GovernanceGroundingResponse(BaseModel):
    evaluations: list[GroundingEvaluation] = Field(default_factory=list)
    avg_score: float = 0.0
    total: int = 0


class GovernanceAuditLogResponse(BaseModel):
    events: list[GovernanceAuditEvent] = Field(default_factory=list)
    total: int = 0
