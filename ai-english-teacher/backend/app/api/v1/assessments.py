from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import Assessment, AssessmentResult, LearnerProfile
from app.schemas import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentResultResponse,
    AssessmentSubmit,
    SkillResult,
)
from app.scoring.engine import aggregate_scores, score_to_cefr, score_to_ielts, score_to_pte

router = APIRouter(prefix="/assessments", tags=["Assessments"])


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.post("", response_model=AssessmentResponse, status_code=201)
async def create_assessment(
    req: AssessmentCreate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    assessment = Assessment(
        tenant_id=user.tenant_id,
        learner_id=learner.id,
        assessment_type=req.assessment_type,
        config=req.config,
    )
    db.add(assessment)
    await db.flush()
    return AssessmentResponse.model_validate(assessment)


@router.get("", response_model=list[AssessmentResponse])
async def list_assessments(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    result = await db.scalars(
        select(Assessment).where(Assessment.learner_id == learner.id).order_by(Assessment.created_at.desc()).limit(20)
    )
    return [AssessmentResponse.model_validate(a) for a in result.all()]


@router.post("/{assessment_id}/start", response_model=AssessmentResponse)
async def start_assessment(
    assessment_id: UUID,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    assessment.status = "in_progress"
    assessment.started_at = datetime.now(timezone.utc)
    return AssessmentResponse.model_validate(assessment)


@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
async def submit_assessment(
    assessment_id: UUID,
    req: AssessmentSubmit,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    learner = await _get_learner(user, db)
    results: dict[str, SkillResult] = {}
    skill_score_map: dict[str, float] = {}

    for answer in req.answers:
        agent = AGENT_REGISTRY.get(answer.skill, AGENT_REGISTRY["assessment"])
        output = await agent.execute(AgentInput(
            learner_id=str(learner.id),
            tenant_id=str(user.tenant_id),
            context={"skill": answer.skill, "responses": [answer.response], "text": answer.response},
        ))
        data = output.data
        score = data.get("score", 70.0)
        skill_score_map[answer.skill] = score

        result = AssessmentResult(
            assessment_id=assessment.id,
            skill=answer.skill,
            score=score,
            confidence=data.get("confidence", 0.8),
            cefr_estimate=data.get("cefr_estimate", score_to_cefr(score)),
            ielts_estimate=data.get("ielts_estimate", score_to_ielts(score)),
            pte_estimate=data.get("pte_estimate", score_to_pte(score)),
            details=data,
        )
        db.add(result)
        results[answer.skill] = SkillResult(
            score=score,
            confidence=data.get("confidence", 0.8),
            cefr_estimate=result.cefr_estimate,
            ielts_estimate=float(result.ielts_estimate) if result.ielts_estimate else None,
            pte_estimate=result.pte_estimate,
            details=data,
        )

    overall = aggregate_scores(skill_score_map)
    assessment.status = "completed"
    assessment.completed_at = datetime.now(timezone.utc)

    learner.current_cefr = overall.cefr
    learner.ielts_estimate = overall.ielts
    learner.pte_estimate = overall.pte

    return AssessmentResultResponse(
        assessment_id=assessment.id,
        status="completed",
        results=results,
        overall=SkillResult(
            score=overall.overall_score,
            confidence=overall.confidence,
            cefr_estimate=overall.cefr,
            ielts_estimate=overall.ielts,
            pte_estimate=overall.pte,
        ),
    )


@router.get("/{assessment_id}/results", response_model=AssessmentResultResponse)
async def get_results(
    assessment_id: UUID,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    assessment = await db.scalar(
        select(Assessment).options(selectinload(Assessment.results)).where(Assessment.id == assessment_id)
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    results = {}
    skill_map = {}
    for r in assessment.results:
        results[r.skill] = SkillResult(
            score=float(r.score),
            confidence=float(r.confidence) if r.confidence else None,
            cefr_estimate=r.cefr_estimate,
            ielts_estimate=float(r.ielts_estimate) if r.ielts_estimate else None,
            pte_estimate=r.pte_estimate,
            details=r.details,
        )
        skill_map[r.skill] = float(r.score)

    overall = aggregate_scores(skill_map) if skill_map else None
    return AssessmentResultResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        results=results,
        overall=SkillResult(
            score=overall.overall_score,
            confidence=overall.confidence,
            cefr_estimate=overall.cefr,
            ielts_estimate=overall.ielts,
            pte_estimate=overall.pte,
        ) if overall else None,
    )
