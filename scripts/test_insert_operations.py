#!/usr/bin/env python3
"""
Database INSERT Operations Test
Tests INSERT operations across all broken models to identify which are functional vs broken.
"""

import os
import sys
import asyncio
from datetime import datetime
import uuid

# Add the backend directory to the Python path
sys.path.append("backend")

from app.utils.database import get_db
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.user_skill import UserSkill
from app.models.career_goal import CareerGoal
from app.models.node_note import NodeNote
from app.models.user_note import UserNote
from app.models.user_profile import UserProfile
from app.models.conversation_category import ConversationCategory
from app.models.user_chat_analytics import UserChatAnalytics

# Test data for different models
TEST_DATA = {
    "User": {
        "email": f"test_{datetime.now().timestamp()}@test.com",
        "clerk_user_id": f"clerk_{uuid.uuid4()}",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True
    },
    "UserSkill": {
        "user_id": 1,  # Will need to handle this dynamically
        "creativity": 0.5,
        "leadership": 0.7,
        "digital_literacy": 0.8
    },
    "CareerGoal": {
        "user_id": 1,
        "title": "Test Career Goal",
        "description": "Test description",
        "is_active": True,
        "progress_percentage": 0.0
    },
    "ConversationCategory": {
        "user_id": 1,
        "name": "Test Category",
        "description": "Test category description",
        "color": "#FF0000"
    },
    "NodeNote": {
        "user_id": 1,
        "node_id": "test_node",
        "content": "Test note content"
    },
    "UserNote": {
        "user_id": 1,
        "content": "Test user note",
        "category": "general"
    },
    "UserProfile": {
        "user_id": 1,
        "bio": "Test bio",
        "location": "Test Location",
        "interests": ["test", "interests"]
    },
    "UserChatAnalytics": {
        "user_id": 1,
        "total_conversations": 0,
        "total_messages": 0,
        "avg_response_time": 1.0
    }
}

async def test_model_insert(db, model_class, test_data):
    """Test inserting a single record for a model."""
    try:
        # Create instance
        instance = model_class(**test_data)
        
        # Add to session
        db.add(instance)
        
        # Try to commit (this is where autoincrement issues appear)
        db.commit()
        
        # If successful, get the generated ID
        generated_id = instance.id
        
        # Clean up - delete the test record
        db.delete(instance)
        db.commit()
        
        return {
            "status": "SUCCESS",
            "generated_id": generated_id,
            "error": None
        }
        
    except Exception as e:
        # Rollback failed transaction
        db.rollback()
        
        return {
            "status": "FAILED",
            "generated_id": None,
            "error": str(e)
        }

async def run_insert_tests():
    """Run INSERT tests across all broken models."""
    
    print("=" * 80)
    print("🧪 DATABASE INSERT OPERATIONS TEST")
    print("=" * 80)
    
    # Get database session
    db = next(get_db())
    
    test_results = {}
    
    # Test models in dependency order (User first, then dependent models)
    test_order = [
        (User, TEST_DATA["User"]),
        (UserSkill, TEST_DATA["UserSkill"]),
        (CareerGoal, TEST_DATA["CareerGoal"]),
        (ConversationCategory, TEST_DATA["ConversationCategory"]),
        (NodeNote, TEST_DATA["NodeNote"]),
        (UserNote, TEST_DATA["UserNote"]),
        (UserProfile, TEST_DATA["UserProfile"]),
        (UserChatAnalytics, TEST_DATA["UserChatAnalytics"])
    ]
    
    # First, try to create a test user to get a valid user_id
    test_user_id = None
    print("\n📝 Creating test user for foreign key references...")
    
    try:
        test_user = User(**TEST_DATA["User"])
        db.add(test_user)
        db.commit()
        test_user_id = test_user.id
        print(f"✅ Test user created with ID: {test_user_id}")
        
        # Update test data with real user_id
        for model_name, data in TEST_DATA.items():
            if "user_id" in data:
                data["user_id"] = test_user_id
                
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        print("⚠️ Tests will use user_id=1 (may cause foreign key errors)")
        
    # Run tests for each model
    for model_class, test_data in test_order:
        model_name = model_class.__name__
        print(f"\n🔍 Testing {model_name}...")
        
        result = await test_model_insert(db, model_class, test_data)
        test_results[model_name] = result
        
        if result["status"] == "SUCCESS":
            print(f"  ✅ SUCCESS - Generated ID: {result['generated_id']}")
        else:
            print(f"  ❌ FAILED - Error: {result['error']}")
    
    # Clean up test user
    if test_user_id:
        try:
            test_user = db.query(User).filter(User.id == test_user_id).first()
            if test_user:
                db.delete(test_user)
                db.commit()
                print(f"\n🧹 Cleaned up test user (ID: {test_user_id})")
        except Exception as e:
            print(f"⚠️ Failed to clean up test user: {e}")
    
    db.close()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    successful = [name for name, result in test_results.items() if result["status"] == "SUCCESS"]
    failed = [name for name, result in test_results.items() if result["status"] == "FAILED"]
    
    print(f"\n✅ SUCCESSFUL INSERTS ({len(successful)}):")
    for model_name in successful:
        print(f"  - {model_name}")
    
    print(f"\n❌ FAILED INSERTS ({len(failed)}):")
    for model_name in failed:
        result = test_results[model_name]
        print(f"  - {model_name}: {result['error']}")
    
    print(f"\n📈 Success Rate: {len(successful)}/{len(test_results)} ({len(successful)/len(test_results)*100:.1f}%)")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(run_insert_tests())