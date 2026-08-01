from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.feedback import GrammarFeedback


class FeedbackService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_feedback(
        self,
        *,
        user_id: UUID,
        original_text: str,
        corrected_text: str,
        explanation: str,
        teacher_response: str,
        mistakes: list[str],
        score: int,
        mode: str,
    ) -> GrammarFeedback:
        feedback = GrammarFeedback(
            user_id=user_id,
            original_text=original_text,
            corrected_text=corrected_text,
            explanation=explanation,
            teacher_response=teacher_response,
            mistake_type=", ".join(mistakes) if mistakes else None,
            score=score,
            mode=mode,
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[GrammarFeedback]:
        result = await self.db.execute(
            select(GrammarFeedback)
            .where(GrammarFeedback.user_id == user_id)
            .order_by(GrammarFeedback.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
