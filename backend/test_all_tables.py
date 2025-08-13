#!/usr/bin/env python3
"""
Test that all tables are now accessible through Prisma
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

async def test_all_tables():
    """Test access to all tables through Prisma"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("🎉 TESTING ACCESS TO ALL TABLES...")
        print("=" * 60)
        
        # Test various tables to confirm they're accessible
        test_queries = [
            ("users", lambda: client.user.count()),
            ("user_profiles", lambda: client.userprofile.count()),
            ("hexaco_questions", lambda: client.hexacoquestion.count()),
            ("conversations", lambda: client.conversation.count()),
            ("chat_messages", lambda: client.chatmessage.count()),
            ("career_goals", lambda: client.careergoal.count()),
            ("personality_assessments", lambda: client.personalityassessment.count()),
            ("user_skills", lambda: client.userskill.count()),
            ("suggested_peers", lambda: client.suggestedpeers.count()),
            ("gca_questions", lambda: client.gcaquestion.count()),
        ]
        
        accessible_tables = []
        failed_tables = []
        
        for table_name, query_func in test_queries:
            try:
                count = await query_func()
                print(f"✅ {table_name:<25} - {count:>6} records")
                accessible_tables.append(table_name)
            except Exception as e:
                print(f"❌ {table_name:<25} - Error: {str(e)[:50]}...")
                failed_tables.append((table_name, str(e)))
        
        print("\n" + "=" * 60)
        print(f"📊 FINAL RESULTS:")
        print(f"✅ Accessible tables: {len(accessible_tables)}")
        print(f"❌ Failed tables: {len(failed_tables)}")
        
        if failed_tables:
            print(f"\n🔧 Tables with issues:")
            for table, error in failed_tables:
                print(f"   - {table}: {error[:100]}...")
        else:
            print(f"\n🎉 ALL TESTED TABLES ARE ACCESSIBLE!")
            print(f"✨ Prisma now has full access to your Railway database!")
        
        await client.disconnect()
        
        return len(accessible_tables), len(failed_tables)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, 1

if __name__ == "__main__":
    print("🚀 Testing Prisma Access to All Tables")
    accessible, failed = asyncio.run(test_all_tables())
    
    if failed == 0:
        print(f"\n🎊 SUCCESS! Prisma has access to all {accessible} tested tables!")
        print("🚀 You now have the full power of Prisma with your Railway database!")
    else:
        print(f"\n⚠️  {failed} tables still have issues that need attention.")