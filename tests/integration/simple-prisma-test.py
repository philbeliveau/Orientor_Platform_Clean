#!/usr/bin/env python3
"""
Simple Prisma Test - Isolate the db.user issue
==============================================

Minimal test to reproduce the exact 'Prisma' object has no attribute 'user' error
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_prisma_attributes():
    """Test what attributes the Prisma client actually has."""
    try:
        from app.utils.prisma_client import get_prisma_client
        
        logger.info("Getting Prisma client...")
        db = await get_prisma_client()
        
        logger.info(f"Prisma client type: {type(db)}")
        logger.info(f"Prisma client attributes: {dir(db)}")
        
        # Check for user vs users
        has_user = hasattr(db, 'user')
        has_users = hasattr(db, 'users') 
        has_user_profiles = hasattr(db, 'user_profiles')
        
        logger.info(f"Has 'user' attribute: {has_user}")
        logger.info(f"Has 'users' attribute: {has_users}")
        logger.info(f"Has 'user_profiles' attribute: {has_user_profiles}")
        
        # Try to list all table-related attributes
        table_attrs = [attr for attr in dir(db) if not attr.startswith('_') and not callable(getattr(db, attr, None))]
        logger.info(f"Table-like attributes: {table_attrs}")
        
        # Test a simple operation
        if has_users:
            logger.info("Testing db.users.find_first()...")
            # Just test the method exists - don't actually query
            find_first_method = getattr(db.users, 'find_first', None)
            logger.info(f"users.find_first method exists: {find_first_method is not None}")
        else:
            logger.error("❌ db.users attribute is missing!")
            
        return {
            "has_user": has_user,
            "has_users": has_users, 
            "has_user_profiles": has_user_profiles,
            "table_attrs": table_attrs
        }
        
    except Exception as e:
        logger.error(f"Error testing Prisma: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def test_onboarding_complete_simulation():
    """Simulate the exact failing operation."""
    try:
        from app.utils.prisma_client import get_prisma_client
        
        logger.info("Simulating onboarding completion operation...")
        db = await get_prisma_client()
        
        # This is the exact operation that should work
        logger.info("Testing db.users.update operation structure...")
        
        # Check if the update method exists
        if hasattr(db, 'users'):
            update_method = getattr(db.users, 'update', None)
            logger.info(f"users.update method exists: {update_method is not None}")
        else:
            logger.error("❌ db.users does not exist!")
            
        # Don't actually execute the update, just test the structure
        logger.info("Structure test completed")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error in simulation: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def main():
    logger.info("🔍 Starting Simple Prisma Test")
    
    # Test 1: Check Prisma client attributes
    logger.info("=" * 50)
    logger.info("TEST 1: Prisma Client Attributes")
    result1 = await test_prisma_attributes()
    logger.info(f"Result: {result1}")
    
    # Test 2: Simulate onboarding operation
    logger.info("=" * 50)
    logger.info("TEST 2: Onboarding Operation Simulation")
    result2 = await test_onboarding_complete_simulation()
    logger.info(f"Result: {result2}")
    
    # Summary
    logger.info("=" * 50)
    logger.info("🎯 SUMMARY")
    
    if result1.get("has_users") and result2.get("status") == "success":
        logger.info("✅ Prisma client appears to be configured correctly")
        logger.info("   The error might be happening in a different context or cached code")
    else:
        logger.error("❌ Found issues with Prisma client setup")
        
    return result1, result2

if __name__ == "__main__":
    asyncio.run(main())