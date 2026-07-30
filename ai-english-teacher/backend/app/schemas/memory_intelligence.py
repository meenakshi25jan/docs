"""Memory Intelligence v1 schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryTurn(BaseModel):
    role: str
    content: str
    created_at: datetime | None = None


class RecurringMistake(BaseModel):
    error: str
    correction: str | None = None
    category: str = "grammar"
    count: int = 1


class LessonReflection(BaseModel):
    content: str
    conversation_id: str | None = None
    recommended_focus: str | None = None
    created_at: datetime | None = None


class TeacherBrainDecisionMemory(BaseModel):
    intent: str | None = None
    teaching_strategy: str | None = None
    skill_focus: str | None = None
    correction_mode: str | None = None
    next_prompt: str | None = None
    conversation_id: str | None = None
    created_at: datetime | None = None


class LearningEventMemory(BaseModel):
    event_type: str
    content: str
    conversation_id: str | None = None
    created_at: datetime | None = None


class MemoryBundleMetadata(BaseModel):
    bundle_created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "memory_intelligence_v1"
    counts: dict[str, int] = Field(default_factory=dict)
    used_fallback: bool = False
    errors: list[str] = Field(default_factory=list)


class MemoryBundle(BaseModel):
    recent_turns: list[MemoryTurn] = Field(default_factory=list)
    recurring_mistakes: list[RecurringMistake] = Field(default_factory=list)
    recent_errors: list[str] = Field(default_factory=list)
    lesson_reflections: list[LessonReflection] = Field(default_factory=list)
    teacher_brain_decisions: list[TeacherBrainDecisionMemory] = Field(default_factory=list)
    learning_events: list[LearningEventMemory] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    skill_weaknesses: list[str] = Field(default_factory=list)
    memory_summary: str = ""
    metadata: MemoryBundleMetadata = Field(default_factory=MemoryBundleMetadata)

    def to_router_dict(self) -> dict[str, Any]:
        """Shape compatible with cognitive memory_router and Teacher Brain."""
        return {
            "recent_turns": [t.model_dump() for t in self.recent_turns],
            "recurring_mistakes": [m.model_dump() for m in self.recurring_mistakes],
            "recent_errors": list(self.recent_errors),
            "lesson_reflections": [r.model_dump() for r in self.lesson_reflections],
            "teacher_brain_decisions": [d.model_dump() for d in self.teacher_brain_decisions],
            "learning_events": [e.model_dump() for e in self.learning_events],
            "preferences": dict(self.preferences),
            "skill_weaknesses": list(self.skill_weaknesses),
            "memory_summary": self.memory_summary,
            "conversation": [
                {"type": "mistake", "text": m.correction or m.error, "category": m.category}
                for m in self.recurring_mistakes[:5]
            ],
            "learning_mistakes": list(self.recent_errors),
            "metadata": self.metadata.model_dump(),
        }

    def to_api_metadata(self) -> dict[str, Any]:
        return {
            "recurring_mistakes_count": len(self.recurring_mistakes),
            "reflections_available": len(self.lesson_reflections) > 0,
            "memory_summary_available": bool(self.memory_summary.strip()),
        }


class MemorySummaryResponse(BaseModel):
    memory_summary: str = ""
    recurring_mistakes_count: int = 0
    reflections_count: int = 0
    skill_weaknesses: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryReflectionsResponse(BaseModel):
    reflections: list[LessonReflection] = Field(default_factory=list)
