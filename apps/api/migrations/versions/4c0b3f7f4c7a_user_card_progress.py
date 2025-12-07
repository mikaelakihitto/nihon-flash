"""add user card progress table

Revision ID: 4c0b3f7f4c7a
Revises: 2b1c0f4b4f1e
Create Date: 2025-02-23 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

from app.models.enums import CardStatus, LearningStage

# revision identifiers, used by Alembic.
revision = "4c0b3f7f4c7a"
down_revision = "2b1c0f4b4f1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_card_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum(CardStatus), nullable=False, server_default="new"),
        sa.Column("stage", sa.Enum(LearningStage), nullable=True),
        sa.Column("srs_interval", sa.Integer(), nullable=True),
        sa.Column("srs_ease", sa.Float(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lapses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "card_id"),
    )


def downgrade() -> None:
    op.drop_table("user_card_progress")
