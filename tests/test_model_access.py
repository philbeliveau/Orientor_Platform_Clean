#!/usr/bin/env python3
"""
Model Access Validation Test
Tests all corrected Prisma model references to ensure they work properly.
"""

import asyncio
from prisma import Prisma

async def test_model_access():
    """Test access to all critical models that were flagged for correction."""
    
    try:
        prisma = Prisma()
        await prisma.connect()
        
        # Test hexaco_questions (was incorrectly called hexacoquestion)
        hexaco_count = await prisma.hexaco_questions.count()
        print(f"✅ hexaco_questions accessible: {hexaco_count} records")
        
        # Test personality_profiles (was using snake_case correctly)
        profile_count = await prisma.personality_profile.count()
        print(f"✅ personality_profile accessible: {profile_count} records")
        
        # Test suggestedpeers (was using correct model name)
        peers_count = await prisma.suggestedpeers.count()
        print(f"✅ suggestedpeers accessible: {peers_count} records")
        
        # Test savedrecommendation (was using correct model name)
        saved_count = await prisma.savedrecommendation.count()
        print(f"✅ savedrecommendation accessible: {saved_count} records")
        
        # Test users model (critical for authentication)
        users_count = await prisma.users.count()
        print(f"✅ users accessible: {users_count} records")
        
        # Test a sample query that was failing before
        sample_hexaco = await prisma.hexaco_questions.find_many(take=1)
        if sample_hexaco:
            print(f"✅ HEXACO query successful: found question '{sample_hexaco[0].item_text[:50]}...'")
        else:
            print("⚠️  No HEXACO questions found in database")
            
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Model access test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_model_access())
    exit(0 if success else 1)