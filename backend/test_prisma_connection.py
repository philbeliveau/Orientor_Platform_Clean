#!/usr/bin/env python3
"""
Test script to verify Prisma connection with Railway database
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_prisma_connection():
    """Test the Prisma connection to Railway database"""
    try:
        print("🔧 Testing Prisma connection to Railway database...")
        
        # Import Prisma client
        from prisma import Prisma
        
        # Create client instance
        client = Prisma()
        
        # Connect to database
        print("🔌 Connecting to database...")
        await client.connect()
        
        # Test basic query
        print("📊 Testing basic query...")
        user_count = await client.users.count()
        print(f"✅ Found {user_count} users in database")
        
        # Test a more complex query with the available models
        print("🔍 Testing user profiles query...")
        profiles_count = await client.user_profiles.count()
        print(f"✅ Found {profiles_count} user profiles")
        
        # Test relation query if users exist
        if user_count > 0:
            print("👤 Testing user with profile query...")
            user_with_profile = await client.users.find_first(
                include={"user_profiles": True}
            )
            if user_with_profile:
                print(f"✅ Successfully loaded user: {user_with_profile.email}")
                print(f"   Profile attached: {bool(user_with_profile.user_profiles)}")
            else:
                print("ℹ️  No users found with profiles")
        
        # Test hexaco questions
        print("🧠 Testing hexaco questions...")
        hexaco_count = await client.hexaco_questions.count()
        print(f"✅ Found {hexaco_count} hexaco questions")
        
        # Test reflection questions  
        print("🤔 Testing reflection questions...")
        reflection_count = await client.reflection_questions.count()
        print(f"✅ Found {reflection_count} reflection questions")
        
        # Disconnect
        await client.disconnect()
        print("🔌 Disconnected from database")
        
        print("\n🎉 Prisma connection test completed successfully!")
        print("✅ Database connection: Working")
        print("✅ Prisma client: Generated and functional")
        print("✅ Query operations: All successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you've run: python -m prisma generate")
        return False
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your DATABASE_URL in .env")
        print("2. Verify Railway database is running")
        print("3. Run: npx prisma db pull")
        print("4. Run: python -m prisma generate")
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_prisma_connection())
    
    if result:
        print("\n🚀 Ready to use Prisma in your FastAPI application!")
        sys.exit(0)
    else:
        print("\n🛠  Please fix the issues above before proceeding")
        sys.exit(1)