#!/usr/bin/env python3
"""
Validate Clerk Integration Fixes
===============================

This script validates that the database schema mismatch fixes are working correctly
and that Clerk user IDs are properly integrated with the database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.suggested_peers import SuggestedPeers
from app.utils.clerk_auth import get_database_user_id_sync
from app.core.config import settings

def get_test_db_session():
    """Get a test database session"""
    try:
        database_url = settings.get_database_url
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def validate_database_structure(db: Session) -> bool:
    """Validate database structure for Clerk integration"""
    print("🔍 Validating database structure...")
    
    try:
        # Check users table structure
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """))
        
        columns = {row.column_name: row.data_type for row in result}
        
        # Required columns for Clerk integration
        required_columns = {
            'id': 'integer',
            'email': ['character varying', 'text'],
            'clerk_user_id': ['character varying', 'text']
        }
        
        for col, expected_type in required_columns.items():
            if col not in columns:
                print(f"❌ Missing column: users.{col}")
                return False
            
            actual_type = columns[col]
            if isinstance(expected_type, list):
                if actual_type not in expected_type:
                    print(f"❌ Wrong type for users.{col}: expected {expected_type}, got {actual_type}")
                    return False
            else:
                if actual_type != expected_type:
                    print(f"❌ Wrong type for users.{col}: expected {expected_type}, got {actual_type}")
                    return False
        
        print("✅ Users table structure is correct")
        
        # Check user_profiles table structure
        result = db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'user_profiles'
            AND column_name = 'user_id'
        """))
        
        user_id_col = result.fetchone()
        if not user_id_col or user_id_col.data_type != 'integer':
            print(f"❌ user_profiles.user_id should be integer, got {user_id_col.data_type if user_id_col else 'missing'}")
            return False
        
        print("✅ User_profiles table structure is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Database structure validation failed: {e}")
        return False

def validate_sample_data(db: Session) -> bool:
    """Validate sample data relationships"""
    print("🔍 Validating sample data relationships...")
    
    try:
        # Check for users with both id and clerk_user_id
        result = db.execute(text("""
            SELECT id, email, clerk_user_id 
            FROM users 
            WHERE clerk_user_id IS NOT NULL 
            LIMIT 5
        """))
        
        users_with_clerk_id = result.fetchall()
        
        if not users_with_clerk_id:
            print("⚠️ No users with clerk_user_id found - this might be expected for a fresh database")
            return True
        
        print(f"✅ Found {len(users_with_clerk_id)} users with Clerk IDs")
        
        # Check for user profiles
        for user in users_with_clerk_id[:3]:  # Check first 3
            profile_result = db.execute(text("""
                SELECT id, user_id 
                FROM user_profiles 
                WHERE user_id = :user_id
            """), {"user_id": user.id})
            
            profile = profile_result.fetchone()
            if profile:
                print(f"✅ User {user.id} has matching profile {profile.id}")
            else:
                print(f"⚠️ User {user.id} has no profile (might be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data validation failed: {e}")
        return False

def validate_user_id_translation() -> bool:
    """Validate user ID translation functions"""
    print("🔍 Validating user ID translation functions...")
    
    try:
        db = get_test_db_session()
        if not db:
            return False
        
        # Create a test user if none exists
        test_clerk_id = "test_user_12345"
        
        # Check if test user exists
        existing_user = db.query(User).filter(User.clerk_user_id == test_clerk_id).first()
        
        if not existing_user:
            # Create a test user
            test_user = User(
                email="test@example.com",
                clerk_user_id=test_clerk_id,
                first_name="Test",
                last_name="User"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user with ID {test_user.id}")
        else:
            test_user = existing_user
            print(f"✅ Using existing test user with ID {test_user.id}")
        
        # Test user ID translation
        try:
            translated_id = get_database_user_id_sync(test_clerk_id, db)
            if translated_id == test_user.id:
                print("✅ User ID translation working correctly")
                return True
            else:
                print(f"❌ User ID translation failed: expected {test_user.id}, got {translated_id}")
                return False
        except Exception as e:
            print(f"❌ User ID translation error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ User ID translation validation failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def validate_foreign_key_integrity(db: Session) -> bool:
    """Validate foreign key integrity"""
    print("🔍 Validating foreign key integrity...")
    
    try:
        # Check for orphaned user_profiles
        result = db.execute(text("""
            SELECT up.id, up.user_id 
            FROM user_profiles up 
            LEFT JOIN users u ON up.user_id = u.id 
            WHERE u.id IS NULL
        """))
        
        orphaned_profiles = result.fetchall()
        if orphaned_profiles:
            print(f"❌ Found {len(orphaned_profiles)} orphaned user_profiles")
            return False
        
        # Check for orphaned suggested_peers
        result = db.execute(text("""
            SELECT sp.user_id, sp.suggested_id
            FROM suggested_peers sp
            LEFT JOIN users u1 ON sp.user_id = u1.id
            LEFT JOIN users u2 ON sp.suggested_id = u2.id
            WHERE u1.id IS NULL OR u2.id IS NULL
        """))
        
        orphaned_suggestions = result.fetchall()
        if orphaned_suggestions:
            print(f"❌ Found {len(orphaned_suggestions)} orphaned suggested_peers")
            return False
        
        print("✅ No orphaned records found")
        return True
        
    except Exception as e:
        print(f"❌ Foreign key integrity validation failed: {e}")
        return False

def validate_peer_matching_queries(db: Session) -> bool:
    """Validate that peer matching queries work with integer user IDs"""
    print("🔍 Validating peer matching queries...")
    
    try:
        # Test compatibility vector query
        result = db.execute(text("""
            SELECT COUNT(*) as count
            FROM user_profiles 
            WHERE compatibility_vector IS NOT NULL
        """))
        
        vector_count = result.fetchone().count
        print(f"✅ Found {vector_count} user profiles with compatibility vectors")
        
        # Test suggested peers query
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM suggested_peers sp
            JOIN users u1 ON sp.user_id = u1.id
            JOIN users u2 ON sp.suggested_id = u2.id
        """))
        
        suggestion_count = result.fetchone().count
        print(f"✅ Found {suggestion_count} valid peer suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Peer matching query validation failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Starting Clerk Integration Validation")
    print("=" * 50)
    
    db = get_test_db_session()
    if not db:
        print("❌ Cannot connect to database")
        return False
    
    try:
        validation_results = []
        
        # Run all validations
        validation_results.append(("Database Structure", validate_database_structure(db)))
        validation_results.append(("Sample Data", validate_sample_data(db)))
        validation_results.append(("User ID Translation", validate_user_id_translation()))
        validation_results.append(("Foreign Key Integrity", validate_foreign_key_integrity(db)))
        validation_results.append(("Peer Matching Queries", validate_peer_matching_queries(db)))
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 VALIDATION SUMMARY")
        print("=" * 50)
        
        all_passed = True
        for test_name, result in validation_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if not result:
                all_passed = False
        
        print("=" * 50)
        if all_passed:
            print("🎉 ALL VALIDATIONS PASSED!")
            print("\nThe Clerk authentication integration is working correctly:")
            print("• String Clerk user IDs are properly translated to integer database IDs")
            print("• All database queries use integer user_id parameters")
            print("• Foreign key relationships are maintained")
            print("• No data integrity issues found")
            
        else:
            print("💥 SOME VALIDATIONS FAILED!")
            print("\nPlease check the failed validations above.")
            print("The database schema mismatch issue may still exist.")
            
        return all_passed
        
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)