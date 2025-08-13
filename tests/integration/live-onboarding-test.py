#!/usr/bin/env python3
"""
Live Onboarding Test - Test actual running server
=================================================

Tests the onboarding completion functionality using the actual running backend server
to identify the real source of the 'Prisma' object has no attribute 'user' error.
"""

import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveOnboardingTest:
    """Test suite for live onboarding functionality."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health endpoint to ensure server is running."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.backend_url}/health")
                return {
                    "test": "health_check",
                    "status": "pass" if response.status_code == 200 else "fail",
                    "status_code": response.status_code,
                    "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
        except Exception as e:
            return {
                "test": "health_check", 
                "status": "error",
                "error": str(e)
            }
    
    async def test_onboarding_status_without_auth(self) -> Dict[str, Any]:
        """Test onboarding status endpoint without auth to see error patterns."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.backend_url}/api/v1/onboarding/status")
                return {
                    "test": "onboarding_status_no_auth",
                    "status": "info",
                    "status_code": response.status_code,
                    "response": response.text[:500],  # First 500 chars
                    "auth_required": response.status_code in [401, 403]
                }
        except Exception as e:
            return {
                "test": "onboarding_status_no_auth",
                "status": "error", 
                "error": str(e)
            }
    
    async def test_onboarding_completion_without_auth(self) -> Dict[str, Any]:
        """Test onboarding completion endpoint without auth."""
        try:
            test_data = {
                "responses": [
                    {
                        "questionId": "test_q1",
                        "question": "Test question for error reproduction",
                        "response": "Test response"
                    }
                ],
                "psychProfile": {
                    "openness": 0.8,
                    "conscientiousness": 0.7,
                    "extraversion": 0.6,
                    "agreeableness": 0.7,
                    "emotionalStability": 0.6,
                    "honestyHumility": 0.8,
                    "description": "Test profile for error reproduction"
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/onboarding/complete",
                    json=test_data
                )
                
                result = {
                    "test": "onboarding_completion_no_auth",
                    "status": "info",
                    "status_code": response.status_code,
                    "response": response.text[:1000],  # First 1000 chars
                    "auth_required": response.status_code in [401, 403]
                }
                
                # Check if the response contains the Prisma error
                response_text = response.text.lower()
                if "prisma" in response_text and "attribute" in response_text and "user" in response_text:
                    result["prisma_error_detected"] = True
                    result["status"] = "fail"
                else:
                    result["prisma_error_detected"] = False
                    
                return result
                
        except Exception as e:
            return {
                "test": "onboarding_completion_no_auth",
                "status": "error",
                "error": str(e)
            }
    
    async def analyze_recent_server_logs(self) -> Dict[str, Any]:
        """Analyze recent server logs for Prisma errors."""
        try:
            log_file = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/backend/app/logs/app.log"
            
            if not Path(log_file).exists():
                return {
                    "test": "log_analysis",
                    "status": "skip",
                    "reason": "Log file not found"
                }
                
            # Get the last 100 lines and look for recent Prisma errors
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            recent_lines = lines[-200:]  # Last 200 lines
            
            prisma_errors = []
            for i, line in enumerate(recent_lines):
                if "'Prisma' object has no attribute 'user'" in line:
                    # Get some context around the error
                    context_start = max(0, i-2)
                    context_end = min(len(recent_lines), i+3)
                    context = recent_lines[context_start:context_end]
                    
                    prisma_errors.append({
                        "line_number": len(lines) - len(recent_lines) + i,
                        "error_line": line.strip(),
                        "context": [l.strip() for l in context]
                    })
            
            return {
                "test": "log_analysis",
                "status": "info",
                "total_lines_analyzed": len(recent_lines),
                "prisma_errors_found": len(prisma_errors),
                "errors": prisma_errors[-3:] if prisma_errors else [],  # Last 3 errors with context
                "has_recent_errors": len(prisma_errors) > 0
            }
            
        except Exception as e:
            return {
                "test": "log_analysis",
                "status": "error",
                "error": str(e)
            }
    
    async def test_log_monitoring_during_request(self) -> Dict[str, Any]:
        """Monitor logs while making a request to catch the error in real-time."""
        try:
            log_file = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/backend/app/logs/app.log"
            
            # Get current log size
            initial_size = Path(log_file).stat().st_size if Path(log_file).exists() else 0
            
            # Make a request that might trigger the error
            test_data = {"responses": [], "psychProfile": {}}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/onboarding/complete",
                    json=test_data
                )
                
            # Check for new log entries
            new_logs = ""
            if Path(log_file).exists():
                current_size = Path(log_file).stat().st_size
                if current_size > initial_size:
                    with open(log_file, 'r') as f:
                        f.seek(initial_size)
                        new_logs = f.read()
            
            # Analyze new logs for Prisma errors
            has_prisma_error = "'Prisma' object has no attribute 'user'" in new_logs
            
            return {
                "test": "log_monitoring_during_request",
                "status": "info", 
                "request_status_code": response.status_code,
                "new_log_content": new_logs[-500:] if new_logs else "",  # Last 500 chars
                "prisma_error_in_new_logs": has_prisma_error,
                "analysis": "Prisma error occurred during request" if has_prisma_error else "No Prisma error in new logs"
            }
            
        except Exception as e:
            return {
                "test": "log_monitoring_during_request",
                "status": "error",
                "error": str(e)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all live tests."""
        logger.info("🔴 LIVE ONBOARDING TEST SUITE")
        logger.info("Testing actual running server for Prisma attribute errors")
        logger.info("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_endpoint()),
            ("Status Endpoint (No Auth)", self.test_onboarding_status_without_auth()),
            ("Completion Endpoint (No Auth)", self.test_onboarding_completion_without_auth()),
            ("Recent Log Analysis", self.analyze_recent_server_logs()),
            ("Real-time Log Monitoring", self.test_log_monitoring_during_request())
        ]
        
        results = []
        for test_name, test_coro in tests:
            logger.info(f"🧪 Running: {test_name}")
            try:
                result = await test_coro
                result["test_name"] = test_name
                results.append(result)
                
                # Log key findings
                if result.get("status") == "pass":
                    logger.info(f"✅ {test_name}: PASSED")
                elif result.get("status") == "fail":
                    logger.error(f"❌ {test_name}: FAILED")
                elif result.get("status") == "error":
                    logger.error(f"💥 {test_name}: ERROR - {result.get('error', 'Unknown')}")
                else:
                    logger.info(f"ℹ️  {test_name}: INFO")
                    
                # Log special findings
                if result.get("prisma_error_detected"):
                    logger.error(f"🚨 PRISMA ERROR DETECTED in {test_name}")
                if result.get("prisma_error_in_new_logs"):
                    logger.error(f"🚨 REAL-TIME PRISMA ERROR in {test_name}")
                    
            except Exception as e:
                error_result = {
                    "test_name": test_name,
                    "test": test_name.lower().replace(" ", "_"),
                    "status": "error",
                    "error": f"Test execution failed: {str(e)}"
                }
                results.append(error_result)
                logger.error(f"💥 {test_name}: EXECUTION ERROR - {str(e)}")
                
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print detailed test summary."""
        logger.info("=" * 60)
        logger.info("📊 LIVE TEST SUMMARY")
        logger.info("=" * 60)
        
        prisma_errors_detected = False
        auth_working = True
        
        for result in results:
            logger.info(f"\n🔸 {result['test_name']}:")
            logger.info(f"   Status: {result.get('status', 'unknown').upper()}")
            
            if result.get('status_code'):
                logger.info(f"   HTTP Status: {result['status_code']}")
                
            if result.get('auth_required'):
                logger.info(f"   Auth Required: {result['auth_required']}")
                
            if result.get('prisma_error_detected'):
                logger.error(f"   🚨 PRISMA ERROR DETECTED!")
                prisma_errors_detected = True
                
            if result.get('prisma_error_in_new_logs'):
                logger.error(f"   🚨 REAL-TIME PRISMA ERROR!")
                prisma_errors_detected = True
                
            if result.get('prisma_errors_found', 0) > 0:
                logger.error(f"   🚨 Found {result['prisma_errors_found']} Prisma errors in logs")
                prisma_errors_detected = True
                
            if result.get('error'):
                logger.error(f"   Error: {result['error']}")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎯 FINAL ANALYSIS")
        logger.info("=" * 60)
        
        if prisma_errors_detected:
            logger.error("❌ CONFIRMATION: 'Prisma' object has no attribute 'user' errors are STILL occurring")
            logger.error("   The fix to change 'db.user' to 'db.users' is NOT complete")
            logger.error("   Additional files need to be updated")
        else:
            logger.info("✅ No Prisma attribute errors detected in current tests")
            logger.info("   The fix may be working, or errors occur only under specific conditions")
            
        return prisma_errors_detected

async def main():
    """Main test execution."""
    test_suite = LiveOnboardingTest()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Save results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = f"/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_Platform_Clean/logs/live_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "test_type": "live_onboarding_test",
                "results": results
            }, f, indent=2)
            
        logger.info(f"💾 Results saved to: {results_file}")
        
        # Print summary and determine exit code
        errors_found = test_suite.print_summary(results)
        
        if errors_found:
            logger.error("\n🚨 ACTION REQUIRED: Additional Prisma fixes needed")
            sys.exit(1)
        else:
            logger.info("\n✅ Test completed - check results for details")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())