#!/usr/bin/env python3
"""
Fix missing primary key constraints for Prisma compatibility
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

# Tables that should have primary keys based on your Prisma schema
TABLES_NEEDING_PRIMARY_KEYS = [
    'behavioral_signals',
    'career_fit_analyses', 
    'career_goals',
    'career_milestones',
    'career_profile_aggregates',
    'career_signals',
    'chat_messages',
    'conversation_categories',
    'conversation_logs',
    'conversation_shares',
    'conversations',
    'courses',
    'developmental_milestones',
    'esco_job_requirements',
    'gca_choices',
    'gca_holland_questions',
    'gca_questions',
    'gca_results',
    'gca_tests',
    'gca_users_answers',
    'institutions',
    'llm_descriptions',
    'message_components',
    'messages',
    'node_notes',
    'personality_assessments',
    'personality_profiles',
    'personality_responses',
    'personality_trends',
    'program_recommendations',
    'programs',
    'psychological_insights',
    'public_feed',
    'saved_jobs',
    'saved_recommendations',
    'suggested_peers',
    'tool_invocations',
    'tree_generations',
    'tree_paths',
    'user_chat_analytics',
    'user_journey_milestones',
    'user_notes',
    'user_program_preferences',
    'user_progress',
    'user_recommendations',
    'user_representation',
    'user_skill_graphs',
    'user_skill_nodes',
    'user_skill_trees',
    'user_skills'
]

async def fix_primary_keys():
    """Add missing primary key constraints"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("🔧 Fixing missing primary key constraints...")
        print("=" * 60)
        
        fixed_tables = []
        failed_tables = []
        
        for table_name in TABLES_NEEDING_PRIMARY_KEYS:
            try:
                print(f"🔍 Checking {table_name}...")
                
                # Check if table exists and has an id column
                table_check = await client.execute_raw(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                        AND table_schema = 'public'
                        AND column_name = 'id'
                """)
                
                if not table_check:
                    print(f"   ⚠️  Table {table_name} doesn't exist or has no id column")
                    continue
                
                # Check if primary key already exists
                pk_check = await client.execute_raw(f"""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = '{table_name}' 
                        AND constraint_type = 'PRIMARY KEY'
                        AND table_schema = 'public'
                """)
                
                if pk_check:
                    print(f"   ✅ {table_name} already has primary key")
                    continue
                
                # Add primary key constraint
                await client.execute_raw(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {table_name}_pkey 
                    PRIMARY KEY (id)
                """)
                
                print(f"   ✅ Added primary key to {table_name}")
                fixed_tables.append(table_name)
                
            except Exception as e:
                print(f"   ❌ Failed to fix {table_name}: {str(e)}")
                failed_tables.append((table_name, str(e)))
        
        print("\n" + "=" * 60)
        print(f"📊 RESULTS:")
        print(f"✅ Successfully fixed: {len(fixed_tables)} tables")
        print(f"❌ Failed to fix: {len(failed_tables)} tables")
        
        if fixed_tables:
            print(f"\n🎉 Fixed tables:")
            for table in fixed_tables:
                print(f"   - {table}")
        
        if failed_tables:
            print(f"\n🔧 Tables that need manual attention:")
            for table, error in failed_tables:
                print(f"   - {table}: {error}")
        
        await client.disconnect()
        
        return len(fixed_tables)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

async def verify_fixes():
    """Verify that the fixes worked"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("\n🔍 Verifying primary key fixes...")
        
        # Count tables with primary keys
        pk_count = await client.execute_raw("""
            SELECT COUNT(DISTINCT table_name) as count
            FROM information_schema.table_constraints 
            WHERE constraint_type = 'PRIMARY KEY'
                AND table_schema = 'public'
                AND table_name != 'alembic_version'
        """)
        
        print(f"✅ Tables with primary keys: {pk_count}")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Primary Key Fix for Prisma Compatibility")
    
    # Fix the primary keys
    fixed_count = asyncio.run(fix_primary_keys())
    
    if fixed_count > 0:
        print(f"\n✅ Fixed {fixed_count} tables")
        print("🔄 Now run these commands to update Prisma:")
        print("   cd backend")
        print("   npx prisma db pull")
        print("   npx prisma generate")
        print("   python -m prisma generate")
    else:
        print("\n⚠️  No tables were fixed. Check the errors above.")
    
    # Verify the fixes
    asyncio.run(verify_fixes())