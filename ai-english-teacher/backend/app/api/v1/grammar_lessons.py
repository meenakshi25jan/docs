"""Grammar Class API — voice-based lessons for grades 5–12."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.orchestration.voice.pipeline import run_voice_analysis
from app.services.grammar_curriculum import (
    GRADE_LEVELS,
    get_grade_info,
    get_lesson,
    get_lessons_for_grade,
)

router = APIRouter(prefix="/grammar", tags=["Grammar Class"])


class GrammarPracticeRequest(BaseModel):
    grade: int = Field(..., ge=5, le=12)
    lesson_id: str
    transcript: str | None = Field(None, max_length=5000)
    audio_base64: str | None = None
    audio_mime_type: str = "audio/webm"
    duration_seconds: float | None = Field(None, ge=0, le=300)


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.get("/grades")
async def list_grades():
    return [
        {"grade": g, **info, "lesson_count": len(get_lessons_for_grade(g))}
        for g, info in sorted(GRADE_LEVELS.items())
    ]


@router.get("/lessons")
async def list_lessons(grade: int = Query(..., ge=5, le=12)):
    info = get_grade_info(grade)
    if not info:
        raise HTTPException(status_code=404, detail="Grade not found")
    return {"grade": grade, **info, "lessons": get_lessons_for_grade(grade)}


@router.post("/practice")
async def grammar_practice(
    req: GrammarPracticeRequest,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    lesson = get_lesson(req.grade, req.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    grade_info = get_grade_info(req.grade)
    cefr = grade_info["cefr"] if grade_info else "B1"

    voice_result: dict = {}
    if req.transcript or req.audio_base64:
        voice_result = await run_voice_analysis(
            learner_id=str(learner.id),
            tenant_id=str(user.tenant_id),
            transcript=req.transcript,
            audio_base64=req.audio_base64,
            audio_mime_type=req.audio_mime_type,
            duration_seconds=req.duration_seconds,
            cefr_level=cefr,
        )
        if voice_result.get("error"):
            raise HTTPException(status_code=400, detail=voice_result["error"])

    student_text = voice_result.get("transcript") or req.transcript or ""
    if not student_text.strip():
        raise HTTPException(status_code=400, detail="Say or type a sentence to practice.")

    grammar_out = await AGENT_REGISTRY["grammar"].execute(AgentInput(
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id),
        context={"text": student_text, "cefr_level": cefr},
    ))

    teacher_out = await AGENT_REGISTRY["grammar_teacher"].execute(AgentInput(
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id),
        context={
            "grade": req.grade,
            "lesson_title": lesson["title"],
            "lesson_rule": lesson["rule"],
            "student_text": student_text,
            "grammar_errors": grammar_out.data.get("errors", []),
            "grammar_score": grammar_out.data.get("score", 0),
        },
    ))

    return {
        "grade": req.grade,
        "lesson": lesson,
        "transcript": student_text,
        "grammar_score": grammar_out.data.get("score"),
        "errors": grammar_out.data.get("errors", []),
        "voice": {
            "fluency": voice_result.get("fluency"),
            "pronunciation": voice_result.get("pronunciation"),
            "overall_score": voice_result.get("overall_score"),
        } if voice_result else None,
        "teacher": teacher_out.data,
    }


@router.get("/intro")
async def lesson_intro(
    grade: int = Query(..., ge=5, le=12),
    lesson_id: str = Query(...),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_learner(user, db)
    lesson = get_lesson(grade, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    intro = await AGENT_REGISTRY["grammar_teacher"].execute(AgentInput(
        learner_id="intro",
        tenant_id=str(user.tenant_id),
        context={
            "grade": grade,
            "lesson_title": lesson["title"],
            "lesson_rule": lesson["rule"],
            "mode": "intro",
            "student_text": "",
            "grammar_errors": [],
            "grammar_score": 0,
        },
    ))
    return {"lesson": lesson, "intro": intro.data}
