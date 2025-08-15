#!/usr/bin/env python3
"""
Data Processing and Edge Case Testing Suite
Tests data handling, edge cases, error boundaries, and defensive programming patterns
"""

import asyncio
import json
import sys
import traceback
import requests
import time
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class DataProcessingEdgeCaseTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "edge_case_tests": {},
            "data_validation_tests": {},
            "error_boundary_tests": {},
            "defensive_programming_tests": {},
            "summary": {}
        }
        self.backend_url = "http://localhost:8000"
        
        # Test data for various edge cases
        self.edge_case_payloads = {
            "empty_data": {},
            "null_values": {"data": None, "items": None},
            "empty_strings": {"name": "", "description": "", "query": ""},
            "whitespace_only": {"name": "   ", "description": "\n\t", "query": " "},
            "very_long_strings": {
                "name": "a" * 1000,
                "description": "x" * 10000,
                "query": "q" * 500
            },
            "special_characters": {
                "name": "Test's \"Name\" & <script>",
                "description": "Data with special chars: !@#$%^&*()[]{}|\\:;\"'<>?,./ unicode: 🚀💻🎯",
                "query": "SELECT * FROM users; DROP TABLE users; --"
            },
            "unicode_data": {
                "name": "测试数据",
                "description": "Données de test en français with émojis 🇫🇷",
                "query": "Тестовые данные на русском языке"
            },
            "number_edge_cases": {
                "zero": 0,
                "negative": -1,
                "large_number": 999999999999999,
                "float_precision": 0.123456789012345,
                "string_number": "123"
            },
            "array_edge_cases": {
                "empty_array": [],
                "single_item": ["one"],
                "null_items": [None, None, None],
                "mixed_types": [1, "string", None, True, {"nested": "object"}]
            },
            "malformed_json_strings": [
                '{"incomplete": true',
                '{"duplicate": "key", "duplicate": "value2"}',
                '{"trailing": "comma",}',
                '{"unescaped": "quote"inside"}',
                '{invalid: "no quotes on key"}'
            ]
        }
    
    def test_api_data_validation(self):
        """Test API endpoints with various data validation scenarios"""
        print("📊 Testing API data validation...")
        
        validation_results = {}
        
        # Test endpoints that accept data
        test_endpoints = [
            {
                "endpoint": "/api/v1/vector-search",
                "method": "POST",
                "description": "Vector search endpoint"
            },
            {
                "endpoint": "/api/v1/socratic-chat/send", 
                "method": "POST",
                "description": "Socratic chat endpoint"
            },
            {
                "endpoint": "/api/v1/job-chat/send",
                "method": "POST", 
                "description": "Job chat endpoint"
            }
        ]
        
        for endpoint_config in test_endpoints:
            endpoint = endpoint_config["endpoint"]
            method = endpoint_config["method"]
            description = endpoint_config["description"]
            
            print(f"   Testing {endpoint}...")
            
            endpoint_results = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "test_cases": {}
            }
            
            # Test each edge case payload
            for case_name, payload in self.edge_case_payloads.items():
                if isinstance(payload, list):
                    # Skip malformed JSON strings for now
                    continue
                    
                try:
                    response = requests.post(
                        f"{self.backend_url}{endpoint}",
                        json=payload,
                        timeout=10
                    )
                    
                    test_result = {
                        "payload": payload,
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "handled_gracefully": self._is_graceful_error_response(response),
                        "returned_error_info": self._extract_error_info(response)
                    }
                    
                    # Check if response is JSON parseable
                    try:
                        if response.headers.get("content-type", "").startswith("application/json"):
                            response_data = response.json()
                            test_result["json_response"] = True
                            test_result["response_structure"] = type(response_data).__name__
                        else:
                            test_result["json_response"] = False
                    except:
                        test_result["json_response"] = False
                    
                except requests.exceptions.ConnectionError:
                    test_result = {
                        "status": "CONNECTION_ERROR",
                        "payload": payload
                    }
                except requests.exceptions.Timeout:
                    test_result = {
                        "status": "TIMEOUT",
                        "payload": payload,
                        "handled_gracefully": False
                    }
                except Exception as e:
                    test_result = {
                        "status": "ERROR",
                        "error": str(e),
                        "payload": payload,
                        "handled_gracefully": False
                    }
                
                endpoint_results["test_cases"][case_name] = test_result
            
            # Evaluate endpoint's data validation
            endpoint_results["validation_score"] = self._calculate_validation_score(endpoint_results["test_cases"])
            validation_results[endpoint] = endpoint_results
        
        self.results["data_validation_tests"] = validation_results
        return validation_results
    
    def test_array_processing_edge_cases(self):
        """Test endpoints that return arrays for edge case handling"""
        print("🔢 Testing array processing edge cases...")
        
        array_test_results = {}
        
        # Test endpoints that return array data
        array_endpoints = [
            "/api/v1/hexaco-test/questions",
            "/api/v1/tests/holland/questions", 
            "/api/v1/jobs",
            "/api/v1/school-programs"
        ]
        
        for endpoint in array_endpoints:
            print(f"   Testing array processing for {endpoint}...")
            
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                
                test_result = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "data_structure_safe": False,
                    "forEach_safe": False,
                    "null_safe": False,
                    "issues": []
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Test data structure safety
                        if isinstance(data, list):
                            test_result["data_structure_safe"] = True
                            test_result["forEach_safe"] = True  # Arrays are forEach safe
                            test_result["array_length"] = len(data)
                            
                            # Check for null items in array
                            null_items = [i for i, item in enumerate(data) if item is None]
                            test_result["null_items"] = len(null_items)
                            test_result["null_safe"] = len(null_items) == 0
                            
                            if len(null_items) > 0:
                                test_result["issues"].append(f"Array contains {len(null_items)} null items")
                            
                            # Check array item structure consistency
                            if len(data) > 0:
                                first_item_type = type(data[0]).__name__
                                inconsistent_types = [i for i, item in enumerate(data) 
                                                    if type(item).__name__ != first_item_type]
                                
                                if len(inconsistent_types) > 0:
                                    test_result["issues"].append(f"Inconsistent array item types at indices: {inconsistent_types[:5]}")
                                
                                test_result["first_item_type"] = first_item_type
                                test_result["type_consistent"] = len(inconsistent_types) == 0
                        
                        elif isinstance(data, dict):
                            # Check if it's a wrapper object with an array inside
                            array_fields = [key for key, value in data.items() if isinstance(value, list)]
                            
                            if array_fields:
                                test_result["data_structure_safe"] = True
                                test_result["wrapper_object"] = True
                                test_result["array_fields"] = array_fields
                                
                                # Check the first array field
                                first_array = data[array_fields[0]]
                                test_result["forEach_safe"] = True
                                test_result["array_length"] = len(first_array)
                            else:
                                test_result["issues"].append("Expected array or object with array, got object without arrays")
                        
                        else:
                            test_result["issues"].append(f"Expected array data structure, got {type(data).__name__}")
                    
                    except json.JSONDecodeError:
                        test_result["issues"].append("Response is not valid JSON")
                        
                elif response.status_code in [401, 403]:
                    test_result["auth_required"] = True
                    test_result["data_structure_safe"] = True  # Auth error is handled properly
                    
                else:
                    test_result["issues"].append(f"HTTP error: {response.status_code}")
                
                # Calculate safety score
                test_result["safety_score"] = self._calculate_array_safety_score(test_result)
                
            except requests.exceptions.ConnectionError:
                test_result = {
                    "endpoint": endpoint,
                    "status": "CONNECTION_ERROR"
                }
            except Exception as e:
                test_result = {
                    "endpoint": endpoint,
                    "status": "ERROR",
                    "error": str(e),
                    "safety_score": 0
                }
            
            array_test_results[endpoint] = test_result
        
        self.results["edge_case_tests"]["array_processing"] = array_test_results
        return array_test_results
    
    def test_error_boundary_scenarios(self):
        """Test error boundary and error handling scenarios"""
        print("🚫 Testing error boundary scenarios...")
        
        error_boundary_results = {}
        
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "nonexistent_endpoint",
                "method": "GET",
                "endpoint": "/api/v1/nonexistent-endpoint",
                "expected_code": 404
            },
            {
                "name": "invalid_method",
                "method": "DELETE",
                "endpoint": "/api/v1/hexaco-test/questions",
                "expected_code": 405
            },
            {
                "name": "malformed_json",
                "method": "POST",
                "endpoint": "/api/v1/socratic-chat/send",
                "payload": "invalid json data",
                "content_type": "application/json",
                "expected_codes": [400, 422]
            },
            {
                "name": "extremely_large_payload",
                "method": "POST", 
                "endpoint": "/api/v1/vector-search",
                "payload": {"data": "x" * 100000},  # 100KB
                "expected_codes": [413, 400, 422]
            },
            {
                "name": "sql_injection_attempt",
                "method": "POST",
                "endpoint": "/api/v1/vector-search",
                "payload": {"query": "'; DROP TABLE users; --"},
                "expected_codes": [200, 400, 422]  # Should be handled safely
            },
            {
                "name": "xss_payload",
                "method": "POST",
                "endpoint": "/api/v1/socratic-chat/send",
                "payload": {"message": "<script>alert('XSS')</script>"},
                "expected_codes": [200, 400, 422]  # Should be sanitized
            }
        ]
        
        for scenario in error_scenarios:
            scenario_name = scenario["name"]
            print(f"   Testing {scenario_name}...")
            
            try:
                method = scenario["method"]
                endpoint = scenario["endpoint"]
                
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                elif method == "POST":
                    payload = scenario.get("payload", {})
                    if isinstance(payload, str):
                        # Send raw string data
                        headers = {"Content-Type": scenario.get("content_type", "text/plain")}
                        response = requests.post(f"{self.backend_url}{endpoint}", data=payload, headers=headers, timeout=10)
                    else:
                        response = requests.post(f"{self.backend_url}{endpoint}", json=payload, timeout=10)
                else:
                    response = requests.request(method, f"{self.backend_url}{endpoint}", timeout=10)
                
                # Evaluate error handling
                expected_codes = scenario.get("expected_codes", [scenario.get("expected_code")])
                expected_codes = [code for code in expected_codes if code is not None]
                
                error_result = {
                    "scenario": scenario_name,
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "expected_codes": expected_codes,
                    "handled_correctly": response.status_code in expected_codes if expected_codes else True,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "server_crashed": response.status_code >= 500,
                    "content_type": response.headers.get("content-type", "unknown")
                }
                
                # Check if error response provides useful information
                try:
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        error_result["provides_error_details"] = "error" in error_data or "message" in error_data
                        error_result["error_response_structure"] = list(error_data.keys())[:5]
                except:
                    error_result["provides_error_details"] = False
                
                error_result["error_handling_grade"] = self._grade_error_handling(error_result)
                
            except requests.exceptions.ConnectionError:
                error_result = {
                    "scenario": scenario_name,
                    "status": "CONNECTION_ERROR"
                }
            except Exception as e:
                error_result = {
                    "scenario": scenario_name,
                    "status": "ERROR",
                    "error": str(e),
                    "error_handling_grade": "F"
                }
            
            error_boundary_results[scenario_name] = error_result
        
        self.results["error_boundary_tests"] = error_boundary_results
        return error_boundary_results
    
    def test_defensive_programming_patterns(self):
        """Test defensive programming patterns in responses"""
        print("🛡️ Testing defensive programming patterns...")
        
        defensive_results = {}
        
        # Test endpoints for defensive programming patterns
        test_endpoints = [
            "/api/v1/hexaco-test/questions",
            "/api/v1/jobs",
            "/api/v1/school-programs"
        ]
        
        for endpoint in test_endpoints:
            print(f"   Testing defensive patterns for {endpoint}...")
            
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                
                defensive_result = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "defensive_patterns": {
                        "null_safety": False,
                        "array_safety": False,
                        "type_consistency": False,
                        "error_information": False,
                        "graceful_degradation": False
                    },
                    "issues": [],
                    "safety_recommendations": []
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check null safety
                        if self._check_null_safety(data):
                            defensive_result["defensive_patterns"]["null_safety"] = True
                        else:
                            defensive_result["issues"].append("Response contains null values that could cause errors")
                            defensive_result["safety_recommendations"].append("Add null checks and default values")
                        
                        # Check array safety
                        if self._check_array_safety(data):
                            defensive_result["defensive_patterns"]["array_safety"] = True
                        else:
                            defensive_result["issues"].append("Arrays in response could cause forEach errors")
                            defensive_result["safety_recommendations"].append("Ensure arrays are always arrays, never null/undefined")
                        
                        # Check type consistency
                        if self._check_type_consistency(data):
                            defensive_result["defensive_patterns"]["type_consistency"] = True
                        else:
                            defensive_result["issues"].append("Inconsistent data types in response")
                            defensive_result["safety_recommendations"].append("Standardize data types across similar objects")
                        
                        # Overall defensive score
                        patterns = defensive_result["defensive_patterns"]
                        defensive_score = sum(patterns.values()) / len(patterns) * 100
                        defensive_result["defensive_score"] = defensive_score
                        defensive_result["defensive_grade"] = self._grade_defensive_programming(defensive_score)
                        
                    except json.JSONDecodeError:
                        defensive_result["issues"].append("Invalid JSON response")
                        defensive_result["defensive_score"] = 0
                        defensive_result["defensive_grade"] = "F"
                
                elif response.status_code in [401, 403]:
                    defensive_result["defensive_patterns"]["graceful_degradation"] = True
                    defensive_result["defensive_score"] = 80  # Auth errors are handled properly
                    defensive_result["defensive_grade"] = "B"
                    
                else:
                    defensive_result["issues"].append(f"HTTP error {response.status_code}")
                    defensive_result["defensive_score"] = 30
                    defensive_result["defensive_grade"] = "D"
                
            except requests.exceptions.ConnectionError:
                defensive_result = {
                    "endpoint": endpoint,
                    "status": "CONNECTION_ERROR"
                }
            except Exception as e:
                defensive_result = {
                    "endpoint": endpoint,
                    "status": "ERROR",
                    "error": str(e),
                    "defensive_score": 0,
                    "defensive_grade": "F"
                }
            
            defensive_results[endpoint] = defensive_result
        
        self.results["defensive_programming_tests"] = defensive_results
        return defensive_results
    
    def _is_graceful_error_response(self, response) -> bool:
        """Check if error response is handled gracefully"""
        # 4xx errors are client errors (good)
        # 2xx is success (good)
        # 5xx errors indicate server problems (bad)
        return response.status_code < 500
    
    def _extract_error_info(self, response) -> Dict[str, Any]:
        """Extract error information from response"""
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
                return {
                    "has_error_message": "error" in data or "message" in data,
                    "error_fields": [key for key in data.keys() if "error" in key.lower() or "message" in key.lower()]
                }
        except:
            pass
        return {"has_error_message": False, "error_fields": []}
    
    def _calculate_validation_score(self, test_cases: Dict[str, Any]) -> int:
        """Calculate validation score based on test cases"""
        if not test_cases:
            return 0
        
        graceful_responses = sum(1 for case in test_cases.values() 
                               if case.get("handled_gracefully", False))
        total_cases = len(test_cases)
        
        return int((graceful_responses / total_cases) * 100)
    
    def _calculate_array_safety_score(self, test_result: Dict[str, Any]) -> int:
        """Calculate array safety score"""
        score = 0
        
        if test_result.get("data_structure_safe", False):
            score += 30
        if test_result.get("forEach_safe", False):
            score += 30
        if test_result.get("null_safe", False):
            score += 25
        if test_result.get("type_consistent", True):  # Default to True if not checked
            score += 15
        
        return score
    
    def _grade_error_handling(self, error_result: Dict[str, Any]) -> str:
        """Grade error handling quality"""
        if error_result.get("server_crashed", False):
            return "F"
        
        handled_correctly = error_result.get("handled_correctly", False)
        provides_details = error_result.get("provides_error_details", False)
        
        if handled_correctly and provides_details:
            return "A"
        elif handled_correctly:
            return "B"
        elif not error_result.get("server_crashed", True):
            return "C"
        else:
            return "D"
    
    def _check_null_safety(self, data: Any) -> bool:
        """Check if data structure is null-safe"""
        if isinstance(data, list):
            return all(item is not None for item in data)
        elif isinstance(data, dict):
            return all(value is not None for value in data.values())
        return data is not None
    
    def _check_array_safety(self, data: Any) -> bool:
        """Check if arrays in data are safe for forEach operations"""
        if isinstance(data, list):
            return True  # Lists are always forEach safe
        elif isinstance(data, dict):
            # Check that any array values are actually arrays
            for value in data.values():
                if value is None:
                    return False
                if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    if not isinstance(value, list):
                        return False
        return True
    
    def _check_type_consistency(self, data: Any) -> bool:
        """Check type consistency in data structures"""
        if isinstance(data, list) and len(data) > 1:
            first_type = type(data[0])
            return all(type(item) == first_type for item in data[1:])
        return True
    
    def _grade_defensive_programming(self, score: float) -> str:
        """Grade defensive programming quality"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_summary(self):
        """Generate comprehensive data processing and edge case testing summary"""
        validation_tests = self.results.get("data_validation_tests", {})
        edge_case_tests = self.results.get("edge_case_tests", {})
        error_boundary_tests = self.results.get("error_boundary_tests", {})
        defensive_tests = self.results.get("defensive_programming_tests", {})
        
        # Analyze validation test results
        validation_scores = []
        for endpoint_data in validation_tests.values():
            if "validation_score" in endpoint_data:
                validation_scores.append(endpoint_data["validation_score"])
        
        # Analyze array processing safety
        array_tests = edge_case_tests.get("array_processing", {})
        array_safety_scores = [test.get("safety_score", 0) for test in array_tests.values() 
                              if "safety_score" in test]
        
        # Analyze error boundary handling
        error_grades = [test.get("error_handling_grade", "F") for test in error_boundary_tests.values() 
                       if "error_handling_grade" in test]
        
        # Analyze defensive programming
        defensive_scores = [test.get("defensive_score", 0) for test in defensive_tests.values() 
                           if "defensive_score" in test]
        
        summary = {
            "data_validation": {
                "endpoints_tested": len(validation_tests),
                "average_validation_score": sum(validation_scores) / len(validation_scores) if validation_scores else 0,
                "validation_grade": self._score_to_grade(sum(validation_scores) / len(validation_scores) if validation_scores else 0)
            },
            "array_processing_safety": {
                "endpoints_tested": len(array_tests),
                "average_safety_score": sum(array_safety_scores) / len(array_safety_scores) if array_safety_scores else 0,
                "safety_grade": self._score_to_grade(sum(array_safety_scores) / len(array_safety_scores) if array_safety_scores else 0),
                "forEach_safe_endpoints": sum(1 for test in array_tests.values() if test.get("forEach_safe", False))
            },
            "error_boundary_handling": {
                "scenarios_tested": len(error_boundary_tests),
                "error_grades": error_grades,
                "overall_error_grade": self._calculate_overall_grade(error_grades),
                "server_crashes": sum(1 for test in error_boundary_tests.values() if test.get("server_crashed", False))
            },
            "defensive_programming": {
                "endpoints_tested": len(defensive_tests),
                "average_defensive_score": sum(defensive_scores) / len(defensive_scores) if defensive_scores else 0,
                "defensive_grade": self._score_to_grade(sum(defensive_scores) / len(defensive_scores) if defensive_scores else 0),
                "null_safe_endpoints": sum(1 for test in defensive_tests.values() 
                                         if test.get("defensive_patterns", {}).get("null_safety", False))
            },
            "critical_issues": self._identify_critical_issues(validation_tests, array_tests, error_boundary_tests, defensive_tests),
            "recommendations": []
        }
        
        # Generate recommendations
        if summary["data_validation"]["validation_grade"] in ["D", "F"]:
            summary["recommendations"].append("🔧 Improve data validation - many endpoints not handling edge cases properly")
        
        if summary["array_processing_safety"]["safety_grade"] in ["D", "F"]:
            summary["recommendations"].append("🔢 Fix array processing - potential forEach errors detected")
        
        if summary["error_boundary_handling"]["server_crashes"] > 0:
            summary["recommendations"].append("🚨 Fix server crashes - some error scenarios causing 500 errors")
        
        if summary["defensive_programming"]["defensive_grade"] in ["D", "F"]:
            summary["recommendations"].append("🛡️ Implement defensive programming patterns - improve null safety and error handling")
        
        if summary["array_processing_safety"]["forEach_safe_endpoints"] == len(array_tests):
            summary["recommendations"].append("✅ Array processing is safe - no forEach errors detected")
        
        if summary["error_boundary_handling"]["overall_error_grade"] in ["A", "B"]:
            summary["recommendations"].append("✅ Error handling is good - graceful error responses")
        
        if (summary["data_validation"]["validation_grade"] in ["A", "B"] and 
            summary["defensive_programming"]["defensive_grade"] in ["A", "B"]):
            summary["recommendations"].append("✅ Data processing is robust - excellent edge case handling")
        
        self.results["summary"] = summary
        return summary
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _calculate_overall_grade(self, grades: List[str]) -> str:
        """Calculate overall grade from list of individual grades"""
        if not grades:
            return "N/A"
        
        grade_points = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        avg_points = sum(grade_points.get(grade, 0) for grade in grades) / len(grades)
        
        if avg_points >= 3.5:
            return "A"
        elif avg_points >= 2.5:
            return "B"
        elif avg_points >= 1.5:
            return "C"
        elif avg_points >= 0.5:
            return "D"
        else:
            return "F"
    
    def _identify_critical_issues(self, validation_tests, array_tests, error_tests, defensive_tests) -> List[str]:
        """Identify critical issues from test results"""
        issues = []
        
        # Check for forEach safety issues
        unsafe_arrays = [endpoint for endpoint, test in array_tests.items() 
                        if not test.get("forEach_safe", True)]
        if unsafe_arrays:
            issues.append(f"forEach unsafe arrays in endpoints: {', '.join(unsafe_arrays[:3])}")
        
        # Check for server crashes
        crashing_scenarios = [test.get("scenario", "unknown") for test in error_tests.values() 
                             if test.get("server_crashed", False)]
        if crashing_scenarios:
            issues.append(f"Server crashes in scenarios: {', '.join(crashing_scenarios[:3])}")
        
        # Check for null safety issues
        null_unsafe = [endpoint for endpoint, test in defensive_tests.items() 
                      if not test.get("defensive_patterns", {}).get("null_safety", True)]
        if null_unsafe:
            issues.append(f"Null safety issues in endpoints: {', '.join(null_unsafe[:3])}")
        
        return issues
    
    def save_results(self):
        """Save data processing and edge case test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_processing_edge_case_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Data processing and edge case test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_data_tests(self):
        """Run complete data processing and edge case testing suite"""
        print("📊 Starting Comprehensive Data Processing and Edge Case Testing...")
        print("=" * 80)
        
        # Test 1: API Data Validation
        print("1. Testing API data validation...")
        validation_results = self.test_api_data_validation()
        
        # Test 2: Array Processing Edge Cases
        print("2. Testing array processing edge cases...")
        array_results = self.test_array_processing_edge_cases()
        
        # Test 3: Error Boundary Scenarios
        print("3. Testing error boundary scenarios...")
        error_results = self.test_error_boundary_scenarios()
        
        # Test 4: Defensive Programming Patterns
        print("4. Testing defensive programming patterns...")
        defensive_results = self.test_defensive_programming_patterns()
        
        # Generate Summary
        print("5. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 80)
        print("📊 DATA PROCESSING AND EDGE CASE TESTING SUMMARY")
        print("=" * 80)
        
        print(f"🔍 Data Validation:")
        print(f"   Endpoints Tested: {summary['data_validation']['endpoints_tested']}")
        print(f"   Validation Score: {summary['data_validation']['average_validation_score']:.1f}/100")
        print(f"   Validation Grade: {summary['data_validation']['validation_grade']}")
        
        print(f"\n🔢 Array Processing Safety:")
        print(f"   Endpoints Tested: {summary['array_processing_safety']['endpoints_tested']}")
        print(f"   Safety Score: {summary['array_processing_safety']['average_safety_score']:.1f}/100")
        print(f"   Safety Grade: {summary['array_processing_safety']['safety_grade']}")
        print(f"   forEach Safe: {summary['array_processing_safety']['forEach_safe_endpoints']}/{summary['array_processing_safety']['endpoints_tested']}")
        
        print(f"\n🚫 Error Boundary Handling:")
        print(f"   Scenarios Tested: {summary['error_boundary_handling']['scenarios_tested']}")
        print(f"   Overall Grade: {summary['error_boundary_handling']['overall_error_grade']}")
        print(f"   Server Crashes: {summary['error_boundary_handling']['server_crashes']}")
        
        print(f"\n🛡️ Defensive Programming:")
        print(f"   Endpoints Tested: {summary['defensive_programming']['endpoints_tested']}")
        print(f"   Defensive Score: {summary['defensive_programming']['average_defensive_score']:.1f}/100")
        print(f"   Defensive Grade: {summary['defensive_programming']['defensive_grade']}")
        print(f"   Null Safe: {summary['defensive_programming']['null_safe_endpoints']}/{summary['defensive_programming']['endpoints_tested']}")
        
        if summary["critical_issues"]:
            print(f"\n⚠️ Critical Issues:")
            for issue in summary["critical_issues"]:
                print(f"   • {issue}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = DataProcessingEdgeCaseTester()
    
    try:
        # Run data processing tests
        results = asyncio.run(tester.run_comprehensive_data_tests())
        
        # Exit code based on results
        summary = results["summary"]
        critical_issues = len(summary["critical_issues"])
        overall_grades = [
            summary["data_validation"]["validation_grade"],
            summary["array_processing_safety"]["safety_grade"],
            summary["error_boundary_handling"]["overall_error_grade"],
            summary["defensive_programming"]["defensive_grade"]
        ]
        
        grade_points = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        avg_grade = sum(grade_points.get(grade, 0) for grade in overall_grades) / len(overall_grades)
        
        if critical_issues == 0 and avg_grade >= 3.5:
            sys.exit(0)  # Excellent
        elif critical_issues <= 2 and avg_grade >= 2.5:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ Data processing and edge case testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()