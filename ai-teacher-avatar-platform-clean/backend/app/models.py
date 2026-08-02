import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base
from app.embeddings import EMBEDDING_DIM


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120), default="")
    voice_pref: Mapped[str] = mapped_column(String(10), default="female")  # female | male
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user")


class ChatSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(20))  # grammar | conversation | assessment
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String(10))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    correction: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class GrammarProgress(Base):
    __tablename__ = "grammar_progress"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    level: Mapped[int] = mapped_column(default=1)
    streak: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(20))
    score_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# --- Teacher persona / lesson-flow state (the "real teacher" layer) ---------

class LessonProgress(Base):
    """One row per user. This is the teacher's memory: what lesson we're on,
    which stage of today's class we're in, and what was assigned last time.
    """

    __tablename__ = "lesson_progress"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    day_number: Mapped[int] = mapped_column(Integer, default=1)
    stage_index: Mapped[int] = mapped_column(Integer, default=0)  # index into STAGE_ORDER
    lesson_topic: Mapped[str] = mapped_column(String(120), default="Daily Conversation")
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    words_learned: Mapped[int] = mapped_column(Integer, default=0)
    last_session_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    homework_text: Mapped[str] = mapped_column(Text, default="")
    homework_done: Mapped[bool] = mapped_column(Boolean, default=False)
    lesson_session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Book(Base):
    """A book/PDF/notes the student uploaded for the teacher to teach from."""

    __tablename__ = "books"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    chunks: Mapped[list["BookChunk"]] = relationship(back_populates="book")


class BookChunk(Base):
    """A retrievable slice of an uploaded book, used for grounding the
    teacher's explanations. Retrieval is vector similarity search via
    pgvector when `embedding` is set (see book_agent.py); falls back to
    keyword overlap for older chunks ingested before this column existed.
    """

    __tablename__ = "book_chunks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    book: Mapped["Book"] = relationship(back_populates="chunks")


class StudentProfile(Base):
    """What the teacher knows about the student as a person, not just their
    lesson-stage position. This is what makes a warm-up feel like 'welcome
    back' instead of a cold start — the teacher can say "last time you
    struggled with X, let's revisit it" instead of just moving on.
    """

    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    level: Mapped[str] = mapped_column(String(20), default="Intermediate")  # Beginner|Intermediate|Advanced
    target_band: Mapped[Optional[float]] = mapped_column(nullable=True)  # e.g. IELTS target, 1.0-9.0
    native_language: Mapped[str] = mapped_column(String(60), default="")
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["Past tense", "Pronunciation"]
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
