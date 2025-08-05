"""Add compatibility vector to user profiles

Revision ID: add_compatibility_vector
Revises: update_vector_dimension
Create Date: 2025-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_compatibility_vector'
down_revision = 'add_avatar_fields_to_user_representation'
branch_labels = None
depends_on = None

def upgrade():
    """Add compatibility_vector column to user_profiles table."""
    op.add_column('user_profiles', 
                  sa.Column('compatibility_vector', 
                           postgresql.JSONB(astext_type=sa.Text()),
                           nullable=True))
    
    # Add index for faster JSONB queries
    op.create_index('idx_user_profiles_compatibility_vector',
                   'user_profiles',
                   ['compatibility_vector'],
                   postgresql_using='gin')

def downgrade():
    """Remove compatibility_vector column from user_profiles table."""
    op.drop_index('idx_user_profiles_compatibility_vector',
                  table_name='user_profiles')
    op.drop_column('user_profiles', 'compatibility_vector')