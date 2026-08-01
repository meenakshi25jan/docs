import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class UserProfile(TimestampMixin, Base):
    """1:1 extension of users — CASCADE: profile has no meaning without the user."""

    __tablename__ = "user_profile"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    native_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    learning_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")
