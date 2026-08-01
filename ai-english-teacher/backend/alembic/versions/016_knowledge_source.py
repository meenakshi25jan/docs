"""knowledge_source table

Revision ID: 016_knowledge_source
Revises: 015_voice_settings
Create Date: 2026-08-01

source_type and ingestion_status use PostgreSQL CHECK constraints for defense in depth;
app-level enums (SourceType, IngestionStatus) remain the primary API contract.

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016_knowledge_source"
down_revision: str | None = "015_voice_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SOURCE_TYPES = "'pdf', 'book', 'website', 'image', 'docx', 'manual'"
_INGESTION_STATUSES = "'pending', 'processing', 'completed', 'failed'"


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "knowledge_source",
        _uuid_pk(),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("publisher", sa.String(length=200), nullable=True),
        sa.Column("license_type", sa.String(length=100), nullable=True),
        sa.Column(
            "ingestion_status",
            sa.String(length=50),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(f"source_type IN ({_SOURCE_TYPES})", name="ck_knowledge_source_source_type"),
        sa.CheckConstraint(
            f"ingestion_status IN ({_INGESTION_STATUSES})",
            name="ck_knowledge_source_ingestion_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_source_source_type"), "knowledge_source", ["source_type"], unique=False)
    op.create_index(
        op.f("ix_knowledge_source_ingestion_status"),
        "knowledge_source",
        ["ingestion_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_source_ingestion_status"), table_name="knowledge_source")
    op.drop_index(op.f("ix_knowledge_source_source_type"), table_name="knowledge_source")
    op.drop_table("knowledge_source")
