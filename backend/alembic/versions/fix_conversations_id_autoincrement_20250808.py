"""fix conversations id autoincrement

Revision ID: fix_conversations_id_autoincrement
Revises: 7085dfa9bba2
Create Date: 2025-08-08 12:05:34

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_conversations_id_autoincrement'
down_revision = '7085dfa9bba2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make the conversations.id column auto-increment (SERIAL)
    # This fixes the issue where new conversations fail with NULL constraint violation
    op.execute("""
        ALTER TABLE conversations 
        ALTER COLUMN id SET DEFAULT nextval('conversations_id_seq');
    """)
    
    # Create the sequence if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'conversations_id_seq') THEN
                CREATE SEQUENCE conversations_id_seq OWNED BY conversations.id;
                SELECT setval('conversations_id_seq', COALESCE((SELECT MAX(id) FROM conversations), 0) + 1);
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    # Remove the default and drop sequence
    op.execute("ALTER TABLE conversations ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS conversations_id_seq CASCADE;")