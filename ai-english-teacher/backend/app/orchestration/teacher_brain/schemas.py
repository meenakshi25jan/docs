"""Teacher Brain v1 schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.student_intelligence import StudentSummaryResponse


class DetectedError(BaseModel):
    type: str
    original_text: str
    suggested_correction: str | None = None
    explanation: str | None = None
    severity: str = "medium"
    source: str = "unknown"


class IntentAnalysis(BaseModel):
    intent: str
    confidence: float = 0.5
    signals: list[str] = Field(default_factory=list)


class ResponsePlan(BaseModel):
    opening_style: str = "supportive"
    include_correction: bool = False
    include_explanation: bool = False
    include_encouragement: bool = True
    practice_question: str | None = None
    max_sentences: int = 4
    tone: str = "friendly"
    next_step: str | None = None
    skill_focus: str | None = None


class TeacherBrainInput(BaseModel):
    user_id: UUID | None = None
    tenant_id: UUID | None = None
    learner_id: UUID | None = None
    transcript: str | None = None
    message: str = ""
    conversation_id: str | None = None
    session_id: str = ""
    scenario: str = "general_conversation"
    persona_id: str = "conversation_partner"
    cefr_level: str = "B1"
    message_history: list[dict[str, str]] = Field(default_factory=list)
    voice_analysis: dict[str, Any] | None = None
    teaching_mode: str | None = None
    teaching_instruction: str | None = None
    student_intelligence_summary: StudentSummaryResponse | None = None
    conversation_context: dict[str, Any] = Field(default_factory=dict)
    memory_bundle: dict[str, Any] | None = None
    orchestration_intent: str | None = None
    is_voice_turn: bool = False

    @classmethod
    def from_teacher_context(
        cls,
        context: dict[str, Any],
        *,
        learner_id: str,
        tenant_id: str | None,
        orchestration_intent: str | None = None,
        is_voice_turn: bool = False,
        session_id: str = "",
    ) -> TeacherBrainInput:
        """Build input from cognitive build_teacher_context output."""
        learner_uuid = None
        user_uuid = None
        tenant_uuid = None
        try:
            learner_uuid = UUID(str(learner_id))
        except (ValueError, TypeError):
            pass
        if context.get("user_id"):
            try:
                user_uuid = UUID(str(context["user_id"]))
            except (ValueError, TypeError):
                pass
        if tenant_id:
            try:
                tenant_uuid = UUID(str(tenant_id))
            except (ValueError, TypeError):
                pass

        message = str(context.get("message", "") or "")
        voice_analysis = context.get("voice_analysis")
        if not voice_analysis and context.get("coach_briefs"):
            voice_analysis = {"details": context.get("coach_briefs")}

        return cls(
            user_id=user_uuid,
            tenant_id=tenant_uuid,
            learner_id=learner_uuid,
            transcript=message if is_voice_turn else None,
            message=message,
            conversation_id=context.get("conversation_id"),
            session_id=session_id or context.get("orchestration_trace_id", ""),
            scenario=str(context.get("scenario", "general_conversation")),
            persona_id=str(context.get("persona_id", "conversation_partner")),
            cefr_level=str(context.get("cefr_level", "B1")),
            message_history=list(context.get("message_history", [])),
            voice_analysis=voice_analysis,
            teaching_mode=context.get("teaching_mode"),
            teaching_instruction=context.get("teaching_instruction"),
            student_intelligence_summary=context.get("student_intelligence_summary"),
            conversation_context={
                "turn_count": context.get("turn_count", 0),
                "pending_corrections": context.get("pending_corrections", []),
                "phase": context.get("lesson_phase", "practice"),
            },
            memory_bundle=context.get("memory_bundle"),
            orchestration_intent=orchestration_intent,
            is_voice_turn=is_voice_turn,
        )


class TeacherBrainOutput(BaseModel):
    intent: str
    detected_errors: list[DetectedError] = Field(default_factory=list)
    teaching_strategy: str
    response_plan: ResponsePlan
    teacher_response: str
    correction_mode: str = "none"
    next_prompt: str | None = None
    skill_focus: str | None = None
    agent_output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_api_metadata(self) -> dict[str, Any]:
        """Optional metadata for API clients."""
        return {
            "intent": self.intent,
            "teaching_strategy": self.teaching_strategy,
            "skill_focus": self.skill_focus,
            "correction_mode": self.correction_mode,
            "next_prompt": self.next_prompt,
        }
