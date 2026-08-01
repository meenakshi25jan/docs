"""document knowledge_chunk as valid knowledge_embedding.knowledge_type

Revision ID: 019_knowledge_embedding_knowledge_chunk
Revises: 018_knowledge_chunk
Create Date: 2026-08-01

knowledge_type is validated in application code (KnowledgeType enum), not via DB CHECK.
This migration documents the additive knowledge_chunk value for ingestion pipeline rows.

"""

from collections.abc import Sequence

from alembic import op

revision: str = "019_kb_embed_chunk_type"
down_revision: str | None = "018_knowledge_chunk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "COMMENT ON COLUMN knowledge_embedding.knowledge_type IS "
            "'Polymorphic target type: lesson_knowledge, knowledge_chunk, grammar_rule, "
            "vocabulary_knowledge (app-level enum, not DB CHECK)'"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("COMMENT ON COLUMN knowledge_embedding.knowledge_type IS NULL")
