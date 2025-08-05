"""add avatar fields to user representation

Revision ID: add_avatar_fields
Revises: 
Create Date: 2025-01-06 14:39:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_avatar_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add avatar fields to user_representation table
    op.add_column('user_representation', sa.Column('avatar_name', sa.String(length=255), nullable=True))
    op.add_column('user_representation', sa.Column('avatar_description', sa.Text(), nullable=True))
    op.add_column('user_representation', sa.Column('avatar_image_url', sa.String(length=500), nullable=True))


def downgrade():
    # Remove avatar fields from user_representation table
    op.drop_column('user_representation', 'avatar_image_url')
    op.drop_column('user_representation', 'avatar_description')
    op.drop_column('user_representation', 'avatar_name')