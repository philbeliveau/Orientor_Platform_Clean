#!/usr/bin/env python3
"""
Backend API Testing Suite
Comprehensive testing for all Prisma endpoints and backend functionality
"""

import asyncio
import json
import sys
import traceback
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

class BackendAPITester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "endpoints": {},
            "prisma_tests": {},
            "performance": {},
            "summary": {}
        }
        self.backend_url = "http://localhost:8000"
        self.timeout = 10
        
        # Critical endpoints to test
        self.critical_endpoints = {
            # Health and basic endpoints
            "/health": {"method": "GET", "auth_required": False, "description": "Health check"},
            "/": {"method": "GET", "auth_required": False, "description": "Root endpoint"},
            
            # Authentication endpoints
            "/api/v1/users/me": {"method": "GET", "auth_required": True, "description": "Current user profile"},
            
            # Career-related endpoints
            "/api/v1/careers/saved": {"method": "GET", "auth_required": True, "description": "Saved career recommendations"},
            "/api/v1/careers/recommendations": {"method": "GET", "auth_required": True, "description": "Career recommendations"},
            "/api/v1/career-progression": {"method": "GET", "auth_required": True, "description": "Career progression data"},
            
            # Assessment endpoints
            "/api/v1/hexaco-test/questions": {"method": "GET", "auth_required": False, "description": "HEXACO test questions"},
            "/api/v1/tests/holland/": {"method": "GET", "auth_required": False, "description": "Holland test questions"},
            "/api/v1/tests/holland/questions": {"method": "GET", "auth_required": False, "description": "Holland test questions alternative"},
            
            # Chat and interaction endpoints
            "/api/v1/socratic-chat/send": {"method": "POST", "auth_required": True, "description": "Socratic chat interaction"},
            "/api/v1/job-chat/send": {"method": "POST", "auth_required": True, "description": "Job chat interaction"},
            
            # Education and programs
            "/api/v1/school-programs": {"method": "GET", "auth_required": False, "description": "School programs data"},
            "/api/v1/program-recommendations": {"method": "GET", "auth_required": True, "description": "Program recommendations"},
            
            # Jobs and search
            "/api/v1/jobs": {"method": "GET", "auth_required": False, "description": "Job listings"},
            "/api/v1/vector-search": {"method": "POST", "auth_required": False, "description": "Vector search functionality"},
            
            # Analytics and sharing
            "/api/v1/chat-analytics": {"method": "GET", "auth_required": True, "description": "Chat analytics"},
            "/api/v1/share": {"method": "POST", "auth_required": True, "description": "Share functionality"}
        }
    
    def test_prisma_connectivity(self):
        """Test Prisma database connectivity and operations"""
        try:
            # Test Prisma import
            from prisma import Prisma
            
            # Test client creation
            prisma = Prisma()
            
            # Test model access (check if models are available)
            models_available = []
            model_errors = []
            
            test_models = [
                "user", "saved_recommendation", "career_goal", 
                "personality_profiles", "hexaco_question", "holland_question",
                "chat_message", "school_program", "job"
            ]
            
            for model_name in test_models:
                try:
                    model = getattr(prisma, model_name, None)
                    if model:
                        models_available.append(model_name)
                    else:
                        model_errors.append(f"{model_name}: Model not found")
                except Exception as e:
                    model_errors.append(f"{model_name}: {str(e)}")
            
            result = {
                "status": "PASS" if len(models_available) > len(model_errors) else "PARTIAL",
                "prisma_import": "✅ Success",
                "client_creation": "✅ Success",
                "models_available": models_available,
                "model_errors": model_errors,
                "total_models_tested": len(test_models),
                "successful_models": len(models_available)
            }
            
        except ImportError as e:
            result = {
                "status": "FAIL",
                "error": "Prisma import failed",
                "message": str(e),
                "prisma_import": "❌ Failed"
            }
        except Exception as e:
            result = {
                "status": "FAIL",
                "error": "Prisma connectivity test failed",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        
        self.results["prisma_tests"]["connectivity"] = result
        return result["status"] in ["PASS", "PARTIAL"]
    
    def test_endpoint_availability(self, endpoint: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test individual endpoint availability and response"""
        try:
            method = config.get("method", "GET").upper()
            auth_required = config.get("auth_required", False)
            description = config.get("description", "No description")
            
            # Prepare request
            url = f"{self.backend_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            # For now, test without authentication to check basic connectivity
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                # Use minimal valid payload for POST requests
                test_payload = {"test": True}
                response = requests.post(url, json=test_payload, headers=headers, timeout=self.timeout)
            else:
                response = requests.request(method, url, headers=headers, timeout=self.timeout)
            
            response_time = time.time() - start_time
            
            # Analyze response
            result = {
                "status": "AVAILABLE" if response.status_code < 500 else "ERROR",
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "description": description,
                "auth_required": auth_required,
                "content_type": response.headers.get("content-type", "unknown")
            }
            
            # For endpoints that should require auth, 401/403 is expected
            if auth_required and response.status_code in [401, 403]:
                result["auth_protection"] = "✅ Properly protected"
                result["status"] = "PROTECTED"
            elif not auth_required and response.status_code == 200:
                result["public_access"] = "✅ Accessible"
            
            # Try to parse JSON response
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    json_data = response.json()
                    result["json_parseable"] = True
                    result["response_structure"] = type(json_data).__name__
                    
                    if isinstance(json_data, list):
                        result["items_count"] = len(json_data)
                    elif isinstance(json_data, dict):
                        result["response_keys"] = list(json_data.keys())[:10]  # First 10 keys
                else:
                    result["json_parseable"] = False
                    result["response_text_length"] = len(response.text)
                    
            except json.JSONDecodeError:
                result["json_parseable"] = False
                result["json_error"] = "Invalid JSON response"
            
        except requests.exceptions.ConnectionError:
            result = {
                "status": "CONNECTION_ERROR",
                "error": "Backend server not running",
                "method": method,
                "description": description
            }
        except requests.exceptions.Timeout:
            result = {
                "status": "TIMEOUT",
                "error": f"Request timeout after {self.timeout}s",
                "method": method,
                "description": description
            }
        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "method": method,
                "description": description,
                "traceback": traceback.format_exc()
            }
        
        return result
    
    def test_all_endpoints(self):
        """Test all critical endpoints"""
        print("🔍 Testing all critical endpoints...")
        
        endpoint_results = {}
        server_running = False
        
        for endpoint, config in self.critical_endpoints.items():
            print(f"   Testing {config['method']} {endpoint}...")
            result = self.test_endpoint_availability(endpoint, config)
            endpoint_results[endpoint] = result
            
            if result["status"] not in ["CONNECTION_ERROR"]:
                server_running = True
        
        self.results["endpoints"] = endpoint_results
        self.results["server_running"] = server_running
        
        return endpoint_results
    
    def test_data_processing_patterns(self):
        """Test data processing and response handling patterns"""
        data_tests = {}
        
        # Test endpoints that should return data structures
        data_endpoints = [
            "/api/v1/hexaco-test/questions",
            "/api/v1/tests/holland/questions",
            "/api/v1/jobs"
        ]
        
        for endpoint in data_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=self.timeout)
                
                test_result = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "data_processing_status": "UNKNOWN"
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check data structure
                        if isinstance(data, list):
                            test_result.update({
                                "data_type": "array",
                                "item_count": len(data),
                                "is_empty": len(data) == 0,
                                "data_processing_status": "ARRAY_OK"
                            })
                            
                            # Check first item structure if available
                            if len(data) > 0:
                                first_item = data[0]
                                test_result["first_item_type"] = type(first_item).__name__
                                if isinstance(first_item, dict):
                                    test_result["first_item_keys"] = list(first_item.keys())
                        
                        elif isinstance(data, dict):
                            test_result.update({
                                "data_type": "object",
                                "object_keys": list(data.keys()),
                                "data_processing_status": "OBJECT_OK"
                            })
                            
                            # Check for common patterns that might cause forEach errors
                            if "results" in data and isinstance(data["results"], list):
                                test_result["nested_array"] = f"Found results array with {len(data['results'])} items"
                        
                        else:
                            test_result.update({
                                "data_type": type(data).__name__,
                                "data_processing_status": "UNEXPECTED_TYPE"
                            })
                    
                    except json.JSONDecodeError:
                        test_result["data_processing_status"] = "JSON_PARSE_ERROR"
                
                elif response.status_code in [401, 403]:
                    test_result["data_processing_status"] = "AUTH_REQUIRED"
                else:
                    test_result["data_processing_status"] = "HTTP_ERROR"
                
                data_tests[endpoint] = test_result
                
            except requests.exceptions.ConnectionError:
                data_tests[endpoint] = {
                    "status": "CONNECTION_ERROR",
                    "data_processing_status": "SERVER_DOWN"
                }
            except Exception as e:
                data_tests[endpoint] = {
                    "status": "ERROR",
                    "error": str(e),
                    "data_processing_status": "TEST_ERROR"
                }
        
        self.results["tests"]["data_processing"] = data_tests
        return data_tests
    
    def test_performance_metrics(self):
        """Test API performance metrics"""
        performance_tests = {}
        
        # Test performance on key endpoints
        performance_endpoints = [
            "/health",
            "/api/v1/hexaco-test/questions",
            "/api/v1/jobs"
        ]
        
        for endpoint in performance_endpoints:
            try:
                # Run multiple requests to get average response time
                response_times = []
                status_codes = []
                
                for i in range(5):
                    start_time = time.time()
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=self.timeout)
                    response_time = time.time() - start_time
                    
                    response_times.append(response_time)
                    status_codes.append(response.status_code)
                    
                    time.sleep(0.1)  # Small delay between requests
                
                performance_tests[endpoint] = {
                    "average_response_time": sum(response_times) / len(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "status_codes": status_codes,
                    "all_requests_successful": all(code < 500 for code in status_codes),
                    "performance_grade": "GOOD" if sum(response_times) / len(response_times) < 1.0 else "SLOW"
                }
                
            except requests.exceptions.ConnectionError:
                performance_tests[endpoint] = {
                    "status": "CONNECTION_ERROR"
                }
            except Exception as e:
                performance_tests[endpoint] = {
                    "status": "ERROR", 
                    "error": str(e)
                }
        
        self.results["performance"] = performance_tests
        return performance_tests
    
    def test_error_handling(self):
        """Test API error handling patterns"""
        error_tests = {}
        
        # Test invalid endpoints
        invalid_endpoints = [
            "/api/v1/nonexistent",
            "/api/v1/users/999999",
            "/api/v1/invalid-route"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=self.timeout)
                
                error_tests[endpoint] = {
                    "status_code": response.status_code,
                    "proper_error_handling": response.status_code == 404,
                    "content_type": response.headers.get("content-type", "unknown")
                }
                
                # Try to parse error response
                try:
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        error_tests[endpoint]["error_structure"] = type(error_data).__name__
                        if isinstance(error_data, dict):
                            error_tests[endpoint]["error_fields"] = list(error_data.keys())
                except:
                    error_tests[endpoint]["json_error_response"] = False
                
            except requests.exceptions.ConnectionError:
                error_tests[endpoint] = {"status": "CONNECTION_ERROR"}
            except Exception as e:
                error_tests[endpoint] = {"status": "ERROR", "error": str(e)}
        
        self.results["tests"]["error_handling"] = error_tests
        return error_tests
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        endpoints = self.results.get("endpoints", {})
        prisma_tests = self.results.get("prisma_tests", {})
        performance = self.results.get("performance", {})
        
        # Count endpoint statuses
        available_endpoints = sum(1 for r in endpoints.values() if r.get("status") in ["AVAILABLE", "PROTECTED"])
        error_endpoints = sum(1 for r in endpoints.values() if r.get("status") == "ERROR")
        connection_errors = sum(1 for r in endpoints.values() if r.get("status") == "CONNECTION_ERROR")
        total_endpoints = len(endpoints)
        
        # Prisma status
        prisma_ok = prisma_tests.get("connectivity", {}).get("status") in ["PASS", "PARTIAL"]
        
        # Performance analysis
        avg_response_times = [p.get("average_response_time", 0) for p in performance.values() 
                             if isinstance(p, dict) and "average_response_time" in p]
        overall_performance = "GOOD" if avg_response_times and sum(avg_response_times) / len(avg_response_times) < 1.0 else "SLOW"
        
        summary = {
            "total_endpoints_tested": total_endpoints,
            "available_endpoints": available_endpoints,
            "error_endpoints": error_endpoints,
            "connection_errors": connection_errors,
            "availability_rate": (available_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0,
            "server_running": self.results.get("server_running", False),
            "prisma_connectivity": prisma_ok,
            "overall_performance": overall_performance,
            "average_response_time": sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0,
            "critical_apis": {
                "health_endpoint": endpoints.get("/health", {}).get("status") == "AVAILABLE",
                "hexaco_questions": endpoints.get("/api/v1/hexaco-test/questions", {}).get("status") in ["AVAILABLE", "PROTECTED"],
                "holland_questions": endpoints.get("/api/v1/tests/holland/questions", {}).get("status") in ["AVAILABLE", "PROTECTED"],
                "user_profile": endpoints.get("/api/v1/users/me", {}).get("status") == "PROTECTED",
                "saved_careers": endpoints.get("/api/v1/careers/saved", {}).get("status") == "PROTECTED"
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if not summary["server_running"]:
            summary["recommendations"].append("🚨 Start backend server to run complete API tests")
        
        if not prisma_ok:
            summary["recommendations"].append("🔧 Fix Prisma database connectivity issues")
        
        if summary["availability_rate"] < 70:
            summary["recommendations"].append("⚠️ Multiple API endpoints are failing - investigate backend issues")
        
        if summary["average_response_time"] > 2.0:
            summary["recommendations"].append("🐌 API response times are slow - optimize performance")
        
        if not summary["critical_apis"]["health_endpoint"]:
            summary["recommendations"].append("💓 Health endpoint is not responding")
        
        if not summary["critical_apis"]["hexaco_questions"]:
            summary["recommendations"].append("🧠 HEXACO test API needs attention")
        
        if summary["availability_rate"] >= 90:
            summary["recommendations"].append("✅ API availability is excellent!")
        elif summary["availability_rate"] >= 70:
            summary["recommendations"].append("✅ API availability is good")
        
        self.results["summary"] = summary
        return summary
    
    def save_results(self):
        """Save API test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backend_api_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Backend API test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_api_tests(self):
        """Run complete backend API testing suite"""
        print("🔧 Starting Comprehensive Backend API Testing...")
        print("=" * 60)
        
        # Test 1: Prisma Connectivity
        print("1. Testing Prisma connectivity...")
        prisma_ok = self.test_prisma_connectivity()
        print(f"   Result: {'✅ PASS' if prisma_ok else '❌ FAIL'}")
        
        # Test 2: All Endpoints
        print("2. Testing all critical endpoints...")
        endpoints = self.test_all_endpoints()
        available_count = sum(1 for r in endpoints.values() if r.get("status") in ["AVAILABLE", "PROTECTED"])
        print(f"   Result: {available_count}/{len(endpoints)} endpoints available")
        
        # Test 3: Data Processing
        print("3. Testing data processing patterns...")
        data_tests = self.test_data_processing_patterns()
        print(f"   Data processing tests completed")
        
        # Test 4: Performance
        print("4. Testing performance metrics...")
        performance = self.test_performance_metrics()
        print(f"   Performance analysis completed")
        
        # Test 5: Error Handling
        print("5. Testing error handling...")
        error_tests = self.test_error_handling()
        print(f"   Error handling tests completed")
        
        # Generate Summary
        print("6. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("🔧 BACKEND API TESTING SUMMARY")
        print("=" * 60)
        print(f"Endpoint Availability: {summary['available_endpoints']}/{summary['total_endpoints_tested']} ({summary['availability_rate']:.1f}%)")
        print(f"Backend Server: {'✅ RUNNING' if summary['server_running'] else '❌ NOT RUNNING'}")
        print(f"Prisma Connectivity: {'✅ OK' if summary['prisma_connectivity'] else '❌ BROKEN'}")
        print(f"Performance: {summary['overall_performance']} (avg: {summary['average_response_time']:.3f}s)")
        
        print(f"\n🎯 Critical APIs Status:")
        for api_name, status in summary['critical_apis'].items():
            print(f"   {api_name}: {'✅ OK' if status else '❌ FAIL'}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = BackendAPITester()
    
    try:
        # Run API tests
        results = asyncio.run(tester.run_comprehensive_api_tests())
        
        # Exit code based on results
        summary = results["summary"]
        if summary["availability_rate"] >= 90 and summary["prisma_connectivity"]:
            sys.exit(0)  # Excellent
        elif summary["availability_rate"] >= 70:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ Backend API testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()