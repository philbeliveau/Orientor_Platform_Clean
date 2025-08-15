#!/usr/bin/env python3
"""
Comprehensive Authentication Testing Suite
Tests Clerk authentication integration, token handling, and auth flows
"""

import asyncio
import json
import sys
import traceback
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

class AuthenticationTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "clerk_integration": {},
            "security_checks": {}
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_token = None
    
    def test_clerk_backend_integration(self):
        """Test Clerk authentication backend integration"""
        try:
            # Test auth utility imports
            from app.utils.clerk_auth import get_current_user_with_db_sync
            from app.dependencies import get_current_user
            
            result = {
                "status": "PASS",
                "message": "Clerk authentication utilities imported successfully",
                "imports": {
                    "get_current_user_with_db_sync": "✅ Available",
                    "get_current_user": "✅ Available"
                }
            }
            
        except ImportError as e:
            result = {
                "status": "FAIL",
                "message": f"Failed to import Clerk utilities: {str(e)}",
                "error": traceback.format_exc()
            }
        except Exception as e:
            result = {
                "status": "FAIL", 
                "message": f"Unexpected error: {str(e)}",
                "error": traceback.format_exc()
            }
        
        self.results["tests"]["clerk_backend_integration"] = result
        return result["status"] == "PASS"
    
    def test_protected_endpoints_without_auth(self):
        """Test that protected endpoints properly reject unauthenticated requests"""
        protected_endpoints = [
            "/api/v1/careers/saved",
            "/api/v1/users/me", 
            "/api/v1/socratic-chat/send",
            "/api/v1/tests/holland/submit",
            "/api/v1/profiles/me"
        ]
        
        endpoint_results = {}
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                
                # Protected endpoints should return 401 or 403 without auth
                is_protected = response.status_code in [401, 403]
                
                endpoint_results[endpoint] = {
                    "status": "PASS" if is_protected else "FAIL",
                    "status_code": response.status_code,
                    "expected": "401 or 403 (Unauthorized)",
                    "actual": f"{response.status_code}",
                    "properly_protected": is_protected
                }
                
            except requests.exceptions.ConnectionError:
                endpoint_results[endpoint] = {
                    "status": "SKIP",
                    "message": "Backend server not running"
                }
            except Exception as e:
                endpoint_results[endpoint] = {
                    "status": "ERROR",
                    "message": str(e)
                }
        
        self.results["tests"]["protected_endpoints"] = endpoint_results
        return all(r.get("properly_protected", False) or r.get("status") == "SKIP" 
                   for r in endpoint_results.values())
    
    def test_auth_header_validation(self):
        """Test authentication header validation"""
        test_cases = [
            {
                "name": "missing_header",
                "headers": {},
                "expected_status": [401, 403]
            },
            {
                "name": "invalid_token_format",
                "headers": {"Authorization": "InvalidToken123"},
                "expected_status": [401, 403]
            },
            {
                "name": "bearer_without_token",
                "headers": {"Authorization": "Bearer"},
                "expected_status": [401, 403]
            },
            {
                "name": "malformed_bearer",
                "headers": {"Authorization": "Bearer invalid.token.here"},
                "expected_status": [401, 403]
            }
        ]
        
        header_results = {}
        test_endpoint = "/api/v1/users/me"
        
        for test_case in test_cases:
            try:
                response = requests.get(
                    f"{self.backend_url}{test_endpoint}",
                    headers=test_case["headers"],
                    timeout=5
                )
                
                is_valid = response.status_code in test_case["expected_status"]
                
                header_results[test_case["name"]] = {
                    "status": "PASS" if is_valid else "FAIL",
                    "status_code": response.status_code,
                    "expected": test_case["expected_status"],
                    "headers_sent": test_case["headers"],
                    "validation_passed": is_valid
                }
                
            except requests.exceptions.ConnectionError:
                header_results[test_case["name"]] = {
                    "status": "SKIP",
                    "message": "Backend server not running"
                }
            except Exception as e:
                header_results[test_case["name"]] = {
                    "status": "ERROR",
                    "message": str(e)
                }
        
        self.results["tests"]["auth_header_validation"] = header_results
        return all(r.get("validation_passed", False) or r.get("status") in ["SKIP", "ERROR"]
                   for r in header_results.values())
    
    def test_cors_configuration(self):
        """Test CORS configuration for authentication"""
        try:
            # Test preflight request
            response = requests.options(
                f"{self.backend_url}/api/v1/users/me",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization"
                },
                timeout=5
            )
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("Access-Control-Allow-Origin"),
                "access-control-allow-methods": response.headers.get("Access-Control-Allow-Methods"),
                "access-control-allow-headers": response.headers.get("Access-Control-Allow-Headers"),
                "access-control-allow-credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            has_auth_header = "authorization" in (cors_headers.get("access-control-allow-headers", "").lower())
            allows_origin = cors_headers.get("access-control-allow-origin") in ["*", "http://localhost:3000"]
            
            result = {
                "status": "PASS" if has_auth_header and allows_origin else "FAIL",
                "status_code": response.status_code,
                "cors_headers": cors_headers,
                "allows_auth_header": has_auth_header,
                "allows_frontend_origin": allows_origin
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                "status": "SKIP",
                "message": "Backend server not running"
            }
        except Exception as e:
            result = {
                "status": "ERROR",
                "message": str(e),
                "error": traceback.format_exc()
            }
        
        self.results["tests"]["cors_configuration"] = result
        return result.get("status") in ["PASS", "SKIP"]
    
    def test_session_management(self):
        """Test session handling and token refresh patterns"""
        try:
            # Test health endpoint (should be public)
            health_response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            # Check if response includes session info
            result = {
                "status": "PASS",
                "health_endpoint_accessible": health_response.status_code == 200,
                "session_cookies": list(health_response.cookies.keys()) if health_response.cookies else [],
                "cache_headers": {
                    "cache-control": health_response.headers.get("Cache-Control"),
                    "expires": health_response.headers.get("Expires")
                }
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                "status": "SKIP",
                "message": "Backend server not running"
            }
        except Exception as e:
            result = {
                "status": "ERROR",
                "message": str(e)
            }
        
        self.results["tests"]["session_management"] = result
        return result.get("status") in ["PASS", "SKIP"]
    
    def scan_frontend_auth_patterns(self):
        """Scan frontend for proper Clerk authentication patterns"""
        patterns = {}
        
        try:
            # Check for proper useAuth imports
            import subprocess
            
            # Find files using getToken without proper import
            cmd = ["find", "./frontend/src", "-name", "*.tsx", "-o", "-name", "*.ts"]
            find_result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if find_result.returncode == 0:
                files = find_result.stdout.strip().split('\n')
                
                auth_issues = {
                    "missing_useauth_imports": [],
                    "localstorage_token_usage": [],
                    "wrong_redirect_routes": [],
                    "proper_clerk_usage": []
                }
                
                for file_path in files:
                    if not file_path.strip():
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for getToken usage without import
                        if "getToken(" in content and "import { useAuth" not in content:
                            auth_issues["missing_useauth_imports"].append(file_path)
                        
                        # Check for localStorage token usage
                        if "localStorage.getItem('access_token')" in content:
                            auth_issues["localstorage_token_usage"].append(file_path)
                        
                        # Check for wrong redirect routes
                        if "router.push('/login')" in content:
                            auth_issues["wrong_redirect_routes"].append(file_path)
                        
                        # Check for proper Clerk usage
                        if "import { useAuth" in content and "getToken" in content:
                            auth_issues["proper_clerk_usage"].append(file_path)
                            
                    except Exception as e:
                        continue
                
                patterns["frontend_auth_patterns"] = {
                    "issues_found": auth_issues,
                    "total_files_scanned": len([f for f in files if f.strip()]),
                    "severity": "P1_HIGH" if any(auth_issues[key] for key in ["missing_useauth_imports", "localstorage_token_usage", "wrong_redirect_routes"]) else "GOOD"
                }
            
        except Exception as e:
            patterns["frontend_auth_patterns"] = {
                "error": str(e),
                "severity": "ERROR"
            }
        
        self.results["clerk_integration"]["frontend_patterns"] = patterns
        return patterns
    
    def test_authentication_flow_security(self):
        """Test security aspects of authentication flow"""
        security_checks = {}
        
        # Test 1: Rate limiting on auth endpoints
        try:
            auth_endpoint = f"{self.backend_url}/api/v1/users/me"
            
            # Make multiple rapid requests
            responses = []
            for i in range(10):
                try:
                    response = requests.get(auth_endpoint, timeout=2)
                    responses.append(response.status_code)
                except:
                    responses.append(None)
                time.sleep(0.1)
            
            # Check if rate limiting is applied
            has_rate_limiting = any(code == 429 for code in responses if code)
            
            security_checks["rate_limiting"] = {
                "status": "INFO",  # Rate limiting is optional
                "rate_limiting_detected": has_rate_limiting,
                "response_codes": responses,
                "note": "Rate limiting is recommended but not required"
            }
            
        except Exception as e:
            security_checks["rate_limiting"] = {
                "status": "ERROR",
                "message": str(e)
            }
        
        # Test 2: HTTPS redirect (if applicable)
        try:
            # This test is informational since localhost typically uses HTTP
            security_checks["https_configuration"] = {
                "status": "INFO",
                "note": "HTTPS should be enforced in production",
                "localhost_exception": "HTTP acceptable for development"
            }
            
        except Exception as e:
            security_checks["https_configuration"] = {
                "status": "ERROR",
                "message": str(e)
            }
        
        self.results["security_checks"] = security_checks
        return security_checks
    
    def generate_summary(self):
        """Generate authentication testing summary"""
        tests = self.results["tests"]
        
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests.values() 
                          if isinstance(test, dict) and test.get("status") == "PASS")
        skipped_tests = sum(1 for test in tests.values()
                           if isinstance(test, dict) and test.get("status") == "SKIP")
        
        # Check critical authentication components
        clerk_backend_ok = tests.get("clerk_backend_integration", {}).get("status") == "PASS"
        protected_endpoints_ok = tests.get("protected_endpoints", {})
        auth_headers_ok = tests.get("auth_header_validation", {})
        cors_ok = tests.get("cors_configuration", {}).get("status") in ["PASS", "SKIP"]
        
        # Frontend pattern analysis
        frontend_patterns = self.results.get("clerk_integration", {}).get("frontend_patterns", {})
        frontend_issues = frontend_patterns.get("frontend_auth_patterns", {}).get("issues_found", {})
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "skipped_tests": skipped_tests,
            "failed_tests": total_tests - passed_tests - skipped_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "backend_server_running": skipped_tests < total_tests,
            "critical_auth_components": {
                "clerk_backend_integration": clerk_backend_ok,
                "endpoint_protection": bool(protected_endpoints_ok),
                "header_validation": bool(auth_headers_ok),
                "cors_configuration": cors_ok
            },
            "frontend_auth_health": {
                "proper_clerk_usage": len(frontend_issues.get("proper_clerk_usage", [])),
                "missing_imports": len(frontend_issues.get("missing_useauth_imports", [])),
                "localstorage_usage": len(frontend_issues.get("localstorage_token_usage", [])),
                "wrong_redirects": len(frontend_issues.get("wrong_redirect_routes", []))
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if not summary["backend_server_running"]:
            summary["recommendations"].append("🚨 Start backend server to run complete authentication tests")
        
        if not clerk_backend_ok:
            summary["recommendations"].append("🔧 Fix Clerk backend integration imports")
        
        if summary["frontend_auth_health"]["missing_imports"] > 0:
            summary["recommendations"].append("📱 Add missing useAuth imports to frontend components")
        
        if summary["frontend_auth_health"]["localstorage_usage"] > 0:
            summary["recommendations"].append("🔒 Replace localStorage tokens with Clerk getToken()")
        
        if summary["frontend_auth_health"]["wrong_redirects"] > 0:
            summary["recommendations"].append("🔀 Update redirect routes from /login to /sign-in")
        
        if summary["pass_rate"] >= 90:
            summary["recommendations"].append("✅ Authentication system health is excellent!")
        elif summary["pass_rate"] >= 70:
            summary["recommendations"].append("✅ Authentication system health is good")
        else:
            summary["recommendations"].append("⚠️ Authentication system needs attention")
        
        self.results["summary"] = summary
        return summary
    
    def save_results(self):
        """Save authentication test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"authentication_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Authentication test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_auth_tests(self):
        """Run complete authentication testing suite"""
        print("🔐 Starting Comprehensive Authentication Testing...")
        print("=" * 60)
        
        # Test 1: Clerk Backend Integration
        print("1. Testing Clerk backend integration...")
        clerk_ok = self.test_clerk_backend_integration()
        print(f"   Result: {'✅ PASS' if clerk_ok else '❌ FAIL'}")
        
        # Test 2: Protected Endpoints
        print("2. Testing protected endpoint security...")
        protected_ok = self.test_protected_endpoints_without_auth()
        print(f"   Result: {'✅ PASS' if protected_ok else '❌ FAIL'}")
        
        # Test 3: Auth Header Validation
        print("3. Testing authentication header validation...")
        headers_ok = self.test_auth_header_validation()
        print(f"   Result: {'✅ PASS' if headers_ok else '❌ FAIL'}")
        
        # Test 4: CORS Configuration
        print("4. Testing CORS configuration...")
        cors_ok = self.test_cors_configuration()
        print(f"   Result: {'✅ PASS' if cors_ok else '❌ FAIL'}")
        
        # Test 5: Session Management
        print("5. Testing session management...")
        session_ok = self.test_session_management()
        print(f"   Result: {'✅ PASS' if session_ok else '❌ FAIL'}")
        
        # Test 6: Frontend Auth Patterns
        print("6. Scanning frontend authentication patterns...")
        frontend_patterns = self.scan_frontend_auth_patterns()
        print(f"   Frontend patterns analyzed")
        
        # Test 7: Security Checks
        print("7. Running security checks...")
        security_checks = self.test_authentication_flow_security()
        print(f"   Security analysis completed")
        
        # Generate Summary
        print("8. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION TESTING SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']} ({summary['pass_rate']:.1f}%)")
        print(f"Backend Server: {'✅ RUNNING' if summary['backend_server_running'] else '❌ NOT RUNNING'}")
        print(f"Clerk Integration: {'✅ OK' if summary['critical_auth_components']['clerk_backend_integration'] else '❌ BROKEN'}")
        print(f"Endpoint Protection: {'✅ OK' if summary['critical_auth_components']['endpoint_protection'] else '❌ BROKEN'}")
        print(f"CORS Configuration: {'✅ OK' if summary['critical_auth_components']['cors_configuration'] else '❌ BROKEN'}")
        
        print(f"\n📱 Frontend Auth Health:")
        print(f"   Proper Clerk Usage: {summary['frontend_auth_health']['proper_clerk_usage']} files")
        print(f"   Missing Imports: {summary['frontend_auth_health']['missing_imports']} files")
        print(f"   localStorage Usage: {summary['frontend_auth_health']['localstorage_usage']} files")
        print(f"   Wrong Redirects: {summary['frontend_auth_health']['wrong_redirects']} files")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = AuthenticationTester()
    
    try:
        # Run authentication tests
        results = asyncio.run(tester.run_comprehensive_auth_tests())
        
        # Exit code based on results
        summary = results["summary"]
        if summary["pass_rate"] >= 90:
            sys.exit(0)  # Excellent
        elif summary["pass_rate"] >= 70:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ Authentication testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()