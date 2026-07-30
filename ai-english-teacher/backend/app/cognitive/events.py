"""Event types for the Cognitive Orchestration Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class EventType(str, Enum):
    VOICE_STARTED = "VOICE_STARTED"
    VOICE_STOPPED = "VOICE_STOPPED"
    USER_SPOKE = "USER_SPOKE"
    INTERRUPTION = "INTERRUPTION"
    NETWORK_LOST = "NETWORK_LOST"
    LESSON_STARTED = "LESSON_STARTED"
    LESSON_PAUSED = "LESSON_PAUSED"
    LESSON_FINISHED = "LESSON_FINISHED"
    LESSON_RESUMED = "LESSON_RESUMED"
    WEB_SEARCH_REQUESTED = "WEB_SEARCH_REQUESTED"
    QUIZ_STARTED = "QUIZ_STARTED"
    PRONUNCIATION_FAILED = "PRONUNCIATION_FAILED"
    HOMEWORK_REQUESTED = "HOMEWORK_REQUESTED"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    TOOL_REQUESTED = "TOOL_REQUESTED"
    SESSION_RECONNECT = "SESSION_RECONNECT"


class IntentType(str, Enum):
    GREETING = "greeting"
    CONVERSATION = "conversation"
    TEACHING = "teaching"
    GRAMMAR_EXPLAIN = "grammar_explain"
    SCENARIO_PRACTICE = "scenario_practice"
    TRANSLATION = "translation"
    WEB_KNOWLEDGE = "web_knowledge"
    CONTINUE_LESSON = "continue_lesson"
    HOMEWORK = "homework"
    QUIZ = "quiz"
    UTILITY = "utility"
    PRONUNCIATION_PRACTICE = "pronunciation_practice"


@dataclass
class CognitiveEvent:
    type: EventType
    session_id: str
    learner_id: str
    tenant_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "type": self.type.value,
            "session_id": self.session_id,
            "learner_id": self.learner_id,
            "tenant_id": self.tenant_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }
