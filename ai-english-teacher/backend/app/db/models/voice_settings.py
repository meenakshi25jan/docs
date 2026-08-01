import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class VoiceSettings(TimestampMixin, Base):
    """CASCADE: per-user TTS preferences."""

    __tablename__ = "voice_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    preferred_voice: Mapped[str] = mapped_column(String(50), default="female", nullable=False)
    speed: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0, nullable=False)
    pitch: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="voice_settings")
