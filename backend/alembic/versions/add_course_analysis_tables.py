"""Add course analysis tables for career profiling

Revision ID: add_course_analysis_tables
Revises: 
Create Date: 2024-06-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_course_analysis_tables'
down_revision = None  # Update this based on latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create courses table
    op.create_table('courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_name', sa.String(length=255), nullable=False),
        sa.Column('course_code', sa.String(length=50), nullable=True),
        sa.Column('semester', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('professor', sa.String(length=255), nullable=True),
        sa.Column('subject_category', sa.String(length=50), nullable=True),
        sa.Column('grade', sa.String(length=10), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('learning_outcomes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_user_id'), 'courses', ['user_id'], unique=False)

    # Create psychological_insights table
    op.create_table('psychological_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(length=100), nullable=False),
        sa.Column('insight_value', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('evidence_source', sa.Text(), nullable=True),
        sa.Column('esco_mapping', sa.JSON(), nullable=True),
        sa.Column('extracted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_psychological_insights_id'), 'psychological_insights', ['id'], unique=False)
    op.create_index(op.f('ix_psychological_insights_user_id'), 'psychological_insights', ['user_id'], unique=False)
    op.create_index(op.f('ix_psychological_insights_course_id'), 'psychological_insights', ['course_id'], unique=False)

    # Create career_signals table
    op.create_table('career_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('signal_type', sa.String(length=100), nullable=False),
        sa.Column('strength_score', sa.Float(), nullable=False),
        sa.Column('evidence_source', sa.Text(), nullable=False),
        sa.Column('pattern_metadata', sa.JSON(), nullable=True),
        sa.Column('esco_skill_mapping', sa.JSON(), nullable=True),
        sa.Column('trend_analysis', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_signals_id'), 'career_signals', ['id'], unique=False)
    op.create_index(op.f('ix_career_signals_user_id'), 'career_signals', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_signals_course_id'), 'career_signals', ['course_id'], unique=False)

    # Create conversation_logs table
    op.create_table('conversation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('question_intent', sa.String(length=100), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('extracted_insights', sa.JSON(), nullable=True),
        sa.Column('sentiment_analysis', sa.JSON(), nullable=True),
        sa.Column('career_implications', sa.JSON(), nullable=True),
        sa.Column('llm_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_logs_id'), 'conversation_logs', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_logs_user_id'), 'conversation_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversation_logs_course_id'), 'conversation_logs', ['course_id'], unique=False)
    op.create_index(op.f('ix_conversation_logs_session_id'), 'conversation_logs', ['session_id'], unique=False)

    # Create career_profile_aggregates table
    op.create_table('career_profile_aggregates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('aggregate_type', sa.String(length=50), nullable=False),
        sa.Column('time_period', sa.String(length=50), nullable=True),
        sa.Column('cognitive_preferences', sa.JSON(), nullable=True),
        sa.Column('work_style_preferences', sa.JSON(), nullable=True),
        sa.Column('subject_affinities', sa.JSON(), nullable=True),
        sa.Column('career_readiness_signals', sa.JSON(), nullable=True),
        sa.Column('esco_path_suggestions', sa.JSON(), nullable=True),
        sa.Column('contradiction_flags', sa.JSON(), nullable=True),
        sa.Column('confidence_metrics', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_profile_aggregates_id'), 'career_profile_aggregates', ['id'], unique=False)
    op.create_index(op.f('ix_career_profile_aggregates_user_id'), 'career_profile_aggregates', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_index(op.f('ix_career_profile_aggregates_user_id'), table_name='career_profile_aggregates')
    op.drop_index(op.f('ix_career_profile_aggregates_id'), table_name='career_profile_aggregates')
    op.drop_table('career_profile_aggregates')
    
    op.drop_index(op.f('ix_conversation_logs_session_id'), table_name='conversation_logs')
    op.drop_index(op.f('ix_conversation_logs_course_id'), table_name='conversation_logs')
    op.drop_index(op.f('ix_conversation_logs_user_id'), table_name='conversation_logs')
    op.drop_index(op.f('ix_conversation_logs_id'), table_name='conversation_logs')
    op.drop_table('conversation_logs')
    
    op.drop_index(op.f('ix_career_signals_course_id'), table_name='career_signals')
    op.drop_index(op.f('ix_career_signals_user_id'), table_name='career_signals')
    op.drop_index(op.f('ix_career_signals_id'), table_name='career_signals')
    op.drop_table('career_signals')
    
    op.drop_index(op.f('ix_psychological_insights_course_id'), table_name='psychological_insights')
    op.drop_index(op.f('ix_psychological_insights_user_id'), table_name='psychological_insights')
    op.drop_index(op.f('ix_psychological_insights_id'), table_name='psychological_insights')
    op.drop_table('psychological_insights')
    
    op.drop_index(op.f('ix_courses_user_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_table('courses')