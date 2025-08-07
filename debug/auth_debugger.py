#!/usr/bin/env python3
"""
Authentication Debugger for Orientor Platform
Diagnoses Clerk authentication issues and token validation problems
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

async def debug_clerk_auth():
    """Debug Clerk authentication configuration and token validation"""
    
    print("🔍 ORIENTOR AUTHENTICATION DEBUGGER")
    print("=" * 50)
    
    # 1. Environment Variables Check
    print("\n1️⃣  ENVIRONMENT VARIABLES CHECK")
    print("-" * 30)
    
    required_env = [
        'CLERK_SECRET_KEY',
        'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', 
        'NEXT_PUBLIC_CLERK_DOMAIN'
    ]
    
    for var in required_env:
        value = os.getenv(var)
        if value:
            masked = f"{value[:8]}...{value[-8:]}" if len(value) > 16 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: MISSING")
    
    # 2. Import Check
    print("\n2️⃣  IMPORT CHECK")
    print("-" * 15)
    
    try:
        from app.utils.clerk_auth import (
            get_current_user_with_db_sync, 
            clerk_health_check,
            fetch_clerk_jwks
        )
        print("✅ Clerk auth functions imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # 3. Health Check
    print("\n3️⃣  CLERK HEALTH CHECK")
    print("-" * 20)
    
    try:
        health_result = await clerk_health_check()
        print(f"✅ Health check: {health_result}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # 4. JWKS Fetch Test
    print("\n4️⃣  JWKS FETCH TEST")
    print("-" * 18)
    
    try:
        jwks = await fetch_clerk_jwks()
        keys_count = len(jwks.get('keys', []))
        print(f"✅ JWKS fetch successful: {keys_count} keys retrieved")
        
        # Show first key info (masked)
        if keys_count > 0:
            first_key = jwks['keys'][0]
            print(f"   First key ID: {first_key.get('kid', 'N/A')}")
            print(f"   Key type: {first_key.get('kty', 'N/A')}")
            print(f"   Algorithm: {first_key.get('alg', 'N/A')}")
            
    except Exception as e:
        print(f"❌ JWKS fetch failed: {e}")
    
    # 5. Token Validation Test
    print("\n5️⃣  TOKEN VALIDATION TEST")
    print("-" * 23)
    
    # Test with invalid token
    try:
        fake_token = "invalid.token.here"
        # Test the actual auth function that's failing
        result = await get_current_user_with_db_sync(fake_token)
        print(f"⚠️  Invalid token validation: {result}")
    except Exception as e:
        print(f"✅ Invalid token correctly rejected: {type(e).__name__}: {str(e)[:100]}")
    
    # 6. Database Connection Check
    print("\n6️⃣  DATABASE CONNECTION CHECK")
    print("-" * 28)
    
    try:
        from app.utils.database import get_database
        db = get_database()
        print("✅ Database connection established")
        
        # Test a simple query
        from app.models.user import User
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"✅ Database query test: {result[0] if result else 'No result'}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # 7. API Endpoint Test
    print("\n7️⃣  API ENDPOINT SIMULATION")
    print("-" * 26)
    
    try:
        # Simulate the auth flow without actual HTTP request
        print("🔄 Simulating authentication flow...")
        
        # This would normally come from request headers
        test_scenarios = [
            ("No token", None),
            ("Invalid token", "invalid.jwt.token"),
            ("Malformed token", "not.a.jwt"),
        ]
        
        for scenario, token in test_scenarios:
            print(f"\n   Testing: {scenario}")
            try:
                if token is None:
                    print("     ❌ No Authorization header - 401 expected")
                else:
                    # This would call get_current_user_with_db_sync
                    print(f"     🔄 Validating token: {token[:20]}...")
                    print("     ❌ Invalid token - 401 expected")
            except Exception as e:
                print(f"     ✅ Correctly handled: {type(e).__name__}")
        
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
    
    # 8. Recommendations
    print("\n8️⃣  RECOMMENDATIONS")
    print("-" * 17)
    
    print("Based on the errors, here are potential fixes:")
    print("1. Verify Clerk domain and keys are correct")
    print("2. Check if frontend is sending valid JWT tokens")
    print("3. Ensure CORS is properly configured")
    print("4. Verify token is being sent in Authorization header")
    print("5. Check for network issues between frontend/backend")
    
    print("\n🔧 DEBUGGING COMMANDS:")
    print("Frontend token check:")
    print("  Open browser console -> localStorage.getItem('clerk-db-jwt')")
    print("  Or check Network tab for Authorization headers")
    
    print("\nBackend logs check:")
    print("  Increase log level to DEBUG in main.py")
    print("  Add more detailed error logging in clerk_auth.py")

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault('CLERK_SECRET_KEY', 'sk_test_1cINwMnu5slBHCftWNHnKMelHORTylnlnFQvhzWO6f')
    os.environ.setdefault('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', 'pk_test_cnVsaW5nLWhhbGlidXQtODkuY2xlcmsuYWNjb3VudHMuZGV2JA')
    os.environ.setdefault('NEXT_PUBLIC_CLERK_DOMAIN', 'ruling-halibut-89.clerk.accounts.dev')
    
    asyncio.run(debug_clerk_auth())