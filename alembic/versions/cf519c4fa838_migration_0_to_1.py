"""migration_0_to_1

Revision ID: cf519c4fa838
Revises:
Create Date: 2026-03-06 14:05:34.881367

"""

from alembic import op

import sqlalchemy as sa


revision = 'cf519c4fa838'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table('users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )

    op.create_table('games',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('author_id', sa.Uuid(), nullable=False),
        sa.Column('admin_ids', sa.JSON(), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'PREPARED', 'RUNNING', 'FINISHED', 'CANCELLED', name='game_status'), nullable=False),
        sa.Column('min_score', sa.Integer(), nullable=False),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    op.create_table('actors',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('FREE', 'BUSY', 'WAITING_SCORE', name='actor_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('teams',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('commander_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('member_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('IDLE', 'EN_ROUTE', 'AT_ACTOR', 'FINISHED', name='team_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['commander_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('stages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('team_id', sa.Uuid(), nullable=False),
        sa.Column('actor_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.Enum('ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', name='stage_status'), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], ),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table('stages')
    op.drop_table('teams')
    op.drop_table('actors')
    op.drop_table('games')
    op.drop_table('users')
