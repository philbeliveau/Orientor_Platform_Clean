#!/usr/bin/env python3
"""
End-to-End User Journey Testing Suite
Tests complete user flows from frontend to backend including authentication,
assessments, recommendations, and core platform features
"""

import asyncio
import json
import sys
import traceback
import requests
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class E2EUserJourneyTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "user_journeys": {},
            "integration_tests": {},
            "workflow_tests": {},
            "critical_paths": {},
            "summary": {}
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.timeout = 15
        
        # Define critical user journeys
        self.user_journeys = {
            "onboarding_flow": {
                "description": "New user onboarding and first assessment",
                "steps": [
                    "Visit homepage",
                    "Navigate to sign-up",
                    "Complete registration",
                    "Access dashboard",
                    "Start first assessment"
                ],
                "critical": True
            },
            "assessment_completion": {
                "description": "Complete personality assessment (HEXACO or Holland)",
                "steps": [
                    "Access assessment page",
                    "Load questions",
                    "Submit responses",
                    "View results",
                    "Get recommendations"
                ],
                "critical": True
            },
            "career_exploration": {
                "description": "Explore career recommendations and save preferences",
                "steps": [
                    "View career recommendations",
                    "Filter and search careers",
                    "Save preferred careers",
                    "Access career details",
                    "View progression paths"
                ],
                "critical": True
            },
            "education_planning": {
                "description": "Explore education programs and get recommendations",
                "steps": [
                    "Access school programs",
                    "Get program recommendations",
                    "Filter by preferences",
                    "View program details",
                    "Save programs of interest"
                ],
                "critical": False
            },
            "chat_interaction": {
                "description": "Use chat features for guidance and support",
                "steps": [
                    "Access chat interface",
                    "Send message",
                    "Receive response",
                    "Continue conversation",
                    "Access chat history"
                ],
                "critical": False
            }
        }
    
    def test_server_availability(self):
        """Test if both frontend and backend servers are running"""
        try:
            # Test backend
            backend_response = requests.get(f"{self.backend_url}/health", timeout=5)
            backend_ok = backend_response.status_code == 200
            
            # Test frontend (basic connectivity)
            try:
                frontend_response = requests.get(self.frontend_url, timeout=5)
                frontend_ok = frontend_response.status_code == 200
            except:
                frontend_ok = False
            
            result = {
                "backend_available": backend_ok,
                "frontend_available": frontend_ok,
                "backend_status": backend_response.status_code if backend_ok else None,
                "frontend_reachable": frontend_ok,
                "ready_for_e2e": backend_ok and frontend_ok
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                "backend_available": False,
                "frontend_available": False,
                "ready_for_e2e": False,
                "error": "Server connection failed"
            }
        except Exception as e:
            result = {
                "backend_available": False,
                "frontend_available": False,
                "ready_for_e2e": False,
                "error": str(e)
            }
        
        self.results["integration_tests"]["server_availability"] = result
        return result.get("ready_for_e2e", False)
    
    def test_onboarding_flow(self):
        """Test new user onboarding flow"""
        journey_result = {
            "journey_name": "onboarding_flow",
            "steps": {},
            "overall_status": "UNKNOWN",
            "critical_issues": [],
            "warnings": []
        }
        
        try:
            # Step 1: Test homepage access
            step_result = self._test_step_homepage_access()
            journey_result["steps"]["homepage_access"] = step_result
            
            # Step 2: Test user registration flow (API)
            step_result = self._test_step_registration_api()
            journey_result["steps"]["registration_api"] = step_result
            
            # Step 3: Test dashboard access (protected route)
            step_result = self._test_step_dashboard_access()
            journey_result["steps"]["dashboard_access"] = step_result
            
            # Step 4: Test assessment availability
            step_result = self._test_step_assessment_availability()
            journey_result["steps"]["assessment_availability"] = step_result
            
            # Evaluate overall journey
            journey_result = self._evaluate_journey_health(journey_result)
            
        except Exception as e:
            journey_result["overall_status"] = "ERROR"
            journey_result["error"] = str(e)
            journey_result["critical_issues"].append(f"Journey test failed: {str(e)}")
        
        self.results["user_journeys"]["onboarding_flow"] = journey_result
        return journey_result
    
    def test_assessment_completion_flow(self):
        """Test assessment completion user journey"""
        journey_result = {
            "journey_name": "assessment_completion",
            "steps": {},
            "overall_status": "UNKNOWN",
            "critical_issues": [],
            "warnings": []
        }
        
        try:
            # Step 1: Test HEXACO questions loading
            step_result = self._test_step_hexaco_questions()
            journey_result["steps"]["hexaco_questions"] = step_result
            
            # Step 2: Test Holland questions loading
            step_result = self._test_step_holland_questions()
            journey_result["steps"]["holland_questions"] = step_result
            
            # Step 3: Test assessment submission (mock)
            step_result = self._test_step_assessment_submission()
            journey_result["steps"]["assessment_submission"] = step_result
            
            # Step 4: Test results access
            step_result = self._test_step_results_access()
            journey_result["steps"]["results_access"] = step_result
            
            # Evaluate overall journey
            journey_result = self._evaluate_journey_health(journey_result)
            
        except Exception as e:
            journey_result["overall_status"] = "ERROR"
            journey_result["error"] = str(e)
            journey_result["critical_issues"].append(f"Assessment journey failed: {str(e)}")
        
        self.results["user_journeys"]["assessment_completion"] = journey_result
        return journey_result
    
    def test_career_exploration_flow(self):
        """Test career exploration and recommendations flow"""
        journey_result = {
            "journey_name": "career_exploration",
            "steps": {},
            "overall_status": "UNKNOWN",
            "critical_issues": [],
            "warnings": []
        }
        
        try:
            # Step 1: Test career recommendations API
            step_result = self._test_step_career_recommendations()
            journey_result["steps"]["career_recommendations"] = step_result
            
            # Step 2: Test saved careers functionality
            step_result = self._test_step_saved_careers()
            journey_result["steps"]["saved_careers"] = step_result
            
            # Step 3: Test career progression data
            step_result = self._test_step_career_progression()
            journey_result["steps"]["career_progression"] = step_result
            
            # Step 4: Test job listings
            step_result = self._test_step_job_listings()
            journey_result["steps"]["job_listings"] = step_result
            
            # Evaluate overall journey
            journey_result = self._evaluate_journey_health(journey_result)
            
        except Exception as e:
            journey_result["overall_status"] = "ERROR"
            journey_result["error"] = str(e)
            journey_result["critical_issues"].append(f"Career exploration failed: {str(e)}")
        
        self.results["user_journeys"]["career_exploration"] = journey_result
        return journey_result
    
    def test_education_planning_flow(self):
        """Test education planning and program recommendations"""
        journey_result = {
            "journey_name": "education_planning",
            "steps": {},
            "overall_status": "UNKNOWN",
            "critical_issues": [],
            "warnings": []
        }
        
        try:
            # Step 1: Test school programs API
            step_result = self._test_step_school_programs()
            journey_result["steps"]["school_programs"] = step_result
            
            # Step 2: Test program recommendations
            step_result = self._test_step_program_recommendations()
            journey_result["steps"]["program_recommendations"] = step_result
            
            # Evaluate overall journey
            journey_result = self._evaluate_journey_health(journey_result)
            
        except Exception as e:
            journey_result["overall_status"] = "ERROR"
            journey_result["error"] = str(e)
            journey_result["critical_issues"].append(f"Education planning failed: {str(e)}")
        
        self.results["user_journeys"]["education_planning"] = journey_result
        return journey_result
    
    def test_chat_interaction_flow(self):
        """Test chat functionality and interactions"""
        journey_result = {
            "journey_name": "chat_interaction",
            "steps": {},
            "overall_status": "UNKNOWN",
            "critical_issues": [],
            "warnings": []
        }
        
        try:
            # Step 1: Test socratic chat API
            step_result = self._test_step_socratic_chat()
            journey_result["steps"]["socratic_chat"] = step_result
            
            # Step 2: Test job chat API
            step_result = self._test_step_job_chat()
            journey_result["steps"]["job_chat"] = step_result
            
            # Step 3: Test chat analytics
            step_result = self._test_step_chat_analytics()
            journey_result["steps"]["chat_analytics"] = step_result
            
            # Evaluate overall journey
            journey_result = self._evaluate_journey_health(journey_result)
            
        except Exception as e:
            journey_result["overall_status"] = "ERROR"
            journey_result["error"] = str(e)
            journey_result["critical_issues"].append(f"Chat interaction failed: {str(e)}")
        
        self.results["user_journeys"]["chat_interaction"] = journey_result
        return journey_result
    
    # Individual step test methods
    def _test_step_homepage_access(self):
        """Test homepage accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=self.timeout)
            return {
                "step": "homepage_access",
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "accessible": response.status_code == 200
            }
        except Exception as e:
            return {
                "step": "homepage_access",
                "status": "ERROR",
                "error": str(e),
                "accessible": False
            }
    
    def _test_step_registration_api(self):
        """Test user registration API availability"""
        try:
            # Test the users endpoint (should require auth, so 401 is expected)
            response = requests.get(f"{self.backend_url}/api/v1/users/me", timeout=self.timeout)
            return {
                "step": "registration_api",
                "status": "PASS" if response.status_code in [401, 403] else "FAIL",
                "status_code": response.status_code,
                "auth_protected": response.status_code in [401, 403],
                "api_available": True
            }
        except Exception as e:
            return {
                "step": "registration_api",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_dashboard_access(self):
        """Test dashboard access (protected route)"""
        try:
            # Test if frontend serves the dashboard route
            response = requests.get(f"{self.frontend_url}/dashboard", timeout=self.timeout)
            return {
                "step": "dashboard_access",
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "route_accessible": response.status_code == 200
            }
        except Exception as e:
            return {
                "step": "dashboard_access",
                "status": "ERROR",
                "error": str(e),
                "route_accessible": False
            }
    
    def _test_step_assessment_availability(self):
        """Test assessment pages availability"""
        try:
            # Test both HEXACO and Holland test routes
            hexaco_response = requests.get(f"{self.frontend_url}/hexaco-test", timeout=self.timeout)
            holland_response = requests.get(f"{self.frontend_url}/tests/hexaco", timeout=self.timeout)
            
            return {
                "step": "assessment_availability",
                "status": "PASS" if hexaco_response.status_code == 200 else "PARTIAL",
                "hexaco_route": hexaco_response.status_code,
                "holland_route": holland_response.status_code,
                "assessments_available": hexaco_response.status_code == 200 or holland_response.status_code == 200
            }
        except Exception as e:
            return {
                "step": "assessment_availability",
                "status": "ERROR",
                "error": str(e),
                "assessments_available": False
            }
    
    def _test_step_hexaco_questions(self):
        """Test HEXACO questions loading"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/hexaco-test/questions", timeout=self.timeout)
            
            result = {
                "step": "hexaco_questions",
                "status_code": response.status_code,
                "questions_loaded": False
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    questions_count = 0
                    
                    if isinstance(data, list):
                        questions_count = len(data)
                    elif isinstance(data, dict) and "questions" in data:
                        questions_count = len(data["questions"])
                    
                    result.update({
                        "status": "PASS" if questions_count > 0 else "FAIL",
                        "questions_loaded": questions_count > 0,
                        "questions_count": questions_count,
                        "data_structure": type(data).__name__
                    })
                    
                except json.JSONDecodeError:
                    result.update({
                        "status": "FAIL",
                        "error": "Invalid JSON response"
                    })
            else:
                result["status"] = "FAIL"
            
            return result
            
        except Exception as e:
            return {
                "step": "hexaco_questions",
                "status": "ERROR",
                "error": str(e),
                "questions_loaded": False
            }
    
    def _test_step_holland_questions(self):
        """Test Holland questions loading"""
        try:
            # Try both possible Holland endpoints
            endpoints = [
                "/api/v1/tests/holland/",
                "/api/v1/tests/holland/questions"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=self.timeout)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            questions_count = 0
                            
                            if isinstance(data, list):
                                questions_count = len(data)
                            elif isinstance(data, dict) and "questions" in data:
                                questions_count = len(data["questions"])
                            
                            return {
                                "step": "holland_questions",
                                "status": "PASS" if questions_count > 0 else "FAIL",
                                "endpoint_used": endpoint,
                                "questions_loaded": questions_count > 0,
                                "questions_count": questions_count,
                                "status_code": response.status_code
                            }
                            
                        except json.JSONDecodeError:
                            continue
                except:
                    continue
            
            return {
                "step": "holland_questions",
                "status": "FAIL",
                "error": "No working Holland questions endpoint found",
                "questions_loaded": False
            }
            
        except Exception as e:
            return {
                "step": "holland_questions",
                "status": "ERROR",
                "error": str(e),
                "questions_loaded": False
            }
    
    def _test_step_assessment_submission(self):
        """Test assessment submission (mock test)"""
        try:
            # Mock submission test - just check if submission endpoints are accessible
            # We test with a minimal payload to see if endpoints accept POST requests
            
            endpoints_to_test = [
                "/api/v1/tests/holland/submit",
                "/api/v1/hexaco-test/submit"
            ]
            
            submission_results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.post(
                        f"{self.backend_url}{endpoint}",
                        json={"test": "submission"},
                        timeout=self.timeout
                    )
                    
                    # 401/403 means endpoint exists but requires auth (good)
                    # 422 means endpoint exists but validation failed (also good)
                    # 404 means endpoint doesn't exist (bad)
                    
                    acceptable_codes = [401, 403, 422, 400]  # Auth required or validation error
                    endpoint_exists = response.status_code != 404
                    
                    submission_results[endpoint] = {
                        "status_code": response.status_code,
                        "endpoint_exists": endpoint_exists,
                        "accepts_submissions": response.status_code in acceptable_codes
                    }
                    
                except Exception as e:
                    submission_results[endpoint] = {
                        "error": str(e),
                        "endpoint_exists": False
                    }
            
            # Overall assessment
            working_endpoints = sum(1 for r in submission_results.values() 
                                  if r.get("endpoint_exists", False))
            
            return {
                "step": "assessment_submission",
                "status": "PASS" if working_endpoints > 0 else "FAIL",
                "endpoints_tested": submission_results,
                "working_endpoints": working_endpoints,
                "submission_possible": working_endpoints > 0
            }
            
        except Exception as e:
            return {
                "step": "assessment_submission",
                "status": "ERROR",
                "error": str(e),
                "submission_possible": False
            }
    
    def _test_step_results_access(self):
        """Test assessment results access"""
        # This would typically require authentication and completed assessments
        # For now, we test if the endpoints are accessible
        try:
            # Test if user profile endpoint is available (where results would be stored)
            response = requests.get(f"{self.backend_url}/api/v1/users/me", timeout=self.timeout)
            
            return {
                "step": "results_access",
                "status": "PASS" if response.status_code in [401, 403] else "FAIL",
                "status_code": response.status_code,
                "endpoint_protected": response.status_code in [401, 403],
                "results_endpoint_available": response.status_code != 404
            }
            
        except Exception as e:
            return {
                "step": "results_access",
                "status": "ERROR",
                "error": str(e),
                "results_endpoint_available": False
            }
    
    def _test_step_career_recommendations(self):
        """Test career recommendations API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/careers/recommendations", timeout=self.timeout)
            
            return {
                "step": "career_recommendations",
                "status": "PASS" if response.status_code in [200, 401, 403] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "auth_required": response.status_code in [401, 403]
            }
            
        except Exception as e:
            return {
                "step": "career_recommendations",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_saved_careers(self):
        """Test saved careers functionality"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/careers/saved", timeout=self.timeout)
            
            return {
                "step": "saved_careers",
                "status": "PASS" if response.status_code in [200, 401, 403] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "auth_required": response.status_code in [401, 403]
            }
            
        except Exception as e:
            return {
                "step": "saved_careers",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_career_progression(self):
        """Test career progression data"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/career-progression", timeout=self.timeout)
            
            return {
                "step": "career_progression",
                "status": "PASS" if response.status_code in [200, 401, 403] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "auth_required": response.status_code in [401, 403]
            }
            
        except Exception as e:
            return {
                "step": "career_progression",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_job_listings(self):
        """Test job listings API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/jobs", timeout=self.timeout)
            
            result = {
                "step": "job_listings",
                "status_code": response.status_code,
                "api_available": response.status_code != 404
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result.update({
                        "status": "PASS",
                        "data_loaded": True,
                        "data_structure": type(data).__name__,
                        "jobs_available": isinstance(data, list) and len(data) > 0
                    })
                except:
                    result["status"] = "PARTIAL"
            else:
                result["status"] = "FAIL" if response.status_code not in [401, 403] else "PROTECTED"
            
            return result
            
        except Exception as e:
            return {
                "step": "job_listings",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_school_programs(self):
        """Test school programs API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/school-programs", timeout=self.timeout)
            
            result = {
                "step": "school_programs",
                "status_code": response.status_code,
                "api_available": response.status_code != 404
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result.update({
                        "status": "PASS",
                        "data_loaded": True,
                        "data_structure": type(data).__name__,
                        "programs_available": isinstance(data, list) and len(data) > 0
                    })
                except:
                    result["status"] = "PARTIAL"
            else:
                result["status"] = "FAIL" if response.status_code not in [401, 403] else "PROTECTED"
            
            return result
            
        except Exception as e:
            return {
                "step": "school_programs",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_program_recommendations(self):
        """Test program recommendations API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/program-recommendations", timeout=self.timeout)
            
            return {
                "step": "program_recommendations",
                "status": "PASS" if response.status_code in [200, 401, 403] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "auth_required": response.status_code in [401, 403]
            }
            
        except Exception as e:
            return {
                "step": "program_recommendations",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_socratic_chat(self):
        """Test socratic chat API"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/socratic-chat/send",
                json={"message": "test"},
                timeout=self.timeout
            )
            
            return {
                "step": "socratic_chat",
                "status": "PASS" if response.status_code in [200, 401, 403, 422] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "accepts_messages": response.status_code in [200, 401, 403, 422]
            }
            
        except Exception as e:
            return {
                "step": "socratic_chat",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_job_chat(self):
        """Test job chat API"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/job-chat/send",
                json={"message": "test"},
                timeout=self.timeout
            )
            
            return {
                "step": "job_chat",
                "status": "PASS" if response.status_code in [200, 401, 403, 422] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "accepts_messages": response.status_code in [200, 401, 403, 422]
            }
            
        except Exception as e:
            return {
                "step": "job_chat",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _test_step_chat_analytics(self):
        """Test chat analytics API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/chat-analytics", timeout=self.timeout)
            
            return {
                "step": "chat_analytics",
                "status": "PASS" if response.status_code in [200, 401, 403] else "FAIL",
                "status_code": response.status_code,
                "api_available": response.status_code != 404,
                "auth_required": response.status_code in [401, 403]
            }
            
        except Exception as e:
            return {
                "step": "chat_analytics",
                "status": "ERROR",
                "error": str(e),
                "api_available": False
            }
    
    def _evaluate_journey_health(self, journey_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate overall health of a user journey"""
        steps = journey_result.get("steps", {})
        
        # Count step statuses
        total_steps = len(steps)
        passed_steps = sum(1 for step in steps.values() if step.get("status") == "PASS")
        failed_steps = sum(1 for step in steps.values() if step.get("status") == "FAIL")
        error_steps = sum(1 for step in steps.values() if step.get("status") == "ERROR")
        
        # Calculate health score
        if total_steps == 0:
            health_score = 0
        else:
            health_score = (passed_steps / total_steps) * 100
        
        # Determine overall status
        if error_steps > 0:
            overall_status = "ERROR"
        elif failed_steps > total_steps / 2:
            overall_status = "BROKEN"
        elif passed_steps == total_steps:
            overall_status = "HEALTHY"
        elif passed_steps >= total_steps / 2:
            overall_status = "PARTIAL"
        else:
            overall_status = "UNHEALTHY"
        
        journey_result.update({
            "overall_status": overall_status,
            "health_score": health_score,
            "step_summary": {
                "total": total_steps,
                "passed": passed_steps,
                "failed": failed_steps,
                "errors": error_steps
            }
        })
        
        return journey_result
    
    def generate_summary(self):
        """Generate comprehensive E2E testing summary"""
        journeys = self.results.get("user_journeys", {})
        integration = self.results.get("integration_tests", {})
        
        # Count journey health
        total_journeys = len(journeys)
        healthy_journeys = sum(1 for j in journeys.values() if j.get("overall_status") == "HEALTHY")
        partial_journeys = sum(1 for j in journeys.values() if j.get("overall_status") == "PARTIAL")
        broken_journeys = sum(1 for j in journeys.values() if j.get("overall_status") in ["BROKEN", "ERROR"])
        
        # Calculate average health score
        health_scores = [j.get("health_score", 0) for j in journeys.values() if "health_score" in j]
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
        
        # Server availability
        server_status = integration.get("server_availability", {})
        servers_ready = server_status.get("ready_for_e2e", False)
        
        # Critical journey status
        critical_journeys = ["onboarding_flow", "assessment_completion", "career_exploration"]
        critical_journey_health = {}
        for journey_name in critical_journeys:
            journey_data = journeys.get(journey_name, {})
            critical_journey_health[journey_name] = journey_data.get("overall_status", "UNKNOWN")
        
        summary = {
            "total_journeys_tested": total_journeys,
            "healthy_journeys": healthy_journeys,
            "partial_journeys": partial_journeys,
            "broken_journeys": broken_journeys,
            "average_health_score": avg_health_score,
            "servers_ready": servers_ready,
            "backend_available": server_status.get("backend_available", False),
            "frontend_available": server_status.get("frontend_available", False),
            "critical_journeys": critical_journey_health,
            "overall_platform_health": self._calculate_platform_health(avg_health_score, servers_ready),
            "recommendations": []
        }
        
        # Generate recommendations
        if not servers_ready:
            summary["recommendations"].append("🚨 Start both frontend and backend servers for complete E2E testing")
        
        if broken_journeys > 0:
            summary["recommendations"].append(f"🔧 Fix {broken_journeys} broken user journeys")
        
        if not summary["critical_journeys"].get("onboarding_flow") == "HEALTHY":
            summary["recommendations"].append("👋 Fix onboarding flow - critical for new users")
        
        if not summary["critical_journeys"].get("assessment_completion") == "HEALTHY":
            summary["recommendations"].append("📊 Fix assessment completion flow - core platform feature")
        
        if not summary["critical_journeys"].get("career_exploration") == "HEALTHY":
            summary["recommendations"].append("💼 Fix career exploration flow - primary value proposition")
        
        if avg_health_score >= 90:
            summary["recommendations"].append("✅ User journeys are in excellent health!")
        elif avg_health_score >= 70:
            summary["recommendations"].append("✅ User journeys are in good health")
        elif avg_health_score >= 50:
            summary["recommendations"].append("⚠️ User journeys need attention")
        else:
            summary["recommendations"].append("🚨 User journeys are in poor health - immediate action required")
        
        self.results["summary"] = summary
        return summary
    
    def _calculate_platform_health(self, avg_health_score: float, servers_ready: bool) -> str:
        """Calculate overall platform health grade"""
        if not servers_ready:
            return "DOWN"
        elif avg_health_score >= 90:
            return "EXCELLENT"
        elif avg_health_score >= 80:
            return "GOOD"
        elif avg_health_score >= 60:
            return "FAIR"
        elif avg_health_score >= 40:
            return "POOR"
        else:
            return "CRITICAL"
    
    def save_results(self):
        """Save E2E test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"e2e_user_journey_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"E2E user journey test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_e2e_tests(self):
        """Run complete end-to-end user journey testing suite"""
        print("🚀 Starting Comprehensive End-to-End User Journey Testing...")
        print("=" * 70)
        
        # Test 0: Server Availability
        print("0. Testing server availability...")
        servers_ready = self.test_server_availability()
        print(f"   Result: {'✅ READY' if servers_ready else '❌ NOT READY'}")
        
        # Test 1: Onboarding Flow
        print("1. Testing onboarding flow...")
        onboarding = self.test_onboarding_flow()
        print(f"   Result: {onboarding.get('overall_status', 'UNKNOWN')} ({onboarding.get('health_score', 0):.1f}%)")
        
        # Test 2: Assessment Completion
        print("2. Testing assessment completion flow...")
        assessment = self.test_assessment_completion_flow()
        print(f"   Result: {assessment.get('overall_status', 'UNKNOWN')} ({assessment.get('health_score', 0):.1f}%)")
        
        # Test 3: Career Exploration
        print("3. Testing career exploration flow...")
        career = self.test_career_exploration_flow()
        print(f"   Result: {career.get('overall_status', 'UNKNOWN')} ({career.get('health_score', 0):.1f}%)")
        
        # Test 4: Education Planning
        print("4. Testing education planning flow...")
        education = self.test_education_planning_flow()
        print(f"   Result: {education.get('overall_status', 'UNKNOWN')} ({education.get('health_score', 0):.1f}%)")
        
        # Test 5: Chat Interaction
        print("5. Testing chat interaction flow...")
        chat = self.test_chat_interaction_flow()
        print(f"   Result: {chat.get('overall_status', 'UNKNOWN')} ({chat.get('health_score', 0):.1f}%)")
        
        # Generate Summary
        print("6. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 70)
        print("🚀 END-TO-END USER JOURNEY TESTING SUMMARY")
        print("=" * 70)
        print(f"Journey Health: {summary['healthy_journeys']}/{summary['total_journeys_tested']} healthy ({summary['average_health_score']:.1f}%)")
        print(f"Platform Health: {summary['overall_platform_health']}")
        print(f"Servers Ready: {'✅ YES' if summary['servers_ready'] else '❌ NO'}")
        
        print(f"\n🎯 Critical Journey Status:")
        for journey_name, status in summary['critical_journeys'].items():
            print(f"   {journey_name}: {status}")
        
        print(f"\n📊 Journey Breakdown:")
        print(f"   Healthy: {summary['healthy_journeys']}")
        print(f"   Partial: {summary['partial_journeys']}")
        print(f"   Broken: {summary['broken_journeys']}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = E2EUserJourneyTester()
    
    try:
        # Run E2E tests
        results = asyncio.run(tester.run_comprehensive_e2e_tests())
        
        # Exit code based on results
        summary = results["summary"]
        if summary["overall_platform_health"] in ["EXCELLENT", "GOOD"]:
            sys.exit(0)  # Excellent
        elif summary["overall_platform_health"] in ["FAIR"]:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ E2E user journey testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()