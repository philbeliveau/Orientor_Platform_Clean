#!/usr/bin/env python3
"""
FastAPI-Focused Comprehensive Endpoint Testing Framework
Real Clerk Authentication + Systematic FastAPI Integration

This approach demonstrates the proper methodology using FastAPI-focused testing
rather than the previous manual requests-based approach.

Usage:
    python fastapi_comprehensive_tester.py --token YOUR_REAL_JWT_TOKEN
    python fastapi_comprehensive_tester.py --auto-discover --token YOUR_TOKEN
"""

import requests
import json
import time
import argparse
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
from urllib.parse import urljoin
import asyncio
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FastAPIEndpoint:
    """Represents a FastAPI endpoint with enhanced metadata"""
    method: str
    path: str
    description: str
    tags: List[str] = None
    requires_auth: bool = True
    expected_status: int = 200
    test_data: Optional[Dict] = None
    critical: bool = False
    parameters: Optional[Dict] = None
    response_model: Optional[str] = None

@dataclass 
class FastAPITestResult:
    """Enhanced test result with FastAPI-specific data"""
    endpoint: FastAPIEndpoint
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    headers: Optional[Dict] = None
    cookies: Optional[Dict] = None

class FastAPIComprehensiveTester:
    """
    FastAPI-focused endpoint testing framework
    
    This approach is superior to the previous manual method because:
    1. Leverages FastAPI's OpenAPI schema for automatic endpoint discovery
    2. Uses both Authorization headers AND cookie authentication
    3. Provides systematic coverage of all endpoints
    4. Tests with real Clerk JWT tokens in both contexts
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.async_client = None
        self.results: List[FastAPITestResult] = []
        self.discovered_endpoints: List[FastAPIEndpoint] = []
        
        # Set headers for both Authorization and Cookie authentication
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cookie': f'__session={self.token}'  # This is what was missing in previous approach!
            })
    
    async def discover_fastapi_endpoints(self) -> List[FastAPIEndpoint]:
        """
        Discover all endpoints from FastAPI's OpenAPI schema
        This is the key advantage over manual endpoint definition
        """
        logger.info("🔍 Discovering FastAPI endpoints from OpenAPI schema...")
        
        try:
            # Get OpenAPI schema from FastAPI
            openapi_response = self.session.get(f"{self.base_url}/openapi.json")
            
            if openapi_response.status_code != 200:
                logger.error(f"Failed to get OpenAPI schema: {openapi_response.status_code}")
                return self.get_fallback_endpoints()
            
            openapi_schema = openapi_response.json()
            endpoints = []
            
            # Parse OpenAPI schema to extract all endpoints
            paths = openapi_schema.get('paths', {})
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        
                        # Extract metadata from OpenAPI schema
                        tags = details.get('tags', [])
                        summary = details.get('summary', '')
                        description = details.get('description', summary)
                        
                        # Determine if authentication is required
                        requires_auth = 'security' in details or any(
                            tag in ['auth', 'user', 'protected'] for tag in tags
                        )
                        
                        # Mark critical endpoints
                        critical = any(keyword in path.lower() or keyword in summary.lower() 
                                     for keyword in ['profile', 'chat', 'test', 'career', 'onboarding'])
                        
                        # Extract parameters
                        parameters = details.get('parameters', [])
                        
                        endpoint = FastAPIEndpoint(
                            method=method.upper(),
                            path=path,
                            description=description or f"{method.upper()} {path}",
                            tags=tags,
                            requires_auth=requires_auth,
                            critical=critical,
                            parameters=parameters
                        )
                        
                        endpoints.append(endpoint)
            
            logger.info(f"✅ Discovered {len(endpoints)} endpoints from OpenAPI schema")
            self.discovered_endpoints = endpoints
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to discover endpoints from OpenAPI: {e}")
            logger.info("Falling back to manual endpoint definition...")
            return self.get_fallback_endpoints()
    
    def get_fallback_endpoints(self) -> List[FastAPIEndpoint]:
        """
        Fallback endpoints if OpenAPI discovery fails
        Based on previous comprehensive analysis but with FastAPI focus
        """
        return [
            # Critical Authentication Endpoints
            FastAPIEndpoint("GET", "/api/v1/profiles/me", "Get current user profile", 
                           tags=["auth", "profile"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/onboarding/status", "Get onboarding status", 
                           tags=["onboarding"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/auth/me", "Get authenticated user", 
                           tags=["auth"], critical=True),
            
            # Assessment System
            FastAPIEndpoint("GET", "/api/v1/tests/holland/questions", "Get Holland test questions", 
                           tags=["assessment"], requires_auth=False, critical=True),
            FastAPIEndpoint("GET", "/api/v1/tests/holland/user-results", "Get Holland test results", 
                           tags=["assessment"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/tests/hexaco/questions", "Get HEXACO test questions", 
                           tags=["assessment"], critical=True),
            
            # Career & Recommendations
            FastAPIEndpoint("GET", "/api/v1/careers/saved", "Get saved careers", 
                           tags=["career"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/careers/recommendations", "Get career recommendations", 
                           tags=["career"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/recommendations", "Get recommendations", 
                           tags=["career"], critical=True),
            
            # Chat System
            FastAPIEndpoint("POST", "/api/v1/chat/send", "Send chat message", 
                           tags=["chat"], critical=True,
                           test_data={"message": "Hello, this is a test message"}),
            FastAPIEndpoint("GET", "/api/v1/chat/conversations", "Get chat conversations", 
                           tags=["chat"], critical=True),
            
            # User Progress & Data
            FastAPIEndpoint("GET", "/user-progress/", "Get user progress", 
                           tags=["progress"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/courses/", "Get user courses", 
                           tags=["education"], critical=True),
            FastAPIEndpoint("GET", "/api/v1/peers/compatible", "Get compatible peers", 
                           tags=["social"], critical=True),
            
            # System Health (No Auth)
            FastAPIEndpoint("GET", "/health", "System health check", 
                           tags=["system"], requires_auth=False),
            FastAPIEndpoint("GET", "/", "Root endpoint", 
                           tags=["system"], requires_auth=False),
        ]
    
    async def test_endpoint(self, endpoint: FastAPIEndpoint) -> FastAPITestResult:
        """
        Test a single endpoint with both Authorization header and Cookie approaches
        This addresses the authentication context issue discovered in previous testing
        """
        url = urljoin(self.base_url, endpoint.path.lstrip('/'))
        start_time = time.time()
        
        logger.info(f"🧪 Testing {endpoint.method} {endpoint.path} - {endpoint.description}")
        
        try:
            # Prepare different authentication approaches
            auth_approaches = []
            
            if endpoint.requires_auth and self.token:
                # Approach 1: Authorization header only (previously failed)
                auth_approaches.append({
                    'name': 'Authorization Header',
                    'headers': {
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json'
                    }
                })
                
                # Approach 2: Cookie only (browser approach)
                auth_approaches.append({
                    'name': 'Cookie Only',
                    'headers': {
                        'Content-Type': 'application/json',
                        'Cookie': f'__session={self.token}'
                    }
                })
                
                # Approach 3: Both (comprehensive approach)
                auth_approaches.append({
                    'name': 'Both Auth + Cookie',
                    'headers': {
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json',
                        'Cookie': f'__session={self.token}'
                    }
                })
            else:
                # No authentication required
                auth_approaches.append({
                    'name': 'No Auth',
                    'headers': {'Content-Type': 'application/json'}
                })
            
            # Test each authentication approach
            best_result = None
            best_status = 999
            
            for approach in auth_approaches:
                try:
                    if endpoint.method == "GET":
                        response = requests.get(url, headers=approach['headers'])
                    elif endpoint.method == "POST":
                        response = requests.post(url, headers=approach['headers'], 
                                               json=endpoint.test_data or {})
                    elif endpoint.method == "PUT":
                        response = requests.put(url, headers=approach['headers'], 
                                              json=endpoint.test_data or {})
                    elif endpoint.method == "DELETE":
                        response = requests.delete(url, headers=approach['headers'])
                    else:
                        continue
                    
                    # Keep the best result (lowest error status code)
                    if response.status_code < best_status:
                        best_status = response.status_code
                        best_result = {
                            'response': response,
                            'approach': approach['name']
                        }
                
                except Exception as e:
                    logger.warning(f"   Auth approach '{approach['name']}' failed: {e}")
                    continue
            
            if not best_result:
                raise Exception("All authentication approaches failed")
            
            response = best_result['response']
            response_time = time.time() - start_time
            
            # Determine success
            success = response.status_code == endpoint.expected_status
            
            # Parse response data
            response_data = None
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500]}
            
            # Create error message if failed
            error_message = None
            if not success:
                error_message = f"Expected {endpoint.expected_status}, got {response.status_code}"
                if response_data and isinstance(response_data, dict) and 'detail' in response_data:
                    error_message += f": {response_data['detail']}"
                error_message += f" (using {best_result['approach']})"
            
            result = FastAPITestResult(
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error_message=error_message,
                response_data=response_data,
                headers=dict(response.headers),
                cookies=dict(response.cookies)
            )
            
            # Log result with authentication context
            status_emoji = "✅" if success else "❌"
            auth_info = f"[{best_result['approach']}]" if endpoint.requires_auth else ""
            logger.info(f"{status_emoji} {endpoint.method} {endpoint.path} -> {response.status_code} {auth_info} ({response_time:.3f}s)")
            
            if not success and endpoint.critical:
                logger.error(f"   🚨 CRITICAL FAILURE: {error_message}")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = f"Request failed: {str(e)}"
            logger.error(f"❌ {endpoint.method} {endpoint.path} -> FAILED: {error_message}")
            
            return FastAPITestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=error_message
            )
    
    async def run_comprehensive_test_suite(self, auto_discover: bool = True) -> Dict:
        """
        Run the complete FastAPI-focused test suite
        """
        logger.info("=" * 100)
        logger.info("🚀 STARTING FASTAPI-FOCUSED COMPREHENSIVE ENDPOINT TESTING")
        logger.info(f"🌐 Base URL: {self.base_url}")
        logger.info(f"🔐 Authentication: {'✅ Real Clerk JWT Token' if self.token else '❌ No Token'}")
        logger.info(f"📊 Discovery Mode: {'🔍 Auto-discover from OpenAPI' if auto_discover else '📋 Manual endpoint list'}")
        logger.info("=" * 100)
        
        # Discover or load endpoints
        if auto_discover:
            endpoints = await self.discover_fastapi_endpoints()
        else:
            endpoints = self.get_fallback_endpoints()
        
        logger.info(f"🎯 Testing {len(endpoints)} endpoints...")
        
        # Test all endpoints
        self.results = []
        for endpoint in endpoints:
            result = await self.test_endpoint(endpoint)
            self.results.append(result)
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        # Generate comprehensive report
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate enhanced report with FastAPI-specific insights"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - passed_tests
        
        # Enhanced categorization
        critical_results = [r for r in self.results if r.endpoint.critical]
        critical_passed = len([r for r in critical_results if r.success])
        critical_total = len(critical_results)
        
        # Authentication analysis
        auth_required = [r for r in self.results if r.endpoint.requires_auth]
        auth_passed = len([r for r in auth_required if r.success])
        auth_total = len(auth_required)
        
        # Tag-based analysis
        tag_analysis = {}
        for result in self.results:
            tags = result.endpoint.tags or ['untagged']
            for tag in tags:
                if tag not in tag_analysis:
                    tag_analysis[tag] = {'total': 0, 'passed': 0}
                tag_analysis[tag]['total'] += 1
                if result.success:
                    tag_analysis[tag]['passed'] += 1
        
        # Error categorization
        auth_failures = [r for r in self.results if not r.success and r.status_code in [401, 403]]
        server_errors = [r for r in self.results if not r.success and r.status_code >= 500]
        client_errors = [r for r in self.results if not r.success and 400 <= r.status_code < 500 and r.status_code not in [401, 403]]
        network_errors = [r for r in self.results if not r.success and r.status_code == 0]
        
        report = {
            "methodology": {
                "approach": "FastAPI-focused comprehensive testing",
                "authentication": "Real Clerk JWT with multiple auth contexts",
                "discovery": "OpenAPI schema-based endpoint discovery",
                "advantages": [
                    "Automatic endpoint discovery from FastAPI OpenAPI schema",
                    "Multiple authentication context testing (header + cookie)",
                    "Enhanced FastAPI-specific metadata extraction",
                    "Systematic coverage without manual endpoint definition"
                ]
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 1),
                "critical_tests": {
                    "total": critical_total,
                    "passed": critical_passed,
                    "success_rate": round((critical_passed / critical_total) * 100, 1) if critical_total > 0 else 0
                },
                "authentication_analysis": {
                    "total_protected": auth_total,
                    "passed_protected": auth_passed,
                    "auth_success_rate": round((auth_passed / auth_total) * 100, 1) if auth_total > 0 else 0
                }
            },
            "failure_analysis": {
                "authentication_failures": len(auth_failures),
                "server_errors": len(server_errors),
                "client_errors": len(client_errors),
                "network_errors": len(network_errors)
            },
            "tag_analysis": {
                tag: {
                    **data,
                    "success_rate": round((data['passed'] / data['total']) * 100, 1)
                }
                for tag, data in tag_analysis.items()
            },
            "endpoint_results": []
        }
        
        # Add detailed results
        for result in self.results:
            result_data = {
                "endpoint": f"{result.endpoint.method} {result.endpoint.path}",
                "description": result.endpoint.description,
                "tags": result.endpoint.tags,
                "status_code": result.status_code,
                "response_time": round(result.response_time, 3),
                "success": result.success,
                "critical": result.endpoint.critical,
                "requires_auth": result.endpoint.requires_auth,
                "error_message": result.error_message
            }
            
            # Include response data for failures
            if not result.success and result.response_data:
                result_data["response_data"] = result.response_data
            
            report["endpoint_results"].append(result_data)
        
        return report
    
    def print_enhanced_summary(self):
        """Print FastAPI-focused summary"""
        if not self.results:
            print("No test results available")
            return
        
        report = self.generate_comprehensive_report()
        summary = report["summary"]
        failures = report["failure_analysis"]
        tags = report["tag_analysis"]
        
        print("\n" + "=" * 100)
        print("🚀 FASTAPI-FOCUSED COMPREHENSIVE TEST SUMMARY")
        print("=" * 100)
        
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']} ({summary['success_rate']}%)")
        print(f"❌ Failed: {summary['failed_tests']}")
        
        if summary['critical_tests']['total'] > 0:
            print(f"🎯 Critical Tests: {summary['critical_tests']['passed']}/{summary['critical_tests']['total']} passed ({summary['critical_tests']['success_rate']}%)")
        
        if summary['authentication_analysis']['total_protected'] > 0:
            print(f"🔐 Protected Endpoints: {summary['authentication_analysis']['passed_protected']}/{summary['authentication_analysis']['total_protected']} passed ({summary['authentication_analysis']['auth_success_rate']}%)")
        
        print("\n📋 Failure Breakdown:")
        print(f"  🔒 Authentication Failures: {failures['authentication_failures']}")
        print(f"  🚨 Server Errors (500+): {failures['server_errors']}")
        print(f"  ⚠️  Client Errors (400-499): {failures['client_errors']}")
        print(f"  🌐 Network Errors: {failures['network_errors']}")
        
        print("\n🏷️ Results by Category:")
        for tag, data in tags.items():
            print(f"  {tag}: {data['passed']}/{data['total']} passed ({data['success_rate']}%)")
        
        # Show critical failures
        critical_failures = [r for r in self.results if r.endpoint.critical and not r.success]
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for result in critical_failures:
                print(f"  ❌ {result.endpoint.method} {result.endpoint.path}")
                print(f"     Status: {result.status_code} | Error: {result.error_message}")
        
        print("=" * 100)
    
    def save_comprehensive_report(self, filename: str):
        """Save detailed FastAPI-focused report"""
        report = self.generate_comprehensive_report()
        report["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "token_provided": bool(self.token),
            "token_preview": self.token[:50] + "..." if self.token else None,
            "discovered_endpoints": len(self.discovered_endpoints),
            "testing_framework": "FastAPI-Focused Comprehensive Tester v2.0"
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Comprehensive FastAPI-focused report saved to: {filename}")

async def main():
    parser = argparse.ArgumentParser(description="FastAPI-Focused Comprehensive Endpoint Testing")
    parser.add_argument("--token", help="Real Clerk JWT authentication token", required=True)
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--auto-discover", action="store_true", help="Auto-discover endpoints from OpenAPI")
    parser.add_argument("--output", help="Output file for detailed report")
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ No authentication token provided.")
        print("Extract token from browser: document.cookie.split(';').find(c => c.includes('__session')).split('=')[1]")
        return
    
    # Initialize FastAPI-focused tester
    tester = FastAPIComprehensiveTester(args.base_url, args.token)
    
    # Run comprehensive testing
    report = await tester.run_comprehensive_test_suite(auto_discover=args.auto_discover)
    
    # Print enhanced summary
    tester.print_enhanced_summary()
    
    # Save comprehensive report
    if args.output:
        tester.save_comprehensive_report(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fastapi_comprehensive_test_report_{timestamp}.json"
        tester.save_comprehensive_report(filename)

if __name__ == "__main__":
    asyncio.run(main())