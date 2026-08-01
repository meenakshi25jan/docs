"""knowledge_document table

Revision ID: 017_knowledge_document
Revises: 016_knowledge_source
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "017_knowledge_document"
down_revision: str | None = "016_knowledge_source"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "knowledge_document",
        _uuid_pk(),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=20), server_default="en", nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_document_source_id"), "knowledge_document", ["source_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_document_source_id"), table_name="knowledge_document")
    op.drop_table("knowledge_document")
