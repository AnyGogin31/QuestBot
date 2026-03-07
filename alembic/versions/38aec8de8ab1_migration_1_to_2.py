"""migration_1_to_2

Revision ID: 38aec8de8ab1
Revises: cf519c4fa838
Create Date: 2026-03-07 14:04:45.468315

"""

from alembic import op

import sqlalchemy as sa


revision = '38aec8de8ab1'
down_revision = 'cf519c4fa838'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column('actors', sa.Column('min_score', sa.Integer(), nullable=True))
    op.add_column('actors', sa.Column('max_score', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('actor_code', sa.String(length=10), nullable=False))
    op.create_unique_constraint(None, 'games', ['actor_code'])
    op.add_column('stages', sa.Column('score', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('stages', 'score')
    op.drop_constraint(None, 'games', type_='unique')
    op.drop_column('games', 'actor_code')
    op.drop_column('actors', 'max_score')
    op.drop_column('actors', 'min_score')
