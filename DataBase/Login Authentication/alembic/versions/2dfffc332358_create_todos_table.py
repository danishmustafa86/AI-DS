"""create todos table

Revision ID: 2dfffc332358
Revises: b207eb5d44bd
Create Date: 2025-03-07 00:43:44.847801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '2dfffc332358'
down_revision: Union[str, None] = 'b207eb5d44bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the current connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if the 'email' column exists
    columns = [col['name'] for col in inspector.get_columns('students')]
    if 'email' not in columns:
        # Add the 'email' column if it doesn't exist
        op.add_column('students', sa.Column('email', sa.String(), nullable=False))
        op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=False)

    # Drop the existing primary key constraint
    op.drop_constraint('students_pkey', 'students', type_='primary')

    # Alter the 'ag' column to remove the primary key constraint
    op.alter_column('students', 'ag', existing_type=sa.Integer(), nullable=True)

    # Add the new primary key constraint
    op.create_primary_key('students_pkey', 'students', ['email'])

    # Drop the 'todos' table if it exists
    op.drop_index('ix_todos_title', table_name='todos')
    op.drop_index('ix_todos_user_id', table_name='todos')
    op.drop_table('todos')


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