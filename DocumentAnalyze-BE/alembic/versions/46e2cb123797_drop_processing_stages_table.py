"""drop processing_stages table

Revision ID: 46e2cb123797
Revises: 393ef0f2f25a
Create Date: 2025-06-25 21:54:05.934305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46e2cb123797'
down_revision: Union[str, Sequence[str], None] = '393ef0f2f25a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('processing_stages')
    pass


def downgrade() -> None:
    op.create_table(
        'processing_stages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True)
    )
    pass
