"""create todos table

Revision ID: 31d22d5e7aa4
Revises: 4cf6befcea0e
Create Date: 2025-03-03 17:04:40.249042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31d22d5e7aa4'
down_revision: Union[str, None] = '4cf6befcea0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_todos_title', table_name='todos')
    op.drop_index('ix_todos_user_id', table_name='todos')
    op.drop_table('todos')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todos',
    sa.Column('user_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('user_id', name='todos_pkey')
    )
    op.create_index('ix_todos_user_id', 'todos', ['user_id'], unique=False)
    op.create_index('ix_todos_title', 'todos', ['title'], unique=False)
    # ### end Alembic commands ###
