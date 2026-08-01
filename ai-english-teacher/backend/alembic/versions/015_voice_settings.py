"""voice_settings table

Revision ID: 015_voice_settings
Revises: 014_knowledge_embedding
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "015_voice_settings"
down_revision: str | None = "014_knowledge_embedding"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "voice_settings",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("preferred_voice", sa.String(length=50), server_default="female", nullable=False),
        sa.Column("speed", sa.Numeric(precision=3, scale=2), server_default="1.0", nullable=False),
        sa.Column("pitch", sa.Numeric(precision=4, scale=2), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_voice_settings_user_id"), "voice_settings", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_voice_settings_user_id"), table_name="voice_settings")
    op.drop_table("voice_settings")
