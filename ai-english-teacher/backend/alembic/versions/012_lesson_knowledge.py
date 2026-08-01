"""lesson_knowledge table

Revision ID: 012_lesson_knowledge
Revises: 011_user_mistake_memory
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_lesson_knowledge"
down_revision: str | None = "011_user_mistake_memory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    bind = op.get_bind()
    tags_type = (
        postgresql.ARRAY(sa.String(length=50))
        if bind.dialect.name == "postgresql"
        else sa.JSON()
    )

    op.create_table(
        "lesson_knowledge",
        _uuid_pk(),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("skill", sa.String(length=50), nullable=False),
        sa.Column("level", sa.String(length=10), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=True),
        sa.Column("tags", tags_type, nullable=True),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lesson_knowledge_title"), "lesson_knowledge", ["title"], unique=False)
    op.create_index(op.f("ix_lesson_knowledge_skill"), "lesson_knowledge", ["skill"], unique=False)
    op.create_index(op.f("ix_lesson_knowledge_level"), "lesson_knowledge", ["level"], unique=False)
    op.create_index(op.f("ix_lesson_knowledge_topic"), "lesson_knowledge", ["topic"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_lesson_knowledge_topic"), table_name="lesson_knowledge")
    op.drop_index(op.f("ix_lesson_knowledge_level"), table_name="lesson_knowledge")
    op.drop_index(op.f("ix_lesson_knowledge_skill"), table_name="lesson_knowledge")
    op.drop_index(op.f("ix_lesson_knowledge_title"), table_name="lesson_knowledge")
    op.drop_table("lesson_knowledge")
