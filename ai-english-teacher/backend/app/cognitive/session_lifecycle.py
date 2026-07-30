"""Session lifecycle — start, pause, resume, end, reconnect."""

from __future__ import annotations

from typing import Any

from app.cognitive.events import EventType
from app.cognitive.state import CognitiveState
from app.orchestration.session_manager import load_session, merge_session, save_session


async def handle_lifecycle_event(
    event_type: EventType,
    session_id: str,
    patch: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = await load_session(session_id)
    patch = patch or {}

    if event_type == EventType.LESSON_STARTED:
        session.update({"status": "active", "lesson_started_at": patch.get("timestamp")})
    elif event_type == EventType.LESSON_PAUSED:
        session["status"] = "paused"
    elif event_type == EventType.LESSON_RESUMED:
        session["status"] = "active"
    elif event_type == EventType.LESSON_FINISHED:
        session["status"] = "completed"
    elif event_type == EventType.SESSION_RECONNECT:
        session["reconnected"] = True
    elif event_type == EventType.NETWORK_LOST:
        session["network_lost"] = True

    session.update(patch)
    await save_session(session_id, session)
    return session


async def persist_cognitive_state(session_id: str, state: CognitiveState) -> None:
    await merge_session(session_id, state.to_session_patch())
