"""learning_plan table

Revision ID: 009_learning_plan
Revises: 008_band_score
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009_learning_plan"
down_revision: str | None = "008_band_score"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    bind = op.get_bind()
    plan_data_type = postgresql.JSONB(astext_type=sa.Text()) if bind.dialect.name == "postgresql" else sa.JSON()

    op.create_table(
        "learning_plan",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_level", sa.String(length=10), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="active", nullable=False),
        sa.Column("plan_data", plan_data_type, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learning_plan_user_id"), "learning_plan", ["user_id"], unique=False)
    op.create_index(op.f("ix_learning_plan_status"), "learning_plan", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_learning_plan_status"), table_name="learning_plan")
    op.drop_index(op.f("ix_learning_plan_user_id"), table_name="learning_plan")
    op.drop_table("learning_plan")
