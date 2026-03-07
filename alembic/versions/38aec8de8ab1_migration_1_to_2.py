"""migration_1_to_2

Revision ID: 38aec8de8ab1
Revises: cf519c4fa838
Create Date: 2026-03-07 14:04:45.468315

"""

from alembic import op

import sqlalchemy as sa


revision = "38aec8de8ab1"
down_revision = "cf519c4fa838"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    with op.batch_alter_table("actors", schema=None) as batch_op:
        batch_op.add_column(sa.Column("min_score", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("max_score", sa.Integer(), nullable=True))

    with op.batch_alter_table("games", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("actor_code", sa.String(length=10), nullable=False)
        )
        batch_op.create_unique_constraint("uq_games_actor_code", ["actor_code"])

    with op.batch_alter_table("stages", schema=None) as batch_op:
        batch_op.add_column(sa.Column("score", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("stages", schema=None) as batch_op:
        batch_op.drop_column("score")

    with op.batch_alter_table("games", schema=None) as batch_op:
        batch_op.drop_constraint("uq_games_actor_code", type_="unique")
        batch_op.drop_column("actor_code")

    with op.batch_alter_table("actors", schema=None) as batch_op:
        batch_op.drop_column("max_score")
        batch_op.drop_column("min_score")
