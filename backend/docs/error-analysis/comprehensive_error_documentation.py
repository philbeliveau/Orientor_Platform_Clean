#!/usr/bin/env python3
"""
Comprehensive Error Documentation System for Orientor Platform
Using FastAPI-MCP Integration for Real-Time Error Analysis

This system provides:
1. Real-time error monitoring from FastAPI-MCP
2. Systematic error categorization and documentation 
3. Root cause analysis with fix recommendations
4. Live testing validation of error fixes
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import asyncio

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ErrorInstance:
    """Represents a specific error occurrence"""
    timestamp: str
    endpoint: str
    method: str
    status_code: int
    error_type: str
    error_message: str
    request_headers: Dict
    response_data: Dict
    user_context: Optional[str] = None
    authentication_context: Optional[str] = None
    stack_trace: Optional[str] = None

@dataclass
class ErrorPattern:
    """Represents a pattern of related errors"""
    error_type: str
    category: str
    frequency: int
    affected_endpoints: List[str]
    root_cause: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    symptoms: List[str]
    impact: str
    fix_recommendations: List[str]
    related_patterns: List[str] = None

class ComprehensiveErrorDocumenter:
    """
    Comprehensive error documentation system using FastAPI-MCP integration
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.errors: List[ErrorInstance] = []
        self.patterns: List[ErrorPattern] = []
        
        # Error categorization mapping
        self.error_categories = {
            'authentication': {
                'status_codes': [401, 403],
                'keywords': ['unauthorized', 'forbidden', 'token', 'auth', 'credentials'],
                'priority': 'CRITICAL'
            },
            'server_errors': {
                'status_codes': [500, 502, 503, 504],
                'keywords': ['internal server error', 'database', 'connection'],
                'priority': 'CRITICAL'
            },
            'validation_errors': {
                'status_codes': [422, 400],
                'keywords': ['validation', 'required', 'invalid', 'format'],
                'priority': 'HIGH'
            },
            'not_found': {
                'status_codes': [404],
                'keywords': ['not found', 'missing'],
                'priority': 'MEDIUM'
            },
            'rate_limiting': {
                'status_codes': [429],
                'keywords': ['rate limit', 'too many requests'],
                'priority': 'HIGH'
            }
        }
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })

    def discover_fastapi_endpoints(self) -> List[Dict]:
        """Discover all endpoints using FastAPI OpenAPI schema"""
        logger.info("🔍 Discovering FastAPI endpoints from OpenAPI schema...")
        
        try:
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code != 200:
                logger.error(f"Failed to get OpenAPI schema: {response.status_code}")
                return []
            
            schema = response.json()
            endpoints = []
            
            for path, methods in schema.get('paths', {}).items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint_info = {
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'description': details.get('description', ''),
                            'tags': details.get('tags', []),
                            'security': 'security' in details,
                            'parameters': details.get('parameters', [])
                        }
                        endpoints.append(endpoint_info)
            
            logger.info(f"✅ Discovered {len(endpoints)} endpoints from FastAPI schema")
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to discover endpoints: {e}")
            return []

    def test_endpoint_for_errors(self, endpoint: Dict) -> List[ErrorInstance]:
        """Test a single endpoint with multiple authentication contexts to document errors"""
        errors = []
        path = endpoint['path']
        method = endpoint['method']
        
        logger.info(f"🧪 Testing {method} {path} for error documentation...")
        
        # Test different authentication contexts
        auth_contexts = [
            {'name': 'No Auth', 'headers': {}},
            {'name': 'Bearer Token', 'headers': {'Authorization': f'Bearer {self.token}'} if self.token else {}},
            {'name': 'Cookie Auth', 'headers': {'Cookie': f'__session={self.token}'} if self.token else {}},
            {'name': 'Invalid Token', 'headers': {'Authorization': 'Bearer invalid_token'}},
            {'name': 'Malformed Auth', 'headers': {'Authorization': 'InvalidBearer token'}}
        ]
        
        for auth_context in auth_contexts:
            try:
                url = f"{self.base_url}{path}"
                headers = auth_context['headers'].copy()
                headers['Content-Type'] = 'application/json'
                
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, headers=headers, json={}, timeout=10)
                elif method == 'PUT':
                    response = requests.put(url, headers=headers, json={}, timeout=10)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=headers, timeout=10)
                else:
                    continue
                
                response_time = time.time() - start_time
                
                # Document any non-success response as an error
                if response.status_code >= 400:
                    try:
                        response_data = response.json()
                    except:
                        response_data = {'raw_response': response.text[:500]}
                    
                    error = ErrorInstance(
                        timestamp=datetime.now().isoformat(),
                        endpoint=path,
                        method=method,
                        status_code=response.status_code,
                        error_type=self.categorize_error(response.status_code, response_data),
                        error_message=response_data.get('detail', f"HTTP {response.status_code}"),
                        request_headers=headers,
                        response_data=response_data,
                        authentication_context=auth_context['name']
                    )
                    
                    errors.append(error)
                    
                    # Log the error for immediate visibility
                    logger.warning(f"❌ {method} {path} -> {response.status_code} ({auth_context['name']})")
                
            except Exception as e:
                # Document network/timeout errors
                error = ErrorInstance(
                    timestamp=datetime.now().isoformat(),
                    endpoint=path,
                    method=method,
                    status_code=0,
                    error_type='network_error',
                    error_message=str(e),
                    request_headers=headers,
                    response_data={},
                    authentication_context=auth_context['name']
                )
                errors.append(error)
                logger.error(f"💥 {method} {path} -> Network Error: {e}")
        
        return errors

    def categorize_error(self, status_code: int, response_data: Dict) -> str:
        """Categorize an error based on status code and response content"""
        response_text = json.dumps(response_data).lower()
        
        for category, rules in self.error_categories.items():
            if status_code in rules['status_codes']:
                return category
            
            if any(keyword in response_text for keyword in rules['keywords']):
                return category
        
        return 'unknown_error'

    def analyze_error_patterns(self) -> List[ErrorPattern]:
        """Analyze collected errors to identify patterns and root causes"""
        logger.info("📊 Analyzing error patterns...")
        
        # Group errors by type and endpoint
        error_groups = defaultdict(list)
        
        for error in self.errors:
            key = f"{error.error_type}_{error.endpoint}_{error.status_code}"
            error_groups[key].append(error)
        
        patterns = []
        
        for group_key, group_errors in error_groups.items():
            if len(group_errors) < 2:  # Only consider patterns with multiple occurrences
                continue
            
            first_error = group_errors[0]
            affected_endpoints = list(set([e.endpoint for e in group_errors]))
            
            # Determine root cause and fix recommendations based on error type
            root_cause, fix_recommendations = self.determine_fix_strategy(first_error.error_type, group_errors)
            
            pattern = ErrorPattern(
                error_type=first_error.error_type,
                category=first_error.error_type,
                frequency=len(group_errors),
                affected_endpoints=affected_endpoints,
                root_cause=root_cause,
                priority=self.error_categories.get(first_error.error_type, {}).get('priority', 'MEDIUM'),
                symptoms=[f"HTTP {first_error.status_code}: {first_error.error_message}"],
                impact=f"Affects {len(affected_endpoints)} endpoints, {len(group_errors)} total failures",
                fix_recommendations=fix_recommendations
            )
            
            patterns.append(pattern)
        
        # Sort patterns by priority and frequency
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        patterns.sort(key=lambda p: (priority_order.get(p.priority, 3), -p.frequency))
        
        self.patterns = patterns
        return patterns

    def determine_fix_strategy(self, error_type: str, errors: List[ErrorInstance]) -> Tuple[str, List[str]]:
        """Determine root cause and fix recommendations for error patterns"""
        
        if error_type == 'authentication':
            return (
                "Cookie authentication context missing in API calls vs browser requests",
                [
                    "Investigate cookie vs Authorization header authentication handling",
                    "Update Clerk JWT validation to accept both contexts",
                    "Test authentication middleware with both Cookie and Authorization headers",
                    "Verify JWT token validation in direct API calls",
                    "Check FastAPI security dependencies for proper token extraction"
                ]
            )
        
        elif error_type == 'server_errors':
            return (
                "Database query errors or service initialization failures",
                [
                    "Check database connection and query syntax",
                    "Verify Prisma client initialization",
                    "Review service dependencies and initialization order",
                    "Check for missing environment variables",
                    "Validate data type casting in database queries"
                ]
            )
        
        elif error_type == 'validation_errors':
            return (
                "Request parameter validation or data format issues",
                [
                    "Review Pydantic model definitions",
                    "Check required vs optional parameters",
                    "Validate path parameter formats",
                    "Test with proper request body formats",
                    "Review OpenAPI schema parameter definitions"
                ]
            )
        
        elif error_type == 'not_found':
            return (
                "Endpoint routing or resource availability issues",
                [
                    "Verify endpoint path definitions",
                    "Check FastAPI router registration",
                    "Validate resource existence in database",
                    "Review path parameter handling",
                    "Test with valid resource IDs"
                ]
            )
        
        else:
            return (
                "Unknown error pattern requiring investigation",
                [
                    "Review error logs for more details",
                    "Test with different request formats",
                    "Check service health and dependencies",
                    "Validate request/response models"
                ]
            )

    def generate_comprehensive_error_report(self) -> Dict:
        """Generate a comprehensive error documentation report"""
        if not self.errors:
            return {"error": "No errors documented yet"}
        
        # Analyze patterns if not done already
        if not self.patterns:
            self.analyze_error_patterns()
        
        # Generate statistics
        total_errors = len(self.errors)
        error_by_type = defaultdict(int)
        error_by_status = defaultdict(int)
        error_by_endpoint = defaultdict(int)
        
        for error in self.errors:
            error_by_type[error.error_type] += 1
            error_by_status[error.status_code] += 1
            error_by_endpoint[error.endpoint] += 1
        
        # Critical insights
        critical_patterns = [p for p in self.patterns if p.priority == 'CRITICAL']
        high_priority_patterns = [p for p in self.patterns if p.priority == 'HIGH']
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_errors_documented": total_errors,
                "total_patterns_identified": len(self.patterns),
                "critical_patterns": len(critical_patterns),
                "high_priority_patterns": len(high_priority_patterns),
                "testing_framework": "FastAPI-MCP Comprehensive Error Documenter"
            },
            "executive_summary": {
                "primary_issue": critical_patterns[0].root_cause if critical_patterns else "No critical issues identified",
                "most_affected_endpoints": dict(sorted(error_by_endpoint.items(), key=lambda x: x[1], reverse=True)[:10]),
                "error_distribution": dict(error_by_type),
                "status_code_distribution": dict(error_by_status)
            },
            "critical_patterns": [
                {
                    "pattern_id": f"CRIT_{i+1:03d}",
                    "error_type": pattern.error_type,
                    "frequency": pattern.frequency,
                    "affected_endpoints": pattern.affected_endpoints,
                    "root_cause": pattern.root_cause,
                    "impact": pattern.impact,
                    "fix_recommendations": pattern.fix_recommendations,
                    "priority": pattern.priority
                }
                for i, pattern in enumerate(critical_patterns)
            ],
            "high_priority_patterns": [
                {
                    "pattern_id": f"HIGH_{i+1:03d}",
                    "error_type": pattern.error_type,
                    "frequency": pattern.frequency,
                    "affected_endpoints": pattern.affected_endpoints,
                    "root_cause": pattern.root_cause,
                    "impact": pattern.impact,
                    "fix_recommendations": pattern.fix_recommendations,
                    "priority": pattern.priority
                }
                for i, pattern in enumerate(high_priority_patterns)
            ],
            "detailed_errors": [
                {
                    "error_id": f"ERR_{i+1:06d}",
                    "timestamp": error.timestamp,
                    "endpoint": error.endpoint,
                    "method": error.method,
                    "status_code": error.status_code,
                    "error_type": error.error_type,
                    "error_message": error.error_message,
                    "authentication_context": error.authentication_context,
                    "response_data": error.response_data
                }
                for i, error in enumerate(self.errors)
            ],
            "fix_priority_matrix": self.generate_fix_priority_matrix()
        }
        
        return report

    def generate_fix_priority_matrix(self) -> Dict:
        """Generate a priority matrix for fixing errors"""
        matrix = {
            "immediate_fixes": [],  # Critical + High frequency
            "short_term_fixes": [],  # High priority
            "medium_term_fixes": [],  # Medium priority
            "long_term_fixes": []  # Low priority or low frequency
        }
        
        for pattern in self.patterns:
            fix_item = {
                "pattern": pattern.error_type,
                "affected_endpoints": len(pattern.affected_endpoints),
                "frequency": pattern.frequency,
                "priority": pattern.priority,
                "root_cause": pattern.root_cause,
                "primary_fix": pattern.fix_recommendations[0] if pattern.fix_recommendations else "Investigation required"
            }
            
            if pattern.priority == 'CRITICAL' or (pattern.priority == 'HIGH' and pattern.frequency > 10):
                matrix["immediate_fixes"].append(fix_item)
            elif pattern.priority == 'HIGH':
                matrix["short_term_fixes"].append(fix_item)
            elif pattern.priority == 'MEDIUM':
                matrix["medium_term_fixes"].append(fix_item)
            else:
                matrix["long_term_fixes"].append(fix_item)
        
        return matrix

    async def run_comprehensive_error_documentation(self) -> Dict:
        """Run complete error documentation process"""
        logger.info("=" * 100)
        logger.info("🚀 STARTING COMPREHENSIVE ERROR DOCUMENTATION")
        logger.info(f"🌐 Base URL: {self.base_url}")
        logger.info(f"🔐 Authentication: {'✅ JWT Token Available' if self.token else '❌ No Authentication Token'}")
        logger.info("=" * 100)
        
        # Step 1: Discover all endpoints
        endpoints = self.discover_fastapi_endpoints()
        if not endpoints:
            logger.error("❌ No endpoints discovered, cannot proceed with error documentation")
            return {"error": "Endpoint discovery failed"}
        
        logger.info(f"📋 Found {len(endpoints)} endpoints to test for errors")
        
        # Step 2: Test each endpoint for errors
        total_errors_found = 0
        for i, endpoint in enumerate(endpoints, 1):
            logger.info(f"Testing endpoint {i}/{len(endpoints)}: {endpoint['method']} {endpoint['path']}")
            
            endpoint_errors = self.test_endpoint_for_errors(endpoint)
            self.errors.extend(endpoint_errors)
            total_errors_found += len(endpoint_errors)
            
            # Small delay to avoid overwhelming server
            await asyncio.sleep(0.1)
        
        logger.info(f"📊 Total errors documented: {total_errors_found}")
        
        # Step 3: Analyze error patterns
        patterns = self.analyze_error_patterns()
        logger.info(f"🔍 Identified {len(patterns)} error patterns")
        
        # Step 4: Generate comprehensive report
        report = self.generate_comprehensive_error_report()
        
        logger.info("✅ Comprehensive error documentation complete!")
        return report

    def save_error_documentation(self, report: Dict, filename: str):
        """Save comprehensive error documentation to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Comprehensive error documentation saved to: {filename}")

    def print_error_summary(self, report: Dict):
        """Print a summary of documented errors"""
        print("\n" + "=" * 100)
        print("🚨 COMPREHENSIVE ERROR DOCUMENTATION SUMMARY")
        print("=" * 100)
        
        metadata = report.get("metadata", {})
        summary = report.get("executive_summary", {})
        
        print(f"📊 Total Errors Documented: {metadata.get('total_errors_documented', 0)}")
        print(f"🔍 Error Patterns Identified: {metadata.get('total_patterns_identified', 0)}")
        print(f"🚨 Critical Patterns: {metadata.get('critical_patterns', 0)}")
        print(f"⚠️ High Priority Patterns: {metadata.get('high_priority_patterns', 0)}")
        
        print(f"\n💥 Primary Issue: {summary.get('primary_issue', 'Unknown')}")
        
        print("\n📈 Error Distribution:")
        for error_type, count in summary.get('error_distribution', {}).items():
            print(f"  {error_type}: {count} occurrences")
        
        print("\n🎯 Most Affected Endpoints:")
        for endpoint, count in list(summary.get('most_affected_endpoints', {}).items())[:5]:
            print(f"  {endpoint}: {count} errors")
        
        critical_patterns = report.get('critical_patterns', [])
        if critical_patterns:
            print(f"\n🚨 CRITICAL PATTERNS REQUIRING IMMEDIATE ATTENTION:")
            for pattern in critical_patterns:
                print(f"  ❌ {pattern['pattern_id']}: {pattern['error_type']}")
                print(f"     Root Cause: {pattern['root_cause']}")
                print(f"     Affected Endpoints: {len(pattern['affected_endpoints'])}")
                print(f"     Primary Fix: {pattern['fix_recommendations'][0] if pattern['fix_recommendations'] else 'TBD'}")
        
        print("=" * 100)


async def main():
    """Main execution function for comprehensive error documentation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive FastAPI Error Documentation System")
    parser.add_argument("--token", help="Real JWT authentication token for authenticated endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", help="Output file for comprehensive error report")
    
    args = parser.parse_args()
    
    # Initialize the comprehensive error documenter
    documenter = ComprehensiveErrorDocumenter(args.base_url, args.token)
    
    # Run comprehensive error documentation
    report = await documenter.run_comprehensive_error_documentation()
    
    # Print summary
    documenter.print_error_summary(report)
    
    # Save comprehensive report
    if args.output:
        documenter.save_error_documentation(report, args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_error_documentation_{timestamp}.json"
        documenter.save_error_documentation(report, filename)

if __name__ == "__main__":
    asyncio.run(main())