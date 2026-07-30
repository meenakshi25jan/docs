"""Unified context for Teacher Brain — orchestrator builds, Teacher never fetches."""

from __future__ import annotations

from typing import Any

from app.cognitive.agent_planner import AgentPlan
from app.cognitive.events import IntentType
from app.cognitive.state import CognitiveState
from app.cognitive.tool_router import ToolName
from app.orchestration.personas import get_persona


async def build_teacher_context(
    state: CognitiveState,
    *,
    intent: IntentType,
    agent_plan: AgentPlan,
    memory_bundle: dict[str, Any],
    tools: list[ToolName],
    coach_briefs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    message = state.voice.transcript or ""
    if not message and state.conversation.message_history:
        last_user = [m for m in state.conversation.message_history if m.get("role") == "user"]
        if last_user:
            message = last_user[-1].get("content", "")

    rag_chunks: list[dict[str, Any]] = []
    if ToolName.CURRICULUM_KB in tools or ToolName.RAG_SCENARIO in tools:
        from app.orchestration.rag_agent import retrieve
        rag_chunks = await retrieve(
            message,
            scenario=state.session.scenario,
            top_k=3,
            tenant_id=None,
        )

    knowledge_lines = [f"- [{c.get('source', 'curriculum')}] {c.get('text', '')}" for c in rag_chunks[:3]]
    errors = list(memory_bundle.get("learning_mistakes", []) or memory_bundle.get("recent_errors", []))
    for m in memory_bundle.get("conversation", []):
        if m.get("type") == "mistake" and m.get("text"):
            errors.append(str(m["text"]))
    errors = list(dict.fromkeys(errors))[:10]

    lesson_reflections = memory_bundle.get("lesson_reflections", [])
    memory_summary = str(memory_bundle.get("memory_summary", "") or "")
    preferences = memory_bundle.get("preferences", {}) or memory_bundle.get("student_profile", {}).get("preferences", {})
    skill_weaknesses = memory_bundle.get("skill_weaknesses", [])

    web_summary = ""
    if state.web_results:
        web_summary = "\n".join(
            f"- {r.get('title', 'source')}: {r.get('snippet', '')[:200]}"
            for r in state.web_results[:3]
        )

    voice_summary = ""
    if state.voice.voice_analysis:
        va = state.voice.voice_analysis
        voice_summary = (
            f"Fluency {va.get('fluency', '—')}, "
            f"Pronunciation {va.get('pronunciation', '—')}, "
            f"Grammar {va.get('grammar_score', '—')}"
        )

    return {
        "scenario": state.session.scenario,
        "cefr_level": state.student.cefr_level,
        "challenge_level": state.student.challenge_level,
        "message": message,
        "message_history": state.conversation.message_history,
        "recent_errors": errors,
        "intent": intent.value,
        "persona_id": state.session.persona_id,
        "lesson_phase": state.conversation.phase,
        "lesson_objective": state.lesson.objective,
        "competency_id": state.lesson.competency_id,
        "knowledge_context": "\n".join(knowledge_lines) if knowledge_lines else "",
        "web_context": web_summary,
        "memory_count": len(memory_bundle.get("conversation", [])),
        "recurring_mistakes": memory_bundle.get("recurring_mistakes", []),
        "student_profile": memory_bundle.get("student_profile", {}),
        "lesson_reflections": lesson_reflections,
        "memory_summary": memory_summary,
        "preferences": preferences,
        "skill_weaknesses": skill_weaknesses,
        "memory_bundle": memory_bundle,
        "teaching_instruction": state.voice.teaching_instruction or "",
        "teaching_mode": state.voice.teaching_mode or "none",
        "voice_summary": voice_summary,
        "voice_analysis": state.voice.voice_analysis,
        "turn_count": state.session.turn_count,
        "pending_corrections": state.conversation.pending_corrections,
        "coach_briefs": coach_briefs or {},
        "tool_results": state.tool_results,
        "agents_invoked": [a.value for a in agent_plan.agents],
        "agents_skipped": agent_plan.skipped,
        "orchestration_trace_id": state.trace_id,
    }
