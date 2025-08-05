"""Add Orientator AI tables and update saved_recommendations

Revision ID: add_orientator_ai_tables
Revises: 7085dfa9bba2
Create Date: 2025-06-24 20:24:07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_orientator_ai_tables'
down_revision = 'add_interactive_tree_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create message_components table
    op.create_table('message_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('component_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('tool_source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('saved', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_components_id'), 'message_components', ['id'], unique=False)
    op.create_index(op.f('ix_message_components_message_id'), 'message_components', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_components_component_type'), 'message_components', ['component_type'], unique=False)
    op.create_index(op.f('ix_message_components_tool_source'), 'message_components', ['tool_source'], unique=False)
    op.create_index(op.f('ix_message_components_created_at'), 'message_components', ['created_at'], unique=False)
    
    # Create tool_invocations table
    op.create_table('tool_invocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('tool_name', sa.String(length=50), nullable=False),
        sa.Column('input_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tool_invocations_id'), 'tool_invocations', ['id'], unique=False)
    op.create_index(op.f('ix_tool_invocations_conversation_id'), 'tool_invocations', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_tool_invocations_tool_name'), 'tool_invocations', ['tool_name'], unique=False)
    op.create_index(op.f('ix_tool_invocations_execution_time_ms'), 'tool_invocations', ['execution_time_ms'], unique=False)
    op.create_index(op.f('ix_tool_invocations_user_id'), 'tool_invocations', ['user_id'], unique=False)
    op.create_index(op.f('ix_tool_invocations_created_at'), 'tool_invocations', ['created_at'], unique=False)
    
    # Create composite indexes for performance
    op.create_index('idx_tool_invocations_conversation_tool', 'tool_invocations', ['conversation_id', 'tool_name'], unique=False)
    op.create_index('idx_tool_invocations_user_tool', 'tool_invocations', ['user_id', 'tool_name'], unique=False)
    
    # Create user_journey_milestones table
    op.create_table('user_journey_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('milestone_type', sa.String(length=50), nullable=False),
        sa.Column('milestone_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('achieved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ai_insights', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('next_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_journey_milestones_id'), 'user_journey_milestones', ['id'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_user_id'), 'user_journey_milestones', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_milestone_type'), 'user_journey_milestones', ['milestone_type'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_category'), 'user_journey_milestones', ['category'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_status'), 'user_journey_milestones', ['status'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_conversation_id'), 'user_journey_milestones', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_user_journey_milestones_created_at'), 'user_journey_milestones', ['created_at'], unique=False)
    
    # Create composite indexes for journey tracking
    op.create_index('idx_journey_user_status', 'user_journey_milestones', ['user_id', 'status'], unique=False)
    op.create_index('idx_journey_user_category', 'user_journey_milestones', ['user_id', 'category'], unique=False)
    
    # Add new columns to saved_recommendations table
    op.add_column('saved_recommendations', sa.Column('source_tool', sa.String(length=50), nullable=True))
    op.add_column('saved_recommendations', sa.Column('conversation_id', sa.Integer(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('component_type', sa.String(length=50), nullable=True))
    op.add_column('saved_recommendations', sa.Column('component_data', sa.JSON(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('interaction_metadata', sa.JSON(), nullable=True))
    
    # Add indexes for new columns
    op.create_index(op.f('ix_saved_recommendations_source_tool'), 'saved_recommendations', ['source_tool'], unique=False)
    op.create_index(op.f('ix_saved_recommendations_conversation_id'), 'saved_recommendations', ['conversation_id'], unique=False)
    
    # Add foreign key constraint for conversation_id
    op.create_foreign_key('fk_saved_recommendations_conversation', 'saved_recommendations', 'conversations', ['conversation_id'], ['id'], ondelete='SET NULL')
    
    # Create GIN indexes for JSONB search optimization
    op.execute("CREATE INDEX idx_message_components_data_gin ON message_components USING gin(component_data);")
    op.execute("CREATE INDEX idx_tool_invocations_params_gin ON tool_invocations USING gin(input_params);")
    op.execute("CREATE INDEX idx_journey_milestones_data_gin ON user_journey_milestones USING gin(milestone_data);")


def downgrade():
    # Drop GIN indexes
    op.execute("DROP INDEX IF EXISTS idx_message_components_data_gin;")
    op.execute("DROP INDEX IF EXISTS idx_tool_invocations_params_gin;")
    op.execute("DROP INDEX IF EXISTS idx_journey_milestones_data_gin;")
    
    # Drop foreign key constraint from saved_recommendations
    op.drop_constraint('fk_saved_recommendations_conversation', 'saved_recommendations', type_='foreignkey')
    
    # Drop indexes from saved_recommendations
    op.drop_index(op.f('ix_saved_recommendations_conversation_id'), table_name='saved_recommendations')
    op.drop_index(op.f('ix_saved_recommendations_source_tool'), table_name='saved_recommendations')
    
    # Drop columns from saved_recommendations
    op.drop_column('saved_recommendations', 'interaction_metadata')
    op.drop_column('saved_recommendations', 'component_data')
    op.drop_column('saved_recommendations', 'component_type')
    op.drop_column('saved_recommendations', 'conversation_id')
    op.drop_column('saved_recommendations', 'source_tool')
    
    # Drop composite indexes from user_journey_milestones
    op.drop_index('idx_journey_user_category', table_name='user_journey_milestones')
    op.drop_index('idx_journey_user_status', table_name='user_journey_milestones')
    
    # Drop indexes from user_journey_milestones
    op.drop_index(op.f('ix_user_journey_milestones_created_at'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_conversation_id'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_status'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_category'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_milestone_type'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_user_id'), table_name='user_journey_milestones')
    op.drop_index(op.f('ix_user_journey_milestones_id'), table_name='user_journey_milestones')
    op.drop_table('user_journey_milestones')
    
    # Drop composite indexes from tool_invocations
    op.drop_index('idx_tool_invocations_user_tool', table_name='tool_invocations')
    op.drop_index('idx_tool_invocations_conversation_tool', table_name='tool_invocations')
    
    # Drop indexes from tool_invocations
    op.drop_index(op.f('ix_tool_invocations_created_at'), table_name='tool_invocations')
    op.drop_index(op.f('ix_tool_invocations_user_id'), table_name='tool_invocations')
    op.drop_index(op.f('ix_tool_invocations_execution_time_ms'), table_name='tool_invocations')
    op.drop_index(op.f('ix_tool_invocations_tool_name'), table_name='tool_invocations')
    op.drop_index(op.f('ix_tool_invocations_conversation_id'), table_name='tool_invocations')
    op.drop_index(op.f('ix_tool_invocations_id'), table_name='tool_invocations')
    op.drop_table('tool_invocations')
    
    # Drop indexes from message_components
    op.drop_index(op.f('ix_message_components_created_at'), table_name='message_components')
    op.drop_index(op.f('ix_message_components_tool_source'), table_name='message_components')
    op.drop_index(op.f('ix_message_components_component_type'), table_name='message_components')
    op.drop_index(op.f('ix_message_components_message_id'), table_name='message_components')
    op.drop_index(op.f('ix_message_components_id'), table_name='message_components')
    op.drop_table('message_components')