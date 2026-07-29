"""Evaluation history foundation: add JSONB results, confidence, source_type, batch_job_id, and batch metrics

Revision ID: 002_evaluation_history_foundation
Revises: 001_initial_schema
Create Date: 2026-07-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_evaluation_history_foundation'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update evaluations table with history persistence fields
    op.add_column('evaluations', sa.Column('retrieved_evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('evaluations', sa.Column('evaluation_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('evaluations', sa.Column('confidence', sa.Float(), nullable=True))
    op.add_column('evaluations', sa.Column('source_type', sa.String(length=50), server_default='SINGLE', nullable=False))
    op.add_column('evaluations', sa.Column('batch_job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('batch_jobs.id', ondelete='CASCADE'), nullable=True))

    op.create_index('ix_evaluations_source_type', 'evaluations', ['source_type'])
    op.create_index('ix_evaluations_batch_job_id', 'evaluations', ['batch_job_id'])

    # 2. Update batch_jobs table with dataset item counters
    op.add_column('batch_jobs', sa.Column('total_items', sa.Integer(), server_default='0', nullable=False))
    op.add_column('batch_jobs', sa.Column('completed_items', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('batch_jobs', 'completed_items')
    op.drop_column('batch_jobs', 'total_items')

    op.drop_index('ix_evaluations_batch_job_id', table_name='evaluations')
    op.drop_index('ix_evaluations_source_type', table_name='evaluations')

    op.drop_column('evaluations', 'batch_job_id')
    op.drop_column('evaluations', 'source_type')
    op.drop_column('evaluations', 'confidence')
    op.drop_column('evaluations', 'evaluation_result')
    op.drop_column('evaluations', 'retrieved_evidence')
