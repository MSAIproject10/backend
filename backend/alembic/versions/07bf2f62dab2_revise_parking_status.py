"""revise parking status

Revision ID: 07bf2f62dab2
Revises: 9ccc556278fe
Create Date: 2025-06-03 01:36:44.253238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = '07bf2f62dab2'
down_revision: Union[str, None] = '9ccc556278fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. 기존 'last_updated' timestamp 컬럼 삭제
    op.drop_column('parking_status', 'last_updated')

    # 2. 새로운 datetime 타입으로 재생성
    op.add_column('parking_status', sa.Column(
        'last_updated',
        sa.DateTime(),
        nullable=False,
        server_default=sa.func.getdate()
    ))

def downgrade():
    op.drop_column('parking_status', 'last_updated')
    # (원래대로 돌리는게 필요하면, timestamp로 다시 만들 수도 있음)
