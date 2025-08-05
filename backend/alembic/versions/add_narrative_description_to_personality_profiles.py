"""Add narrative_description field to personality_profiles table

Revision ID: add_narrative_description
Revises: add_llm_analysis_fields
Create Date: 2025-06-05 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_narrative_description'
down_revision = 'add_llm_analysis_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table personality_profiles si elle n'existe pas
    op.execute("""
        CREATE TABLE IF NOT EXISTS personality_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            assessment_id INTEGER,
            profile_type VARCHAR(50) NOT NULL DEFAULT 'hexaco',
            language VARCHAR(10) DEFAULT 'fr',
            scores JSONB,
            percentile_ranks JSONB,
            reliability_estimates JSONB,
            assessment_version VARCHAR(50),
            narrative_description TEXT,
            computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Ajouter des index pour optimiser les requêtes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_personality_profiles_user_id 
        ON personality_profiles(user_id)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_personality_profiles_type_version 
        ON personality_profiles(profile_type, assessment_version)
    """)
    
    # Créer la table personality_assessments si elle n'existe pas
    op.execute("""
        CREATE TABLE IF NOT EXISTS personality_assessments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            assessment_type VARCHAR(50) NOT NULL DEFAULT 'hexaco',
            assessment_version VARCHAR(50),
            status VARCHAR(20) DEFAULT 'in_progress',
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_personality_assessments_session_id 
        ON personality_assessments(session_id)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_personality_assessments_user_id 
        ON personality_assessments(user_id)
    """)


def downgrade():
    # En cas de rollback, on ne supprime pas les tables car elles peuvent contenir des données importantes
    # On supprime seulement le champ narrative_description s'il a été ajouté
    op.execute("""
        ALTER TABLE personality_profiles 
        DROP COLUMN IF EXISTS narrative_description
    """)