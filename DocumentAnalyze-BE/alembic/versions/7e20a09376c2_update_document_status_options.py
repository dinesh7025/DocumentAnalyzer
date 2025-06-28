"""Update document status options

Revision ID: 7e20a09376c2
Revises: 53297a0e3996
Create Date: 2025-06-27 13:04:00.757784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e20a09376c2'
down_revision: Union[str, Sequence[str], None] = '53297a0e3996'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE IF EXISTS documents
        DROP CONSTRAINT IF EXISTS documents_status_check;
    """)
    op.execute("""
        ALTER TABLE documents
        ADD CONSTRAINT documents_status_check
        CHECK (
            status IN ('processed', 'classified', 'review_needed', 'routed')
        );
    """)

def downgrade():
    op.execute("""
        ALTER TABLE documents
        DROP CONSTRAINT IF EXISTS documents_status_check;
    """)
    op.execute("""
        ALTER TABLE documents
        ADD CONSTRAINT documents_status_check
        CHECK (
            status IN ('pending', 'processed', 'error', 'routed')
        );
    """)

