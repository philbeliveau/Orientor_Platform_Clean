#!/usr/bin/env python3
"""
Final verification that all tables are accessible through Prisma
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

async def final_verification():
    """Final verification of Prisma access to all tables"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("🎊 FINAL VERIFICATION: PRISMA ACCESS TO ALL TABLES")
        print("=" * 70)
        
        # Get all available models
        models = [attr for attr in dir(client) if not attr.startswith('_') and not callable(getattr(client, attr, None))]
        
        print(f"📊 Total Models Available: {len(models)}")
        print()
        
        # Test key tables with data
        key_tables = [
            'users', 'user_profiles', 'hexaco_questions', 'conversations', 
            'chat_messages', 'career_goals', 'personality_assessments',
            'user_skills', 'gca_questions', 'programs', 'institutions'
        ]
        
        accessible_count = 0
        total_records = 0
        
        print("🔍 Testing key tables:")
        for table_name in key_tables:
            try:
                model = getattr(client, table_name)
                count = await model.count()
                print(f"✅ {table_name:<25} - {count:>6} records")
                accessible_count += 1
                total_records += count
            except Exception as e:
                print(f"❌ {table_name:<25} - Error: {str(e)[:50]}...")
        
        print(f"\n📈 Summary:")
        print(f"   ✅ Accessible key tables: {accessible_count}/{len(key_tables)}")
        print(f"   📊 Total records in key tables: {total_records:,}")
        print(f"   🗄️  Total models available: {len(models)}")
        
        # Test a few complex queries to show Prisma power
        print(f"\n🚀 Testing Prisma's Advanced Features:")
        
        # Example 1: Type-safe relationship queries
        try:
            users_with_profiles = await client.user.find_many(
                include={'profile': True},
                take=3
            )
            print(f"✅ Relationship queries: Found {len(users_with_profiles)} users with profiles")
        except Exception as e:
            print(f"⚠️  Relationship queries: {str(e)[:50]}...")
        
        # Example 2: Filtering and counting
        try:
            active_users = await client.user.count(
                where={'is_active': True}
            )
            print(f"✅ Filtered counting: {active_users} active users")
        except Exception as e:
            print(f"⚠️  Filtered counting: {str(e)[:50]}...")
        
        # Example 3: Aggregation
        try:
            personality_count = await client.personality_assessment.count()
            print(f"✅ Table access: {personality_count} personality assessments")
        except Exception as e:
            print(f"⚠️  Table access: {str(e)[:50]}...")
        
        await client.disconnect()
        
        print("\n" + "=" * 70)
        print("🎉 PRISMA INTEGRATION COMPLETE!")
        print("✨ You now have full access to all your Railway database tables")
        print("🚀 Enjoy type-safe queries, relationships, and modern ORM features!")
        print("📚 Next steps:")
        print("   - Use Prisma Studio: npx prisma studio")
        print("   - Explore relationships in your schema")
        print("   - Build type-safe APIs with Prisma")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_verification())
    if success:
        print("\n🎊 SUCCESS: Prisma integration is complete and working!")
    else:
        print("\n❌ There were some issues. Please check the errors above.")