from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user, require_role
from app.models import (
    Assessment,
    LearnerProfile,
    LearningPlan,
    LearningPlanItem,
    ProgressSnapshot,
    User,
    WritingSubmission,
)
from app.schemas import (
    AdminDashboard,
    LearningPlanCreate,
    ReportGenerate,
    SkillScores,
    StudentDashboard,
    TeacherDashboard,
    WritingResponse,
    WritingSubmit,
)

router = APIRouter(tags=["Extended APIs"])


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


# ── Writing ───────────────────────────────────────────────────────────────────

writing_router = APIRouter(prefix="/writing", tags=["Writing"])


@writing_router.post("/submit", response_model=WritingResponse)
async def submit_writing(
    req: WritingSubmit,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    agent = AGENT_REGISTRY["writing"]
    output = await agent.execute(AgentInput(
        learner_id=str(learner.id),
        context={"prompt": req.prompt, "content": req.content},
    ))
    data = output.data
    submission = WritingSubmission(
        tenant_id=user.tenant_id,
        learner_id=learner.id,
        prompt=req.prompt,
        content=req.content,
        word_count=len(req.content.split()),
        grammar_score=data.get("grammatical_range"),
        vocabulary_score=data.get("lexical_resource"),
        coherence_score=data.get("coherence"),
        overall_score=data.get("overall_score"),
        feedback=data,
    )
    db.add(submission)
    await db.flush()

    return WritingResponse(
        id=submission.id,
        scores={
            "grammar": data.get("grammatical_range", 70),
            "vocabulary": data.get("lexical_resource", 70),
            "coherence": data.get("coherence", 70),
            "overall": data.get("overall_score", 70),
        },
        feedback={
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
            "errors": data.get("errors", []),
        },
        estimates=data.get("estimates", {}),
    )


# ── Learning Plans ────────────────────────────────────────────────────────────

plans_router = APIRouter(prefix="/learning-plans", tags=["Learning Plans"])


@plans_router.post("", status_code=201)
async def create_learning_plan(
    req: LearningPlanCreate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    agent = AGENT_REGISTRY["planner"]
    output = await agent.execute(AgentInput(
        learner_id=str(learner.id),
        context={
            "duration_weeks": req.duration_weeks,
            "cefr_level": learner.current_cefr or "B1",
            "target_exam": req.target_exam,
            "target_score": req.target_score,
            "hours_per_week": req.hours_per_week,
            "skill_scores": {},
        },
    ))
    plan_data = output.data
    from datetime import datetime, timezone, timedelta

    plan = LearningPlan(
        tenant_id=user.tenant_id,
        learner_id=learner.id,
        goals=plan_data.get("goals", []),
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(weeks=req.duration_weeks),
    )
    db.add(plan)
    await db.flush()

    for week in plan_data.get("weeks", []):
        for item in week.get("items", []):
            db.add(LearningPlanItem(
                plan_id=plan.id,
                skill=item.get("skill", "grammar"),
                item_type=item.get("type", "exercise"),
                description=item.get("description", ""),
                priority=item.get("priority", 0),
            ))

    return {"id": plan.id, "goals": plan.goals, "weeks": plan_data.get("weeks", [])}


# ── Dashboard ───────────────────────────────────────────────────────────────

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/student", response_model=StudentDashboard)
async def student_dashboard(
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    latest = await db.scalar(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.learner_id == learner.id)
        .order_by(ProgressSnapshot.snapshot_at.desc())
        .limit(1)
    )

    scores = SkillScores()
    if latest:
        scores = SkillScores(
            grammar=float(latest.grammar_score or 0),
            vocabulary=float(latest.vocabulary_score or 0),
            writing=float(latest.writing_score or 0),
            reading=float(latest.reading_score or 0),
            listening=float(latest.listening_score or 0),
            speaking=float(latest.speaking_score or 0),
        )

    return StudentDashboard(
        learner={
            "current_cefr": learner.current_cefr or "B1",
            "ielts_estimate": float(learner.ielts_estimate or 6.0),
            "pte_estimate": learner.pte_estimate or 50,
        },
        skill_scores=scores,
        learning_plan_progress={"completed": 0, "total": 0, "percentage": 0},
    )


@dashboard_router.get("/teacher", response_model=TeacherDashboard)
async def teacher_dashboard(
    user: TokenPayload = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    count = await db.scalar(
        select(func.count()).select_from(LearnerProfile).where(LearnerProfile.tenant_id == user.tenant_id)
    )
    return TeacherDashboard(
        class_size=count or 0,
        average_scores=SkillScores(grammar=72, vocabulary=68, writing=70, reading=75, listening=70, speaking=65),
        active_learners=count or 0,
    )


@dashboard_router.get("/admin", response_model=AdminDashboard)
async def admin_dashboard(
    user: TokenPayload = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    user_count = await db.scalar(select(func.count()).select_from(User))
    return AdminDashboard(
        total_users=user_count or 0,
        total_tenants=1,
        active_sessions=0,
        ai_calls_today=0,
        system_health={"status": "healthy", "uptime": "99.9%"},
    )


# ── Reports ───────────────────────────────────────────────────────────────────

reports_router = APIRouter(prefix="/reports", tags=["Reports"])


@reports_router.post("/generate")
async def generate_report(
    req: ReportGenerate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    agent = AGENT_REGISTRY["report"]
    output = await agent.execute(AgentInput(
        learner_id=str(learner.id),
        context={"report_type": req.report_type, "progress_data": {"cefr": learner.current_cefr}},
    ))
    return {"id": uuid4(), "report_type": req.report_type, "content": output.data}
