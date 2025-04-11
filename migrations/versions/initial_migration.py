"""Initial database setup

Revision ID: 1a1a1a1a1a1a
Revises: 
Create Date: 2023-11-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '1a1a1a1a1a1a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create questions table
    op.create_table('questions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('cognitive_complexity', sa.String(length=50), nullable=True),
        sa.Column('blooms_taxonomy_level', sa.String(length=50), nullable=True),
        sa.Column('surgically_appropriate', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create question_options table
    op.create_table('question_options',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create comparison_results table
    op.create_table('comparison_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=False),
        sa.Column('direct_output', sa.Text(), nullable=False),
        sa.Column('agent_output', sa.Text(), nullable=False),
        sa.Column('direct_processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('agent_processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('direct_output_data', sqlite.JSON(), nullable=True),
        sa.Column('agent_output_data', sqlite.JSON(), nullable=True),
        sa.Column('agent_steps', sqlite.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_feedback table
    op.create_table('user_feedback',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('comparison_id', sa.String(length=36), nullable=False),
        sa.Column('preferred_output', sa.String(length=10), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('direct_rating', sa.Integer(), nullable=True),
        sa.Column('agent_rating', sa.Integer(), nullable=True),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['comparison_id'], ['comparison_results.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comparison_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_questions_domain'), 'questions', ['domain'], unique=False)
    op.create_index(op.f('ix_question_options_question_id'), 'question_options', ['question_id'], unique=False)
    op.create_index(op.f('ix_comparison_results_question_id'), 'comparison_results', ['question_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_feedback')
    op.drop_table('comparison_results')
    op.drop_table('question_options')
    op.drop_table('questions') 