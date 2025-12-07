"""add card_review_log table

Revision ID: 7f3e9b2b6f9f
Revises: 4c0b3f7f4c7a
Create Date: 2025-12-07 16:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

from app.models.enums import CardStatus, LearningStage

# revision identifiers, used by Alembic.
revision = "7f3e9b2b6f9f"
down_revision = "4c0b3f7f4c7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "card_review_log",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("card_id", sa.Integer(), nullable=False, index=True),
        sa.Column("note_id", sa.Integer(), nullable=False, index=True),
        sa.Column("deck_id", sa.Integer(), nullable=False, index=True),
        sa.Column("correct", sa.Boolean(), nullable=False, default=False),
        sa.Column("stage_before", sa.Enum(LearningStage), nullable=True),
        sa.Column("stage_after", sa.Enum(LearningStage), nullable=True),
        sa.Column("status_after", sa.Enum(CardStatus), nullable=True),
        sa.Column("due_at_after", sa.DateTime(timezone=True), nullable=True),
        sa.Column("srs_interval_after", sa.Integer(), nullable=True),
        sa.Column("srs_ease_after", sa.Float(), nullable=True),
        sa.Column("reps_after", sa.Integer(), nullable=True),
        sa.Column("lapses_after", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("card_review_log")
