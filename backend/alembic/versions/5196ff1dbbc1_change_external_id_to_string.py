"""Change external_id to String

Revision ID: 5196ff1dbbc1
Revises: 7734b2dede17
Create Date: 2025-06-02 16:50:31.722202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5196ff1dbbc1'
down_revision: Union[str, None] = '7734b2dede17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parking', sa.Column('external_id', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parking', 'external_id')
    # ### end Alembic commands ###
