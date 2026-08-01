"""
Knowledge embeddings for RAG.

NOTE: Grok (xAI) does NOT provide a public embeddings API. Vectors are produced by a
separate embedding pipeline (default: sentence-transformers/all-MiniLM-L6-v2).

Embedding dimension is provider-dependent — currently set for all-MiniLM-L6-v2 (384-dim).
If switching embedding providers, this column must be migrated (ALTER COLUMN ... TYPE vector(N))
and all existing embeddings regenerated, since vectors from different models are not
compatible or comparable.

Deferred (future phase): vocabulary_mastery, achievement, user_achievement, grammar_rule,
vocabulary_knowledge, tenant, teacher, organization, course, assignment, report,
audit_log, subscription, payment.
"""

import uuid

from sqlalchemy import Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.types import EmbeddingVector

_EMBEDDING_DIM = get_settings().EMBEDDING_DIMENSION


class KnowledgeEmbedding(TimestampMixin, Base):
    """Polymorphic embedding row — knowledge_type validated in app code, not DB FK."""

    __tablename__ = "knowledge_embedding"
    __table_args__ = (
        Index("ix_knowledge_embedding_type_id", "knowledge_type", "knowledge_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    knowledge_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    knowledge_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(EmbeddingVector(_EMBEDDING_DIM), nullable=False)
