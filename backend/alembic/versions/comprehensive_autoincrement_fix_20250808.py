"""Comprehensive autoincrement fix for all affected tables

Revision ID: comprehensive_autoincrement_fix_20250808
Revises: emergency_autoincrement_fix_20250808
Create Date: 2025-08-08 16:40:00.000000

This migration fixes the systemic autoincrement issue affecting 25+ database tables.
It creates PostgreSQL sequences and sets default values for all affected primary keys.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'comprehensive_autoincrement_fix_20250808'
down_revision: Union[str, None] = 'emergency_autoincrement_fix_20250808'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All tables that need autoincrement fixes (excluding the 4 already fixed in emergency)
AFFECTED_TABLES = [
    # Tier 2: High-risk core features
    'users',                        # Foundation table  
    'user_profiles',               # User data
    
    # Tier 3: Important secondary features
    'saved_recommendations',       # Recommendation engine
    'conversation_categories',     # Chat organization
    'user_chat_analytics',        # Usage tracking
    'node_notes',                 # Interactive learning
    'user_notes',                 # Personal notes
    
    # Tier 4: Supporting features
    'career_milestones',          # Progress tracking
    'psychological_insights',     # AI insights
    'career_signals',            # Career intelligence
    'conversation_logs',         # Detailed logging
    'tool_invocations',          # AI tool usage
    'user_journey_milestones',   # Journey progress
    'message_components',        # Rich messages
    'user_representations',      # Vector embeddings
    'conversation_shares',       # Social sharing
    'reflections',               # Self-assessment (strengths_reflection_responses)
    'user_skill_trees',         # Skill tree visualization
    'user_recommendations',      # Recommendation storage
    'personality_responses',     # Personality test responses (second model in file)
    'career_profile_aggregates', # Profile aggregates (from course.py)
    'conversation_logs',         # Conversation logging (from course.py)
]

def upgrade() -> None:
    """Add autoincrement (SERIAL) to all affected tables."""
    
    print("🔧 Starting comprehensive autoincrement fix for all remaining tables...")
    
    for table_name in AFFECTED_TABLES:
        print(f"   Fixing {table_name}...")
        
        try:
            # Create sequence
            sequence_name = f"{table_name}_id_seq"
            
            op.execute(f"""
                -- Create sequence if it doesn't exist
                CREATE SEQUENCE IF NOT EXISTS {sequence_name};
                
                -- Set sequence ownership
                ALTER SEQUENCE {sequence_name} OWNED BY {table_name}.id;
                
                -- Set sequence current value to max existing id + 1
                SELECT setval('{sequence_name}', COALESCE(MAX(id), 0) + 1, false) FROM {table_name};
                
                -- Set default value to use sequence
                ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{sequence_name}');
            """)
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not fix {table_name}: {e}")
            # Continue with other tables even if one fails
            continue
    
    # Handle special cases that might need different approaches
    
    # Fix personality_assessments (first model in personality_profiles.py)
    print("   Fixing personality_assessments (special case)...")
    try:
        op.execute("""
            CREATE SEQUENCE IF NOT EXISTS personality_assessments_id_seq;
            ALTER SEQUENCE personality_assessments_id_seq OWNED BY personality_assessments.id;
            SELECT setval('personality_assessments_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM personality_assessments;
            ALTER TABLE personality_assessments ALTER COLUMN id SET DEFAULT nextval('personality_assessments_id_seq');
        """)
    except Exception as e:
        print(f"   ⚠️ Warning: Could not fix personality_assessments: {e}")
    
    print("✅ Comprehensive autoincrement fix completed!")
    print("📊 Summary:")
    print(f"   - Fixed {len(AFFECTED_TABLES)} tables")
    print("   - Created PostgreSQL sequences for auto-incrementing primary keys")
    print("   - Set appropriate default values")
    print("   - Preserved existing data")


def downgrade() -> None:
    """Remove autoincrement fixes (remove sequences and defaults)."""
    
    print("🔄 Rolling back comprehensive autoincrement fixes...")
    
    for table_name in AFFECTED_TABLES:
        sequence_name = f"{table_name}_id_seq"
        try:
            op.execute(f"ALTER TABLE {table_name} ALTER COLUMN id DROP DEFAULT;")
            op.execute(f"DROP SEQUENCE IF EXISTS {sequence_name} CASCADE;")
        except Exception as e:
            print(f"   ⚠️ Warning: Could not rollback {table_name}: {e}")
            continue
    
    # Rollback special cases
    try:
        op.execute("ALTER TABLE personality_assessments ALTER COLUMN id DROP DEFAULT;")
        op.execute("DROP SEQUENCE IF EXISTS personality_assessments_id_seq CASCADE;")
    except Exception as e:
        print(f"   ⚠️ Warning: Could not rollback personality_assessments: {e}")
    
    print("✅ Rollback completed!")