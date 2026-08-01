import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import ConversationMode, SessionStatus
from app.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class ConversationSession(TimestampMixin, Base):
    """CASCADE from user: sessions are owned by the learner."""

    __tablename__ = "conversation_session"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mode: Mapped[str] = mapped_column(
        String(30), default=ConversationMode.GRAMMAR.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default=SessionStatus.ACTIVE.value, nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="conversation_sessions")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ConversationMessage(TimestampMixin, Base):
    """CASCADE from session: messages cannot exist without their session."""

    __tablename__ = "conversation_message"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversation_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    session: Mapped["ConversationSession"] = relationship(
        "ConversationSession", back_populates="messages"
    )
