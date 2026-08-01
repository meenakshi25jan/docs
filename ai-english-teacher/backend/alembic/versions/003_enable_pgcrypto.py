"""enable pgcrypto extension for gen_random_uuid()

Revision ID: 003_enable_pgcrypto
Revises: 002_mvp_conversation
Create Date: 2026-08-01

"""

from collections.abc import Sequence

from alembic import op

revision: str = "003_enable_pgcrypto"
down_revision: str | None = "002_mvp_conversation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP EXTENSION IF EXISTS pgcrypto")
