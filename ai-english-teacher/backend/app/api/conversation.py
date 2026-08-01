from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import OrchestratorAgent
from app.api.schemas.conversation import (
    AudioConversationResponse,
    BandScoreResponse,
    ConversationRequest,
    ConversationResponse,
    FeedbackItem,
    FeedbackListResponse,
    GrammarCorrectionResult,
    VoiceOutput,
)
from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.services.feedback_service import FeedbackService
from app.services.stt_service import STTService
from app.services.tts_service import TTSService

router = APIRouter(tags=["conversation"])


def get_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


def get_stt_service() -> STTService:
    return STTService()


def get_tts_service() -> TTSService:
    return TTSService()


async def _build_conversation_response(
    *,
    db: AsyncSession,
    user: User,
    mode: str,
    input_type: str,
    result: dict,
    tts_service: TTSService,
) -> ConversationResponse:
    voice_output_data = await tts_service.speak(
        result["teacher_response"],
        voice=user.teacher_voice,
    )
    feedback = await FeedbackService(db).save_feedback(
        user_id=user.id,
        original_text=result.get("original_text", ""),
        corrected_text=result.get("corrected_text", ""),
        explanation=result.get("explanation", ""),
        teacher_response=result.get("teacher_response", ""),
        mistakes=result.get("mistakes", []),
        score=int(result.get("score", 0)),
        mode=mode,
    )
    return ConversationResponse(
        input_type=input_type,
        mode=mode,
        result=GrammarCorrectionResult(**result),
        voice_output=VoiceOutput(**voice_output_data),
        feedback_id=feedback.id,
    )


@router.post("/conversation", response_model=ConversationResponse)
async def conversation(
    payload: ConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
    tts_service: TTSService = Depends(get_tts_service),
) -> ConversationResponse:
    result = await orchestrator.handle(payload.mode, payload.text)
    return await _build_conversation_response(
        db=db,
        user=current_user,
        mode=payload.mode,
        input_type="text",
        result=result,
        tts_service=tts_service,
    )


@router.post("/audio-conversation", response_model=AudioConversationResponse)
async def audio_conversation(
    mode: str = Form("grammar"),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
    stt_service: STTService = Depends(get_stt_service),
    tts_service: TTSService = Depends(get_tts_service),
) -> AudioConversationResponse:
    audio_bytes = await audio.read()
    transcribed_text = await stt_service.transcribe(audio_bytes, filename=audio.filename or "audio.wav")
    result = await orchestrator.handle(mode, transcribed_text)
    base_response = await _build_conversation_response(
        db=db,
        user=current_user,
        mode=mode,
        input_type="audio",
        result=result,
        tts_service=tts_service,
    )
    return AudioConversationResponse(
        **base_response.model_dump(),
        transcribed_text=transcribed_text,
    )


@router.post("/grammar-check", response_model=GrammarCorrectionResult)
async def grammar_check(
    payload: ConversationRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
) -> GrammarCorrectionResult:
    result = await orchestrator.handle("grammar", payload.text)
    return GrammarCorrectionResult(**result)


@router.post("/band-score", response_model=BandScoreResponse)
async def band_score(
    payload: ConversationRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
) -> BandScoreResponse:
    grammar_result = await orchestrator.handle("grammar", payload.text)
    score = int(grammar_result.get("score", 0))

    if score >= 90:
        cefr, ielts = "C1", 7.5
    elif score >= 80:
        cefr, ielts = "B2", 6.5
    elif score >= 65:
        cefr, ielts = "B1", 5.5
    elif score >= 50:
        cefr, ielts = "A2", 4.5
    else:
        cefr, ielts = "A1", 3.5

    return BandScoreResponse(
        grammar_score=score,
        estimated_cefr=cefr,
        estimated_ielts_band=ielts,
        note="This is a basic MVP estimate. Later use a full scoring rubric.",
    )


@router.get("/feedback", response_model=FeedbackListResponse)
async def feedback_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackListResponse:
    items = await FeedbackService(db).list_for_user(current_user.id)
    return FeedbackListResponse(
        items=[FeedbackItem.model_validate(item) for item in items],
        count=len(items),
    )
