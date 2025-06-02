"""change to NVARCHAR

Revision ID: 9ccc556278fe
Revises: 51323d642f15
Create Date: 2025-06-02 23:21:25.015822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ccc556278fe'
down_revision: Union[str, None] = '51323d642f15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('parking',
        sa.Column('ocr_linked', sa.Boolean(), nullable=False, server_default=sa.text('0'))
    )

def downgrade():
    op.drop_column('parking', 'ocr_linked')

