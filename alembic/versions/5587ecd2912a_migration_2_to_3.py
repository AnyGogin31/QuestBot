"""migration_2_to_3

Revision ID: 5587ecd2912a
Revises: 38aec8de8ab1
Create Date: 2026-03-09 13:46:58.424229

"""

from alembic import op

import sqlalchemy as sa

from sqlalchemy.dialects import sqlite


revision = "5587ecd2912a"
down_revision = "38aec8de8ab1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "games",
        sa.Column(
            "commanders_closed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )
    op.add_column(
        "games",
        sa.Column(
            "actors_closed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )
    op.drop_column("games", "admin_ids")


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column("games", sa.Column("admin_ids", sqlite.JSON(), nullable=False))
    op.drop_column("games", "actors_closed")
    op.drop_column("games", "commanders_closed")
