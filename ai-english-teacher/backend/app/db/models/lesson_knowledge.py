import uuid

from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.types import StringArray


class LessonKnowledge(TimestampMixin, Base):
    """Standalone knowledge base content (RAG source documents)."""

    __tablename__ = "lesson_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    skill: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    topic: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[list[str] | None] = mapped_column(StringArray, nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
