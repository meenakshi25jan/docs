from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.lesson_orchestrator import lesson_orchestrator
from app.database import get_db
from app.guardrails import GuardrailError
from app.models import User
from app.schemas import LessonMessageRequest, LessonMessageResponse, LessonTodayResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/lesson", tags=["lesson"])


@router.get("/today", response_model=LessonTodayResponse)
async def get_today(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Called when the student opens the classroom. Returns the teacher's
    greeting/opening line for wherever they are in today's class — resuming
    an in-progress lesson, or starting a fresh day.
    """
    try:
        return await lesson_orchestrator.get_today(db, user)
    except GuardrailError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.message)


@router.post("/message", response_model=LessonMessageResponse)
async def send_lesson_message(
    req: LessonMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await lesson_orchestrator.handle_message(db, user, req.session_id, req.text)
    except GuardrailError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.message)
