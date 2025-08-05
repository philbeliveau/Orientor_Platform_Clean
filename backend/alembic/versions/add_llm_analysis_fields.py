"""Add LLM analysis fields to saved_recommendations table

Revision ID: add_llm_analysis_fields
Revises: d7662b16ae56
Create Date: 2025-05-22 16:19:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_llm_analysis_fields'
down_revision = 'd7662b16ae56'  # Assurez-vous que cette valeur correspond à la dernière révision existante
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les nouveaux champs à la table saved_recommendations
    op.add_column('saved_recommendations', sa.Column('personal_analysis', sa.Text(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('entry_qualifications', sa.Text(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('suggested_improvements', sa.Text(), nullable=True))


def downgrade():
    # Supprimer les champs en cas de rollback
    op.drop_column('saved_recommendations', 'personal_analysis')
    op.drop_column('saved_recommendations', 'entry_qualifications')
    op.drop_column('saved_recommendations', 'suggested_improvements')