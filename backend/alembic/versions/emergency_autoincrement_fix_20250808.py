"""Emergency autoincrement fix for critical tables

Revision ID: emergency_autoincrement_fix_20250808
Revises: fix_conversations_id_autoincrement_20250808
Create Date: 2025-08-08 16:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'emergency_autoincrement_fix_20250808'
down_revision: Union[str, None] = 'fix_conversations_id_autoincrement_20250808'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Emergency fix for critical autoincrement issues.
    
    This migration adds SERIAL autoincrement to the most critical tables
    that are confirmed to be blocking user functionality:
    - user_skills (blocking skills assessment)
    - career_goals (blocking goal setting)
    - chat_messages (high-risk for chat system)
    - courses (blocking academic tracking)
    """
    
    # Fix user_skills table - CRITICAL (confirmed broken)
    print("🚨 Fixing user_skills table (CRITICAL - Skills assessment broken)")
    op.execute("""
        -- Create sequence for user_skills.id if it doesn't exist
        CREATE SEQUENCE IF NOT EXISTS user_skills_id_seq;
        
        -- Set sequence ownership and current value
        ALTER SEQUENCE user_skills_id_seq OWNED BY user_skills.id;
        SELECT setval('user_skills_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM user_skills;
        
        -- Set default value to use sequence
        ALTER TABLE user_skills ALTER COLUMN id SET DEFAULT nextval('user_skills_id_seq');
    """)
    
    # Fix career_goals table - CRITICAL (confirmed broken)  
    print("🚨 Fixing career_goals table (CRITICAL - Goal setting broken)")
    op.execute("""
        -- Create sequence for career_goals.id if it doesn't exist
        CREATE SEQUENCE IF NOT EXISTS career_goals_id_seq;
        
        -- Set sequence ownership and current value
        ALTER SEQUENCE career_goals_id_seq OWNED BY career_goals.id;
        SELECT setval('career_goals_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM career_goals;
        
        -- Set default value to use sequence
        ALTER TABLE career_goals ALTER COLUMN id SET DEFAULT nextval('career_goals_id_seq');
    """)
    
    # Fix chat_messages table - HIGH-RISK (chat system core)
    print("⚠️ Fixing chat_messages table (HIGH-RISK - Chat system)")
    op.execute("""
        -- Create sequence for chat_messages.id if it doesn't exist
        CREATE SEQUENCE IF NOT EXISTS chat_messages_id_seq;
        
        -- Set sequence ownership and current value
        ALTER SEQUENCE chat_messages_id_seq OWNED BY chat_messages.id;
        SELECT setval('chat_messages_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM chat_messages;
        
        -- Set default value to use sequence
        ALTER TABLE chat_messages ALTER COLUMN id SET DEFAULT nextval('chat_messages_id_seq');
    """)
    
    # Fix courses table - HIGH-RISK (academic tracking)
    print("⚠️ Fixing courses table (HIGH-RISK - Academic tracking)")
    op.execute("""
        -- Create sequence for courses.id if it doesn't exist
        CREATE SEQUENCE IF NOT EXISTS courses_id_seq;
        
        -- Set sequence ownership and current value
        ALTER SEQUENCE courses_id_seq OWNED BY courses.id;
        SELECT setval('courses_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM courses;
        
        -- Set default value to use sequence
        ALTER TABLE courses ALTER COLUMN id SET DEFAULT nextval('courses_id_seq');
    """)
    
    print("✅ Emergency autoincrement fix completed for critical tables")


def downgrade() -> None:
    """Rollback autoincrement fixes (remove sequences and defaults)."""
    
    # Rollback user_skills
    op.execute("ALTER TABLE user_skills ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS user_skills_id_seq CASCADE;")
    
    # Rollback career_goals
    op.execute("ALTER TABLE career_goals ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS career_goals_id_seq CASCADE;")
    
    # Rollback chat_messages
    op.execute("ALTER TABLE chat_messages ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS chat_messages_id_seq CASCADE;")
    
    # Rollback courses
    op.execute("ALTER TABLE courses ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS courses_id_seq CASCADE;")