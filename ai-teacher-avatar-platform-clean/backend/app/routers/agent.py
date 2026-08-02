from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import orchestrator
from app.database import get_db
from app.guardrails import GuardrailError
from app.models import GrammarProgress, User
from app.schemas import AgentMessageRequest, AgentMessageResponse, GrammarNextResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/message", response_model=AgentMessageResponse)
async def send_message(
    req: AgentMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await orchestrator.handle(db, user, req)
    except GuardrailError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.message if hasattr(e, "message") else str(e))


@router.get("/grammar/level", response_model=GrammarNextResponse)
async def get_grammar_level(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(GrammarProgress).where(GrammarProgress.user_id == user.id))
    progress = result.scalar_one_or_none()
    level = progress.level if progress else 1
    return GrammarNextResponse(level=level, exercise="Say a sentence using the verb 'to be'.")
