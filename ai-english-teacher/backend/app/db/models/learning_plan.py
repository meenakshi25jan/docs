import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.types import JsonDocument

if TYPE_CHECKING:
    from app.db.models.user import User


class LearningPlan(TimestampMixin, Base):
    """CASCADE: personalized plan is deleted with the user."""

    __tablename__ = "learning_plan"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)
    plan_data: Mapped[dict[str, Any] | None] = mapped_column(JsonDocument, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="learning_plans")
