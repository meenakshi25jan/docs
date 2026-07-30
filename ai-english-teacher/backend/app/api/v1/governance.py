"""AI Governance API — read-only evaluation and audit endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.schemas.governance import (
    GovernanceAuditLogResponse,
    GovernanceEvaluationsResponse,
    GovernanceGroundingResponse,
    GovernanceQualityResponse,
    GovernanceSummary,
    StudentOutcomeEvaluation,
)
from app.services.governance_service import (
    get_stored_audit_events,
    get_stored_evaluations,
    get_stored_grounding_evaluations,
    GovernanceService,
)
from app.services.student_intelligence_service import get_summary

router = APIRouter(prefix="/governance", tags=["AI Governance"])
_service = GovernanceService()


async def _learner_id(user: TokenPayload, db: AsyncSession):
    learner = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not learner:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Learner profile not found")
    return learner


@router.get("/summary", response_model=GovernanceSummary)
async def governance_summary(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _learner_id(user, db)
    learner_id = str(learner.id)
    student_outcome = None
    try:
        summary = await get_summary(db, user_id=user.user_id)
        trends = {}
        skills = summary.skills
        for name in ("grammar", "vocabulary", "speaking", "fluency", "pronunciation"):
            detail = getattr(skills, name, None)
            if detail and detail.trend:
                trends[name] = detail.trend
        confidence = summary.profile.confidence_score
        if confidence is None and summary.latest_progress:
            confidence = summary.latest_progress.confidence_score
        student_outcome = _service.evaluate_student_outcome(
            strongest_skill=summary.strongest_skill,
            weakest_skill=summary.weakest_skill,
            confidence_score=confidence,
            skill_trends=trends,
            has_data=summary.has_data,
        )
    except Exception:  # noqa: BLE001
        student_outcome = StudentOutcomeEvaluation(score=0.5, status="fair")

    return _service.build_governance_summary(
        learner_id=learner_id,
        student_outcome=student_outcome,
    )


@router.get("/evaluations", response_model=GovernanceEvaluationsResponse)
async def list_evaluations(
    limit: int = Query(20, ge=1, le=100),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _learner_id(user, db)
    evals = get_stored_evaluations(str(learner.id), limit=limit)
    return GovernanceEvaluationsResponse(evaluations=evals, total=len(evals))


@router.get("/quality", response_model=GovernanceQualityResponse)
async def governance_quality(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _learner_id(user, db)
    evals = get_stored_evaluations(str(learner.id), limit=100)
    if not evals:
        return GovernanceQualityResponse(evaluation_count=0)

    n = len(evals)
    warning_count = sum(len(e.warnings) for e in evals)
    return GovernanceQualityResponse(
        avg_teacher_response_score=round(sum(e.teacher_response_score for e in evals) / n, 3),
        avg_grounding_score=round(sum(e.grounding_score for e in evals) / n, 3),
        avg_curriculum_score=round(sum(e.curriculum_score for e in evals) / n, 3),
        avg_memory_score=round(sum(e.memory_score for e in evals) / n, 3),
        avg_overall_score=round(sum(e.overall_score for e in evals) / n, 3),
        evaluation_count=n,
        warning_count=warning_count,
    )


@router.get("/grounding", response_model=GovernanceGroundingResponse)
async def governance_grounding(
    limit: int = Query(20, ge=1, le=100),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _learner_id(user, db)
    evals = get_stored_grounding_evaluations(str(learner.id), limit=limit)
    avg = round(sum(e.score for e in evals) / len(evals), 3) if evals else 0.0
    return GovernanceGroundingResponse(evaluations=evals, avg_score=avg, total=len(evals))


@router.get("/audit-log", response_model=GovernanceAuditLogResponse)
async def governance_audit_log(
    limit: int = Query(50, ge=1, le=200),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _learner_id(user, db)
    events = get_stored_audit_events(str(learner.id), limit=limit)
    return GovernanceAuditLogResponse(events=events, total=len(events))
