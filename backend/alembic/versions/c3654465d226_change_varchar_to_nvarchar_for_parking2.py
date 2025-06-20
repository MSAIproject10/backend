"""Change VARCHAR to NVARCHAR for Parking2

Revision ID: c3654465d226
Revises: 0c03b393b530
Create Date: 2025-06-02 17:19:08.073859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import NVARCHAR


# revision identifiers, used by Alembic.
revision: str = 'c3654465d226'
down_revision: Union[str, None] = '0c03b393b530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
