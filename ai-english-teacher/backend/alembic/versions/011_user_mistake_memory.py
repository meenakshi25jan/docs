"""user_mistake_memory table

Revision ID: 011_user_mistake_memory
Revises: 010_user_progress
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011_user_mistake_memory"
down_revision: str | None = "010_user_progress"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "user_mistake_memory",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mistake_pattern", sa.String(length=200), nullable=False),
        sa.Column("example_text", sa.Text(), nullable=False),
        sa.Column("correction", sa.Text(), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_mistake_memory_user_id"), "user_mistake_memory", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_user_mistake_memory_mistake_pattern"),
        "user_mistake_memory",
        ["mistake_pattern"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_mistake_memory_mistake_pattern"), table_name="user_mistake_memory")
    op.drop_index(op.f("ix_user_mistake_memory_user_id"), table_name="user_mistake_memory")
    op.drop_table("user_mistake_memory")
