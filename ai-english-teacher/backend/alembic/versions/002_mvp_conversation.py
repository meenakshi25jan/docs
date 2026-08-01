"""mvp user fields and grammar feedback

Revision ID: 002_mvp_conversation
Revises: 001_initial_users
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_mvp_conversation"
down_revision: str | None = "001_initial_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(length=100), server_default="", nullable=False))
        batch_op.add_column(sa.Column("phone_number", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("role", sa.String(length=30), server_default="student", nullable=False))
        batch_op.add_column(sa.Column("teacher_voice", sa.String(length=20), server_default="female", nullable=False))

    op.create_table(
        "grammar_feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("teacher_response", sa.Text(), nullable=False),
        sa.Column("mistake_type", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=30), server_default="grammar", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grammar_feedback_user_id"), "grammar_feedback", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_grammar_feedback_user_id"), table_name="grammar_feedback")
    op.drop_table("grammar_feedback")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("teacher_voice")
        batch_op.drop_column("role")
        batch_op.drop_column("phone_number")
        batch_op.drop_column("name")
