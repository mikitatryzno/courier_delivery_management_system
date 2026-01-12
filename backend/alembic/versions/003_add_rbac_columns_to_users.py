"""Add RBAC columns to users

Revision ID: 003
Revises: 002
Create Date: 2026-01-12 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('1')))
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default=sa.text('0')))
    op.add_column('users', sa.Column('permissions', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'permissions')
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'is_active')
