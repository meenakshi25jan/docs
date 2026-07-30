"""Curriculum Intelligence API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CurriculumTopicResponse(BaseModel):
    id: str
    title: str
    description: str


class CurriculumSkillResponse(BaseModel):
    id: str
    topic_id: str
    title: str
    description: str


class CurriculumLessonResponse(BaseModel):
    lesson_id: str
    title: str
    topic_id: str
    skill_id: str
    skill_focus: str
    route: str
    cefr_level: str = "B1"
    description: str = ""
    exam_tag: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LessonRecommendationResponse(BaseModel):
    lesson_id: str
    title: str
    reason: str
    route: str
    skill_focus: str
    priority: int = 5


class RevisionItemResponse(BaseModel):
    id: str | None = None
    lesson_id: str
    title: str
    reason: str = ""
    route: str
    skill_focus: str
    due_at: datetime | None = None
    status: str = "scheduled"
    priority: int = 5
    source_type: str | None = None


class LearningPathResponse(BaseModel):
    path_id: str
    title: str
    description: str
    items: list[LessonRecommendationResponse] = Field(default_factory=list)


class LessonCompletionRequest(BaseModel):
    lesson_id: str = Field(..., max_length=120)
    title: str | None = Field(None, max_length=255)
    skill_focus: str | None = Field(None, max_length=50)
    route: str | None = Field(None, max_length=500)
    score: float | None = Field(None, ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LessonCompletionResponse(BaseModel):
    id: str
    lesson_id: str
    title: str
    skill_focus: str
    route: str
    score: float | None = None
    completed_at: datetime


class CurriculumRecommendationBundle(BaseModel):
    primary: LessonRecommendationResponse
    alternates: list[LessonRecommendationResponse] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
