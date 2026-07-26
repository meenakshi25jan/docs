from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    tenant_slug: str = "default"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    first_name: str | None
    last_name: str | None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


# ── Assessment ────────────────────────────────────────────────────────────────

class AssessmentCreate(BaseModel):
    assessment_type: str = Field(pattern="^(placement|grammar|vocabulary|writing|reading|listening|speaking|full)$")
    config: dict = Field(default_factory=dict)


class AnswerSubmission(BaseModel):
    skill: str
    question_id: str
    response: str
    metadata: dict = Field(default_factory=dict)


class AssessmentSubmit(BaseModel):
    answers: list[AnswerSubmission]


class SkillResult(BaseModel):
    score: float
    confidence: float | None = None
    cefr_estimate: str | None = None
    ielts_estimate: float | None = None
    pte_estimate: int | None = None
    details: dict = Field(default_factory=dict)


class AssessmentResponse(BaseModel):
    id: UUID
    assessment_type: str
    status: str
    config: dict
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentResultResponse(BaseModel):
    assessment_id: UUID
    status: str
    results: dict[str, SkillResult]
    overall: SkillResult | None = None


# ── Conversation ──────────────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    scenario: str
    context: dict = Field(default_factory=dict)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    role: str
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class ConversationResponse(BaseModel):
    id: UUID
    scenario: str
    status: str
    initial_message: MessageResponse | None = None

    model_config = {"from_attributes": True}


# ── Writing ───────────────────────────────────────────────────────────────────

class WritingSubmit(BaseModel):
    prompt: str
    content: str = Field(min_length=50, max_length=5000)
    task_type: str = "ielts_task2"


class WritingFeedback(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    errors: list[dict] = Field(default_factory=list)


class WritingResponse(BaseModel):
    id: UUID
    scores: dict[str, float]
    feedback: WritingFeedback
    estimates: dict[str, str | float | int]


# ── Learning Plan ─────────────────────────────────────────────────────────────

class LearningPlanCreate(BaseModel):
    duration_weeks: int = Field(default=4, ge=1, le=52)
    target_exam: str = "ielts"
    target_score: float = 7.0
    hours_per_week: int = Field(default=5, ge=1, le=40)


# ── Dashboard ─────────────────────────────────────────────────────────────────

class SkillScores(BaseModel):
    grammar: float = 0
    vocabulary: float = 0
    writing: float = 0
    reading: float = 0
    listening: float = 0
    speaking: float = 0


class StudentDashboard(BaseModel):
    learner: dict
    skill_scores: SkillScores
    recent_activity: list[dict] = Field(default_factory=list)
    learning_plan_progress: dict = Field(default_factory=dict)
    upcoming_reviews: dict = Field(default_factory=dict)


class TeacherDashboard(BaseModel):
    class_size: int
    average_scores: SkillScores
    active_learners: int
    recent_assessments: list[dict] = Field(default_factory=list)
    learners_needing_attention: list[dict] = Field(default_factory=list)


class AdminDashboard(BaseModel):
    total_users: int
    total_tenants: int
    active_sessions: int
    ai_calls_today: int
    system_health: dict = Field(default_factory=dict)


# ── Reports ───────────────────────────────────────────────────────────────────

class ReportGenerate(BaseModel):
    report_type: str = "progress_summary"
    period_days: int = Field(default=30, ge=7, le=365)
    format: str = "json"
