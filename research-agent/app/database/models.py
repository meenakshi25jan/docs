"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.utils.helpers import utc_now


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


class CrawlJob(Base):
    """Represents a research crawl job."""

    __tablename__ = "crawl_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    depth: Mapped[int] = mapped_column(Integer, default=2)
    max_pages: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_paths: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    pages: Mapped[list[Page]] = relationship(
        "Page", back_populates="job", cascade="all, delete-orphan"
    )


class Page(Base):
    """Crawled page content and metadata."""

    __tablename__ = "pages"
    __table_args__ = (UniqueConstraint("job_id", "url", name="uq_job_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("crawl_jobs.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    h1: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    h2: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    paragraphs: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    lists: Mapped[list[list[str]] | None] = mapped_column(JSON, nullable=True)
    tables: Mapped[list[list[list[str]]] | None] = mapped_column(JSON, nullable=True)
    images: Mapped[list[dict[str, str]] | None] = mapped_column(JSON, nullable=True)
    links: Mapped[list[dict[str, str]] | None] = mapped_column(JSON, nullable=True)
    pdfs: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    visible_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    depth: Mapped[int] = mapped_column(Integer, default=0)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetch_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    job: Mapped[CrawlJob] = relationship("CrawlJob", back_populates="pages")


class SearchResult(Base):
    """Stored search engine results for a job."""

    __tablename__ = "search_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("crawl_jobs.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    provider: Mapped[str] = mapped_column(String(32), default="duckduckgo")


def page_to_dict(page: Page) -> dict[str, Any]:
    """Serialize a Page model to a dictionary."""
    return {
        "id": page.id,
        "url": page.url,
        "title": page.title,
        "meta_description": page.meta_description,
        "h1": page.h1 or [],
        "h2": page.h2 or [],
        "paragraphs": page.paragraphs or [],
        "lists": page.lists or [],
        "tables": page.tables or [],
        "images": page.images or [],
        "links": page.links or [],
        "pdfs": page.pdfs or [],
        "visible_text": page.visible_text,
        "language": page.language,
        "depth": page.depth,
        "status_code": page.status_code,
        "crawled_at": page.crawled_at.isoformat() if page.crawled_at else None,
    }
