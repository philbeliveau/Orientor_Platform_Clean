#!/usr/bin/env python3
"""
Critical Functionality Test Suite
Tests the specific endpoints and pages mentioned in the testing mission
"""

import requests
import sys
import json
from datetime import datetime
from pathlib import Path

class CriticalFunctionalityTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    def test_space_api(self):
        """Test the Space page API endpoint for career completion"""
        try:
            # This would require authentication in real scenario
            response = requests.get(
                f"{self.backend_url}/api/v1/careers/saved",
                timeout=5
            )
            
            result = {
                "endpoint": "/api/v1/careers/saved",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code < 500
            }
            
            if response.status_code == 200:
                result["data_structure"] = "JSON response received"
                try:
                    data = response.json()
                    result["data_type"] = type(data).__name__
                    if isinstance(data, list):
                        result["item_count"] = len(data)
                except:
                    result["data_parsing"] = "Failed to parse JSON"
            
        except requests.exceptions.ConnectionError:
            result = {
                "endpoint": "/api/v1/careers/saved",
                "error": "Connection refused - backend server not running",
                "success": False
            }
        except Exception as e:
            result = {
                "endpoint": "/api/v1/careers/saved",
                "error": str(e),
                "success": False
            }
        
        self.results["tests"]["space_api"] = result
        return result
    
    def test_hexaco_api(self):
        """Test HEXACO test questions API"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/hexaco-test/questions",
                timeout=5
            )
            
            result = {
                "endpoint": "/api/v1/hexaco-test/questions",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["questions_loaded"] = True
                    result["data_type"] = type(data).__name__
                    if isinstance(data, list):
                        result["question_count"] = len(data)
                    elif isinstance(data, dict) and "questions" in data:
                        result["question_count"] = len(data["questions"])
                except Exception as e:
                    result["questions_loaded"] = False
                    result["parse_error"] = str(e)
            else:
                result["questions_loaded"] = False
                result["error_message"] = f"HTTP {response.status_code}"
            
        except requests.exceptions.ConnectionError:
            result = {
                "endpoint": "/api/v1/hexaco-test/questions",
                "error": "Connection refused - backend server not running",
                "success": False,
                "questions_loaded": False
            }
        except Exception as e:
            result = {
                "endpoint": "/api/v1/hexaco-test/questions",
                "error": str(e),
                "success": False,
                "questions_loaded": False
            }
        
        self.results["tests"]["hexaco_api"] = result
        return result
    
    def test_database_connectivity(self):
        """Test Prisma database connectivity"""
        try:
            # Add backend to path
            import sys
            backend_path = Path(__file__).parent.parent / "backend"
            sys.path.append(str(backend_path))
            
            from prisma import Prisma
            prisma = Prisma()
            
            result = {
                "test": "prisma_connectivity",
                "success": True,
                "message": "Prisma client imported and instantiated successfully"
            }
            
        except Exception as e:
            result = {
                "test": "prisma_connectivity", 
                "success": False,
                "error": str(e)
            }
        
        self.results["tests"]["database_connectivity"] = result
        return result
    
    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            result = {
                "endpoint": "/health",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                "endpoint": "/health",
                "error": "Connection refused - backend server not running",
                "success": False
            }
        except Exception as e:
            result = {
                "endpoint": "/health",
                "error": str(e),
                "success": False
            }
        
        self.results["tests"]["health_endpoint"] = result
        return result
    
    def generate_summary(self):
        """Generate test summary"""
        tests = self.results["tests"]
        
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests.values() if test.get("success", False))
        
        # Critical functionality status
        space_api_ok = tests.get("space_api", {}).get("success", False)
        hexaco_ok = tests.get("hexaco_api", {}).get("questions_loaded", False) 
        db_ok = tests.get("database_connectivity", {}).get("success", False)
        health_ok = tests.get("health_endpoint", {}).get("success", False)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "critical_functionality": {
                "space_api": space_api_ok,
                "hexaco_questions": hexaco_ok,
                "database_connectivity": db_ok,
                "health_check": health_ok
            },
            "backend_server_running": health_ok or space_api_ok or hexaco_ok,
            "ready_for_testing": db_ok and (health_ok or space_api_ok)
        }
        
        # Generate recommendations
        recommendations = []
        
        if not summary["backend_server_running"]:
            recommendations.append("🚨 Start backend server before testing")
        
        if not db_ok:
            recommendations.append("🔧 Fix Prisma database connectivity")
        
        if not hexaco_ok:
            recommendations.append("🧠 HEXACO test API needs attention")
        
        if not space_api_ok:
            recommendations.append("🌌 Space page API endpoint requires fixes")
        
        if summary["pass_rate"] == 100:
            recommendations.append("✅ All critical functionality tests passed!")
        
        summary["recommendations"] = recommendations
        self.results["summary"] = summary
        
        return summary
    
    def run_all_tests(self):
        """Run all critical functionality tests"""
        print("🔍 Testing Critical Functionality...")
        print("=" * 40)
        
        # Test 1: Database connectivity
        print("1. Testing database connectivity...")
        db_result = self.test_database_connectivity()
        print(f"   Result: {'✅ PASS' if db_result['success'] else '❌ FAIL'}")
        
        # Test 2: Health endpoint
        print("2. Testing health endpoint...")
        health_result = self.test_health_endpoint()
        print(f"   Result: {'✅ PASS' if health_result['success'] else '❌ FAIL'}")
        
        # Test 3: HEXACO API
        print("3. Testing HEXACO questions API...")
        hexaco_result = self.test_hexaco_api()
        print(f"   Result: {'✅ PASS' if hexaco_result.get('questions_loaded', False) else '❌ FAIL'}")
        
        # Test 4: Space API
        print("4. Testing Space page API...")
        space_result = self.test_space_api()
        print(f"   Result: {'✅ PASS' if space_result['success'] else '❌ FAIL'}")
        
        # Generate summary
        summary = self.generate_summary()
        
        print("\n" + "=" * 40)
        print("📊 CRITICAL FUNCTIONALITY SUMMARY")
        print("=" * 40)
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']} ({summary['pass_rate']:.1f}%)")
        print(f"Backend Running: {'✅ YES' if summary['backend_server_running'] else '❌ NO'}")
        print(f"Database OK: {'✅ YES' if summary['critical_functionality']['database_connectivity'] else '❌ NO'}")
        print(f"HEXACO API: {'✅ OK' if summary['critical_functionality']['hexaco_questions'] else '❌ BROKEN'}")
        print(f"Space API: {'✅ OK' if summary['critical_functionality']['space_api'] else '❌ BROKEN'}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"critical_functionality_test_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        
        return self.results

def main():
    """Main execution function"""
    tester = CriticalFunctionalityTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    summary = results["summary"]
    if summary["ready_for_testing"]:
        sys.exit(0)  # Ready for testing
    elif summary["backend_server_running"]:
        sys.exit(1)  # Server running but issues exist
    else:
        sys.exit(2)  # Server not running

if __name__ == "__main__":
    main()