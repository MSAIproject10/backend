"""resize searchlog

Revision ID: 747b52d99920
Revises: e20dce554f9b
Create Date: 2025-06-02 20:57:37.283490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '747b52d99920'
down_revision: Union[str, None] = 'e20dce554f9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('search_log_table', 'keyword',
               existing_type=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.Unicode(length=30),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('search_log_table', 'keyword',
               existing_type=sa.Unicode(length=30),
               type_=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    # ### end Alembic commands ###
