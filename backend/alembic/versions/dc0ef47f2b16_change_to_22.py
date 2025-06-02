"""add vehicle_record (parking_record_table)

Revision ID: dc0ef47f2b16
Revises: 3fe240145c69
Create Date: 2025-06-02 21:23:43.131521
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc0ef47f2b16'
down_revision: Union[str, None] = '3fe240145c69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'parking_record_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('parking_id', sa.Integer, sa.ForeignKey('parking.id'), nullable=False),
        sa.Column('vehicle_id', sa.Integer, sa.ForeignKey('vehicle_table.vehicle_id'), nullable=True),
        sa.Column('ocr_plate', sa.Unicode(10), nullable=False),
        sa.Column('entry_time', sa.DateTime, nullable=False),
        sa.Column('exit_time', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('parking_record_table')
