"""reverse validation checks

Revision ID: 01c16e8e6aa7
Revises: 3d3808de2be6
Create Date: 2024-03-17 03:48:29.345196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01c16e8e6aa7'
down_revision: Union[str, None] = '3d3808de2be6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###