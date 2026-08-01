import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.band_score import BandScore
    from app.db.models.conversation import ConversationSession
    from app.db.models.feedback import GrammarFeedback
    from app.db.models.learning_plan import LearningPlan
    from app.db.models.user_mistake_memory import UserMistakeMemory
    from app.db.models.user_profile import UserProfile
    from app.db.models.user_progress import UserProgress
    from app.db.models.voice_settings import VoiceSettings


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="student", nullable=False)
    teacher_voice: Mapped[str] = mapped_column(String(20), default="female", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile: Mapped["UserProfile | None"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    conversation_sessions: Mapped[list["ConversationSession"]] = relationship(
        "ConversationSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list["GrammarFeedback"]] = relationship(
        "GrammarFeedback",
        back_populates="user",
    )
    band_scores: Mapped[list["BandScore"]] = relationship(
        "BandScore",
        back_populates="user",
    )
    learning_plans: Mapped[list["LearningPlan"]] = relationship(
        "LearningPlan",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    progress_entries: Mapped[list["UserProgress"]] = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    mistake_memories: Mapped[list["UserMistakeMemory"]] = relationship(
        "UserMistakeMemory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    voice_settings: Mapped["VoiceSettings | None"] = relationship(
        "VoiceSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
