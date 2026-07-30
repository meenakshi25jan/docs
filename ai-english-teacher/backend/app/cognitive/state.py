"""Shared cognitive state — every agent reads/writes through orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionSlice:
    status: str = "active"
    turn_count: int = 0
    persona_id: str = "conversation_partner"
    scenario: str = "general_conversation"
    device_id: str | None = None


@dataclass
class ConversationSlice:
    phase: str = "practice"
    message_history: list[dict[str, str]] = field(default_factory=list)
    pending_corrections: list[dict[str, Any]] = field(default_factory=list)
    last_intent: str | None = None


@dataclass
class LessonSlice:
    objective: str | None = None
    competency_id: str | None = None
    lesson_id: str | None = None


@dataclass
class StudentSlice:
    cefr_level: str = "B1"
    challenge_level: float = 50.0
    preferences: dict[str, Any] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)


@dataclass
class VoiceSlice:
    transcript: str = ""
    duration_seconds: float | None = None
    voice_analysis: dict[str, Any] | None = None
    teaching_mode: str | None = None
    teaching_instruction: str | None = None


@dataclass
class AssessmentSlice:
    last_scores: dict[str, float] = field(default_factory=dict)
    pending_assessment: bool = False


@dataclass
class CognitiveState:
    session: SessionSlice = field(default_factory=SessionSlice)
    conversation: ConversationSlice = field(default_factory=ConversationSlice)
    lesson: LessonSlice = field(default_factory=LessonSlice)
    student: StudentSlice = field(default_factory=StudentSlice)
    voice: VoiceSlice = field(default_factory=VoiceSlice)
    assessment: AssessmentSlice = field(default_factory=AssessmentSlice)
    emotion: dict[str, Any] = field(default_factory=dict)
    analytics: dict[str, Any] = field(default_factory=dict)
    memory_refs: dict[str, Any] = field(default_factory=dict)
    tool_results: dict[str, Any] = field(default_factory=dict)
    web_results: list[dict[str, Any]] = field(default_factory=list)
    trace_id: str = ""

    def to_session_patch(self) -> dict[str, Any]:
        return {
            "turn_count": self.session.turn_count,
            "persona_id": self.session.persona_id,
            "scenario": self.session.scenario,
            "pending_corrections": self.conversation.pending_corrections,
            "lesson_phase": self.conversation.phase,
            "challenge_level": self.student.challenge_level,
            "last_intent": self.conversation.last_intent,
        }

    @classmethod
    def from_session_dict(
        cls,
        session_data: dict[str, Any],
        *,
        scenario: str,
        cefr_level: str,
        persona_id: str,
        message_history: list[dict[str, str]],
    ) -> "CognitiveState":
        state = cls()
        state.session.turn_count = int(session_data.get("turn_count", 0))
        state.session.persona_id = persona_id or session_data.get("persona_id", "conversation_partner")
        state.session.scenario = scenario
        state.conversation.message_history = list(message_history)
        state.conversation.pending_corrections = list(session_data.get("pending_corrections", []))
        state.conversation.phase = session_data.get("lesson_phase", "practice")
        state.student.cefr_level = cefr_level
        state.student.challenge_level = float(session_data.get("challenge_level", 50.0))
        return state
