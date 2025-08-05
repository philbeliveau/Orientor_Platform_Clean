"""Add OaSIS columns to user_profiles

Revision ID: add_oasis_columns
Revises: 7085dfa9bba2
Create Date: 2025-05-16 12:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_oasis_columns'
down_revision = '7085dfa9bba2'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne oasis_profile pour stocker le profil formaté selon le style OaSIS
    op.add_column('user_profiles', sa.Column('oasis_profile', sa.Text(), nullable=True))
    
    # Ajouter la colonne oasis_embedding pour stocker l'embedding généré à partir du profil OaSIS
    op.add_column('user_profiles', sa.Column('oasis_embedding', JSONB(), nullable=True))
    
    # Ajouter un index sur la colonne oasis_embedding pour améliorer les performances de recherche
    op.create_index(op.f('ix_user_profiles_oasis_embedding'), 'user_profiles', ['oasis_embedding'], unique=False)


def downgrade():
    # Supprimer l'index
    op.drop_index(op.f('ix_user_profiles_oasis_embedding'), table_name='user_profiles')
    
    # Supprimer les colonnes
    op.drop_column('user_profiles', 'oasis_embedding')
    op.drop_column('user_profiles', 'oasis_profile')