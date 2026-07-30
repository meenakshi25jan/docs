"""AI Governance v1 — deterministic evaluation and audit layer."""

from __future__ import annotations

import json
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque

from app.schemas.governance import (
    CurriculumEvaluation,
    EvaluationSignals,
    GovernanceAuditEvent,
    GovernanceMetadata,
    GovernanceSummary,
    GroundingEvaluation,
    MemoryEvaluation,
    StudentOutcomeEvaluation,
    TeacherResponseEvaluation,
    TurnGovernanceEvaluation,
)

logger = logging.getLogger(__name__)

GOVERNANCE_VERSION = "governance_v1"
MAX_RESPONSE_CHARS_VOICE = 500
MAX_STORED_EVALUATIONS = 100
MAX_STORED_AUDIT_EVENTS = 200

_TEACHING_INTENTS = frozenset(
    {"teaching", "grammar_explain", "grammar_correction", "scenario_practice", "quiz", "continue_lesson"}
)

_EVAL_STORE: dict[str, Deque[GovernanceMetadata]] = {}
_AUDIT_STORE: dict[str, Deque[GovernanceAuditEvent]] = {}


def _clamp(score: float) -> float:
    return round(max(0.0, min(1.0, score)), 3)


def _status_from_score(score: float) -> str:
    if score >= 0.75:
        return "good"
    if score >= 0.5:
        return "fair"
    return "needs_attention"


def _store_evaluation(learner_id: str, meta: GovernanceMetadata) -> None:
    if not learner_id:
        return
    bucket = _EVAL_STORE.setdefault(learner_id, deque(maxlen=MAX_STORED_EVALUATIONS))
    bucket.append(meta)


def _store_audit(learner_id: str, event: GovernanceAuditEvent) -> None:
    if not learner_id:
        return
    bucket = _AUDIT_STORE.setdefault(learner_id, deque(maxlen=MAX_STORED_AUDIT_EVENTS))
    bucket.append(event)


def get_stored_evaluations(learner_id: str, limit: int = 20) -> list[GovernanceMetadata]:
    items = list(_EVAL_STORE.get(learner_id, []))
    return items[-limit:]


def get_stored_audit_events(learner_id: str, limit: int = 50) -> list[GovernanceAuditEvent]:
    items = list(_AUDIT_STORE.get(learner_id, []))
    return items[-limit:]


def get_stored_grounding_evaluations(learner_id: str, limit: int = 20) -> list[GroundingEvaluation]:
    out: list[GroundingEvaluation] = []
    for meta in get_stored_evaluations(learner_id, limit=limit):
        g = meta.metadata.get("grounding_evaluation")
        if g:
            out.append(GroundingEvaluation.model_validate(g))
    return out


class GovernanceService:
    def evaluate_teacher_response(
        self,
        *,
        response: str,
        teacher_brain: dict[str, Any] | None = None,
        corrections: list[Any] | None = None,
        teaching_mode: str | None = None,
        intent: str | None = None,
        agent_output: dict[str, Any] | None = None,
    ) -> TeacherResponseEvaluation:
        teacher_brain = teacher_brain or {}
        agent_output = agent_output or {}
        warnings: list[str] = []
        reasons: list[str] = []

        text = (response or "").strip()
        if not text:
            return TeacherResponseEvaluation(
                score=0.0,
                status="needs_attention",
                reasons=["empty_response"],
                warnings=["empty_response"],
            )

        length = len(text)
        length_compliance = 1.0 if length <= MAX_RESPONSE_CHARS_VOICE else max(
            0.3, 1.0 - (length - MAX_RESPONSE_CHARS_VOICE) / MAX_RESPONSE_CHARS_VOICE
        )
        if length > MAX_RESPONSE_CHARS_VOICE:
            warnings.append("excessive_response_length")

        encouragement_quality = 0.7
        encouragement = agent_output.get("encouragement") or text
        if any(w in encouragement.lower() for w in ("great", "good", "well done", "nice", "keep")):
            encouragement_quality = 1.0
            reasons.append("encouragement_present")

        correction_quality = 0.5
        corr_list = corrections or agent_output.get("grammar_corrections") or []
        if corr_list:
            correction_quality = 0.9
            reasons.append("corrections_provided")
        elif teaching_mode and teaching_mode not in ("none", "delayed"):
            correction_quality = 0.6

        explanation_quality = 0.6
        if teacher_brain.get("teaching_strategy") in (
            "explain_rule", "socratic_question", "immediate_correction", "guided_practice"
        ):
            explanation_quality = 0.85
            reasons.append("teaching_strategy_set")
        if len(text.split()) >= 8:
            explanation_quality = min(1.0, explanation_quality + 0.1)

        practice_prompt_quality = 0.5
        next_prompt = teacher_brain.get("next_prompt") or agent_output.get("follow_up_question")
        if next_prompt and str(next_prompt).strip():
            practice_prompt_quality = 0.95
            reasons.append("practice_prompt_present")
        elif intent in _TEACHING_INTENTS:
            warnings.append("missing_practice_prompt")

        score = _clamp(
            correction_quality * 0.25
            + explanation_quality * 0.25
            + encouragement_quality * 0.15
            + practice_prompt_quality * 0.2
            + length_compliance * 0.15
        )

        return TeacherResponseEvaluation(
            score=score,
            status=_status_from_score(score),
            correction_quality=_clamp(correction_quality),
            explanation_quality=_clamp(explanation_quality),
            encouragement_quality=_clamp(encouragement_quality),
            practice_prompt_quality=_clamp(practice_prompt_quality),
            length_compliance=_clamp(length_compliance),
            reasons=reasons,
            warnings=warnings,
            signals=EvaluationSignals(
                items=[f"length:{length}", f"intent:{intent or 'unknown'}"],
                metadata={"teaching_mode": teaching_mode or "none"},
            ),
        )

    def evaluate_curriculum_recommendation(
        self,
        *,
        curriculum_recommendation: dict[str, Any] | None = None,
        weakest_skill: str | None = None,
        curriculum_metadata: dict[str, Any] | None = None,
        confidence_score: float | None = None,
    ) -> CurriculumEvaluation:
        rec = curriculum_recommendation or {}
        meta = curriculum_metadata or {}
        warnings: list[str] = []
        reasons: list[str] = []

        if not rec.get("lesson_id"):
            return CurriculumEvaluation(
                score=0.5,
                status="fair",
                reasons=["no_curriculum_recommendation"],
                warnings=["no_curriculum_recommendation"],
            )

        skill_focus = str(rec.get("skill_focus", "") or "").lower()
        weakest = str(weakest_skill or "").lower()

        weakest_skill_match = 0.5
        if weakest and skill_focus:
            if skill_focus == weakest or weakest in skill_focus or skill_focus in weakest:
                weakest_skill_match = 1.0
                reasons.append("weakest_skill_aligned")
            else:
                warnings.append("curriculum_mismatch")
                weakest_skill_match = 0.35
        elif skill_focus:
            weakest_skill_match = 0.7

        lesson_relevance = 0.8 if rec.get("title") and rec.get("route") else 0.5
        if rec.get("reason"):
            lesson_relevance = 0.9
            reasons.append("recommendation_reason_present")

        revision_relevance = 0.7
        rule = str(meta.get("rule", ""))
        if rule == "due_revision":
            revision_relevance = 1.0
            reasons.append("revision_rule")

        path_consistency = 0.75
        if rule in ("weakest_skill", "cefr_path", "target_exam"):
            path_consistency = 0.9

        if confidence_score is not None and confidence_score < 0.5:
            if "confidence" not in rec.get("lesson_id", ""):
                warnings.append("weak_recommendation_confidence")

        score = _clamp(
            weakest_skill_match * 0.35
            + lesson_relevance * 0.25
            + revision_relevance * 0.2
            + path_consistency * 0.2
        )

        return CurriculumEvaluation(
            score=score,
            status=_status_from_score(score),
            weakest_skill_match=_clamp(weakest_skill_match),
            lesson_relevance=_clamp(lesson_relevance),
            revision_relevance=_clamp(revision_relevance),
            path_consistency=_clamp(path_consistency),
            reasons=reasons,
            warnings=warnings,
            signals=EvaluationSignals(
                items=[f"lesson:{rec.get('lesson_id')}", f"rule:{rule or 'none'}"],
                metadata={"skill_focus": skill_focus, "weakest_skill": weakest},
            ),
        )

    def evaluate_grounding(
        self,
        *,
        knowledge_grounding: dict[str, Any] | None = None,
        intent: str | None = None,
        tools_invoked: list[str] | None = None,
        teaching_instruction: str | None = None,
    ) -> GroundingEvaluation:
        kg = knowledge_grounding or {}
        warnings: list[str] = []
        reasons: list[str] = []

        chunk_count = int(kg.get("chunk_count", 0) or 0)
        sources = kg.get("sources") or []
        fallback_used = bool(kg.get("fallback_used"))
        lesson_id = kg.get("lesson_id")

        grounding_present = 1.0 if chunk_count > 0 or (
            teaching_instruction and "Teaching knowledge:" in teaching_instruction
        ) else 0.0

        if intent in _TEACHING_INTENTS and grounding_present == 0.0:
            warnings.append("ungrounded_teaching")

        source_count_score = _clamp(min(1.0, chunk_count / 3.0) if chunk_count else (0.5 if teaching_instruction else 0.0))
        if sources:
            reasons.append(f"sources:{len(sources)}")

        fallback_penalty = 0.85 if fallback_used else 1.0
        if fallback_used:
            warnings.append("grounding_fallback_used")

        lesson_match = 0.7
        if lesson_id:
            lesson_match = 1.0
            reasons.append("lesson_grounding_id")

        knowledge_quality = source_count_score * fallback_penalty
        if "grammar_curriculum" in sources:
            knowledge_quality = min(1.0, knowledge_quality + 0.15)
            reasons.append("grammar_curriculum_source")

        score = _clamp(
            grounding_present * 0.3
            + source_count_score * 0.25
            + lesson_match * 0.2
            + knowledge_quality * 0.25
        )

        tools = tools_invoked or []
        if "curriculum_knowledge_base" in tools or "rag_scenario" in tools:
            if chunk_count == 0 and not teaching_instruction:
                warnings.append("knowledge_expected_but_absent")

        return GroundingEvaluation(
            score=score,
            status=_status_from_score(score),
            grounding_present=_clamp(grounding_present),
            source_count_score=_clamp(source_count_score),
            fallback_penalty=_clamp(fallback_penalty),
            lesson_match=_clamp(lesson_match),
            knowledge_quality=_clamp(knowledge_quality),
            reasons=reasons,
            warnings=warnings,
            signals=EvaluationSignals(
                items=[f"chunks:{chunk_count}", f"fallback:{fallback_used}"],
                metadata={"sources": sources, "lesson_id": lesson_id},
            ),
        )

    def evaluate_memory_usage(
        self,
        *,
        memory_meta: dict[str, Any] | None = None,
        recurring_mistakes_count: int | None = None,
    ) -> MemoryEvaluation:
        mem = memory_meta or {}
        warnings: list[str] = []
        reasons: list[str] = []

        mistakes_count = recurring_mistakes_count
        if mistakes_count is None:
            mistakes_count = int(mem.get("recurring_mistakes_count", 0) or 0)

        reflections = bool(mem.get("reflections_available"))
        summary = bool(mem.get("memory_summary_available"))

        recurring_mistakes_used = 0.6 if mistakes_count > 0 else 0.8
        if mistakes_count > 0:
            reasons.append("recurring_mistakes_tracked")
            if not summary:
                warnings.append("missing_memory_context")

        reflections_used = 1.0 if reflections else 0.5
        if reflections:
            reasons.append("reflections_available")

        summary_available = 1.0 if summary else 0.4
        if summary:
            reasons.append("memory_summary_available")

        score = _clamp(
            recurring_mistakes_used * 0.35
            + reflections_used * 0.25
            + summary_available * 0.4
        )

        return MemoryEvaluation(
            score=score,
            status=_status_from_score(score),
            recurring_mistakes_used=_clamp(recurring_mistakes_used),
            reflections_used=_clamp(reflections_used),
            summary_available=_clamp(summary_available),
            reasons=reasons,
            warnings=warnings,
            signals=EvaluationSignals(
                items=[f"mistakes:{mistakes_count}", f"summary:{summary}"],
                metadata=mem,
            ),
        )

    def evaluate_student_outcome(
        self,
        *,
        strongest_skill: str | None = None,
        weakest_skill: str | None = None,
        confidence_score: float | None = None,
        skill_trends: dict[str, str] | None = None,
        has_data: bool = False,
        lesson_completions_count: int = 0,
        assessment_improved: bool = False,
    ) -> StudentOutcomeEvaluation:
        warnings: list[str] = []
        reasons: list[str] = []
        trends = skill_trends or {}

        up = sum(1 for t in trends.values() if t == "up")
        down = sum(1 for t in trends.values() if t == "down")
        progress_trend = 0.5
        if up > down:
            progress_trend = 0.85
            reasons.append("skills_improving")
        elif down > up:
            progress_trend = 0.35
            warnings.append("skills_declining")

        confidence_trend = 0.5
        if confidence_score is not None:
            if confidence_score >= 0.6:
                confidence_trend = 0.9
                reasons.append("confidence_healthy")
            elif confidence_score < 0.4:
                confidence_trend = 0.35
                warnings.append("low_confidence")

        lesson_activity = _clamp(min(1.0, lesson_completions_count / 5.0))
        if lesson_completions_count > 0:
            reasons.append(f"lessons_completed:{lesson_completions_count}")

        assessment_improvement = 0.7 if assessment_improved else 0.5
        if assessment_improved:
            reasons.append("assessment_improved")

        if not has_data:
            return StudentOutcomeEvaluation(
                score=0.5,
                status="fair",
                reasons=["limited_outcome_data"],
                warnings=["limited_outcome_data"],
            )

        score = _clamp(
            progress_trend * 0.35
            + confidence_trend * 0.25
            + lesson_activity * 0.2
            + assessment_improvement * 0.2
        )

        return StudentOutcomeEvaluation(
            score=score,
            status=_status_from_score(score),
            progress_trend=_clamp(progress_trend),
            confidence_trend=_clamp(confidence_trend),
            lesson_activity=_clamp(lesson_activity),
            assessment_improvement=_clamp(assessment_improvement),
            reasons=reasons,
            warnings=warnings,
            signals=EvaluationSignals(
                items=[f"strongest:{strongest_skill}", f"weakest:{weakest_skill}"],
                metadata={"trends": trends},
            ),
        )

    def build_governance_summary(
        self,
        *,
        learner_id: str,
        student_outcome: StudentOutcomeEvaluation | None = None,
    ) -> GovernanceSummary:
        evals = get_stored_evaluations(learner_id)
        if not evals:
            return GovernanceSummary(
                learner_id=learner_id,
                evaluation_count=0,
                student_outcome=student_outcome,
                metadata={"version": GOVERNANCE_VERSION},
            )

        def avg(field: str) -> float:
            vals = [getattr(e, field) for e in evals]
            return round(sum(vals) / len(vals), 3)

        warnings: list[str] = []
        for e in evals:
            warnings.extend(e.warnings[:3])
        warnings = list(dict.fromkeys(warnings))[:10]

        return GovernanceSummary(
            learner_id=learner_id,
            evaluation_count=len(evals),
            avg_teacher_response_score=avg("teacher_response_score"),
            avg_curriculum_score=avg("curriculum_score"),
            avg_grounding_score=avg("grounding_score"),
            avg_memory_score=avg("memory_score"),
            avg_overall_score=avg("overall_score"),
            student_outcome=student_outcome,
            recent_warnings=warnings,
            metadata={"version": GOVERNANCE_VERSION},
        )

    def create_audit_event(
        self,
        *,
        event_type: str,
        learner_id: str | None = None,
        tenant_id: str | None = None,
        trace_id: str | None = None,
        conversation_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> GovernanceAuditEvent:
        event = GovernanceAuditEvent(
            event_type=event_type,
            learner_id=learner_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            conversation_id=conversation_id,
            payload=payload or {},
            created_at=datetime.now(timezone.utc),
        )
        if learner_id:
            _store_audit(learner_id, event)
        return event

    async def persist_audit_event_async(
        self,
        event: GovernanceAuditEvent,
        *,
        learner_id: str,
        tenant_id: str | None,
    ) -> None:
        """Optional persistence via Memory Intelligence learning_event (no new migration)."""
        if not tenant_id:
            return
        try:
            from app.services.memory_intelligence_service import MemoryIntelligenceService

            detail = json.dumps(
                {
                    "governance_event": event.event_type,
                    "trace_id": event.trace_id,
                    "payload": event.payload,
                }
            )[:300]
            await MemoryIntelligenceService().write_learning_event(
                learner_id=learner_id,
                tenant_id=str(tenant_id),
                event_type=f"governance_{event.event_type}",
                detail=detail,
                conversation_id=event.conversation_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("governance.audit_persist_failed", extra={"error": str(exc)})

    def evaluate_turn(
        self,
        *,
        learner_id: str,
        tenant_id: str | None = None,
        trace_id: str | None = None,
        conversation_id: str | None = None,
        response: str,
        intent: str | None = None,
        teacher_brain: dict[str, Any] | None = None,
        agent_output: dict[str, Any] | None = None,
        corrections: list[Any] | None = None,
        teaching_mode: str | None = None,
        teaching_instruction: str | None = None,
        memory_meta: dict[str, Any] | None = None,
        knowledge_grounding: dict[str, Any] | None = None,
        curriculum_recommendation: dict[str, Any] | None = None,
        weakest_skill: str | None = None,
        confidence_score: float | None = None,
        curriculum_rule: str | None = None,
        tools_invoked: list[str] | None = None,
        store: bool = True,
        persist_audit: bool = False,
    ) -> TurnGovernanceEvaluation:
        teacher_eval = self.evaluate_teacher_response(
            response=response,
            teacher_brain=teacher_brain,
            corrections=corrections,
            teaching_mode=teaching_mode,
            intent=intent,
            agent_output=agent_output,
        )
        curriculum_eval = self.evaluate_curriculum_recommendation(
            curriculum_recommendation=curriculum_recommendation,
            weakest_skill=weakest_skill,
            curriculum_metadata={"rule": curriculum_rule or ""},
            confidence_score=confidence_score,
        )
        grounding_eval = self.evaluate_grounding(
            knowledge_grounding=knowledge_grounding,
            intent=intent,
            tools_invoked=tools_invoked,
            teaching_instruction=teaching_instruction,
        )
        memory_eval = self.evaluate_memory_usage(memory_meta=memory_meta)

        warnings = list(dict.fromkeys(
            teacher_eval.warnings
            + curriculum_eval.warnings
            + grounding_eval.warnings
            + memory_eval.warnings
        ))

        overall = _clamp(
            teacher_eval.score * 0.3
            + curriculum_eval.score * 0.2
            + grounding_eval.score * 0.25
            + memory_eval.score * 0.25
        )

        governance = GovernanceMetadata(
            teacher_response_score=teacher_eval.score,
            curriculum_score=curriculum_eval.score,
            grounding_score=grounding_eval.score,
            memory_score=memory_eval.score,
            overall_score=overall,
            warnings=warnings,
            status="ok" if not warnings else "warning",
            trace_id=trace_id,
            metadata={
                "version": GOVERNANCE_VERSION,
                "intent": intent,
                "grounding_evaluation": grounding_eval.model_dump(),
                "teacher_evaluation": teacher_eval.model_dump(),
                "curriculum_evaluation": curriculum_eval.model_dump(),
                "memory_evaluation": memory_eval.model_dump(),
            },
        )

        if store and learner_id:
            _store_evaluation(learner_id, governance)

        audit = self.create_audit_event(
            event_type="teacher_response_generated",
            learner_id=learner_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            conversation_id=conversation_id,
            payload={
                "governance": governance.model_dump(),
                "intent": intent,
            },
        )

        if warnings:
            self.create_audit_event(
                event_type="governance_warning",
                learner_id=learner_id,
                tenant_id=tenant_id,
                trace_id=trace_id,
                conversation_id=conversation_id,
                payload={"warnings": warnings},
            )

        return TurnGovernanceEvaluation(
            teacher=teacher_eval,
            curriculum=curriculum_eval,
            grounding=grounding_eval,
            memory=memory_eval,
            governance=governance,
            audit_event=audit,
        )

    async def evaluate_turn_safe(
        self,
        **kwargs: Any,
    ) -> GovernanceMetadata | None:
        try:
            result = self.evaluate_turn(**kwargs)
            if kwargs.get("persist_audit") and kwargs.get("learner_id"):
                await self.persist_audit_event_async(
                    result.audit_event,
                    learner_id=str(kwargs["learner_id"]),
                    tenant_id=kwargs.get("tenant_id"),
                )
            return result.governance
        except Exception as exc:  # noqa: BLE001
            logger.warning("governance.evaluate_turn_failed", extra={"error": str(exc)})
            return None

    def to_api_metadata(self, governance: GovernanceMetadata) -> dict[str, Any]:
        return {
            "teacher_response_score": governance.teacher_response_score,
            "grounding_score": governance.grounding_score,
            "curriculum_score": governance.curriculum_score,
            "memory_score": governance.memory_score,
            "overall_score": governance.overall_score,
            "warnings": governance.warnings,
            "status": governance.status,
        }
