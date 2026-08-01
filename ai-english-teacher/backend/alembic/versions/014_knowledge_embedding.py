"""knowledge_embedding table with pgvector HNSW index

Revision ID: 014_knowledge_embedding
Revises: 013_enable_vector
Create Date: 2026-08-01

Embedding dimension is provider-dependent — currently set for all-MiniLM-L6-v2 (384-dim).
If switching embedding providers, this column must be migrated (ALTER COLUMN ... TYPE vector(N))
and all existing embeddings regenerated, since vectors from different models are not
compatible or comparable.

HNSW index: no training step required (unlike IVFFlat), better recall on small/medium
knowledge bases, and supports incremental inserts — good fit for MVP RAG growth.

"""

from collections.abc import Sequence
import os

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "014_knowledge_embedding"
down_revision: str | None = "013_enable_vector"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", "384"))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.create_table(
        "knowledge_embedding",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("knowledge_type", sa.String(length=50), nullable=False),
        sa.Column("knowledge_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSION), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_knowledge_embedding_knowledge_type"),
        "knowledge_embedding",
        ["knowledge_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_embedding_knowledge_id"),
        "knowledge_embedding",
        ["knowledge_id"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_embedding_type_id",
        "knowledge_embedding",
        ["knowledge_type", "knowledge_id"],
        unique=False,
    )
    op.execute(
        "CREATE INDEX ix_knowledge_embedding_embedding_hnsw "
        "ON knowledge_embedding USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS ix_knowledge_embedding_embedding_hnsw")
    op.drop_index("ix_knowledge_embedding_type_id", table_name="knowledge_embedding")
    op.drop_index(op.f("ix_knowledge_embedding_knowledge_id"), table_name="knowledge_embedding")
    op.drop_index(op.f("ix_knowledge_embedding_knowledge_type"), table_name="knowledge_embedding")
    op.drop_table("knowledge_embedding")
