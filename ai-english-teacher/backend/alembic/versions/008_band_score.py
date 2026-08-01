"""band_score table

Revision ID: 008_band_score
Revises: 007_grammar_feedback_extend
Create Date: 2026-08-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008_band_score"
down_revision: str | None = "007_grammar_feedback_extend"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_pk() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)
    return sa.Column("id", sa.Uuid(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "band_score",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("assessment_type", sa.String(length=50), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("grammar_score", sa.Integer(), nullable=True),
        sa.Column("vocabulary_score", sa.Integer(), nullable=True),
        sa.Column("fluency_score", sa.Integer(), nullable=True),
        sa.Column("pronunciation_score", sa.Integer(), nullable=True),
        sa.Column("cefr_level", sa.String(length=10), nullable=True),
        sa.Column("ielts_band", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_band_score_user_id"), "band_score", ["user_id"], unique=False)
    op.create_index(op.f("ix_band_score_assessment_type"), "band_score", ["assessment_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_band_score_assessment_type"), table_name="band_score")
    op.drop_index(op.f("ix_band_score_user_id"), table_name="band_score")
    op.drop_table("band_score")
