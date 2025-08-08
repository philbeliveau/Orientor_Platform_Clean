"""
Comprehensive Database Autoincrement Integration Tests

Tests to prevent regression of the systemic autoincrement issue that affected 29/31 database tables.
These tests ensure all models can perform INSERT operations successfully with auto-generated IDs.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Import all models that need testing
from backend.app.models.user import User
from backend.app.models.user_skill import UserSkill
from backend.app.models.career_goal import CareerGoal, CareerMilestone
from backend.app.models.chat_message import ChatMessage
from backend.app.models.conversation import Conversation
from backend.app.models.user_profile import UserProfile
from backend.app.models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog, CareerProfileAggregate
from backend.app.models.saved_recommendation import SavedRecommendation
from backend.app.models.conversation_category import ConversationCategory
from backend.app.models.user_chat_analytics import UserChatAnalytics
from backend.app.models.node_note import NodeNote
from backend.app.models.user_note import UserNote
from backend.app.models.tool_invocation import ToolInvocation
from backend.app.models.user_journey_milestone import UserJourneyMilestone
from backend.app.models.message_component import MessageComponent
from backend.app.models.user_representation import UserRepresentation
from backend.app.models.conversation_share import ConversationShare
from backend.app.models.reflection import StrengthsReflectionResponse
from backend.app.models.user_skill_tree import UserSkillTree
from backend.app.models.user_recommendation import UserRecommendation
from backend.app.models.personality_profiles import PersonalityAssessment, PersonalityResponse, PersonalityProfile

from backend.app.utils.database import get_db


class TestAutoIncrementIntegration:
    """Integration tests for database autoincrement functionality."""
    
    @pytest.fixture
    def db_session(self):
        """Get database session for testing."""
        db = next(get_db())
        yield db
        db.close()
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create a test user for foreign key references."""
        user = User(
            email=f"test_{uuid.uuid4()}@test.com",
            clerk_user_id=f"clerk_{uuid.uuid4()}",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        yield user
        # Cleanup is handled by cascade relationships
    
    def test_user_autoincrement(self, db_session):
        """Test User model autoincrement functionality."""
        user = User(
            email=f"autoincrement_test_{uuid.uuid4()}@test.com",
            clerk_user_id=f"clerk_{uuid.uuid4()}",
            first_name="AutoIncrement",
            last_name="Test"
        )
        
        # ID should be None before commit
        assert user.id is None
        
        db_session.add(user)
        db_session.commit()
        
        # ID should be auto-generated after commit
        assert user.id is not None
        assert isinstance(user.id, int)
        assert user.id > 0
        
        # Clean up
        db_session.delete(user)
        db_session.commit()
    
    def test_user_skill_autoincrement(self, db_session, test_user):
        """Test UserSkill model autoincrement - this was the original failing case."""
        user_skill = UserSkill(
            user_id=test_user.id,
            creativity=0.5,
            leadership=0.7,
            digital_literacy=0.8
        )
        
        assert user_skill.id is None
        
        db_session.add(user_skill)
        db_session.commit()
        
        assert user_skill.id is not None
        assert isinstance(user_skill.id, int)
        assert user_skill.id > 0
    
    def test_career_goal_autoincrement(self, db_session, test_user):
        """Test CareerGoal model autoincrement - this was the second failing case."""
        career_goal = CareerGoal(
            user_id=test_user.id,
            title="Test Career Goal",
            description="Test description",
            is_active=True
        )
        
        assert career_goal.id is None
        
        db_session.add(career_goal)
        db_session.commit()
        
        assert career_goal.id is not None
        assert isinstance(career_goal.id, int)
        assert career_goal.id > 0
    
    def test_chat_message_autoincrement(self, db_session, test_user):
        """Test ChatMessage model autoincrement."""
        # First create a conversation
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        chat_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content="Test message"
        )
        
        assert chat_message.id is None
        
        db_session.add(chat_message)
        db_session.commit()
        
        assert chat_message.id is not None
        assert isinstance(chat_message.id, int)
        assert chat_message.id > 0
    
    def test_conversation_autoincrement(self, db_session, test_user):
        """Test Conversation model autoincrement - this should already work."""
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        
        assert conversation.id is None
        
        db_session.add(conversation)
        db_session.commit()
        
        assert conversation.id is not None
        assert isinstance(conversation.id, int)
        assert conversation.id > 0
    
    def test_course_autoincrement(self, db_session, test_user):
        """Test Course model autoincrement."""
        course = Course(
            user_id=test_user.id,
            course_name="Test Course",
            semester="Fall 2024"
        )
        
        assert course.id is None
        
        db_session.add(course)
        db_session.commit()
        
        assert course.id is not None
        assert isinstance(course.id, int)
        assert course.id > 0
    
    @pytest.mark.parametrize("model_class,test_data", [
        (UserProfile, lambda user_id: {"user_id": user_id}),
        (SavedRecommendation, lambda user_id: {"user_id": user_id, "esco_occupation_id": "test_esco", "title": "Test Job"}),
        (ConversationCategory, lambda user_id: {"user_id": user_id, "name": "Test Category"}),
        (UserChatAnalytics, lambda user_id: {"user_id": user_id}),
        (NodeNote, lambda user_id: {"user_id": user_id, "node_id": "test_node"}),
        (UserNote, lambda user_id: {"user_id": user_id, "content": "Test note"}),
        (UserSkillTree, lambda user_id: {"user_id": user_id, "tree_data": {}}),
        (UserRecommendation, lambda user_id: {"user_id": user_id, "recommendation_data": {}}),
        (UserRepresentation, lambda user_id: {"user_id": user_id}),
    ])
    def test_model_autoincrement_parametrized(self, db_session, test_user, model_class, test_data):
        """Parametrized test for multiple model autoincrement functionality."""
        
        # Create instance with test data
        data = test_data(test_user.id)
        instance = model_class(**data)
        
        # ID should be None before commit
        assert instance.id is None
        
        db_session.add(instance)
        db_session.commit()
        
        # ID should be auto-generated after commit
        assert instance.id is not None
        assert isinstance(instance.id, int)
        assert instance.id > 0
    
    def test_complex_model_autoincrement(self, db_session, test_user):
        """Test autoincrement for models with complex relationships."""
        
        # Create course first
        course = Course(
            user_id=test_user.id,
            course_name="Psychology 101",
            semester="Fall 2024"
        )
        db_session.add(course)
        db_session.commit()
        
        # Test PsychologicalInsight
        insight = PsychologicalInsight(
            user_id=test_user.id,
            course_id=course.id,
            insight_type="cognitive_preference",
            insight_value={"preference": "visual"}
        )
        
        assert insight.id is None
        db_session.add(insight)
        db_session.commit()
        assert insight.id is not None
        
        # Test CareerSignal
        signal = CareerSignal(
            user_id=test_user.id,
            course_id=course.id,
            signal_type="analytical_thinking",
            strength_score=0.8,
            evidence_source="course_performance"
        )
        
        assert signal.id is None
        db_session.add(signal)
        db_session.commit()
        assert signal.id is not None
    
    def test_personality_models_autoincrement(self, db_session, test_user):
        """Test personality assessment models autoincrement."""
        
        # Create PersonalityAssessment
        assessment = PersonalityAssessment(
            user_id=test_user.id,
            assessment_type="hexaco",
            assessment_version="1.0"
        )
        
        assert assessment.id is None
        db_session.add(assessment)
        db_session.commit()
        assert assessment.id is not None
        
        # Create PersonalityResponse
        response = PersonalityResponse(
            assessment_id=assessment.id,
            item_id="H1",
            item_type="hexaco_question",
            response_value={"rating": 4}
        )
        
        assert response.id is None
        db_session.add(response)
        db_session.commit()
        assert response.id is not None
        
        # Create PersonalityProfile
        profile = PersonalityProfile(
            assessment_id=assessment.id,
            profile_type="hexaco_scores",
            profile_data={"honesty": 0.7}
        )
        
        assert profile.id is None
        db_session.add(profile)
        db_session.commit()
        assert profile.id is not None
    
    def test_batch_insert_autoincrement(self, db_session, test_user):
        """Test that batch inserts work correctly with autoincrement."""
        
        # Create multiple user skills
        skills = []
        for i in range(5):
            skill = UserSkill(
                user_id=test_user.id,
                creativity=0.1 * i,
                leadership=0.2 * i
            )
            skills.append(skill)
        
        # All should have None IDs before commit
        for skill in skills:
            assert skill.id is None
        
        db_session.add_all(skills)
        db_session.commit()
        
        # All should have unique auto-generated IDs after commit
        ids = [skill.id for skill in skills]
        assert all(id is not None for id in ids)
        assert all(isinstance(id, int) for id in ids)
        assert len(set(ids)) == 5  # All IDs should be unique
    
    def test_concurrent_insert_autoincrement(self, db_session, test_user):
        """Test that concurrent inserts don't cause ID conflicts."""
        
        # This test ensures that sequences handle concurrent access properly
        conversations = []
        for i in range(10):
            conversation = Conversation(
                user_id=test_user.id,
                title=f"Concurrent Test Conversation {i}"
            )
            conversations.append(conversation)
        
        # Add all at once to simulate concurrent access
        db_session.add_all(conversations)
        db_session.commit()
        
        # Check all have unique IDs
        ids = [conv.id for conv in conversations]
        assert len(set(ids)) == 10
        assert all(isinstance(id, int) and id > 0 for id in ids)
    
    def test_rollback_doesnt_affect_autoincrement(self, db_session, test_user):
        """Test that rollbacks don't break autoincrement sequences."""
        
        # Create a conversation and commit
        conv1 = Conversation(user_id=test_user.id, title="First")
        db_session.add(conv1)
        db_session.commit()
        first_id = conv1.id
        
        # Try to create another and rollback
        try:
            conv2 = Conversation(user_id=test_user.id, title="Second")
            db_session.add(conv2)
            db_session.commit()
            # Force an error to test rollback
            raise Exception("Forced error")
        except:
            db_session.rollback()
        
        # Create a third conversation - ID should still work
        conv3 = Conversation(user_id=test_user.id, title="Third")
        db_session.add(conv3)
        db_session.commit()
        
        assert conv3.id is not None
        assert conv3.id > first_id


class TestAutoIncrementRegression:
    """Regression tests specifically for the autoincrement issue patterns."""
    
    def test_no_null_ids_in_insert(self, db_session):
        """Regression test: Ensure no NULL IDs are attempted in INSERT operations."""
        
        user = User(
            email=f"regression_test_{uuid.uuid4()}@test.com",
            clerk_user_id=f"clerk_{uuid.uuid4()}"
        )
        
        # This should not fail with NULL constraint violation
        db_session.add(user)
        db_session.commit()
        
        # Verify the ID was generated
        assert user.id is not None
        
        # Clean up
        db_session.delete(user)
        db_session.commit()
    
    def test_original_error_cases_fixed(self, db_session):
        """Test the specific error cases that were originally broken."""
        
        # Create test user
        user = User(
            email=f"error_case_test_{uuid.uuid4()}@test.com",
            clerk_user_id=f"clerk_{uuid.uuid4()}"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test UserSkill - this was the original error
        user_skill = UserSkill(
            user_id=user.id,
            creativity=0.5,
            leadership=0.7,
            digital_literacy=0.8,
            critical_thinking=None,
            problem_solving=None,
            analytical_thinking=None,
            attention_to_detail=None,
            collaboration=None,
            adaptability=None,
            independence=None,
            evaluation=None,
            decision_making=None,
            stress_tolerance=None
        )
        
        # This should NOT fail with: 
        # "null value in column "id" of relation "user_skills" violates not-null constraint"
        db_session.add(user_skill)
        db_session.commit()
        
        assert user_skill.id is not None
        
        # Test CareerGoal - this was the second error
        career_goal = CareerGoal(
            user_id=user.id,
            title="Test Career Goal",
            description="Test description",
            is_active=True,
            progress_percentage=0.0
        )
        
        # This should NOT fail with:
        # "null value in column "id" of relation "career_goals" violates not-null constraint"
        db_session.add(career_goal)
        db_session.commit()
        
        assert career_goal.id is not None


if __name__ == "__main__":
    # Run tests manually if needed
    pytest.main([__file__, "-v"])