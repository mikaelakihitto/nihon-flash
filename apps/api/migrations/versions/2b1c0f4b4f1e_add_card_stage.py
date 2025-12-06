"""Add card stage for fixed SRS progression

Revision ID: 2b1c0f4b4f1e
Revises: b2de42f5a4ce
Create Date: 2025-12-06 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2b1c0f4b4f1e"
down_revision = "b2de42f5a4ce"
branch_labels = None
depends_on = None

LEARNING_STAGE = sa.Enum(
    "curto_prazo",
    "transicao",
    "consolidacao",
    "longo_prazo",
    "memoria_estavel",
    name="learningstage",
)


def upgrade() -> None:
    LEARNING_STAGE.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "cards",
        sa.Column("stage", LEARNING_STAGE, server_default="curto_prazo", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("cards", "stage")
    LEARNING_STAGE.drop(op.get_bind(), checkfirst=True)
