# Testing and Debugging Guide - Onboarding System

## Table of Contents
1. [Comprehensive Test Suite Design](#1-comprehensive-test-suite-design)
2. [Debugging Procedures](#2-debugging-procedures)
3. [Common Issue Scenarios](#3-common-issue-scenarios)
4. [Testing Automation](#4-testing-automation)

---

## 1. Comprehensive Test Suite Design

### 1.1 Unit Tests for Data Serialization

#### Date Handling Tests
```python
# backend/tests/test_onboarding_serialization.py
import pytest
from datetime import datetime
from app.routers.onboarding import OnboardingResponse, OnboardingData
from app.utils.error_handling import handle_prisma_error

class TestDateSerialization:
    """Test date serialization in onboarding responses"""
    
    def test_onboarding_response_with_datetime(self):
        """Test OnboardingResponse with datetime serialization"""
        timestamp = datetime.utcnow()
        response = OnboardingResponse(
            questionId="q1",
            question="What is your career goal?",
            response="Software Engineer",
            timestamp=timestamp
        )
        
        # Test serialization
        response_dict = response.dict()
        assert "timestamp" in response_dict
        assert isinstance(response_dict["timestamp"], datetime)
        
        # Test JSON serialization
        response_json = response.json()
        assert "timestamp" in response_json
    
    def test_onboarding_response_without_timestamp(self):
        """Test OnboardingResponse without timestamp (should default to None)"""
        response = OnboardingResponse(
            questionId="q1",
            question="What is your career goal?",
            response="Software Engineer"
        )
        
        response_dict = response.dict()
        assert response_dict["timestamp"] is None
    
    def test_onboarding_response_iso_format(self):
        """Test timestamp ISO format serialization"""
        timestamp = datetime.utcnow()
        response = OnboardingResponse(
            questionId="q1",
            question="Test question",
            response="Test response",
            timestamp=timestamp
        )
        
        # Custom serializer test
        serialized = response.dict()
        if serialized["timestamp"]:
            iso_string = serialized["timestamp"].isoformat()
            assert "T" in iso_string
            assert len(iso_string) >= 19  # YYYY-MM-DDTHH:MM:SS

class TestTypeValidation:
    """Test type validation for onboarding data"""
    
    def test_valid_onboarding_data(self):
        """Test valid OnboardingData creation"""
        responses = [
            OnboardingResponse(
                questionId="q1",
                question="Career goal?",
                response="Engineer",
                timestamp=datetime.utcnow()
            )
        ]
        
        data = OnboardingData(
            responses=responses,
            psychProfile={"personality": "INTJ"}
        )
        
        assert len(data.responses) == 1
        assert data.psychProfile["personality"] == "INTJ"
    
    def test_empty_responses_list(self):
        """Test OnboardingData with empty responses"""
        data = OnboardingData(responses=[], psychProfile=None)
        assert len(data.responses) == 0
        assert data.psychProfile is None
    
    def test_invalid_response_type(self):
        """Test OnboardingData with invalid response type"""
        with pytest.raises(ValueError):
            OnboardingData(responses="invalid_type")
    
    def test_malformed_psych_profile(self):
        """Test OnboardingData with malformed psychological profile"""
        # Should accept any dict structure
        data = OnboardingData(
            responses=[],
            psychProfile={"invalid": "structure", "nested": {"data": True}}
        )
        assert data.psychProfile["invalid"] == "structure"
```

#### API Data Validation Tests
```python
# backend/tests/test_onboarding_validation.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.utils.clerk_auth import get_current_user_with_onboarding

client = TestClient(app)

class TestOnboardingValidation:
    """Test API endpoint validation"""
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    def test_save_response_valid_data(self, mock_auth):
        """Test saving valid onboarding response"""
        mock_user = Mock()
        mock_user.id = 123
        mock_user.onboarding_completed = False
        mock_auth.return_value = mock_user
        
        response_data = {
            "questionId": "q1",
            "question": "What motivates you?",
            "response": "Helping others through technology",
            "timestamp": "2025-01-08T12:00:00.000Z"
        }
        
        with patch('app.routers.onboarding.prisma.onboardingresponse.create') as mock_create:
            mock_create.return_value = Mock(id="response_123")
            
            response = client.post(
                "/onboarding/response",
                json=response_data,
                headers={"Authorization": "Bearer fake_token"}
            )
            
            assert response.status_code == 200
            assert "id" in response.json()
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    def test_save_response_invalid_timestamp(self, mock_auth):
        """Test saving response with invalid timestamp format"""
        mock_user = Mock()
        mock_user.id = 123
        mock_user.onboarding_completed = False
        mock_auth.return_value = mock_user
        
        response_data = {
            "questionId": "q1",
            "question": "What motivates you?",
            "response": "Helping others",
            "timestamp": "invalid-timestamp"
        }
        
        response = client.post(
            "/onboarding/response",
            json=response_data,
            headers={"Authorization": "Bearer fake_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    def test_complete_onboarding_invalid_data_format(self, mock_auth):
        """Test completing onboarding with invalid data format"""
        mock_user = Mock()
        mock_user.id = 123
        mock_user.onboarding_completed = False
        mock_auth.return_value = mock_user
        
        invalid_data = {
            "responses": "not_a_list",  # Should be a list
            "psychProfile": "not_a_dict"  # Should be a dict
        }
        
        response = client.post(
            "/onboarding/complete",
            json=invalid_data,
            headers={"Authorization": "Bearer fake_token"}
        )
        
        assert response.status_code == 422
        assert "validation" in response.json()["detail"].lower()
```

### 1.2 Integration Tests for API Endpoints

#### Validation Scenarios
```python
# backend/tests/test_onboarding_integration.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from prisma.errors import UniqueViolationError, RecordNotFoundError

client = TestClient(app)

class TestOnboardingIntegration:
    """Integration tests for onboarding API endpoints"""
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    @patch('app.routers.onboarding.prisma')
    async def test_full_onboarding_flow(self, mock_prisma, mock_auth):
        """Test complete onboarding flow from start to finish"""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 123
        mock_user.onboarding_completed = False
        mock_auth.return_value = mock_user
        
        # Mock database responses
        mock_prisma.onboardingresponse.create.return_value = Mock(id="resp_1")
        mock_prisma.user.update.return_value = Mock(
            id=123, onboarding_completed=True
        )
        mock_prisma.userprofile.create.return_value = Mock(id="profile_1")
        
        # Step 1: Start onboarding
        start_response = client.post(
            "/onboarding/start",
            headers={"Authorization": "Bearer fake_token"}
        )
        assert start_response.status_code == 200
        
        # Step 2: Save responses
        responses_data = [
            {
                "questionId": "q1",
                "question": "Career goal?",
                "response": "Software Engineer",
                "timestamp": "2025-01-08T12:00:00.000Z"
            },
            {
                "questionId": "q2", 
                "question": "Strengths?",
                "response": "Problem solving",
                "timestamp": "2025-01-08T12:05:00.000Z"
            }
        ]
        
        for response_data in responses_data:
            save_response = client.post(
                "/onboarding/response",
                json=response_data,
                headers={"Authorization": "Bearer fake_token"}
            )
            assert save_response.status_code == 200
        
        # Step 3: Complete onboarding
        completion_data = {
            "responses": responses_data,
            "psychProfile": {
                "personality": "INTJ",
                "strengths": ["analytical", "strategic"]
            }
        }
        
        complete_response = client.post(
            "/onboarding/complete",
            json=completion_data,
            headers={"Authorization": "Bearer fake_token"}
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["onboarding_completed"] is True
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    @patch('app.routers.onboarding.prisma')
    def test_database_constraint_violations(self, mock_prisma, mock_auth):
        """Test handling of database constraint violations"""
        mock_user = Mock()
        mock_user.id = 123
        mock_auth.return_value = mock_user
        
        # Test unique constraint violation
        mock_prisma.onboardingresponse.create.side_effect = UniqueViolationError(
            "Unique constraint violation"
        )
        
        response_data = {
            "questionId": "q1",
            "question": "Test question",
            "response": "Test response"
        }
        
        response = client.post(
            "/onboarding/response",
            json=response_data,
            headers={"Authorization": "Bearer fake_token"}
        )
        
        assert response.status_code == 409
        assert "Duplicate record" in response.json()["detail"]
    
    @patch('app.routers.onboarding.get_current_user_with_onboarding')
    @patch('app.routers.onboarding.prisma')
    def test_record_not_found_error(self, mock_prisma, mock_auth):
        """Test handling of record not found errors"""
        mock_user = Mock()
        mock_user.id = 999  # Non-existent user
        mock_auth.return_value = mock_user
        
        mock_prisma.user.update.side_effect = RecordNotFoundError(
            "User not found"
        )
        
        completion_data = {
            "responses": [],
            "psychProfile": {"test": "data"}
        }
        
        response = client.post(
            "/onboarding/complete",
            json=completion_data,
            headers={"Authorization": "Bearer fake_token"}
        )
        
        assert response.status_code == 404
        assert "Record not found" in response.json()["detail"]
```

### 1.3 End-to-End Tests

```python
# backend/tests/test_onboarding_e2e.py
import pytest
import asyncio
from playwright.async_api import async_playwright
from fastapi.testclient import TestClient
from app.main import app

class TestOnboardingE2E:
    """End-to-end tests for complete onboarding flow"""
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_flow_ui(self):
        """Test complete onboarding flow through UI"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to onboarding page
                await page.goto("http://localhost:3000/onboarding")
                
                # Start onboarding
                await page.click('[data-testid="start-onboarding"]')
                await page.wait_for_selector('[data-testid="chat-interface"]')
                
                # Answer first question
                await page.fill('[data-testid="chat-input"]', 
                               "I want to become a software engineer")
                await page.click('[data-testid="send-button"]')
                
                # Wait for response and next question
                await page.wait_for_selector('[data-testid="bot-message"]')
                await page.wait_for_timeout(1000)
                
                # Answer more questions
                questions_and_answers = [
                    "I'm good at problem solving and logical thinking",
                    "I prefer working independently but enjoy team collaboration",
                    "I'm motivated by creating solutions that help people"
                ]
                
                for answer in questions_and_answers:
                    await page.fill('[data-testid="chat-input"]', answer)
                    await page.click('[data-testid="send-button"]')
                    await page.wait_for_timeout(2000)
                
                # Complete onboarding
                await page.click('[data-testid="complete-onboarding"]')
                await page.wait_for_selector('[data-testid="onboarding-complete"]')
                
                # Verify completion
                completion_message = await page.text_content(
                    '[data-testid="completion-message"]'
                )
                assert "successfully completed" in completion_message.lower()
                
            finally:
                await browser.close()
    
    @pytest.mark.asyncio
    async def test_onboarding_error_recovery(self):
        """Test error recovery in onboarding flow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Simulate network error during onboarding
                await context.route("**/onboarding/response", 
                                  lambda route: route.abort())
                
                await page.goto("http://localhost:3000/onboarding")
                await page.click('[data-testid="start-onboarding"]')
                
                # Try to send a response (should fail)
                await page.fill('[data-testid="chat-input"]', "Test response")
                await page.click('[data-testid="send-button"]')
                
                # Wait for error message
                await page.wait_for_selector('[data-testid="error-message"]')
                error_message = await page.text_content('[data-testid="error-message"]')
                assert "error" in error_message.lower()
                
                # Resume normal network behavior
                await context.unroute("**/onboarding/response")
                
                # Retry the response
                await page.click('[data-testid="retry-button"]')
                await page.wait_for_selector('[data-testid="bot-message"]', timeout=10000)
                
            finally:
                await browser.close()
```

### 1.4 Database Constraint Testing

```python
# backend/tests/test_onboarding_database_constraints.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.user_profile import UserProfile
from app.database import Base

class TestDatabaseConstraints:
    """Test database constraints and data integrity"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_user_email_uniqueness(self, db_session):
        """Test user email uniqueness constraint"""
        # Create first user
        user1 = User(
            email="test@example.com",
            clerk_user_id="clerk_123",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",  # Duplicate email
            clerk_user_id="clerk_456",
            first_name="Another",
            last_name="User"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_clerk_user_id_uniqueness(self, db_session):
        """Test Clerk user ID uniqueness constraint"""
        # Create first user
        user1 = User(
            email="user1@example.com",
            clerk_user_id="clerk_123",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same Clerk ID
        user2 = User(
            email="user2@example.com",
            clerk_user_id="clerk_123",  # Duplicate Clerk ID
            first_name="Another",
            last_name="User"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_profile_foreign_key(self, db_session):
        """Test UserProfile foreign key constraint"""
        # Try to create profile without valid user
        profile = UserProfile(
            user_id=999,  # Non-existent user
            career_goal="Software Engineer",
            personality_type="INTJ"
        )
        db_session.add(profile)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_onboarding_data_integrity(self, db_session):
        """Test onboarding data integrity constraints"""
        # Create user
        user = User(
            email="test@example.com",
            clerk_user_id="clerk_123",
            first_name="Test",
            last_name="User",
            onboarding_completed=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Create profile before onboarding completion (should be allowed)
        profile = UserProfile(
            user_id=user.id,
            career_goal="Engineer",
            personality_type="INTJ"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Update user to completed
        user.onboarding_completed = True
        db_session.commit()
        
        # Verify data consistency
        assert user.onboarding_completed is True
        assert profile.user_id == user.id
```

---

## 2. Debugging Procedures

### 2.1 Validation Error Diagnosis

#### Step-by-Step Diagnosis Process

```bash
# 1. Check API endpoint logs
tail -f logs/onboarding.log | grep "validation"

# 2. Examine request payload structure
curl -X POST "http://localhost:8000/onboarding/response" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "questionId": "q1",
    "question": "Test?",
    "response": "Test answer",
    "timestamp": "2025-01-08T12:00:00.000Z"
  }' -v

# 3. Validate timestamp format
python3 -c "
from datetime import datetime
import json
timestamp = '2025-01-08T12:00:00.000Z'
try:
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    print(f'Valid timestamp: {dt}')
except ValueError as e:
    print(f'Invalid timestamp: {e}')
"

# 4. Check Pydantic model validation
python3 -c "
from app.routers.onboarding import OnboardingResponse
try:
    response = OnboardingResponse(
        questionId='q1',
        question='Test?',
        response='Test answer',
        timestamp='invalid-timestamp'
    )
    print('Validation passed')
except Exception as e:
    print(f'Validation failed: {e}')
"
```

#### Common Validation Error Patterns

```python
# backend/scripts/debug_validation.py
import json
import traceback
from datetime import datetime
from app.routers.onboarding import OnboardingResponse, OnboardingData

def debug_validation_error(payload_json: str):
    """Debug validation errors in onboarding payloads"""
    
    print("=== ONBOARDING VALIDATION DEBUGGER ===")
    print(f"Input payload: {payload_json}")
    
    try:
        payload = json.loads(payload_json)
        print(f"✓ JSON parsing successful")
        
        # Check required fields
        required_fields = ["questionId", "question", "response"]
        missing_fields = [field for field in required_fields 
                         if field not in payload]
        
        if missing_fields:
            print(f"✗ Missing required fields: {missing_fields}")
            return False
        else:
            print(f"✓ All required fields present")
        
        # Check timestamp format if present
        if "timestamp" in payload and payload["timestamp"] is not None:
            try:
                if isinstance(payload["timestamp"], str):
                    # Try to parse ISO format
                    dt = datetime.fromisoformat(
                        payload["timestamp"].replace('Z', '+00:00')
                    )
                    print(f"✓ Timestamp format valid: {dt}")
                else:
                    print(f"✗ Timestamp must be string, got {type(payload['timestamp'])}")
                    return False
            except ValueError as e:
                print(f"✗ Invalid timestamp format: {e}")
                return False
        
        # Try Pydantic validation
        try:
            response_obj = OnboardingResponse(**payload)
            print(f"✓ Pydantic validation successful")
            print(f"Created object: {response_obj}")
            return True
            
        except Exception as e:
            print(f"✗ Pydantic validation failed: {e}")
            traceback.print_exc()
            return False
            
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing failed: {e}")
        return False

# Usage example
if __name__ == "__main__":
    # Test valid payload
    valid_payload = json.dumps({
        "questionId": "q1",
        "question": "What is your career goal?",
        "response": "Software Engineer",
        "timestamp": "2025-01-08T12:00:00.000Z"
    })
    debug_validation_error(valid_payload)
    
    # Test invalid payload
    invalid_payload = json.dumps({
        "questionId": "q1",
        "question": "What is your career goal?",
        "response": "Software Engineer",
        "timestamp": "invalid-timestamp"
    })
    debug_validation_error(invalid_payload)
```

### 2.2 Database Connectivity Troubleshooting

#### Connection Health Check Script

```python
# backend/scripts/debug_database_connection.py
import asyncio
import traceback
from datetime import datetime
from app.utils.prisma_client import prisma

async def debug_database_connection():
    """Debug database connectivity issues"""
    
    print("=== DATABASE CONNECTION DEBUGGER ===")
    print(f"Timestamp: {datetime.utcnow()}")
    
    try:
        # Test basic connection
        print("1. Testing database connection...")
        await prisma.connect()
        print("✓ Database connection successful")
        
        # Test simple query
        print("2. Testing simple query...")
        user_count = await prisma.user.count()
        print(f"✓ Query successful - Found {user_count} users")
        
        # Test onboarding-specific queries
        print("3. Testing onboarding queries...")
        
        # Count onboarding responses
        response_count = await prisma.onboardingresponse.count()
        print(f"✓ Onboarding responses: {response_count}")
        
        # Count completed onboarding users
        completed_users = await prisma.user.count(
            where={"onboarding_completed": True}
        )
        print(f"✓ Completed onboarding users: {completed_users}")
        
        # Test user profile queries
        profile_count = await prisma.userprofile.count()
        print(f"✓ User profiles: {profile_count}")
        
        print("4. Testing complex join query...")
        users_with_profiles = await prisma.user.find_many(
            include={"profile": True},
            take=5
        )
        print(f"✓ Users with profiles query successful: {len(users_with_profiles)} records")
        
        # Test write operation (safe test)
        print("5. Testing write operation...")
        test_response = await prisma.onboardingresponse.create(
            data={
                "user_id": 1,  # Assume user 1 exists
                "question_id": "debug_test",
                "question": "Debug test question",
                "response": "Debug test response",
                "created_at": datetime.utcnow()
            }
        )
        print(f"✓ Write operation successful: {test_response.id}")
        
        # Clean up test data
        await prisma.onboardingresponse.delete(
            where={"id": test_response.id}
        )
        print("✓ Test data cleaned up")
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        traceback.print_exc()
        return False
        
    finally:
        await prisma.disconnect()
        print("Database connection closed")
    
    print("=== DATABASE CONNECTION DEBUG COMPLETE ===")
    return True

# Connection pool monitoring
async def monitor_connection_pool():
    """Monitor database connection pool status"""
    
    print("=== CONNECTION POOL MONITOR ===")
    
    try:
        # Check connection pool stats
        from app.utils.database import get_connection_pool_stats
        
        stats = get_connection_pool_stats()
        print(f"Connection Pool Stats:")
        print(f"  Active connections: {stats.get('active', 'N/A')}")
        print(f"  Idle connections: {stats.get('idle', 'N/A')}")
        print(f"  Total connections: {stats.get('total', 'N/A')}")
        print(f"  Pool size: {stats.get('pool_size', 'N/A')}")
        
    except Exception as e:
        print(f"Could not retrieve connection pool stats: {e}")

if __name__ == "__main__":
    # Run connection test
    success = asyncio.run(debug_database_connection())
    
    # Monitor connection pool
    asyncio.run(monitor_connection_pool())
    
    if success:
        print("✓ All database tests passed")
    else:
        print("✗ Database tests failed")
```

### 2.3 Frontend/Backend Data Mismatch Debugging

#### Data Flow Validation Script

```typescript
// frontend/src/utils/onboardingDebugger.ts
interface DebugResponse {
  endpoint: string;
  request: any;
  response: any;
  statusCode: number;
  error?: string;
}

export class OnboardingDebugger {
  private debugLog: DebugResponse[] = [];
  
  async debugAPICall(
    endpoint: string, 
    method: string, 
    data?: any,
    headers?: Record<string, string>
  ): Promise<DebugResponse> {
    
    console.log(`=== DEBUGGING API CALL: ${method} ${endpoint} ===`);
    console.log('Request data:', JSON.stringify(data, null, 2));
    
    try {
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: data ? JSON.stringify(data) : undefined
      });
      
      const responseData = await response.json();
      
      const debugResponse: DebugResponse = {
        endpoint,
        request: data,
        response: responseData,
        statusCode: response.status
      };
      
      if (!response.ok) {
        debugResponse.error = responseData.detail || 'Unknown error';
        console.error('API Error:', debugResponse.error);
      } else {
        console.log('API Success:', responseData);
      }
      
      this.debugLog.push(debugResponse);
      return debugResponse;
      
    } catch (error) {
      console.error('Network error:', error);
      
      const debugResponse: DebugResponse = {
        endpoint,
        request: data,
        response: null,
        statusCode: 0,
        error: error instanceof Error ? error.message : 'Network error'
      };
      
      this.debugLog.push(debugResponse);
      return debugResponse;
    }
  }
  
  validateOnboardingResponse(response: any): boolean {
    console.log('=== VALIDATING ONBOARDING RESPONSE ===');
    
    const requiredFields = ['questionId', 'question', 'response'];
    const missingFields = requiredFields.filter(field => !response[field]);
    
    if (missingFields.length > 0) {
      console.error('Missing required fields:', missingFields);
      return false;
    }
    
    // Validate timestamp format if present
    if (response.timestamp) {
      try {
        const date = new Date(response.timestamp);
        if (isNaN(date.getTime())) {
          console.error('Invalid timestamp format:', response.timestamp);
          return false;
        }
        console.log('Valid timestamp:', date.toISOString());
      } catch (error) {
        console.error('Timestamp parsing error:', error);
        return false;
      }
    }
    
    console.log('✓ Response validation passed');
    return true;
  }
  
  async debugFullOnboardingFlow(): Promise<void> {
    console.log('=== DEBUGGING FULL ONBOARDING FLOW ===');
    
    try {
      // Get authentication token
      const { getToken } = useAuth();
      const token = await getToken();
      
      if (!token) {
        console.error('No authentication token available');
        return;
      }
      
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // 1. Check onboarding status
      await this.debugAPICall('/api/onboarding/status', 'GET', null, headers);
      
      // 2. Start onboarding
      await this.debugAPICall('/api/onboarding/start', 'POST', {}, headers);
      
      // 3. Save a test response
      const testResponse = {
        questionId: 'debug_q1',
        question: 'Debug test question?',
        response: 'Debug test answer',
        timestamp: new Date().toISOString()
      };
      
      if (this.validateOnboardingResponse(testResponse)) {
        await this.debugAPICall('/api/onboarding/response', 'POST', testResponse, headers);
      }
      
      // 4. Get saved responses
      await this.debugAPICall('/api/onboarding/responses', 'GET', null, headers);
      
      // 5. Test completion (dry run)
      const completionData = {
        responses: [testResponse],
        psychProfile: {
          personality: 'DEBUG',
          strengths: ['debugging']
        }
      };
      
      console.log('Would complete onboarding with:', completionData);
      
    } catch (error) {
      console.error('Debug flow error:', error);
    }
  }
  
  getDebugReport(): string {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      totalCalls: this.debugLog.length,
      errors: this.debugLog.filter(log => log.error).length,
      log: this.debugLog
    }, null, 2);
  }
  
  exportDebugLog(): void {
    const report = this.getDebugReport();
    const blob = new Blob([report], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `onboarding-debug-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}
```

### 2.4 Error Log Analysis Techniques

#### Log Analysis Script

```python
# backend/scripts/analyze_onboarding_logs.py
import re
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any

class OnboardingLogAnalyzer:
    """Analyze onboarding-related logs for patterns and issues"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.error_patterns = {
            'validation_error': r'validation.*error|invalid.*data|422',
            'database_error': r'database.*error|prisma.*error|connection.*error',
            'authentication_error': r'auth.*error|unauthorized|401|403',
            'timeout_error': r'timeout|timed.*out',
            'serialization_error': r'serializ.*error|json.*error|encoding.*error'
        }
    
    def parse_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse a single log entry"""
        
        # Basic log format: TIMESTAMP LEVEL MESSAGE
        pattern = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+(\w+)\s+(.+)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, level, message = match.groups()
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            except ValueError:
                timestamp = None
                
            return {
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'raw_line': line.strip()
            }
        
        return {'raw_line': line.strip()}
    
    def categorize_error(self, message: str) -> List[str]:
        """Categorize error message based on patterns"""
        categories = []
        
        message_lower = message.lower()
        for category, pattern in self.error_patterns.items():
            if re.search(pattern, message_lower):
                categories.append(category)
        
        return categories if categories else ['unknown_error']
    
    def analyze_logs(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze logs for the specified time period"""
        
        print(f"Analyzing logs for the last {hours_back} hours...")
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        error_counts = Counter()
        error_categories = Counter()
        error_timeline = defaultdict(list)
        validation_errors = []
        database_errors = []
        
        total_lines = 0
        onboarding_lines = 0
        error_lines = 0
        
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    total_lines += 1
                    
                    # Filter onboarding-related logs
                    if not re.search(r'onboard', line, re.IGNORECASE):
                        continue
                    
                    onboarding_lines += 1
                    entry = self.parse_log_entry(line)
                    
                    # Skip entries without timestamp or outside time window
                    if not entry.get('timestamp') or entry['timestamp'] < cutoff_time:
                        continue
                    
                    # Analyze error entries
                    if entry.get('level') in ['ERROR', 'CRITICAL']:
                        error_lines += 1
                        message = entry['message']
                        
                        # Categorize error
                        categories = self.categorize_error(message)
                        for category in categories:
                            error_categories[category] += 1
                        
                        # Store specific error types for detailed analysis
                        if 'validation_error' in categories:
                            validation_errors.append({
                                'timestamp': entry['timestamp'],
                                'message': message
                            })
                        
                        if 'database_error' in categories:
                            database_errors.append({
                                'timestamp': entry['timestamp'],
                                'message': message
                            })
                        
                        # Track errors over time (hourly buckets)
                        hour_bucket = entry['timestamp'].replace(minute=0, second=0, microsecond=0)
                        error_timeline[hour_bucket].append({
                            'categories': categories,
                            'message': message[:100] + '...' if len(message) > 100 else message
                        })
                        
                        # Count specific error messages
                        error_counts[message[:100]] += 1
        
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file_path}")
            return {}
        
        # Analyze patterns
        top_errors = error_counts.most_common(10)
        hourly_error_distribution = {
            str(hour): len(errors) for hour, errors in error_timeline.items()
        }
        
        analysis_result = {
            'summary': {
                'total_lines': total_lines,
                'onboarding_lines': onboarding_lines,
                'error_lines': error_lines,
                'analysis_period_hours': hours_back
            },
            'error_categories': dict(error_categories),
            'top_errors': top_errors,
            'hourly_distribution': hourly_error_distribution,
            'validation_errors': validation_errors[:10],  # Latest 10
            'database_errors': database_errors[:10],  # Latest 10
            'recommendations': self._generate_recommendations(error_categories, validation_errors, database_errors)
        }
        
        return analysis_result
    
    def _generate_recommendations(self, error_categories: Counter, 
                                validation_errors: List, database_errors: List) -> List[str]:
        """Generate recommendations based on error analysis"""
        recommendations = []
        
        if error_categories.get('validation_error', 0) > 10:
            recommendations.append(
                "High validation error rate detected. Check frontend data validation and API contract consistency."
            )
        
        if error_categories.get('database_error', 0) > 5:
            recommendations.append(
                "Database errors detected. Check connection pool settings and query performance."
            )
        
        if error_categories.get('authentication_error', 0) > 5:
            recommendations.append(
                "Authentication errors detected. Verify Clerk token handling and refresh logic."
            )
        
        if len(validation_errors) > 0:
            # Analyze common validation error patterns
            validation_messages = [err['message'] for err in validation_errors]
            common_validation_issues = Counter()
            
            for message in validation_messages:
                if 'timestamp' in message.lower():
                    common_validation_issues['timestamp_format'] += 1
                elif 'required' in message.lower():
                    common_validation_issues['missing_fields'] += 1
                elif 'type' in message.lower():
                    common_validation_issues['type_mismatch'] += 1
            
            if common_validation_issues['timestamp_format'] > 3:
                recommendations.append(
                    "Multiple timestamp format errors. Review date serialization between frontend and backend."
                )
        
        return recommendations
    
    def generate_report(self, hours_back: int = 24) -> str:
        """Generate a formatted analysis report"""
        analysis = self.analyze_logs(hours_back)
        
        if not analysis:
            return "No analysis data available"
        
        report = f"""
=== ONBOARDING LOG ANALYSIS REPORT ===
Analysis Period: {hours_back} hours
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Total log lines: {analysis['summary']['total_lines']}
- Onboarding-related lines: {analysis['summary']['onboarding_lines']}
- Error lines: {analysis['summary']['error_lines']}

ERROR CATEGORIES:
"""
        
        for category, count in analysis['error_categories'].items():
            report += f"- {category.replace('_', ' ').title()}: {count}\n"
        
        report += "\nTOP ERROR MESSAGES:\n"
        for i, (error_msg, count) in enumerate(analysis['top_errors'], 1):
            report += f"{i}. ({count}x) {error_msg}\n"
        
        if analysis['recommendations']:
            report += "\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        return report

# Usage
if __name__ == "__main__":
    analyzer = OnboardingLogAnalyzer('/var/log/orientor/onboarding.log')
    report = analyzer.generate_report(hours_back=24)
    print(report)
    
    # Save detailed analysis
    analysis = analyzer.analyze_logs(24)
    with open(f'/tmp/onboarding-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
```

---

## 3. Common Issue Scenarios

### 3.1 "Invalid Data Format" Error Resolution

#### Diagnostic Steps

```bash
#!/bin/bash
# scripts/debug_invalid_data_format.sh

echo "=== DEBUGGING 'Invalid Data Format' ERROR ==="

# Step 1: Check current API request structure
echo "1. Capturing current API request structure..."
curl -X POST "http://localhost:8000/onboarding/response" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "questionId": "debug",
    "question": "Debug question?",
    "response": "Debug response",
    "timestamp": "2025-01-08T12:00:00.000Z"
  }' \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
  -s -o /tmp/api_response.json

echo "API Response:"
cat /tmp/api_response.json | jq '.' 2>/dev/null || cat /tmp/api_response.json

# Step 2: Validate JSON structure
echo -e "\n2. Validating JSON structure..."
python3 << 'EOF'
import json

test_payload = {
    "questionId": "debug",
    "question": "Debug question?",
    "response": "Debug response",
    "timestamp": "2025-01-08T12:00:00.000Z"
}

try:
    json_str = json.dumps(test_payload)
    parsed = json.loads(json_str)
    print("✓ JSON structure is valid")
    print(f"Payload: {json_str}")
except json.JSONDecodeError as e:
    print(f"✗ JSON structure error: {e}")
EOF

# Step 3: Test timestamp formats
echo -e "\n3. Testing various timestamp formats..."
TIMESTAMPS=(
    "2025-01-08T12:00:00.000Z"
    "2025-01-08T12:00:00Z"
    "2025-01-08 12:00:00"
    "2025-01-08T12:00:00.000000"
    "invalid-timestamp"
)

for ts in "${TIMESTAMPS[@]}"; do
    echo "Testing timestamp: $ts"
    python3 -c "
from datetime import datetime
try:
    dt = datetime.fromisoformat('$ts'.replace('Z', '+00:00'))
    print('  ✓ Valid')
except ValueError as e:
    print('  ✗ Invalid:', e)
"
done

# Step 4: Check backend validation
echo -e "\n4. Testing backend Pydantic validation..."
python3 << 'EOF'
import sys
sys.path.append('/path/to/backend')

try:
    from app.routers.onboarding import OnboardingResponse
    
    test_cases = [
        {
            "questionId": "q1",
            "question": "Test?",
            "response": "Test",
            "timestamp": "2025-01-08T12:00:00.000Z"
        },
        {
            "questionId": "q1",
            "question": "Test?",
            "response": "Test",
            "timestamp": None
        },
        {
            "questionId": "q1",
            "question": "Test?",
            "response": "Test",
            # Missing timestamp field
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            obj = OnboardingResponse(**case)
            print(f"Test case {i}: ✓ Valid")
        except Exception as e:
            print(f"Test case {i}: ✗ Invalid - {e}")
            
except ImportError as e:
    print(f"Could not import backend modules: {e}")
EOF

echo -e "\n=== DEBUG COMPLETE ==="
```

#### Common Fixes

```python
# Fix 1: Frontend timestamp standardization
# frontend/src/utils/dateUtils.ts

export const formatTimestampForAPI = (date: Date): string => {
  // Ensure consistent ISO format with milliseconds and UTC
  return date.toISOString();
};

export const createOnboardingResponse = (
  questionId: string,
  question: string, 
  response: string
) => {
  return {
    questionId,
    question,
    response,
    timestamp: formatTimestampForAPI(new Date())
  };
};

// Fix 2: Backend flexible timestamp parsing
# backend/app/routers/onboarding.py

from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, validator

class OnboardingResponse(BaseModel):
    questionId: str
    question: str  
    response: str
    timestamp: Optional[datetime] = None
    
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        if v is None:
            return None
            
        if isinstance(v, datetime):
            return v
            
        if isinstance(v, str):
            # Handle various string formats
            formats_to_try = [
                '%Y-%m-%dT%H:%M:%S.%fZ',     # 2025-01-08T12:00:00.000Z
                '%Y-%m-%dT%H:%M:%SZ',        # 2025-01-08T12:00:00Z
                '%Y-%m-%dT%H:%M:%S.%f',      # 2025-01-08T12:00:00.000
                '%Y-%m-%dT%H:%M:%S',         # 2025-01-08T12:00:00
                '%Y-%m-%d %H:%M:%S',         # 2025-01-08 12:00:00
            ]
            
            for fmt in formats_to_try:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
                    
            # If all formats fail, try fromisoformat
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"Invalid timestamp format: {v}")
                
        raise ValueError(f"Timestamp must be string or datetime, got {type(v)}")

# Fix 3: Enhanced error messages
@router.post("/response")
async def save_onboarding_response(
    response_data: OnboardingResponse,
    current_user: User = Depends(get_current_user_with_onboarding)
):
    try:
        # Validation is handled by Pydantic
        # Additional business logic validation
        if not response_data.questionId or not response_data.questionId.strip():
            raise HTTPException(
                status_code=400, 
                detail="questionId cannot be empty"
            )
            
        if not response_data.response or not response_data.response.strip():
            raise HTTPException(
                status_code=400,
                detail="response cannot be empty"
            )
        
        # Save to database...
        
    except ValueError as e:
        # Handle Pydantic validation errors
        raise HTTPException(
            status_code=422,
            detail=f"Data validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in save_onboarding_response: {str(e)}")
        raise handle_prisma_error(e, "save onboarding response")
```

### 3.2 Date Serialization Failure Debugging

#### Debug Script
```python
# backend/scripts/debug_date_serialization.py

import json
from datetime import datetime, timezone
from typing import Any, Dict

def debug_date_serialization():
    """Debug common date serialization issues"""
    
    print("=== DATE SERIALIZATION DEBUG ===")
    
    # Test various date formats
    test_dates = [
        datetime.now(),
        datetime.now(timezone.utc),
        datetime(2025, 1, 8, 12, 0, 0),
        datetime(2025, 1, 8, 12, 0, 0, 123456),  # With microseconds
    ]
    
    for i, test_date in enumerate(test_dates, 1):
        print(f"\nTest {i}: {test_date}")
        print(f"Type: {type(test_date)}")
        print(f"Timezone: {test_date.tzinfo}")
        
        # Test different serialization methods
        try:
            iso_format = test_date.isoformat()
            print(f"ISO format: {iso_format}")
        except Exception as e:
            print(f"ISO format error: {e}")
        
        try:
            json_serializable = {
                "timestamp": test_date,
                "iso_string": test_date.isoformat()
            }
            # This will fail for datetime objects
            json_str = json.dumps(json_serializable)
            print(f"JSON serialization: ✓")
        except TypeError as e:
            print(f"JSON serialization error: {e}")
            
            # Try with custom serializer
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object {obj} not JSON serializable")
            
            try:
                json_str = json.dumps(json_serializable, default=datetime_serializer)
                print(f"JSON with custom serializer: ✓")
                print(f"Result: {json_str}")
            except Exception as e:
                print(f"Custom serializer error: {e}")
    
    # Test parsing back
    print("\n=== PARSING TEST ===")
    iso_string = "2025-01-08T12:00:00.000Z"
    
    parsing_methods = [
        lambda s: datetime.fromisoformat(s.replace('Z', '+00:00')),
        lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ'),
    ]
    
    for i, method in enumerate(parsing_methods, 1):
        try:
            parsed = method(iso_string)
            print(f"Parsing method {i}: ✓ -> {parsed}")
        except Exception as e:
            print(f"Parsing method {i}: ✗ -> {e}")

if __name__ == "__main__":
    debug_date_serialization()
```

### 3.3 Database Schema Corruption Detection

#### Schema Validation Script
```python
# backend/scripts/validate_database_schema.py

import asyncio
from sqlalchemy import inspect, MetaData, Table
from app.database import engine
from app.models.user import User
from app.utils.prisma_client import prisma

async def validate_database_schema():
    """Validate database schema integrity"""
    
    print("=== DATABASE SCHEMA VALIDATION ===")
    
    # Check SQLAlchemy schema
    print("1. Validating SQLAlchemy schema...")
    inspector = inspect(engine)
    
    # Check if required tables exist
    required_tables = [
        'users', 'user_profiles', 'onboarding_responses',
        'conversations', 'conversation_categories'
    ]
    
    existing_tables = inspector.get_table_names()
    print(f"Existing tables: {existing_tables}")
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    if missing_tables:
        print(f"✗ Missing tables: {missing_tables}")
        return False
    else:
        print("✓ All required tables exist")
    
    # Check column integrity
    print("\n2. Validating column integrity...")
    
    # Users table validation
    user_columns = inspector.get_columns('users')
    user_column_names = [col['name'] for col in user_columns]
    
    required_user_columns = [
        'id', 'email', 'clerk_user_id', 'first_name', 'last_name',
        'is_active', 'created_at', 'onboarding_completed'
    ]
    
    missing_user_columns = [col for col in required_user_columns if col not in user_column_names]
    if missing_user_columns:
        print(f"✗ Missing user columns: {missing_user_columns}")
    else:
        print("✓ User table columns are complete")
    
    # Check constraints
    print("\n3. Validating constraints...")
    
    # Check primary keys
    user_pk = inspector.get_pk_constraint('users')
    if user_pk['constrained_columns'] != ['id']:
        print(f"✗ User table primary key issue: {user_pk}")
    else:
        print("✓ User table primary key is correct")
    
    # Check unique constraints
    user_unique_constraints = inspector.get_unique_constraints('users')
    email_unique = any('email' in constraint['column_names'] for constraint in user_unique_constraints)
    clerk_id_unique = any('clerk_user_id' in constraint['column_names'] for constraint in user_unique_constraints)
    
    if not email_unique:
        print("✗ Email uniqueness constraint missing")
    else:
        print("✓ Email uniqueness constraint exists")
        
    if not clerk_id_unique:
        print("✗ Clerk user ID uniqueness constraint missing")
    else:
        print("✓ Clerk user ID uniqueness constraint exists")
    
    # Test Prisma connection
    print("\n4. Validating Prisma connection...")
    try:
        await prisma.connect()
        
        # Test basic queries
        user_count = await prisma.user.count()
        print(f"✓ Prisma connection successful - {user_count} users found")
        
        # Test model relationships
        users_with_profiles = await prisma.user.find_many(
            include={'profile': True},
            take=1
        )
        print("✓ Prisma relationships working")
        
        await prisma.disconnect()
        
    except Exception as e:
        print(f"✗ Prisma validation error: {e}")
        return False
    
    print("\n=== SCHEMA VALIDATION COMPLETE ===")
    return True

async def detect_data_corruption():
    """Detect potential data corruption issues"""
    
    print("=== DATA CORRUPTION DETECTION ===")
    
    try:
        await prisma.connect()
        
        # Check for orphaned records
        print("1. Checking for orphaned records...")
        
        # Users without profiles who completed onboarding
        users_without_profiles = await prisma.user.find_many(
            where={
                'onboarding_completed': True,
                'profile': None
            }
        )
        
        if users_without_profiles:
            print(f"✗ Found {len(users_without_profiles)} users with completed onboarding but no profile")
            for user in users_without_profiles[:5]:  # Show first 5
                print(f"  User {user.id}: {user.email}")
        else:
            print("✓ No orphaned user profiles found")
        
        # Onboarding responses without users
        onboarding_responses = await prisma.onboardingresponse.find_many(
            include={'user': True}
        )
        
        orphaned_responses = [resp for resp in onboarding_responses if not resp.user]
        if orphaned_responses:
            print(f"✗ Found {len(orphaned_responses)} orphaned onboarding responses")
        else:
            print("✓ No orphaned onboarding responses found")
        
        # Check data consistency
        print("\n2. Checking data consistency...")
        
        # Users with invalid email formats
        users = await prisma.user.find_many()
        invalid_emails = []
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for user in users:
            if user.email and not re.match(email_pattern, user.email):
                invalid_emails.append(user)
        
        if invalid_emails:
            print(f"✗ Found {len(invalid_emails)} users with invalid email formats")
        else:
            print("✓ All user emails have valid formats")
        
        # Check for duplicate clerk_user_ids
        all_clerk_ids = [user.clerk_user_id for user in users if user.clerk_user_id]
        duplicate_clerk_ids = [id for id in set(all_clerk_ids) if all_clerk_ids.count(id) > 1]
        
        if duplicate_clerk_ids:
            print(f"✗ Found duplicate Clerk user IDs: {duplicate_clerk_ids}")
        else:
            print("✓ No duplicate Clerk user IDs found")
        
        await prisma.disconnect()
        
    except Exception as e:
        print(f"✗ Data corruption detection error: {e}")
        return False
    
    print("\n=== DATA CORRUPTION DETECTION COMPLETE ===")
    return True

if __name__ == "__main__":
    # Run schema validation
    schema_valid = asyncio.run(validate_database_schema())
    
    # Run corruption detection
    data_clean = asyncio.run(detect_data_corruption())
    
    if schema_valid and data_clean:
        print("\n✓ Database validation passed")
    else:
        print("\n✗ Database validation failed")
```

### 3.4 Validation Pipeline Failure Diagnosis

#### Pipeline Debug Script
```python
# backend/scripts/debug_validation_pipeline.py

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from app.routers.onboarding import OnboardingResponse, OnboardingData
from app.utils.error_handling import handle_prisma_error

class ValidationPipelineDebugger:
    """Debug the complete validation pipeline"""
    
    def __init__(self):
        self.debug_steps = []
    
    def log_step(self, step: str, success: bool, details: str = ""):
        """Log a validation step"""
        self.debug_steps.append({
            'step': step,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow()
        })
        
        status = "✓" if success else "✗"
        print(f"{status} {step}: {details}")
    
    async def debug_full_pipeline(self, test_data: Dict[str, Any]):
        """Debug the complete validation pipeline"""
        
        print("=== VALIDATION PIPELINE DEBUG ===")
        print(f"Test data: {test_data}")
        
        # Step 1: JSON parsing
        try:
            import json
            json_str = json.dumps(test_data)
            parsed_data = json.loads(json_str)
            self.log_step("JSON Parsing", True, "Data successfully serialized/deserialized")
        except Exception as e:
            self.log_step("JSON Parsing", False, f"Error: {e}")
            return
        
        # Step 2: Pydantic model validation
        try:
            if 'responses' in test_data:
                # Validating OnboardingData
                onboarding_data = OnboardingData(**test_data)
                self.log_step("Pydantic Model Validation (OnboardingData)", True, 
                             f"Created with {len(onboarding_data.responses)} responses")
            else:
                # Validating OnboardingResponse
                response = OnboardingResponse(**test_data)
                self.log_step("Pydantic Model Validation (OnboardingResponse)", True,
                             f"Response for question {response.questionId}")
        except Exception as e:
            self.log_step("Pydantic Model Validation", False, f"Error: {e}")
            return
        
        # Step 3: Business logic validation
        try:
            if 'questionId' in test_data:
                if not test_data['questionId'] or not test_data['questionId'].strip():
                    raise ValueError("questionId cannot be empty")
                
                if not test_data.get('response') or not test_data['response'].strip():
                    raise ValueError("response cannot be empty")
            
            self.log_step("Business Logic Validation", True, "All business rules passed")
        except Exception as e:
            self.log_step("Business Logic Validation", False, f"Error: {e}")
            return
        
        # Step 4: Database constraints simulation
        try:
            # Simulate database constraint checking
            if 'questionId' in test_data:
                # Check for potential duplicates (simulated)
                if test_data['questionId'] == "duplicate_test":
                    raise ValueError("Simulated duplicate constraint violation")
                
                # Check foreign key constraints (simulated)
                if test_data.get('user_id') == 999:
                    raise ValueError("Simulated foreign key constraint violation")
            
            self.log_step("Database Constraints", True, "All constraints satisfied")
        except Exception as e:
            self.log_step("Database Constraints", False, f"Error: {e}")
            return
        
        # Step 5: Serialization for storage
        try:
            if 'responses' in test_data:
                data_obj = OnboardingData(**test_data)
            else:
                data_obj = OnboardingResponse(**test_data)
            
            # Test serialization
            serialized = data_obj.dict()
            
            # Handle datetime serialization
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            import json
            json_serialized = json.dumps(serialized, default=serialize_datetime)
            
            self.log_step("Serialization for Storage", True, "Object successfully serialized")
        except Exception as e:
            self.log_step("Serialization for Storage", False, f"Error: {e}")
            return
        
        print(f"\n=== PIPELINE DEBUG COMPLETE ===")
        print(f"Total steps: {len(self.debug_steps)}")
        successful_steps = sum(1 for step in self.debug_steps if step['success'])
        print(f"Successful steps: {successful_steps}/{len(self.debug_steps)}")
        
        return successful_steps == len(self.debug_steps)
    
    def generate_debug_report(self) -> str:
        """Generate a detailed debug report"""
        
        report = "\n=== VALIDATION PIPELINE DEBUG REPORT ===\n"
        report += f"Generated: {datetime.utcnow()}\n"
        report += f"Total validation steps: {len(self.debug_steps)}\n\n"
        
        for i, step in enumerate(self.debug_steps, 1):
            status = "PASS" if step['success'] else "FAIL"
            report += f"{i}. {step['step']}: {status}\n"
            if step['details']:
                report += f"   Details: {step['details']}\n"
            report += f"   Timestamp: {step['timestamp']}\n\n"
        
        # Summary
        failed_steps = [step for step in self.debug_steps if not step['success']]
        if failed_steps:
            report += "FAILED STEPS:\n"
            for step in failed_steps:
                report += f"- {step['step']}: {step['details']}\n"
        else:
            report += "✓ All validation steps passed successfully\n"
        
        return report

async def run_validation_tests():
    """Run various validation test scenarios"""
    
    debugger = ValidationPipelineDebugger()
    
    # Test cases
    test_cases = [
        {
            "name": "Valid OnboardingResponse",
            "data": {
                "questionId": "q1",
                "question": "What is your career goal?",
                "response": "Software Engineer",
                "timestamp": "2025-01-08T12:00:00.000Z"
            }
        },
        {
            "name": "OnboardingResponse without timestamp",
            "data": {
                "questionId": "q2",
                "question": "What are your strengths?",
                "response": "Problem solving"
            }
        },
        {
            "name": "Invalid timestamp format",
            "data": {
                "questionId": "q3",
                "question": "Test question",
                "response": "Test response",
                "timestamp": "invalid-timestamp"
            }
        },
        {
            "name": "Empty required fields",
            "data": {
                "questionId": "",
                "question": "Test question",
                "response": ""
            }
        },
        {
            "name": "Valid OnboardingData",
            "data": {
                "responses": [
                    {
                        "questionId": "q1",
                        "question": "Career goal?",
                        "response": "Engineer"
                    }
                ],
                "psychProfile": {
                    "personality": "INTJ"
                }
            }
        }
    ]
    
    print("=== RUNNING VALIDATION TEST SUITE ===\n")
    
    results = {}
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print("-" * 50)
        
        debugger = ValidationPipelineDebugger()  # Fresh debugger for each test
        success = await debugger.debug_full_pipeline(test_case['data'])
        
        results[test_case['name']] = {
            'success': success,
            'report': debugger.generate_debug_report()
        }
        
        print(f"Result: {'PASS' if success else 'FAIL'}\n")
    
    # Generate summary report
    print("=== TEST SUMMARY ===")
    for test_name, result in results.items():
        status = "PASS" if result['success'] else "FAIL"
        print(f"{test_name}: {status}")
    
    # Save detailed reports
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    for test_name, result in results.items():
        filename = f"/tmp/validation_debug_{test_name.replace(' ', '_')}_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(result['report'])
        print(f"Detailed report saved: {filename}")

if __name__ == "__main__":
    asyncio.run(run_validation_tests())
```

---

## 4. Testing Automation

### 4.1 Automated Test Execution Commands

#### Test Runner Script
```bash
#!/bin/bash
# scripts/run_onboarding_tests.sh

set -e  # Exit on any error

echo "=== ONBOARDING AUTOMATED TEST SUITE ==="
echo "Started: $(date)"

# Configuration
TEST_ENV="${TEST_ENV:-test}"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-80}"
TIMEOUT="${TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Set up test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Export test environment variables
    export DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/test_orientor"
    export CLERK_SECRET_KEY="test_clerk_key"
    export ENVIRONMENT="test"
    
    # Create test database if it doesn't exist
    if ! psql -lqt | cut -d \| -f 1 | grep -qw test_orientor; then
        log_info "Creating test database..."
        createdb test_orientor
    fi
    
    # Run database migrations
    log_info "Running database migrations..."
    cd backend && alembic upgrade head
    
    log_info "Test environment setup complete"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    cd backend
    
    # Run onboarding-specific unit tests
    python -m pytest tests/test_onboarding_serialization.py \
                     tests/test_onboarding_validation.py \
                     -v \
                     --cov=app.routers.onboarding \
                     --cov=app.services \
                     --cov-report=xml \
                     --cov-report=html \
                     --cov-report=term \
                     --timeout=${TIMEOUT} \
                     --junit-xml=test-results/unit-tests.xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_info "Unit tests passed"
    else
        log_error "Unit tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    # Check coverage
    coverage_percentage=$(coverage report | tail -n 1 | awk '{print $4}' | sed 's/%//')
    if [ $(echo "$coverage_percentage >= $COVERAGE_THRESHOLD" | bc) -eq 1 ]; then
        log_info "Coverage threshold met: ${coverage_percentage}%"
    else
        log_warn "Coverage below threshold: ${coverage_percentage}% (required: ${COVERAGE_THRESHOLD}%)"
    fi
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    cd backend
    
    # Start test server in background
    log_info "Starting test server..."
    python -m app.main --port 8001 --env test &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Check if server is running
    if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_error "Test server failed to start"
        kill $SERVER_PID 2>/dev/null || true
        return 1
    fi
    
    # Run integration tests
    python -m pytest tests/test_onboarding_integration.py \
                     -v \
                     --timeout=${TIMEOUT} \
                     --junit-xml=test-results/integration-tests.xml
    
    local exit_code=$?
    
    # Stop test server
    kill $SERVER_PID 2>/dev/null || true
    
    if [ $exit_code -eq 0 ]; then
        log_info "Integration tests passed"
    else
        log_error "Integration tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run end-to-end tests
run_e2e_tests() {
    log_info "Running end-to-end tests..."
    
    # Install Playwright browsers if needed
    if [ ! -d "$HOME/.cache/ms-playwright" ]; then
        log_info "Installing Playwright browsers..."
        cd frontend && npx playwright install
    fi
    
    # Start both backend and frontend
    log_info "Starting backend server..."
    cd backend && python -m app.main --port 8000 --env test &
    BACKEND_PID=$!
    
    log_info "Starting frontend server..."
    cd frontend && npm run dev &
    FRONTEND_PID=$!
    
    # Wait for servers to start
    sleep 10
    
    # Check if servers are running
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_error "Backend server failed to start"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        return 1
    fi
    
    if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_error "Frontend server failed to start"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        return 1
    fi
    
    # Run E2E tests
    cd backend
    python -m pytest tests/test_onboarding_e2e.py \
                     -v \
                     --timeout=$((TIMEOUT * 2)) \
                     --junit-xml=test-results/e2e-tests.xml
    
    local exit_code=$?
    
    # Stop servers
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    
    if [ $exit_code -eq 0 ]; then
        log_info "E2E tests passed"
    else
        log_error "E2E tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run database tests
run_database_tests() {
    log_info "Running database constraint tests..."
    
    cd backend
    python -m pytest tests/test_onboarding_database_constraints.py \
                     -v \
                     --timeout=${TIMEOUT} \
                     --junit-xml=test-results/database-tests.xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_info "Database tests passed"
    else
        log_error "Database tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run performance tests
run_performance_tests() {
    log_info "Running performance tests..."
    
    cd backend
    
    # Performance test with load simulation
    python -c "
import asyncio
import time
import aiohttp
import json
from concurrent.futures import ThreadPoolExecutor

async def performance_test():
    print('Starting performance test...')
    
    test_data = {
        'questionId': 'perf_test',
        'question': 'Performance test question?',
        'response': 'Performance test response'
    }
    
    start_time = time.time()
    concurrent_requests = 50
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrent_requests):
            task = session.post(
                'http://localhost:8001/onboarding/response',
                json=test_data,
                headers={'Authorization': 'Bearer fake_token'}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    successful_requests = sum(1 for r in results if not isinstance(r, Exception))
    requests_per_second = concurrent_requests / duration
    
    print(f'Performance Test Results:')
    print(f'  Total requests: {concurrent_requests}')
    print(f'  Successful: {successful_requests}')
    print(f'  Duration: {duration:.2f}s')
    print(f'  Requests/second: {requests_per_second:.2f}')
    
    # Performance thresholds
    if requests_per_second < 10:
        print('❌ Performance test failed: Too slow')
        return False
    else:
        print('✅ Performance test passed')
        return True

asyncio.run(performance_test())
"
    
    if [ $? -eq 0 ]; then
        log_info "Performance tests passed"
    else
        log_error "Performance tests failed"
        return 1
    fi
}

# Generate test report
generate_test_report() {
    log_info "Generating test report..."
    
    cd backend
    
    # Create test results directory if it doesn't exist
    mkdir -p test-results
    
    # Generate HTML test report
    python -c "
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import os

def parse_junit_xml(filename):
    if not os.path.exists(filename):
        return {'tests': 0, 'failures': 0, 'errors': 0, 'time': 0}
    
    tree = ET.parse(filename)
    root = tree.getroot()
    
    return {
        'tests': int(root.get('tests', 0)),
        'failures': int(root.get('failures', 0)),
        'errors': int(root.get('errors', 0)),
        'time': float(root.get('time', 0))
    }

# Parse all test results
test_files = [
    'test-results/unit-tests.xml',
    'test-results/integration-tests.xml',
    'test-results/e2e-tests.xml',
    'test-results/database-tests.xml'
]

results = {}
for filename in test_files:
    test_type = filename.split('/')[-1].replace('.xml', '').replace('-tests', '')
    results[test_type] = parse_junit_xml(filename)

# Generate summary
total_tests = sum(r['tests'] for r in results.values())
total_failures = sum(r['failures'] for r in results.values())
total_errors = sum(r['errors'] for r in results.values())
total_time = sum(r['time'] for r in results.values())

report = {
    'timestamp': datetime.utcnow().isoformat(),
    'summary': {
        'total_tests': total_tests,
        'total_failures': total_failures,
        'total_errors': total_errors,
        'total_time': total_time,
        'success_rate': (total_tests - total_failures - total_errors) / max(total_tests, 1) * 100
    },
    'details': results
}

# Save JSON report
with open('test-results/test-summary.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f'Test Summary:')
print(f'  Total tests: {total_tests}')
print(f'  Failures: {total_failures}')
print(f'  Errors: {total_errors}')
print(f'  Success rate: {report[\"summary\"][\"success_rate\"]:.1f}%')
print(f'  Total time: {total_time:.2f}s')

if total_failures > 0 or total_errors > 0:
    exit(1)
else:
    exit(0)
"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_info "All tests passed! 🎉"
    else
        log_error "Some tests failed. Check test-results/ for details."
    fi
    
    return $exit_code
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Create results directory
    mkdir -p backend/test-results
    
    # Run test suite
    setup_test_environment || exit 1
    run_unit_tests || exit 1
    run_integration_tests || exit 1
    run_database_tests || exit 1
    run_e2e_tests || exit 1
    run_performance_tests || exit 1
    
    # Generate report
    generate_test_report
    local test_exit_code=$?
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "Test suite completed in ${duration}s"
    
    exit $test_exit_code
}

# Handle script arguments
case "${1:-all}" in
    "unit")
        setup_test_environment && run_unit_tests
        ;;
    "integration")
        setup_test_environment && run_integration_tests
        ;;
    "e2e")
        setup_test_environment && run_e2e_tests
        ;;
    "database")
        setup_test_environment && run_database_tests
        ;;
    "performance")
        setup_test_environment && run_performance_tests
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 [unit|integration|e2e|database|performance|all]"
        exit 1
        ;;
esac
```

### 4.2 Continuous Integration Setup

#### GitHub Actions Workflow
```yaml
# .github/workflows/onboarding-tests.yml
name: Onboarding System Tests

on:
  push:
    branches: [ main, api, develop ]
    paths:
      - 'backend/app/routers/onboarding.py'
      - 'backend/app/services/**'
      - 'frontend/src/components/onboarding/**'
      - 'frontend/src/services/onboardingService.ts'
  pull_request:
    branches: [ main ]
    paths:
      - 'backend/app/routers/onboarding.py'
      - 'backend/app/services/**'
      - 'frontend/src/components/onboarding/**'
      - 'frontend/src/services/onboardingService.ts'

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  POSTGRES_VERSION: '15'

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_orientor
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest-cov pytest-timeout pytest-asyncio
    
    - name: Set up test environment
      run: |
        echo "DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_orientor" >> $GITHUB_ENV
        echo "CLERK_SECRET_KEY=test_key" >> $GITHUB_ENV
        echo "ENVIRONMENT=test" >> $GITHUB_ENV
    
    - name: Run database migrations
      run: |
        cd backend
        alembic upgrade head
    
    - name: Run unit tests
      run: |
        cd backend
        python -m pytest tests/test_onboarding_serialization.py \
                         tests/test_onboarding_validation.py \
                         -v \
                         --cov=app.routers.onboarding \
                         --cov=app.services \
                         --cov-report=xml \
                         --cov-report=html \
                         --cov-report=term \
                         --timeout=300 \
                         --junit-xml=test-results/unit-tests.xml
    
    - name: Run integration tests
      run: |
        cd backend
        python -m app.main --port 8001 --env test &
        sleep 5
        python -m pytest tests/test_onboarding_integration.py \
                         -v \
                         --timeout=300 \
                         --junit-xml=test-results/integration-tests.xml
        kill %1 || true
    
    - name: Run database constraint tests
      run: |
        cd backend
        python -m pytest tests/test_onboarding_database_constraints.py \
                         -v \
                         --timeout=300 \
                         --junit-xml=test-results/database-tests.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage.xml
        flags: backend
        name: backend-coverage
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: backend-test-results
        path: backend/test-results/

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm run test -- --coverage --watchAll=false
    
    - name: Upload frontend coverage
      uses: codecov/codecov-action@v3
      with:
        file: frontend/coverage/lcov.info
        flags: frontend
        name: frontend-coverage

  test-e2e:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_orientor
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd backend && pip install -r requirements.txt
        cd ../frontend && npm ci
    
    - name: Install Playwright
      run: |
        cd frontend
        npx playwright install --with-deps
    
    - name: Set up test environment
      run: |
        echo "DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_orientor" >> $GITHUB_ENV
        echo "CLERK_SECRET_KEY=test_key" >> $GITHUB_ENV
        echo "ENVIRONMENT=test" >> $GITHUB_ENV
    
    - name: Run database migrations
      run: |
        cd backend
        alembic upgrade head
    
    - name: Start backend server
      run: |
        cd backend
        python -m app.main --port 8000 --env test &
        sleep 5
    
    - name: Start frontend server
      run: |
        cd frontend
        npm run dev &
        sleep 10
    
    - name: Wait for servers
      run: |
        timeout 30 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
        timeout 30 bash -c 'until curl -f http://localhost:3000; do sleep 2; done'
    
    - name: Run E2E tests
      run: |
        cd backend
        python -m pytest tests/test_onboarding_e2e.py \
                         -v \
                         --timeout=600 \
                         --junit-xml=test-results/e2e-tests.xml
    
    - name: Upload E2E test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: e2e-test-results
        path: |
          backend/test-results/
          frontend/playwright-report/

  test-performance:
    runs-on: ubuntu-latest
    needs: [test-backend]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_orientor
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install locust aiohttp
    
    - name: Set up test environment
      run: |
        echo "DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_orientor" >> $GITHUB_ENV
        echo "CLERK_SECRET_KEY=test_key" >> $GITHUB_ENV
        echo "ENVIRONMENT=test" >> $GITHUB_ENV
    
    - name: Run database migrations
      run: |
        cd backend
        alembic upgrade head
    
    - name: Start backend server
      run: |
        cd backend
        python -m app.main --port 8001 --env test &
        sleep 5
    
    - name: Run performance tests
      run: |
        cd backend
        python -c "
import asyncio
import aiohttp
import time
import json

async def performance_test():
    test_data = {
        'questionId': 'perf_test',
        'question': 'Performance test question?',
        'response': 'Performance test response'
    }
    
    concurrent_requests = 100
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrent_requests):
            task = session.post(
                'http://localhost:8001/onboarding/response',
                json=test_data,
                headers={'Authorization': 'Bearer test_token'}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    duration = time.time() - start_time
    successful = sum(1 for r in results if not isinstance(r, Exception))
    rps = concurrent_requests / duration
    
    print(f'Performance Results:')
    print(f'  Requests: {concurrent_requests}')
    print(f'  Successful: {successful}')
    print(f'  Duration: {duration:.2f}s')
    print(f'  RPS: {rps:.2f}')
    
    # Performance thresholds
    assert rps >= 10, f'Performance too slow: {rps} RPS'
    assert successful >= concurrent_requests * 0.95, f'Too many failures: {successful}/{concurrent_requests}'

asyncio.run(performance_test())
"

  generate-report:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, test-e2e, test-performance]
    if: always()
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Download all test results
      uses: actions/download-artifact@v3
    
    - name: Generate consolidated report
      run: |
        python -c "
import json
import os
from datetime import datetime

# Collect all test results
results = {
    'timestamp': datetime.utcnow().isoformat(),
    'workflow_run': '${{ github.run_number }}',
    'branch': '${{ github.ref_name }}',
    'commit': '${{ github.sha }}',
    'tests': {}
}

# Parse test results (simplified)
for test_type in ['backend', 'frontend', 'e2e', 'performance']:
    results['tests'][test_type] = {
        'status': 'completed',
        'artifacts': f'{test_type}-test-results'
    }

# Save report
with open('test-report.json', 'w') as f:
    json.dump(results, f, indent=2)

print('Consolidated test report generated')
"
    
    - name: Upload consolidated report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: test-report.json
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          
          let comment = '## 🧪 Onboarding System Test Results\n\n';
          comment += `- **Backend Tests**: ${{ needs.test-backend.result }}\n`;
          comment += `- **Frontend Tests**: ${{ needs.test-frontend.result }}\n`;
          comment += `- **E2E Tests**: ${{ needs.test-e2e.result }}\n`;
          comment += `- **Performance Tests**: ${{ needs.test-performance.result }}\n\n`;
          comment += `**Workflow Run**: #${{ github.run_number }}\n`;
          comment += `**Commit**: ${{ github.sha }}\n`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### 4.3 Performance Regression Testing

#### Performance Test Suite
```python
# backend/tests/test_onboarding_performance.py
import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import json

class OnboardingPerformanceTests:
    """Performance regression tests for onboarding system"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.performance_thresholds = {
            'single_response_time': 1.0,  # seconds
            'bulk_save_time': 5.0,  # seconds
            'completion_time': 3.0,  # seconds
            'concurrent_requests_rps': 10,  # requests per second
            'memory_usage_mb': 100,  # MB
        }
    
    async def test_single_response_performance(self):
        """Test single response save performance"""
        
        test_data = {
            "questionId": "perf_q1",
            "question": "Performance test question?",
            "response": "Performance test response",
            "timestamp": "2025-01-08T12:00:00.000Z"
        }
        
        times = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(10):  # 10 samples
                start_time = time.time()
                
                try:
                    async with session.post(
                        f"{self.base_url}/onboarding/response",
                        json=test_data,
                        headers={"Authorization": "Bearer test_token"}
                    ) as response:
                        await response.json()
                        
                    end_time = time.time()
                    times.append(end_time - start_time)
                    
                except Exception as e:
                    pytest.fail(f"Request failed: {e}")
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        print(f"Single response performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")
        
        # Assertions
        assert avg_time < self.performance_thresholds['single_response_time'], \
            f"Average response time too slow: {avg_time:.3f}s"
        
        assert p95_time < self.performance_thresholds['single_response_time'] * 2, \
            f"95th percentile too slow: {p95_time:.3f}s"
    
    async def test_bulk_operations_performance(self):
        """Test bulk operations performance"""
        
        # Prepare bulk data
        responses = []
        for i in range(20):  # 20 responses
            responses.append({
                "questionId": f"bulk_q{i}",
                "question": f"Bulk question {i}?",
                "response": f"Bulk response {i}",
                "timestamp": "2025-01-08T12:00:00.000Z"
            })
        
        completion_data = {
            "responses": responses,
            "psychProfile": {
                "personality": "INTJ",
                "strengths": ["analytical", "strategic"],
                "interests": ["technology", "problem-solving"]
            }
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/onboarding/complete",
                    json=completion_data,
                    headers={"Authorization": "Bearer test_token"}
                ) as response:
                    result = await response.json()
                    
            except Exception as e:
                pytest.fail(f"Bulk operation failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Bulk operations performance:")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Responses processed: {len(responses)}")
        print(f"  Rate: {len(responses)/duration:.2f} responses/second")
        
        assert duration < self.performance_thresholds['bulk_save_time'], \
            f"Bulk operation too slow: {duration:.3f}s"
    
    async def test_concurrent_requests_performance(self):
        """Test concurrent requests performance"""
        
        test_data = {
            "questionId": "concurrent_test",
            "question": "Concurrent test question?",
            "response": "Concurrent test response",
            "timestamp": "2025-01-08T12:00:00.000Z"
        }
        
        concurrent_requests = 50
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for i in range(concurrent_requests):
                task = session.post(
                    f"{self.base_url}/onboarding/response",
                    json=test_data,
                    headers={"Authorization": "Bearer test_token"}
                )
                tasks.append(task)
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                pytest.fail(f"Concurrent requests failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Count successful requests
        successful_requests = sum(
            1 for result in results 
            if not isinstance(result, Exception) and hasattr(result, 'status') and result.status < 400
        )
        
        requests_per_second = concurrent_requests / duration
        success_rate = successful_requests / concurrent_requests * 100
        
        print(f"Concurrent requests performance:")
        print(f"  Total requests: {concurrent_requests}")
        print(f"  Successful: {successful_requests}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Requests per second: {requests_per_second:.2f}")
        
        assert requests_per_second >= self.performance_thresholds['concurrent_requests_rps'], \
            f"Concurrent performance too slow: {requests_per_second:.2f} RPS"
        
        assert success_rate >= 95, f"Success rate too low: {success_rate:.1f}%"
    
    def test_memory_usage_performance(self):
        """Test memory usage during operations"""
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Measure initial memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate heavy onboarding operations
        large_responses = []
        for i in range(1000):  # Create 1000 responses
            response_data = {
                "questionId": f"memory_test_{i}",
                "question": f"Memory test question {i}? " + "x" * 100,  # Longer text
                "response": f"Memory test response {i} " + "y" * 200,  # Even longer response
                "timestamp": "2025-01-08T12:00:00.000Z"
            }
            large_responses.append(response_data)
        
        # Simulate processing
        processed_data = []
        for response in large_responses:
            # Simulate validation and processing
            processed = {
                **response,
                "processed": True,
                "validation_result": "passed",
                "metadata": {
                    "processing_time": time.time(),
                    "validator": "test_validator"
                }
            }
            processed_data.append(processed)
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Clean up and measure final memory
        del large_responses, processed_data
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = peak_memory - initial_memory
        memory_leak = final_memory - initial_memory
        
        print(f"Memory usage performance:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Peak memory: {peak_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        print(f"  Potential leak: {memory_leak:.2f} MB")
        
        assert memory_increase < self.performance_thresholds['memory_usage_mb'], \
            f"Memory usage too high: {memory_increase:.2f} MB"
        
        assert memory_leak < 10, f"Potential memory leak: {memory_leak:.2f} MB"
    
    async def run_performance_regression_suite(self):
        """Run complete performance regression test suite"""
        
        print("=== ONBOARDING PERFORMANCE REGRESSION SUITE ===")
        
        test_results = {}
        
        try:
            # Single response performance
            await self.test_single_response_performance()
            test_results['single_response'] = 'PASS'
        except Exception as e:
            test_results['single_response'] = f'FAIL: {e}'
        
        try:
            # Bulk operations performance
            await self.test_bulk_operations_performance()
            test_results['bulk_operations'] = 'PASS'
        except Exception as e:
            test_results['bulk_operations'] = f'FAIL: {e}'
        
        try:
            # Concurrent requests performance
            await self.test_concurrent_requests_performance()
            test_results['concurrent_requests'] = 'PASS'
        except Exception as e:
            test_results['concurrent_requests'] = f'FAIL: {e}'
        
        try:
            # Memory usage performance
            self.test_memory_usage_performance()
            test_results['memory_usage'] = 'PASS'
        except Exception as e:
            test_results['memory_usage'] = f'FAIL: {e}'
        
        # Generate performance report
        print("\n=== PERFORMANCE TEST RESULTS ===")
        for test_name, result in test_results.items():
            status = "✓" if result == 'PASS' else "✗"
            print(f"{status} {test_name}: {result}")
        
        # Overall result
        failed_tests = [name for name, result in test_results.items() if result != 'PASS']
        if failed_tests:
            print(f"\n❌ Performance regression detected in: {', '.join(failed_tests)}")
            return False
        else:
            print(f"\n✅ All performance tests passed")
            return True

# Pytest integration
@pytest.mark.asyncio
async def test_onboarding_performance_regression():
    """Run performance regression tests"""
    
    performance_tester = OnboardingPerformanceTests()
    success = await performance_tester.run_performance_regression_suite()
    
    assert success, "Performance regression tests failed"

if __name__ == "__main__":
    # Run performance tests directly
    asyncio.run(OnboardingPerformanceTests().run_performance_regression_suite())
```

### 4.4 Error Monitoring and Alerting Setup

#### Monitoring Configuration
```python
# backend/app/monitoring/onboarding_monitor.py
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass
import smtplib
from email.mime.text import MimeText
import json

@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    error_rate_per_hour: int = 10
    validation_error_rate: int = 5
    database_error_rate: int = 3
    response_time_p95_ms: float = 2000
    concurrent_failure_rate: float = 5.0  # percentage

class OnboardingMonitor:
    """Monitor onboarding system health and performance"""
    
    def __init__(self, alert_thresholds: AlertThreshold = None):
        self.thresholds = alert_thresholds or AlertThreshold()
        self.logger = logging.getLogger("onboarding_monitor")
        
        # Metrics storage (in production, use proper metrics store)
        self.metrics = {
            'errors': [],
            'response_times': [],
            'requests': [],
            'validations': []
        }
    
    def record_request(self, endpoint: str, response_time_ms: float, status_code: int):
        """Record a request metric"""
        
        request_data = {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'status_code': status_code,
            'success': status_code < 400
        }
        
        self.metrics['requests'].append(request_data)
        self.metrics['response_times'].append(response_time_ms)
        
        # Keep only last 1000 entries
        if len(self.metrics['requests']) > 1000:
            self.metrics['requests'] = self.metrics['requests'][-1000:]
        
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error occurrence"""
        
        error_data = {
            'timestamp': datetime.utcnow(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        self.metrics['errors'].append(error_data)
        
        # Keep only last 500 errors
        if len(self.metrics['errors']) > 500:
            self.metrics['errors'] = self.metrics['errors'][-500:]
        
        # Log error
        self.logger.error(f"Onboarding error: {error_type} - {error_message}", extra=error_data)
    
    def record_validation_error(self, field: str, error_message: str, user_data: Dict[str, Any] = None):
        """Record a validation error"""
        
        validation_data = {
            'timestamp': datetime.utcnow(),
            'field': field,
            'error_message': error_message,
            'user_data': user_data or {}
        }
        
        self.metrics['validations'].append(validation_data)
        
        # Keep only last 200 validation errors
        if len(self.metrics['validations']) > 200:
            self.metrics['validations'] = self.metrics['validations'][-200:]
    
    def check_alert_conditions(self) -> List[Dict[str, Any]]:
        """Check if any alert conditions are met"""
        
        alerts = []
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Check error rate in last hour
        recent_errors = [
            error for error in self.metrics['errors']
            if error['timestamp'] > one_hour_ago
        ]
        
        if len(recent_errors) > self.thresholds.error_rate_per_hour:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"High error rate: {len(recent_errors)} errors in last hour",
                'threshold': self.thresholds.error_rate_per_hour,
                'actual': len(recent_errors),
                'details': recent_errors[-5:]  # Last 5 errors
            })
        
        # Check validation error rate
        recent_validation_errors = [
            error for error in self.metrics['validations']
            if error['timestamp'] > one_hour_ago
        ]
        
        if len(recent_validation_errors) > self.thresholds.validation_error_rate:
            alerts.append({
                'type': 'high_validation_error_rate',
                'severity': 'medium',
                'message': f"High validation error rate: {len(recent_validation_errors)} in last hour",
                'threshold': self.thresholds.validation_error_rate,
                'actual': len(recent_validation_errors),
                'details': recent_validation_errors[-3:]
            })
        
        # Check database error rate
        recent_db_errors = [
            error for error in recent_errors
            if 'database' in error['error_type'].lower() or 'prisma' in error['error_type'].lower()
        ]
        
        if len(recent_db_errors) > self.thresholds.database_error_rate:
            alerts.append({
                'type': 'high_database_error_rate',
                'severity': 'critical',
                'message': f"High database error rate: {len(recent_db_errors)} in last hour",
                'threshold': self.thresholds.database_error_rate,
                'actual': len(recent_db_errors),
                'details': recent_db_errors
            })
        
        # Check response time performance
        recent_response_times = [
            rt for rt in self.metrics['response_times'][-100:]  # Last 100 requests
            if rt is not None
        ]
        
        if recent_response_times:
            # Calculate 95th percentile
            sorted_times = sorted(recent_response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
            
            if p95_time > self.thresholds.response_time_p95_ms:
                alerts.append({
                    'type': 'slow_response_time',
                    'severity': 'medium',
                    'message': f"Slow response times: P95 = {p95_time:.1f}ms",
                    'threshold': self.thresholds.response_time_p95_ms,
                    'actual': p95_time,
                    'details': {
                        'sample_size': len(recent_response_times),
                        'avg_time': sum(recent_response_times) / len(recent_response_times)
                    }
                })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send alerts via email or other channels"""
        
        if not alerts:
            return
        
        # Group alerts by severity
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        high_alerts = [a for a in alerts if a['severity'] == 'high']
        medium_alerts = [a for a in alerts if a['severity'] == 'medium']
        
        # Send email alert
        subject = f"Orientor Onboarding System Alert - {len(alerts)} issues detected"
        
        body = f"""
ORIENTOR ONBOARDING SYSTEM ALERT
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

SUMMARY:
- Critical alerts: {len(critical_alerts)}
- High severity: {len(high_alerts)}
- Medium severity: {len(medium_alerts)}

"""
        
        for alert in alerts:
            body += f"""
ALERT: {alert['type'].upper()}
Severity: {alert['severity'].upper()}
Message: {alert['message']}
Threshold: {alert.get('threshold', 'N/A')}
Actual: {alert.get('actual', 'N/A')}

"""
            if alert.get('details'):
                body += f"Details: {json.dumps(alert['details'], indent=2, default=str)}\n"
        
        body += """
Please investigate the onboarding system immediately.

View logs: tail -f /var/log/orientor/onboarding.log
Check metrics: http://your-monitoring-dashboard.com/onboarding
"""
        
        self._send_email_alert(subject, body)
        
        # Log alerts
        for alert in alerts:
            self.logger.critical(f"ALERT: {alert['type']} - {alert['message']}")
    
    def _send_email_alert(self, subject: str, body: str):
        """Send email alert"""
        
        # Email configuration (should be in environment variables)
        smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
        smtp_port = 587
        sender_email = "alerts@orientor.com"  # Replace with your email
        sender_password = "your_app_password"  # Use app password or OAuth
        recipient_emails = ["admin@orientor.com", "dev-team@orientor.com"]
        
        try:
            msg = MimeText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipient_emails)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Alert email sent to {recipient_emails}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate a health report"""
        
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Recent metrics
        recent_requests = [
            req for req in self.metrics['requests']
            if req['timestamp'] > one_hour_ago
        ]
        
        recent_errors = [
            error for error in self.metrics['errors']
            if error['timestamp'] > one_hour_ago
        ]
        
        # Calculate statistics
        total_requests = len(recent_requests)
        successful_requests = sum(1 for req in recent_requests if req['success'])
        error_rate = (len(recent_errors) / max(total_requests, 1)) * 100
        
        if recent_requests:
            avg_response_time = sum(req['response_time_ms'] for req in recent_requests) / len(recent_requests)
        else:
            avg_response_time = 0
        
        health_status = "healthy"
        if len(recent_errors) > self.thresholds.error_rate_per_hour:
            health_status = "unhealthy"
        elif len(recent_errors) > self.thresholds.error_rate_per_hour // 2:
            health_status = "degraded"
        
        return {
            'timestamp': now.isoformat(),
            'status': health_status,
            'metrics': {
                'requests_last_hour': total_requests,
                'successful_requests': successful_requests,
                'error_rate_percent': error_rate,
                'avg_response_time_ms': avg_response_time,
                'errors_last_hour': len(recent_errors)
            },
            'thresholds': {
                'max_errors_per_hour': self.thresholds.error_rate_per_hour,
                'max_response_time_ms': self.thresholds.response_time_p95_ms
            },
            'recent_errors': recent_errors[-3:] if recent_errors else []
        }

# Monitoring service instance
onboarding_monitor = OnboardingMonitor()

# FastAPI middleware for automatic monitoring
from fastapi import Request, Response
import time

async def monitoring_middleware(request: Request, call_next):
    """Middleware to automatically monitor onboarding requests"""
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record request
        response_time_ms = (time.time() - start_time) * 1000
        
        if request.url.path.startswith('/onboarding'):
            onboarding_monitor.record_request(
                endpoint=request.url.path,
                response_time_ms=response_time_ms,
                status_code=response.status_code
            )
        
        return response
        
    except Exception as e:
        # Record error
        if request.url.path.startswith('/onboarding'):
            onboarding_monitor.record_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={
                    'endpoint': request.url.path,
                    'method': request.method
                }
            )
        
        raise

# Scheduled monitoring task
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def run_monitoring_checks():
    """Periodic monitoring checks"""
    
    print("Running onboarding monitoring checks...")
    
    # Check for alerts
    alerts = onboarding_monitor.check_alert_conditions()
    
    if alerts:
        print(f"Found {len(alerts)} alerts")
        onboarding_monitor.send_alerts(alerts)
    
    # Generate health report
    health_report = onboarding_monitor.generate_health_report()
    
    # Log health status
    status = health_report['status']
    if status != 'healthy':
        onboarding_monitor.logger.warning(f"Onboarding system health: {status}")
    
    print(f"Health check complete - Status: {status}")

# Initialize scheduler
def start_monitoring():
    """Start the monitoring system"""
    
    scheduler = AsyncIOScheduler()
    
    # Run monitoring checks every 10 minutes
    scheduler.add_job(
        run_monitoring_checks,
        'interval',
        minutes=10,
        id='onboarding_monitoring'
    )
    
    # Generate daily health report
    scheduler.add_job(
        lambda: print(json.dumps(onboarding_monitor.generate_health_report(), indent=2)),
        'cron',
        hour=9,  # 9 AM daily
        id='daily_health_report'
    )
    
    scheduler.start()
    print("Onboarding monitoring started")

if __name__ == "__main__":
    # Start monitoring
    start_monitoring()
    
    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Monitoring stopped")
```

---

## Summary

This comprehensive testing and debugging guide provides:

1. **Complete test suite design** with unit, integration, and E2E tests covering all onboarding scenarios
2. **Step-by-step debugging procedures** for common issues like validation errors, database problems, and data mismatches
3. **Common issue resolution scenarios** with specific diagnostic steps and fixes
4. **Full testing automation** including CI/CD integration, performance regression testing, and error monitoring

The documentation includes runnable code examples, automated test scripts, and monitoring systems that can be immediately implemented to ensure the onboarding system's reliability and performance.

All scripts are designed to work with the existing Orientor Platform architecture and can be customized based on specific deployment requirements.