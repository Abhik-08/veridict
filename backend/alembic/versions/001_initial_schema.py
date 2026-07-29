"""Initial schema: profiles, evaluations, batch_jobs, batch_results

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW_SERVER_DEFAULT = sa.text('now()')


def upgrade() -> None:
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='email'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
    )
    op.create_index('ix_profiles_id', 'profiles', ['id'])
    op.create_index('ix_profiles_email', 'profiles', ['email'])
    op.create_index('ix_profiles_created_at', 'profiles', ['created_at'])

    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('ai_response', sa.Text(), nullable=False),
        sa.Column('reference_answer', sa.Text(), nullable=True),
        sa.Column('retrieved_context', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('hallucination_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('verdict', sa.String(length=50), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
    )
    op.create_index('ix_evaluations_id', 'evaluations', ['id'])
    op.create_index('ix_evaluations_user_id', 'evaluations', ['user_id'])
    op.create_index('ix_evaluations_overall_score', 'evaluations', ['overall_score'])
    op.create_index('ix_evaluations_verdict', 'evaluations', ['verdict'])
    op.create_index('ix_evaluations_created_at', 'evaluations', ['created_at'])

    # Create batch_jobs table
    op.create_table(
        'batch_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
    )
    op.create_index('ix_batch_jobs_id', 'batch_jobs', ['id'])
    op.create_index('ix_batch_jobs_user_id', 'batch_jobs', ['user_id'])
    op.create_index('ix_batch_jobs_status', 'batch_jobs', ['status'])
    op.create_index('ix_batch_jobs_created_at', 'batch_jobs', ['created_at'])

    # Create batch_results table
    op.create_table(
        'batch_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('batch_job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('batch_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('ai_response', sa.Text(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('verdict', sa.String(length=50), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW_SERVER_DEFAULT, nullable=False),
    )
    op.create_index('ix_batch_results_id', 'batch_results', ['id'])
    op.create_index('ix_batch_results_batch_job_id', 'batch_results', ['batch_job_id'])
    op.create_index('ix_batch_results_overall_score', 'batch_results', ['overall_score'])
    op.create_index('ix_batch_results_verdict', 'batch_results', ['verdict'])


def downgrade() -> None:
    op.drop_table('batch_results')
    op.drop_table('batch_jobs')
    op.drop_table('evaluations')
    op.drop_table('profiles')
