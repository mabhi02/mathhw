"""Add agent state tables

Revision ID: 2b2b2b2b2b2b
Revises: 1a1a1a1a1a1a
Create Date: 2023-12-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2b2b2b2b2b2b'
down_revision = '1a1a1a1a1a1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agent_states table
    op.create_table('agent_states',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('agent_id', sa.String(length=255), nullable=False, index=True),
        sa.Column('agent_type', sa.String(length=255), nullable=False, index=True),
        sa.Column('state_data', sa.JSON(), nullable=False),
        sa.Column('pipeline_id', sa.String(length=255), nullable=True, index=True),
        sa.Column('step_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_executed', sa.String(length=255), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agent_state_checkpoints table
    op.create_table('agent_state_checkpoints',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('agent_state_id', sa.String(length=36), nullable=False),
        sa.Column('state_data', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['agent_state_id'], ['agent_states.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('agent_state_checkpoints')
    op.drop_table('agent_states') 