"""change tiebreaker and model names

Revision ID: e67a85993d5e
Revises: 0e50c37793d1
Create Date: 2024-01-17 06:07:31.831519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e67a85993d5e'
down_revision: Union[str, None] = '0e50c37793d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('initiative_members', sa.Column('tiebreaker', sa.Integer(), nullable=True))
    op.drop_column('initiative_members', 'tiebreaker_order')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('initiative_members', sa.Column('tiebreaker_order', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('initiative_members', 'tiebreaker')
    # ### end Alembic commands ###
