"""Add user_representation table

Revision ID: add_user_representation_table
Revises: 7085dfa9bba2
Create Date: 2025-01-06 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_representation_table'
down_revision = '7085dfa9bba2'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_representation table
    op.create_table('user_representation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('format_version', sa.String(length=10), nullable=False, server_default='v1'),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_representation_id'), 'user_representation', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_representation_id'), table_name='user_representation')
    op.drop_table('user_representation')