"""Add school programs tables

Revision ID: school_programs_001
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'school_programs_001'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add school programs tables"""
    
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # Create institutions table
    op.create_table('institutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('name_fr', sa.VARCHAR(255)),
        sa.Column('institution_type', sa.VARCHAR(50), nullable=False),
        sa.Column('country', sa.VARCHAR(2), nullable=False, server_default='CA'),
        sa.Column('province_state', sa.VARCHAR(50)),
        sa.Column('city', sa.VARCHAR(100)),
        sa.Column('postal_code', sa.VARCHAR(20)),
        sa.Column('website_url', sa.TEXT),
        sa.Column('accreditation_status', sa.VARCHAR(100)),
        sa.Column('student_count', sa.INTEGER),
        sa.Column('established_year', sa.INTEGER),
        sa.Column('languages_offered', postgresql.ARRAY(sa.VARCHAR(10)), server_default="ARRAY['en']"),
        sa.Column('contact_info', postgresql.JSONB, server_default='{}'),
        sa.Column('geographic_coordinates', postgresql.POINT),
        sa.Column('source_system', sa.VARCHAR(50), nullable=False),
        sa.Column('source_id', sa.VARCHAR(100), nullable=False),
        sa.Column('source_url', sa.TEXT),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_synced', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('active', sa.BOOLEAN, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_system', 'source_id'),
        sa.CheckConstraint("institution_type IN ('cegep', 'university', 'college')")
    )
    
    # Create programs table
    op.create_table('programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('title', sa.VARCHAR(255), nullable=False),
        sa.Column('title_fr', sa.VARCHAR(255)),
        sa.Column('description', sa.TEXT),
        sa.Column('description_fr', sa.TEXT),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('program_type', sa.VARCHAR(50), nullable=False),
        sa.Column('level', sa.VARCHAR(50), nullable=False),
        sa.Column('field_of_study', sa.VARCHAR(100)),
        sa.Column('field_of_study_fr', sa.VARCHAR(100)),
        sa.Column('duration_months', sa.INTEGER),
        sa.Column('credits', sa.DECIMAL(5, 2)),
        sa.Column('semester_count', sa.INTEGER),
        sa.Column('language', postgresql.ARRAY(sa.VARCHAR(10)), server_default="ARRAY['en']"),
        sa.Column('delivery_mode', sa.VARCHAR(50), server_default='in-person'),
        sa.Column('cip_code', sa.VARCHAR(10)),
        sa.Column('isced_code', sa.VARCHAR(10)),
        sa.Column('noc_code', sa.VARCHAR(10)),
        sa.Column('program_code', sa.VARCHAR(20)),
        sa.Column('admission_requirements', postgresql.JSONB, server_default="'[]'"),
        sa.Column('prerequisite_courses', postgresql.JSONB, server_default="'[]'"),
        sa.Column('min_gpa', sa.DECIMAL(3, 2)),
        sa.Column('language_requirements', postgresql.JSONB, server_default="'{}'"),
        sa.Column('curriculum_outline', postgresql.JSONB, server_default="'{}'"),
        sa.Column('internship_required', sa.BOOLEAN, server_default='false'),
        sa.Column('coop_available', sa.BOOLEAN, server_default='false'),
        sa.Column('thesis_required', sa.BOOLEAN, server_default='false'),
        sa.Column('career_outcomes', postgresql.JSONB, server_default="'[]'"),
        sa.Column('employment_rate', sa.DECIMAL(3, 2)),
        sa.Column('average_salary_range', postgresql.JSONB, server_default="'{}'"),
        sa.Column('top_employers', postgresql.JSONB, server_default="'[]'"),
        sa.Column('tuition_domestic', sa.DECIMAL(10, 2)),
        sa.Column('tuition_international', sa.DECIMAL(10, 2)),
        sa.Column('fees_additional', postgresql.JSONB, server_default="'{}'"),
        sa.Column('financial_aid_available', sa.BOOLEAN, server_default='false'),
        sa.Column('scholarships_available', postgresql.JSONB, server_default="'[]'"),
        sa.Column('application_deadline', sa.DATE),
        sa.Column('application_method', sa.VARCHAR(100)),
        sa.Column('application_fee', sa.DECIMAL(8, 2)),
        sa.Column('application_requirements', postgresql.JSONB, server_default="'[]'"),
        sa.Column('source_system', sa.VARCHAR(50), nullable=False),
        sa.Column('source_id', sa.VARCHAR(100), nullable=False),
        sa.Column('source_url', sa.TEXT),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_synced', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('active', sa.BOOLEAN, server_default='true'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_system', 'source_id'),
        sa.CheckConstraint("level IN ('certificate', 'diploma', 'associate', 'bachelor', 'master', 'phd', 'professional')"),
        sa.CheckConstraint('duration_months > 0'),
        sa.CheckConstraint('employment_rate >= 0 AND employment_rate <= 1')
    )
    
    # Create program_classifications table
    op.create_table('program_classifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('classification_system', sa.VARCHAR(50), nullable=False),
        sa.Column('code', sa.VARCHAR(20), nullable=False),
        sa.Column('title', sa.VARCHAR(255), nullable=False),
        sa.Column('title_fr', sa.VARCHAR(255)),
        sa.Column('description', sa.TEXT),
        sa.Column('level', sa.INTEGER, server_default='1'),
        sa.Column('parent_code', sa.VARCHAR(20)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('program_id', 'classification_system', 'code')
    )
    
    # Create user_program_preferences table
    op.create_table('user_program_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', sa.INTEGER, nullable=True),
        sa.Column('preferred_countries', postgresql.ARRAY(sa.VARCHAR(2)), server_default="ARRAY['CA']"),
        sa.Column('preferred_provinces', postgresql.ARRAY(sa.VARCHAR(50)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('preferred_cities', postgresql.ARRAY(sa.VARCHAR(100)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('max_distance_km', sa.INTEGER),
        sa.Column('willing_to_relocate', sa.BOOLEAN, server_default='false'),
        sa.Column('preferred_languages', postgresql.ARRAY(sa.VARCHAR(10)), server_default="ARRAY['en']"),
        sa.Column('program_types', postgresql.ARRAY(sa.VARCHAR(50)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('program_levels', postgresql.ARRAY(sa.VARCHAR(50)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('fields_of_interest', postgresql.ARRAY(sa.VARCHAR(100)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('delivery_modes', postgresql.ARRAY(sa.VARCHAR(50)), server_default="ARRAY['in-person']"),
        sa.Column('max_duration_months', sa.INTEGER),
        sa.Column('min_duration_months', sa.INTEGER),
        sa.Column('preferred_start_terms', postgresql.ARRAY(sa.VARCHAR(20)), server_default="ARRAY['fall']"),
        sa.Column('part_time_acceptable', sa.BOOLEAN, server_default='false'),
        sa.Column('max_budget', sa.DECIMAL(10, 2)),
        sa.Column('budget_currency', sa.VARCHAR(3), server_default='CAD'),
        sa.Column('financial_aid_required', sa.BOOLEAN, server_default='false'),
        sa.Column('scholarship_priority', sa.BOOLEAN, server_default='false'),
        sa.Column('min_employment_rate', sa.DECIMAL(3, 2)),
        sa.Column('internship_preference', sa.VARCHAR(20), server_default='optional'),
        sa.Column('coop_preference', sa.VARCHAR(20), server_default='optional'),
        sa.Column('target_career_fields', postgresql.ARRAY(sa.VARCHAR(100)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('salary_expectations', postgresql.JSONB, server_default="'{}'"),
        sa.Column('work_environment_preferences', postgresql.JSONB, server_default="'{}'"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create user_program_interactions table  
    op.create_table('user_program_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', sa.INTEGER, nullable=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('interaction_type', sa.VARCHAR(50), nullable=False),
        sa.Column('interaction_duration_seconds', sa.INTEGER),
        sa.Column('interaction_source', sa.VARCHAR(50)),
        sa.Column('search_query', sa.TEXT),
        sa.Column('search_filters', postgresql.JSONB),
        sa.Column('page_position', sa.INTEGER),
        sa.Column('session_id', postgresql.UUID(as_uuid=True)),
        sa.Column('rating', sa.INTEGER),
        sa.Column('feedback_text', sa.TEXT),
        sa.Column('relevance_score', sa.DECIMAL(3, 2)),
        sa.Column('device_type', sa.VARCHAR(20)),
        sa.Column('user_agent', sa.TEXT),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('rating BETWEEN 1 AND 5')
    )
    
    # Create user_saved_programs table
    op.create_table('user_saved_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', sa.INTEGER, nullable=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('personal_notes', sa.TEXT),
        sa.Column('priority_level', sa.INTEGER, server_default='1'),
        sa.Column('application_status', sa.VARCHAR(50), server_default='interested'),
        sa.Column('application_deadline', sa.DATE),
        sa.Column('reminder_date', sa.DATE),
        sa.Column('user_tags', postgresql.ARRAY(sa.VARCHAR(50)), server_default="ARRAY[]::VARCHAR[]"),
        sa.Column('saved_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'program_id'),
        sa.CheckConstraint('priority_level BETWEEN 1 AND 5')
    )
    
    # Add generated column for search vector to programs table
    op.execute("""
        ALTER TABLE programs ADD COLUMN search_vector tsvector 
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(field_of_study, '')), 'C')
        ) STORED
    """)
    
    # Create indexes
    op.create_index('idx_institutions_type', 'institutions', ['institution_type'])
    op.create_index('idx_institutions_location', 'institutions', ['country', 'province_state', 'city'])
    op.create_index('idx_institutions_active', 'institutions', ['active'], postgresql_where=sa.text('active = true'))
    op.create_index('idx_institutions_source', 'institutions', ['source_system', 'source_id'])
    
    op.create_index('idx_programs_institution', 'programs', ['institution_id'])
    op.create_index('idx_programs_type_level', 'programs', ['program_type', 'level'])
    op.create_index('idx_programs_cip', 'programs', ['cip_code'], postgresql_where=sa.text('cip_code IS NOT NULL'))
    op.create_index('idx_programs_active', 'programs', ['active'], postgresql_where=sa.text('active = true'))
    op.create_index('idx_programs_source', 'programs', ['source_system', 'source_id'])
    op.create_index('idx_programs_search', 'programs', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_programs_title_trgm', 'programs', ['title'], postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.create_index('idx_programs_field_study', 'programs', ['field_of_study'], postgresql_where=sa.text('field_of_study IS NOT NULL'))
    op.create_index('idx_programs_duration', 'programs', ['duration_months'], postgresql_where=sa.text('duration_months IS NOT NULL'))
    op.create_index('idx_programs_employment_rate', 'programs', ['employment_rate'], postgresql_where=sa.text('employment_rate IS NOT NULL'))
    
    op.create_index('idx_user_interactions_user_date', 'user_program_interactions', ['user_id', sa.text('created_at DESC')])
    op.create_index('idx_user_interactions_program_type', 'user_program_interactions', ['program_id', 'interaction_type'])
    op.create_index('idx_user_interactions_session', 'user_program_interactions', ['session_id', 'created_at'])
    
    op.create_index('idx_user_preferences_user', 'user_program_preferences', ['user_id'])
    op.create_index('idx_saved_programs_user', 'user_saved_programs', ['user_id', sa.text('saved_at DESC')])
    op.create_index('idx_saved_programs_status', 'user_saved_programs', ['user_id', 'application_status'])
    
    # Create search function
    op.execute("""
    CREATE OR REPLACE FUNCTION search_programs(
        search_text TEXT DEFAULT '',
        program_types TEXT[] DEFAULT ARRAY[]::TEXT[],
        levels TEXT[] DEFAULT ARRAY[]::TEXT[],
        countries TEXT[] DEFAULT ARRAY[]::TEXT[],
        provinces TEXT[] DEFAULT ARRAY[]::TEXT[],
        languages TEXT[] DEFAULT ARRAY[]::TEXT[],
        max_duration INTEGER DEFAULT NULL,
        min_employment_rate DECIMAL DEFAULT NULL,
        limit_count INTEGER DEFAULT 20,
        offset_count INTEGER DEFAULT 0
    )
    RETURNS TABLE (
        id UUID,
        title TEXT,
        institution_name TEXT,
        city TEXT,
        province_state TEXT,
        program_type TEXT,
        level TEXT,
        duration_months INTEGER,
        employment_rate DECIMAL,
        search_rank REAL
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            p.id,
            p.title,
            i.name as institution_name,
            i.city,
            i.province_state,
            p.program_type,
            p.level,
            p.duration_months,
            p.employment_rate,
            CASE 
                WHEN search_text = '' THEN 1.0
                ELSE ts_rank(p.search_vector, plainto_tsquery('english', search_text))
            END as search_rank
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE 
            p.active = true AND i.active = true
            AND (search_text = '' OR p.search_vector @@ plainto_tsquery('english', search_text))
            AND (array_length(program_types, 1) IS NULL OR p.program_type = ANY(program_types))
            AND (array_length(levels, 1) IS NULL OR p.level = ANY(levels))
            AND (array_length(countries, 1) IS NULL OR i.country = ANY(countries))
            AND (array_length(provinces, 1) IS NULL OR i.province_state = ANY(provinces))
            AND (array_length(languages, 1) IS NULL OR p.language && languages)
            AND (max_duration IS NULL OR p.duration_months <= max_duration)
            AND (min_employment_rate IS NULL OR p.employment_rate >= min_employment_rate)
        ORDER BY search_rank DESC, p.title
        LIMIT limit_count OFFSET offset_count;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for updated_at
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)
    
    # Create triggers
    op.execute("CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
    op.execute("CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
    op.execute("CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_program_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
    op.execute("CREATE TRIGGER update_saved_programs_updated_at BEFORE UPDATE ON user_saved_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")


def downgrade():
    """Remove school programs tables"""
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_saved_programs_updated_at ON user_saved_programs")
    op.execute("DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_program_preferences")
    op.execute("DROP TRIGGER IF EXISTS update_programs_updated_at ON programs")
    op.execute("DROP TRIGGER IF EXISTS update_institutions_updated_at ON institutions")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.execute("DROP FUNCTION IF EXISTS search_programs(TEXT, TEXT[], TEXT[], TEXT[], TEXT[], TEXT[], INTEGER, DECIMAL, INTEGER, INTEGER)")
    
    # Drop tables (in reverse order due to foreign keys)
    op.drop_table('user_saved_programs')
    op.drop_table('user_program_interactions')
    op.drop_table('user_program_preferences')
    op.drop_table('program_classifications')
    op.drop_table('programs')
    op.drop_table('institutions')