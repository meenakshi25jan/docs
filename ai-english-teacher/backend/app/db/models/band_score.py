import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class BandScore(TimestampMixin, Base):
    """RESTRICT on user delete: preserve assessment history for analytics/audit."""

    __tablename__ = "band_score"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grammar_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vocabulary_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fluency_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pronunciation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cefr_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ielts_band: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="band_scores")
