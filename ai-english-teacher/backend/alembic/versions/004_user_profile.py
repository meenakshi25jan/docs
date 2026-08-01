"""user_profile table

Revision ID: 004_user_profile
Revises: 003_enable_pgcrypto
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_user_profile"
down_revision: str | None = "003_enable_pgcrypto"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "user_profile",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("native_language", sa.String(length=50), nullable=True),
        sa.Column("target_level", sa.String(length=10), nullable=True),
        sa.Column("learning_goals", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_profile_user_id"), "user_profile", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_profile_user_id"), table_name="user_profile")
    op.drop_table("user_profile")
