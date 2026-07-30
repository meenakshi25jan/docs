from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import LearnerProfile
from app.orchestration.personas import list_personas, list_scenarios
from app.orchestration.voice.pipeline import run_voice_analysis
from app.orchestration.voice.voice_turn import run_voice_turn
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/voice", tags=["Voice"])


class VoiceAnalyzeRequest(BaseModel):
    transcript: str | None = Field(None, max_length=10000)
    audio_base64: str | None = None
    audio_mime_type: str = "audio/webm"
    duration_seconds: float | None = Field(None, ge=0, le=600)
    audio_metrics: dict | None = None
    conversation_id: UUID | None = None


class VoiceTurnRequest(BaseModel):
    transcript: str | None = Field(None, max_length=10000)
    audio_base64: str | None = None
    audio_mime_type: str = "audio/webm"
    duration_seconds: float | None = Field(None, ge=0, le=600)
    audio_metrics: dict | None = None
    conversation_id: UUID | None = None
    scenario: str = "general_conversation"
    persona_id: str = "conversation_partner"
    message_history: list[dict[str, str]] = Field(default_factory=list)


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.get("/personas")
async def get_personas():
    return {"personas": list_personas(), "scenarios": list_scenarios()}


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


@router.post("/turn")
async def voice_turn(
    req: VoiceTurnRequest,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unified voice conversation turn — analyze speech, coach agents, teacher response."""
    learner = await _get_learner(user, db)
    if not req.transcript and not req.audio_base64:
        raise HTTPException(status_code=400, detail="Provide transcript or audio_base64")

    session_id = str(req.conversation_id) if req.conversation_id else f"voice-{learner.id}"

    result = await run_voice_turn(
        session_id=session_id,
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        scenario=req.scenario,
        cefr_level=learner.current_cefr or "B1",
        message_history=req.message_history,
        transcript=req.transcript,
        audio_base64=req.audio_base64,
        audio_mime_type=req.audio_mime_type,
        duration_seconds=req.duration_seconds,
        audio_metrics=req.audio_metrics,
        persona_id=req.persona_id,
        conversation_id=str(req.conversation_id) if req.conversation_id else None,
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result
