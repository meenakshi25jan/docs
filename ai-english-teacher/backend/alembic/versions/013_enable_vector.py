"""enable pgvector extension

Revision ID: 013_enable_vector
Revises: 012_lesson_knowledge
Create Date: 2026-08-01

"""

from collections.abc import Sequence

from alembic import op

revision: str = "013_enable_vector"
down_revision: str | None = "012_lesson_knowledge"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP EXTENSION IF EXISTS vector")
