"""Add last_clerk_sync timestamp to users table for database optimization

Revision ID: add_last_clerk_sync_timestamp
Revises: add_clerk_user_fields
Create Date: 2025-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_last_clerk_sync_timestamp'
down_revision = 'add_clerk_user_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add the last_clerk_sync timestamp column to users table
    op.add_column('users', sa.Column('last_clerk_sync', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Remove the last_clerk_sync column
    op.drop_column('users', 'last_clerk_sync')