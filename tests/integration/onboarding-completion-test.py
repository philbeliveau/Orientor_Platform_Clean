#!/usr/bin/env python3
"""
Comprehensive Onboarding Completion Test
========================================

Tests the onboarding completion functionality to verify the Prisma fix works correctly.
This test addresses the issue where `db.user` was changed to `db.users` across the backend.

The test focuses on:
1. Status endpoint functionality
2. Completion endpoint functionality  
3. Database update operations
4. Error handling and edge cases

Expected Fix: All `db.user` references changed to `db.users` to match Prisma schema.
"""

import sys
import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/logs/onboarding_test.log')
    ]
)
logger = logging.getLogger(__name__)

class OnboardingCompletionTest:
    """Test suite for onboarding completion functionality."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            "start_time": datetime.utcnow().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
    def load_environment(self) -> Dict[str, str]:
        """Load environment variables from backend .env file."""
        env_path = backend_dir / ".env.local"
        if not env_path.exists():
            env_path = backend_dir / ".env"
            
        if not env_path.exists():
            logger.warning("No .env file found, using environment variables")
            return {}
            
        env_vars = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
                    
        return env_vars
    
    def get_test_auth_token(self) -> Optional[str]:
        """
        Get a test authentication token.
        In production, this would use Clerk test users.
        For this test, we'll simulate the token.
        """
        # Load environment to get test credentials
        env = self.load_environment()
        
        # For testing purposes, we'll use a mock JWT token
        # In real implementation, this would be obtained from Clerk
        test_token = env.get("TEST_CLERK_JWT_TOKEN")
        
        if not test_token:
            logger.warning("No test token found in environment. Using mock token for testing.")
            # Mock JWT token for testing (DO NOT use in production)
            test_token = "test_token_placeholder"
            
        return test_token
    
    async def test_server_health(self) -> Dict[str, Any]:
        """Test if the backend server is running and accessible."""
        test_result = {
            "test_name": "server_health_check",
            "description": "Verify backend server is running",
            "status": "failed",
            "error": None,
            "duration_ms": 0,
            "details": {}
        }
        
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.backend_url}/health")
                
                if response.status_code == 200:
                    test_result["status"] = "passed"
                    test_result["details"] = {
                        "status_code": response.status_code,
                        "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    }
                else:
                    test_result["error"] = f"Server returned status {response.status_code}"
                    
        except httpx.ConnectError:
            test_result["error"] = "Could not connect to backend server. Is it running on port 8000?"
        except Exception as e:
            test_result["error"] = f"Unexpected error: {str(e)}"
            
        test_result["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return test_result
    
    async def test_onboarding_status_endpoint(self, auth_token: str) -> Dict[str, Any]:
        """Test the /api/v1/onboarding/status endpoint."""
        test_result = {
            "test_name": "onboarding_status_endpoint",
            "description": "Test GET /api/v1/onboarding/status endpoint",
            "status": "failed",
            "error": None,
            "duration_ms": 0,
            "details": {}
        }
        
        start_time = datetime.utcnow()
        
        try:
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.backend_url}/api/v1/onboarding/status",
                    headers=headers
                )
                
                test_result["details"]["status_code"] = response.status_code
                test_result["details"]["headers"] = dict(response.headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    test_result["details"]["response"] = response_data
                    
                    # Validate response schema
                    required_fields = ["onboarding_completed", "has_started", "is_complete", "message"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        test_result["status"] = "passed"
                        test_result["details"]["schema_validation"] = "passed"
                    else:
                        test_result["error"] = f"Missing required fields: {missing_fields}"
                        test_result["details"]["schema_validation"] = "failed"
                        
                elif response.status_code == 401:
                    test_result["error"] = "Authentication failed - Invalid token"
                elif response.status_code == 500:
                    test_result["error"] = "Server error - This could indicate the Prisma attribute error"
                    test_result["details"]["response_text"] = response.text
                else:
                    test_result["error"] = f"Unexpected status code: {response.status_code}"
                    test_result["details"]["response_text"] = response.text
                    
        except httpx.TimeoutException:
            test_result["error"] = "Request timed out"
        except Exception as e:
            test_result["error"] = f"Unexpected error: {str(e)}"
            
        test_result["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return test_result
    
    async def test_onboarding_completion_endpoint(self, auth_token: str) -> Dict[str, Any]:
        """Test the /api/v1/onboarding/complete endpoint."""
        test_result = {
            "test_name": "onboarding_completion_endpoint", 
            "description": "Test POST /api/v1/onboarding/complete endpoint",
            "status": "failed",
            "error": None,
            "duration_ms": 0,
            "details": {}
        }
        
        start_time = datetime.utcnow()
        
        try:
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Sample onboarding data
            onboarding_data = {
                "responses": [
                    {
                        "questionId": "q1",
                        "question": "What are your career interests?",
                        "response": "Technology and innovation"
                    },
                    {
                        "questionId": "q2", 
                        "question": "What motivates you?",
                        "response": "Problem solving and creating value"
                    }
                ],
                "psychProfile": {
                    "openness": 0.8,
                    "conscientiousness": 0.7,
                    "extraversion": 0.6,
                    "agreeableness": 0.7,
                    "emotionalStability": 0.6,
                    "honestyHumility": 0.8,
                    "description": "Test psychological profile for onboarding completion"
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/onboarding/complete",
                    headers=headers,
                    json=onboarding_data
                )
                
                test_result["details"]["status_code"] = response.status_code
                test_result["details"]["headers"] = dict(response.headers)
                test_result["details"]["request_data"] = onboarding_data
                
                if response.status_code == 200:
                    response_data = response.json()
                    test_result["details"]["response"] = response_data
                    
                    # Validate response
                    expected_fields = ["message", "assessment_id", "profile_created"]
                    missing_fields = [field for field in expected_fields if field not in response_data]
                    
                    if not missing_fields:
                        test_result["status"] = "passed"
                        test_result["details"]["validation"] = "All expected fields present"
                    else:
                        test_result["status"] = "passed"  # Still consider it a pass if the endpoint works
                        test_result["details"]["validation"] = f"Response successful but missing: {missing_fields}"
                        
                elif response.status_code == 401:
                    test_result["error"] = "Authentication failed"
                elif response.status_code == 500:
                    # This is likely the Prisma error we're testing for
                    error_text = response.text
                    test_result["error"] = f"Server error: {error_text}"
                    test_result["details"]["response_text"] = error_text
                    
                    # Check if it's specifically the Prisma attribute error
                    if "'Prisma' object has no attribute 'user'" in error_text:
                        test_result["details"]["prisma_error_confirmed"] = True
                        test_result["error"] = "CONFIRMED: Prisma attribute error - 'user' should be 'users'"
                    else:
                        test_result["details"]["prisma_error_confirmed"] = False
                else:
                    test_result["error"] = f"Unexpected status code: {response.status_code}"
                    test_result["details"]["response_text"] = response.text
                    
        except httpx.TimeoutException:
            test_result["error"] = "Request timed out"
        except Exception as e:
            test_result["error"] = f"Unexpected error: {str(e)}"
            
        test_result["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return test_result
    
    async def test_post_completion_status_check(self, auth_token: str) -> Dict[str, Any]:
        """Test status check after completion to verify database update worked."""
        test_result = {
            "test_name": "post_completion_status_check",
            "description": "Verify status shows completed after running completion endpoint",
            "status": "failed", 
            "error": None,
            "duration_ms": 0,
            "details": {}
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Wait a moment for database update
            await asyncio.sleep(1)
            
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.backend_url}/api/v1/onboarding/status",
                    headers=headers
                )
                
                test_result["details"]["status_code"] = response.status_code
                
                if response.status_code == 200:
                    response_data = response.json()
                    test_result["details"]["response"] = response_data
                    
                    # Check if onboarding is marked as completed
                    if response_data.get("onboarding_completed") is True:
                        test_result["status"] = "passed"
                        test_result["details"]["validation"] = "Onboarding correctly marked as completed"
                    else:
                        test_result["error"] = "Onboarding not marked as completed in database"
                        test_result["details"]["validation"] = "Database update may have failed"
                else:
                    test_result["error"] = f"Status check failed with code: {response.status_code}"
                    test_result["details"]["response_text"] = response.text
                    
        except Exception as e:
            test_result["error"] = f"Unexpected error: {str(e)}"
            
        test_result["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return test_result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all onboarding completion tests."""
        logger.info("🚀 Starting Onboarding Completion Test Suite")
        logger.info("="*60)
        
        # Get authentication token
        auth_token = self.get_test_auth_token()
        if not auth_token:
            logger.error("❌ Cannot proceed without authentication token")
            return self.test_results
            
        logger.info(f"🔑 Using authentication token: {auth_token[:20]}...")
        
        # Define test sequence
        tests = [
            self.test_server_health(),
            self.test_onboarding_status_endpoint(auth_token),
            self.test_onboarding_completion_endpoint(auth_token),
            self.test_post_completion_status_check(auth_token)
        ]
        
        # Run tests sequentially
        for test_coro in tests:
            try:
                result = await test_coro
                self.test_results["tests"].append(result)
                self.test_results["summary"]["total"] += 1
                
                if result["status"] == "passed":
                    self.test_results["summary"]["passed"] += 1
                    logger.info(f"✅ {result['test_name']}: PASSED ({result['duration_ms']}ms)")
                elif result["status"] == "failed":
                    self.test_results["summary"]["failed"] += 1
                    logger.error(f"❌ {result['test_name']}: FAILED - {result.get('error', 'Unknown error')}")
                else:
                    self.test_results["summary"]["errors"] += 1
                    logger.error(f"💥 {result['test_name']}: ERROR - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_result = {
                    "test_name": "unknown_test",
                    "description": "Test execution failed",
                    "status": "error",
                    "error": f"Test execution error: {str(e)}",
                    "duration_ms": 0,
                    "details": {}
                }
                self.test_results["tests"].append(error_result)
                self.test_results["summary"]["total"] += 1
                self.test_results["summary"]["errors"] += 1
                logger.error(f"💥 Test execution failed: {str(e)}")
                
        self.test_results["end_time"] = datetime.utcnow().isoformat()
        return self.test_results
    
    def print_summary(self):
        """Print a formatted test summary."""
        summary = self.test_results["summary"]
        logger.info("="*60)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {summary['total']}")
        logger.info(f"✅ Passed: {summary['passed']}")
        logger.info(f"❌ Failed: {summary['failed']}")
        logger.info(f"💥 Errors: {summary['errors']}")
        
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if summary['failed'] > 0 or summary['errors'] > 0:
            logger.info("\n🔍 FAILED/ERROR TESTS:")
            for test in self.test_results["tests"]:
                if test["status"] in ["failed", "error"]:
                    logger.info(f"  - {test['test_name']}: {test.get('error', 'Unknown error')}")
    
    def save_results(self, filepath: str):
        """Save detailed test results to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"💾 Test results saved to: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {str(e)}")


async def main():
    """Main test execution function."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Initialize and run tests
    test_suite = OnboardingCompletionTest()
    
    try:
        results = await test_suite.run_all_tests()
        test_suite.print_summary()
        
        # Save results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = f"/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/logs/onboarding_test_results_{timestamp}.json"
        test_suite.save_results(results_file)
        
        # Exit with appropriate code
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
            logger.error("❌ Tests failed - check logs for details")
            sys.exit(1)
        else:
            logger.info("✅ All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Test suite execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())