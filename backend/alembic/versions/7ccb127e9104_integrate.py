"""integrate

Revision ID: 7ccb127e9104
Revises: 747b52d99920
Create Date: 2025-06-02 21:11:20.303227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ccb127e9104'
down_revision: Union[str, None] = '747b52d99920'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parking', 'external_id',
               existing_type=sa.NVARCHAR(length=6, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.Unicode(length=10),
               existing_nullable=True)
    op.add_column('parking_status', sa.Column('entry_count', sa.Integer(), nullable=True))
    op.add_column('parking_status', sa.Column('exit_count', sa.Integer(), nullable=True))
    op.add_column('vehicle_table', sa.Column('license_plate', sa.Unicode(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vehicle_table', 'license_plate')
    op.drop_column('parking_status', 'exit_count')
    op.drop_column('parking_status', 'entry_count')
    op.alter_column('parking', 'external_id',
               existing_type=sa.Unicode(length=10),
               type_=sa.NVARCHAR(length=6, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=True)
    # ### end Alembic commands ###
