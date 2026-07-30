from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.openai_client import extract_teacher_response
from app.orchestration import run_conversation_turn
from app.orchestration.voice.lesson_report import generate_lesson_report
from app.orchestration.voice.voice_turn import run_voice_turn
from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import Conversation, ConversationMessage, LearnerProfile
from app.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse, VoiceTurnRequest

router = APIRouter(prefix="/conversations", tags=["Conversations"])


async def _get_learner(user: TokenPayload, db: AsyncSession) -> LearnerProfile:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == user.user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return profile


@router.post("", response_model=ConversationResponse, status_code=201)
async def start_conversation(
    req: ConversationCreate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await _get_learner(user, db)
    conv = Conversation(
        tenant_id=user.tenant_id,
        learner_id=learner.id,
        scenario=req.scenario,
        context={"persona_id": req.persona_id, **req.context},
    )
    db.add(conv)
    await db.flush()

    output = await run_conversation_turn(
        session_id=str(conv.id),
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        scenario=req.scenario,
        cefr_level=learner.current_cefr or "B1",
        message="Start the conversation.",
        message_history=[],
    )
    initial_content = extract_teacher_response(output.data) or "Hello! Let's begin our practice session."
    msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=initial_content,
        metadata_=output.data,
    )
    db.add(msg)
    await db.flush()

    return ConversationResponse(
        id=conv.id,
        scenario=conv.scenario,
        status=conv.status,
        initial_message=MessageResponse(role="assistant", content=initial_content),
    )


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    req: MessageCreate,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.scalar(
        select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    learner = await _get_learner(user, db)
    user_msg = ConversationMessage(conversation_id=conv.id, role="user", content=req.content)
    db.add(user_msg)

    history = [{"role": m.role, "content": m.content} for m in conv.messages]
    output = await run_conversation_turn(
        session_id=str(conv.id),
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        scenario=conv.scenario,
        cefr_level=learner.current_cefr or "B1",
        message=req.content,
        message_history=history,
    )

    assistant_content = extract_teacher_response(output.data) or "Could you tell me more about that?"
    response_metadata = dict(output.data)
    if output.metadata:
        response_metadata["_orchestration"] = output.metadata
    assistant_msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_content,
        metadata_=response_metadata,
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "user_message": MessageResponse(role="user", content=req.content),
        "assistant_message": MessageResponse(
            role="assistant",
            content=assistant_content,
            metadata=response_metadata,
        ),
    }


@router.post("/{conversation_id}/voice-turn")
async def voice_turn_in_conversation(
    conversation_id: UUID,
    req: VoiceTurnRequest,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Voice-first turn within an active conversation — unified pipeline."""
    conv = await db.scalar(
        select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    learner = await _get_learner(user, db)
    if not req.transcript and not req.audio_base64:
        raise HTTPException(status_code=400, detail="Provide transcript or audio_base64")

    history = [{"role": m.role, "content": m.content} for m in conv.messages]
    persona_id = req.persona_id or (conv.context or {}).get("persona_id", "conversation_partner")

    result = await run_voice_turn(
        session_id=str(conv.id),
        learner_id=str(learner.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        scenario=conv.scenario,
        cefr_level=learner.current_cefr or "B1",
        message_history=history,
        transcript=req.transcript,
        audio_base64=req.audio_base64,
        audio_mime_type=req.audio_mime_type,
        duration_seconds=req.duration_seconds,
        audio_metrics=req.audio_metrics,
        persona_id=persona_id,
        conversation_id=str(conv.id),
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    transcript = result["transcript"]
    response_text = result["response"]

    user_msg = ConversationMessage(conversation_id=conv.id, role="user", content=transcript)
    db.add(user_msg)

    response_metadata = {
        **result.get("agent_output", {}),
        "voice_scores": result.get("voice_scores"),
        "teaching_mode": result.get("teaching_mode"),
        "corrections": result.get("corrections"),
        "estimates": result.get("estimates"),
        "_orchestration": result.get("metadata"),
        "memory": result.get("memory"),
        "curriculum_recommendation": result.get("curriculum_recommendation"),
        "knowledge_grounding": result.get("knowledge_grounding"),
    }
    assistant_msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=response_text,
        metadata_=response_metadata,
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "transcript": transcript,
        "response": response_text,
        "teaching_mode": result.get("teaching_mode"),
        "corrections": result.get("corrections", []),
        "voice_scores": result.get("voice_scores"),
        "estimates": result.get("estimates"),
        "teacher_brain": result.get("teacher_brain"),
        "memory": result.get("memory"),
        "curriculum_recommendation": result.get("curriculum_recommendation"),
        "knowledge_grounding": result.get("knowledge_grounding"),
        "user_message": MessageResponse(role="user", content=transcript),
        "assistant_message": MessageResponse(
            role="assistant",
            content=response_text,
            metadata=response_metadata,
        ),
    }


@router.get("/{conversation_id}/lesson-report")
async def get_lesson_report(
    conversation_id: UUID,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.scalar(select(Conversation).where(Conversation.id == conversation_id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    learner = await _get_learner(user, db)
    persona_id = (conv.context or {}).get("persona_id")

    report = await generate_lesson_report(
        db=db,
        learner_id=learner.id,
        tenant_id=user.tenant_id,
        conversation_id=conversation_id,
        persona_id=persona_id,
        scenario=conv.scenario,
    )
    if report.get("error"):
        raise HTTPException(status_code=404, detail=report["error"])
    return report
