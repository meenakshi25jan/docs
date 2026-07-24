"""SQLAlchemy database models and schema."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ArchiveRecord(Base):
    __tablename__ = "archives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(512))
    file_type: Mapped[str] = mapped_column(String(32))
    original_size: Mapped[int] = mapped_column(Integer)
    compressed_size: Mapped[int] = mapped_column(Integer)
    total_dna_length: Mapped[int] = mapped_column(Integer)
    num_blocks: Mapped[int] = mapped_column(Integer)
    encoding: Mapped[str] = mapped_column(String(32))
    ecc: Mapped[str] = mapped_column(String(32))
    compression: Mapped[str] = mapped_column(String(32))
    checksum: Mapped[str] = mapped_column(String(64))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class DNARecord(Base):
    __tablename__ = "dna_sequences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    archive_id: Mapped[str] = mapped_column(String(36), index=True)
    block_index: Mapped[int] = mapped_column(Integer)
    sequence: Mapped[str] = mapped_column(Text)
    fitness_score: Mapped[float] = mapped_column(Float, default=0.0)
    gc_content: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class ExperimentRecord(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
