"""Add first_name, last_name, is_active fields to User model

Revision ID: add_clerk_user_fields
Revises: 7085dfa9bba2
Create Date: 2025-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_clerk_user_fields'
down_revision = '7085dfa9bba2'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new fields to the users table
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    # Remove the new fields
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')