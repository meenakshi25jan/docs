import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.assessment_agent import assessment_agent
from app.agents.conversation_agent import conversation_agent
from app.agents.grammar_agent import grammar_agent
from app.guardrails import GuardrailError, check_input
from app.models import Attempt, ChatSession, GrammarProgress, Message, User
from app.schemas import AgentMessageRequest, AgentMessageResponse


class Orchestrator:
    """Routes a validated request to the right worker agent, persists the
    exchange, and returns a fully-populated response. This is the ONLY place
    that knows about all three agents — agents don't call each other.
    """

    async def handle(
        self, db: AsyncSession, user: User, req: AgentMessageRequest
    ) -> AgentMessageResponse:
        clean_text = check_input(req.text)  # raises GuardrailError if unsafe

        session = await self._get_or_create_session(db, user, req)

        if req.mode == "grammar":
            progress = await self._get_or_create_progress(db, user)
            response, advanced = await grammar_agent.handle(clean_text, progress.level)
            if advanced:
                progress.level = response.level

        elif req.mode == "conversation":
            response = await conversation_agent.handle(clean_text)

        elif req.mode == "assessment":
            response = await assessment_agent.handle(clean_text)
            db.add(
                Attempt(
                    user_id=user.id,
                    mode="assessment",
                    score_json={
                        "band_score": response.band_score,
                        **(response.details or {}),
                    },
                )
            )
        else:
            raise GuardrailError(f"Unknown mode: {req.mode}")

        response.session_id = session.id

        db.add(Message(session_id=session.id, role="user", content=clean_text))
        db.add(
            Message(
                session_id=session.id,
                role="assistant",
                content=response.reply_text,
                correction=response.correction or "",
            )
        )
        await db.commit()

        return response

    async def _get_or_create_session(
        self, db: AsyncSession, user: User, req: AgentMessageRequest
    ) -> ChatSession:
        if req.session_id:
            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.id == req.session_id, ChatSession.user_id == user.id
                )
            )
            session = result.scalar_one_or_none()
            if session:
                return session

        session = ChatSession(id=str(uuid.uuid4()), user_id=user.id, mode=req.mode)
        db.add(session)
        await db.flush()
        return session

    async def _get_or_create_progress(self, db: AsyncSession, user: User) -> GrammarProgress:
        result = await db.execute(
            select(GrammarProgress).where(GrammarProgress.user_id == user.id)
        )
        progress = result.scalar_one_or_none()
        if progress:
            return progress
        progress = GrammarProgress(user_id=user.id, level=1)
        db.add(progress)
        await db.flush()
        return progress


orchestrator = Orchestrator()
