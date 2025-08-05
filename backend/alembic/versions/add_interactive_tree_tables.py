"""Add interactive tree enhancement tables

Revision ID: add_interactive_tree_tables
Revises: d7662b16ae56
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_interactive_tree_tables'
down_revision = 'd7662b16ae56'
branch_labels = None
depends_on = None


def upgrade():
    # Create saved_jobs table for storing jobs from tree exploration
    op.create_table('saved_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('esco_id', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=500), nullable=False),
        sa.Column('skills_required', sa.JSON(), nullable=True),
        sa.Column('discovery_source', sa.String(length=50), nullable=True, server_default='tree'),
        sa.Column('tree_graph_id', postgresql.UUID(), nullable=True),
        sa.Column('relevance_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True, server_default='{}'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'esco_id', name='uq_user_job')
    )
    op.create_index(op.f('ix_saved_jobs_user_id'), 'saved_jobs', ['user_id'], unique=False)
    op.create_index(op.f('ix_saved_jobs_esco_id'), 'saved_jobs', ['esco_id'], unique=False)
    op.create_index('idx_saved_jobs_user_source', 'saved_jobs', ['user_id', 'discovery_source'], unique=False)

    # Create career_goals table for managing user career objectives
    op.create_table('career_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('set_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('previous_goal_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('progress_metrics', sa.JSON(), nullable=True, server_default='{}'),
        sa.CheckConstraint("status IN ('active', 'archived', 'achieved', 'paused')", name='check_goal_status'),
        sa.ForeignKeyConstraint(['job_id'], ['saved_jobs.id'], ),
        sa.ForeignKeyConstraint(['previous_goal_id'], ['career_goals.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_goals_user_id'), 'career_goals', ['user_id'], unique=False)
    op.create_index('idx_career_goals_user_status', 'career_goals', ['user_id', 'status'], unique=False)

    # Create program_recommendations table for educational pathways
    op.create_table('program_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('program_name', sa.String(length=500), nullable=False),
        sa.Column('institution', sa.String(length=500), nullable=False),
        sa.Column('institution_type', sa.String(length=50), nullable=True),
        sa.Column('program_code', sa.String(length=100), nullable=True),
        sa.Column('duration', sa.String(length=100), nullable=True),
        sa.Column('admission_requirements', sa.JSON(), nullable=True),
        sa.Column('match_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('cost_estimate', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('location', sa.JSON(), nullable=True),
        sa.Column('intake_dates', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('match_score >= 0 AND match_score <= 1', name='check_match_score_range'),
        sa.ForeignKeyConstraint(['goal_id'], ['career_goals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_recommendations_goal_id'), 'program_recommendations', ['goal_id'], unique=False)

    # Create llm_descriptions table for caching generated descriptions
    op.create_table('llm_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('prompt_template', sa.String(length=100), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("node_type IN ('skill', 'occupation', 'skillgroup')", name='check_node_type'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('node_id', 'user_id', name='uq_node_user_description')
    )
    op.create_index('idx_llm_descriptions_node_user', 'llm_descriptions', ['node_id', 'user_id'], unique=False)

    # Create tree_generations table for enhanced tree caching
    op.create_table('tree_generations',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('anchor_skills', sa.JSON(), nullable=False),
        sa.Column('graph_data', sa.JSON(), nullable=False),
        sa.Column('generation_options', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tree_generations_user_created', 'tree_generations', ['user_id', 'created_at'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index('idx_tree_generations_user_created', table_name='tree_generations')
    op.drop_index('idx_llm_descriptions_node_user', table_name='llm_descriptions')
    op.drop_index(op.f('ix_program_recommendations_goal_id'), table_name='program_recommendations')
    op.drop_index('idx_career_goals_user_status', table_name='career_goals')
    op.drop_index(op.f('ix_career_goals_user_id'), table_name='career_goals')
    op.drop_index('idx_saved_jobs_user_source', table_name='saved_jobs')
    op.drop_index(op.f('ix_saved_jobs_esco_id'), table_name='saved_jobs')
    op.drop_index(op.f('ix_saved_jobs_user_id'), table_name='saved_jobs')
    
    # Drop tables in reverse order of creation (due to foreign key constraints)
    op.drop_table('tree_generations')
    op.drop_table('llm_descriptions')
    op.drop_table('program_recommendations')
    op.drop_table('career_goals')
    op.drop_table('saved_jobs')