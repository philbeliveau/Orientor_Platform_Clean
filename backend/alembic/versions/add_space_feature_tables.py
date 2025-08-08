"""add space feature tables

Revision ID: add_space_feature_tables
Revises: add_chat_persistence
Create Date: 2025-08-08 12:07:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_space_feature_tables'
down_revision = 'add_chat_persistence'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a placeholder migration that was referenced but missing
    # The actual space feature tables are implemented in other migrations
    pass


def downgrade() -> None:
    # This is a placeholder migration that was referenced but missing
    pass