"""extend grammar_feedback with updated_at and explicit ON DELETE RESTRICT

Revision ID: 007_grammar_feedback_extend
Revises: 006_conversation_message
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_grammar_feedback_extend"
down_revision: str | None = "006_conversation_message"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "grammar_feedback",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_constraint("grammar_feedback_user_id_fkey", "grammar_feedback", type_="foreignkey")
        op.create_foreign_key(
            "grammar_feedback_user_id_fkey",
            "grammar_feedback",
            "users",
            ["user_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_constraint("grammar_feedback_user_id_fkey", "grammar_feedback", type_="foreignkey")
        op.create_foreign_key(
            "grammar_feedback_user_id_fkey",
            "grammar_feedback",
            "users",
            ["user_id"],
            ["id"],
        )

    op.drop_column("grammar_feedback", "updated_at")
