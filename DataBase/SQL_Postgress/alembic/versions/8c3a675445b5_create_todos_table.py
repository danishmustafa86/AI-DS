"""create todos table

Revision ID: 8c3a675445b5
Revises: fcfe5686f737
Create Date: 2025-02-17 00:06:11.495326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c3a675445b5'
down_revision: Union[str, None] = 'fcfe5686f737'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('name', sa.Boolean(), nullable=True))
    op.add_column('todos', sa.Column('completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'completed')
    op.drop_column('todos', 'name')
    # ### end Alembic commands ###
