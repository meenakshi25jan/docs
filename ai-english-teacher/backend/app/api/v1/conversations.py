from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import get_db
from app.core.security import TokenPayload, get_current_user
from app.models import Conversation, ConversationMessage, LearnerProfile
from app.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse

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
        context=req.context,
    )
    db.add(conv)
    await db.flush()

    teacher = AGENT_REGISTRY["teacher"]
    output = await teacher.execute(AgentInput(
        learner_id=str(learner.id),
        context={
            "scenario": req.scenario,
            "cefr_level": learner.current_cefr or "B1",
            "message": "Start the conversation.",
            "message_history": [],
        },
    ))
    initial_content = output.data.get("response", "Hello! Let's begin our practice session.")
    msg = ConversationMessage(conversation_id=conv.id, role="assistant", content=initial_content)
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
    teacher = AGENT_REGISTRY["teacher"]
    output = await teacher.execute(AgentInput(
        learner_id=str(learner.id),
        context={
            "scenario": conv.scenario,
            "cefr_level": learner.current_cefr or "B1",
            "message": req.content,
            "message_history": history,
        },
    ))

    assistant_content = output.data.get("response", "Interesting! Tell me more.")
    assistant_msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_content,
        metadata_=output.data,
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "user_message": MessageResponse(role="user", content=req.content),
        "assistant_message": MessageResponse(
            role="assistant",
            content=assistant_content,
            metadata=output.data,
        ),
    }
