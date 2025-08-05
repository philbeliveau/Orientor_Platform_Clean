"""Add chat persistence tables

Revision ID: add_chat_persistence
Revises: add_compatibility_vector
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# revision identifiers, used by Alembic.
revision = 'add_chat_persistence'
down_revision = 'add_narrative_description'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversation_categories table
    op.create_table('conversation_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='_user_category_uc')
    )
    op.create_index(op.f('ix_conversation_categories_user_id'), 'conversation_categories', ['user_id'], unique=False)
    
    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('auto_generated_title', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_archived', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['category_id'], ['conversation_categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversations_category_id'), 'conversations', ['category_id'], unique=False)
    op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversations_is_favorite'), 'conversations', ['is_favorite'], unique=False)
    op.create_index(op.f('ix_conversations_is_archived'), 'conversations', ['is_archived'], unique=False)
    op.create_index('idx_user_conversations', 'conversations', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_user_favorites', 'conversations', ['user_id', 'is_favorite'], unique=False)
    
    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(length=50), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role_values'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_conversation_id'), 'chat_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_created_at'), 'chat_messages', ['created_at'], unique=False)
    op.create_index('idx_conversation_messages', 'chat_messages', ['conversation_id', 'created_at'], unique=False)
    
    # Create GIN index for full-text search on message content
    op.execute("CREATE INDEX idx_content_search ON chat_messages USING gin(to_tsvector('english', content));")
    
    # Create conversation_shares table
    op.create_table('conversation_shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('shared_by', sa.Integer(), nullable=False),
        sa.Column('share_token', sa.String(length=255), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_token')
    )
    op.create_index(op.f('ix_conversation_shares_id'), 'conversation_shares', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_shares_conversation_id'), 'conversation_shares', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_shares_shared_by'), 'conversation_shares', ['shared_by'], unique=False)
    op.create_index(op.f('ix_conversation_shares_share_token'), 'conversation_shares', ['share_token'], unique=True)
    op.create_index('idx_share_token', 'conversation_shares', ['share_token'], unique=False)
    
    # Create user_chat_analytics table
    op.create_table('user_chat_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('messages_sent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('conversations_started', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('most_used_category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['most_used_category_id'], ['conversation_categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='_user_date_analytics_uc')
    )
    op.create_index(op.f('ix_user_chat_analytics_id'), 'user_chat_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_user_chat_analytics_user_id'), 'user_chat_analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_chat_analytics_date'), 'user_chat_analytics', ['date'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_user_chat_analytics_date'), table_name='user_chat_analytics')
    op.drop_index(op.f('ix_user_chat_analytics_user_id'), table_name='user_chat_analytics')
    op.drop_index(op.f('ix_user_chat_analytics_id'), table_name='user_chat_analytics')
    op.drop_table('user_chat_analytics')
    
    op.drop_index('idx_share_token', table_name='conversation_shares')
    op.drop_index(op.f('ix_conversation_shares_share_token'), table_name='conversation_shares')
    op.drop_index(op.f('ix_conversation_shares_shared_by'), table_name='conversation_shares')
    op.drop_index(op.f('ix_conversation_shares_conversation_id'), table_name='conversation_shares')
    op.drop_index(op.f('ix_conversation_shares_id'), table_name='conversation_shares')
    op.drop_table('conversation_shares')
    
    # Drop GIN index
    op.execute("DROP INDEX IF EXISTS idx_content_search;")
    
    op.drop_index('idx_conversation_messages', table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_created_at'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_conversation_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index('idx_user_favorites', table_name='conversations')
    op.drop_index('idx_user_conversations', table_name='conversations')
    op.drop_index(op.f('ix_conversations_is_archived'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_is_favorite'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_created_at'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_category_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index(op.f('ix_conversation_categories_user_id'), table_name='conversation_categories')
    op.drop_table('conversation_categories')