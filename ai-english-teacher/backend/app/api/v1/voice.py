from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.orchestration.voice.pipeline import run_voice_analysis
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/voice", tags=["Voice"])


class VoiceAnalyzeRequest(BaseModel):
    transcript: str | None = Field(None, max_length=10000)
    audio_base64: str | None = None
    audio_mime_type: str = "audio/webm"
    duration_seconds: float | None = Field(None, ge=0, le=600)
    audio_metrics: dict | None = None
    conversation_id: UUID | None = None


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.post("/analyze")
async def analyze_voice(
    req: VoiceAnalyzeRequest,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    if not req.transcript and not req.audio_base64:
        raise HTTPException(status_code=400, detail="Provide transcript or audio_base64")

    result = await run_voice_analysis(
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id),
        transcript=req.transcript,
        audio_base64=req.audio_base64,
        audio_mime_type=req.audio_mime_type,
        duration_seconds=req.duration_seconds,
        audio_metrics=req.audio_metrics,
        conversation_id=str(req.conversation_id) if req.conversation_id else None,
        cefr_level=learner.current_cefr or "B1",
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result
