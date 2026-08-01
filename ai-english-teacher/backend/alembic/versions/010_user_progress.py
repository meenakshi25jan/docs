"""user_progress table

Revision ID: 010_user_progress
Revises: 009_learning_plan
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010_user_progress"
down_revision: str | None = "009_learning_plan"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "user_progress",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("skill_area", sa.String(length=50), nullable=False),
        sa.Column("level", sa.String(length=10), nullable=True),
        sa.Column("progress_percent", sa.Integer(), server_default="0", nullable=False),
        sa.Column("streak_days", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_area", name="uq_user_progress_skill"),
    )
    op.create_index(op.f("ix_user_progress_user_id"), "user_progress", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_progress_skill_area"), "user_progress", ["skill_area"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_progress_skill_area"), table_name="user_progress")
    op.drop_index(op.f("ix_user_progress_user_id"), table_name="user_progress")
    op.drop_table("user_progress")
