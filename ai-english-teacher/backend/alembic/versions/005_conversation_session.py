"""conversation_session table

Revision ID: 005_conversation_session
Revises: 004_user_profile
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_conversation_session"
down_revision: str | None = "004_user_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "conversation_session",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("mode", sa.String(length=30), server_default="grammar", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_session_user_id"), "conversation_session", ["user_id"], unique=False)
    op.create_index(op.f("ix_conversation_session_status"), "conversation_session", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_conversation_session_status"), table_name="conversation_session")
    op.drop_index(op.f("ix_conversation_session_user_id"), table_name="conversation_session")
    op.drop_table("conversation_session")
