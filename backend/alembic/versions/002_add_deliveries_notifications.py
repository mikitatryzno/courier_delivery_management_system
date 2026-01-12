"""Add deliveries and notifications tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-12 08:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create delivery status enum
    delivery_status = sa.Enum(
        'created', 'assigned', 'picked_up', 'in_transit', 'delivered', 'failed', 'cancelled',
        name='deliverystatus'
    )
    delivery_status.create(op.get_bind(), checkfirst=True)

    # Create notification type enum
    notification_type = sa.Enum('info', 'warning', 'alert', name='notificationtype')
    notification_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('status', delivery_status, nullable=True),
        sa.Column('current_lat', sa.Float(), nullable=True),
        sa.Column('current_lng', sa.Float(), nullable=True),
        sa.Column('last_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ),
        sa.ForeignKeyConstraint(['courier_id'], ['users.id'], ),
    )

    op.create_index(op.f('ix_deliveries_id'), 'deliveries', ['id'], unique=False)

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', notification_type, nullable=True),
        sa.Column('read', sa.Boolean(), nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_index(op.f('ix_deliveries_id'), table_name='deliveries')
    op.drop_table('deliveries')

    # Drop enums
    notification_type = sa.Enum(name='notificationtype')
    notification_type.drop(op.get_bind(), checkfirst=True)

    delivery_status = sa.Enum(name='deliverystatus')
    delivery_status.drop(op.get_bind(), checkfirst=True)
