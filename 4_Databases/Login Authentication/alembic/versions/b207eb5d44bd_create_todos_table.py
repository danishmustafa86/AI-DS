"""change primary key from ag to email

Revision ID: b207eb5d44bd
Revises: 5c682718535b
Create Date: 2025-03-07 00:22:41.699730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b207eb5d44bd'
down_revision: Union[str, None] = '5c682718535b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing primary key constraint
    op.drop_constraint('students_pkey', 'students', type_='primary')

    # Alter the 'ag' column to remove the primary key constraint
    op.alter_column('students', 'ag', existing_type=sa.Integer(), nullable=True)

    # Add the new primary key constraint
    op.create_primary_key('students_pkey', 'students', ['email'])

    # Add the 'email' column if it doesn't exist
    op.add_column('students', sa.Column('email', sa.String(), nullable=False))
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=False)


def downgrade() -> None:
    # Drop the new primary key constraint
    op.drop_constraint('students_pkey', 'students', type_='primary')

    # Revert the 'ag' column to be the primary key
    op.alter_column('students', 'ag', existing_type=sa.Integer(), nullable=False)
    op.create_primary_key('students_pkey', 'students', ['ag'])

    # Drop the 'email' column
    op.drop_index(op.f('ix_students_email'), table_name='students')
    op.drop_column('students', 'email')

    # Recreate the 'todos' table
    op.create_table('todos',
    sa.Column('user_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('user_id', name='todos_pkey')
    )
    op.create_index('ix_todos_user_id', 'todos', ['user_id'], unique=False)
    op.create_index('ix_todos_title', 'todos', ['title'], unique=False)