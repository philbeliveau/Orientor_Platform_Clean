#!/usr/bin/env python3
"""
PRISMA MODEL NAME VALIDATION SCRIPT
Post-migration validation for instances 301-315

This script validates that all Prisma model name mismatches have been corrected.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from prisma import Prisma

async def validate_model_corrections():
    """Validate all corrected Prisma model names work correctly"""
    
    print("🔍 PRISMA MODEL NAME VALIDATION")
    print("=" * 50)
    
    client = Prisma()
    
    try:
        await client.connect()
        print("✅ Prisma connection established")
        
        # Test Instance 301 & 314: suggestedpeers model
        print("\n📊 Testing Instance 301 & 314: suggestedpeers")
        try:
            count = await client.suggestedpeers.count()
            print(f"✅ suggestedpeers.count(): {count}")
        except Exception as e:
            print(f"❌ suggestedpeers failed: {e}")
            return False
        
        # Test Instance 302-303: personality_profile model  
        print("\n📊 Testing Instance 302-303: personality_profile")
        try:
            count = await client.personality_profile.count()
            print(f"✅ personality_profile.count(): {count}")
        except Exception as e:
            print(f"❌ personality_profile failed: {e}")
            return False
        
        # Test Instance 304-313: personality_profile queries
        print("\n📊 Testing Instance 304-313: personality_profile operations")
        try:
            # Test find_first operation
            profile = await client.personality_profile.find_first()
            print(f"✅ personality_profile.find_first(): {'Found' if profile else 'None'}")
            
            # Test find_many operation  
            profiles = await client.personality_profile.find_many(take=1)
            print(f"✅ personality_profile.find_many(): {len(profiles)} records")
        except Exception as e:
            print(f"❌ personality_profile operations failed: {e}")
            return False
        
        # Test Instance 315: Prisma operations instead of raw SQL
        print("\n📊 Testing Instance 315: Prisma operations vs raw SQL")
        try:
            # Test update_many operation
            result = await client.personality_profile.update_many(
                where={"user_id": -999},  # Non-existent user
                data={"updated_at": "2024-01-01T00:00:00Z"}
            )
            print(f"✅ personality_profile.update_many(): {result} records updated")
        except Exception as e:
            print(f"❌ personality_profile update_many failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("✅ ALL MODEL NAME CORRECTIONS VALIDATED SUCCESSFULLY")
        print("🎯 Instances 301-315 have been fully resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
        
    finally:
        await client.disconnect()
        print("🔌 Prisma connection closed")

if __name__ == "__main__":
    success = asyncio.run(validate_model_corrections())
    sys.exit(0 if success else 1)