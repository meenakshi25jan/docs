"""Pydantic schemas for Student Intelligence v1."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StudentProfileResponse(BaseModel):
    user_id: UUID
    name: str | None = None
    cefr_level: str | None = None
    ielts_estimate: float | None = None
    pte_estimate: int | None = None
    confidence_score: float | None = None
    learning_goal: str | None = None
    current_level: str | None = None
    target_exam: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StudentProfileUpdate(BaseModel):
    learning_goal: str | None = Field(None, max_length=500)
    target_cefr_level: str | None = Field(None, max_length=5)
    target_exam: str | None = Field(None, max_length=50)
    preferred_learning_style: str | None = Field(None, max_length=100)
    daily_goal_minutes: int | None = Field(None, ge=5, le=240)


class SkillScoreDetail(BaseModel):
    score: float = 0
    level: str | None = None
    trend: str | None = None  # up | down | stable | unknown
    last_updated: datetime | None = None


class StudentSkillsResponse(BaseModel):
    speaking: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    listening: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    reading: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    writing: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    grammar: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    vocabulary: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    pronunciation: SkillScoreDetail = Field(default_factory=SkillScoreDetail)
    fluency: SkillScoreDetail = Field(default_factory=SkillScoreDetail)


class StudentMistake(BaseModel):
    mistake_type: str
    original_text: str
    corrected_text: str | None = None
    explanation: str | None = None
    severity: str = "low"
    occurrence_count: int = 1
    last_seen_at: datetime | None = None


class StudentMistakesResponse(BaseModel):
    mistakes: list[StudentMistake] = Field(default_factory=list)
    total: int = 0


class LearningPreferencesResponse(BaseModel):
    learning_goal: str | None = None
    target_cefr_level: str | None = None
    target_exam: str | None = None
    preferred_learning_style: str | None = None
    daily_goal_minutes: int | None = None


class LearningPreferencesUpdate(BaseModel):
    learning_goal: str | None = Field(None, max_length=500)
    target_cefr_level: str | None = Field(None, max_length=5)
    target_exam: str | None = Field(None, max_length=50)
    preferred_learning_style: str | None = Field(None, max_length=100)
    daily_goal_minutes: int | None = Field(None, ge=5, le=240)


class ProgressSnapshotSummary(BaseModel):
    snapshot_at: datetime | None = None
    cefr_estimate: str | None = None
    ielts_estimate: float | None = None
    pte_estimate: int | None = None
    confidence_score: float | None = None
    speaking_score: float | None = None
    grammar_score: float | None = None


class StudentSummaryResponse(BaseModel):
    profile: StudentProfileResponse
    skills: StudentSkillsResponse
    top_mistakes: list[StudentMistake] = Field(default_factory=list)
    latest_progress: ProgressSnapshotSummary | None = None
    strongest_skill: str | None = None
    weakest_skill: str | None = None
    recommended_next_focus: str = "placement assessment"
    has_data: bool = False
