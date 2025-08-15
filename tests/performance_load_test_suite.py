#!/usr/bin/env python3
"""
Performance and Load Testing Suite
Tests API performance, response times, concurrency handling, and system load capacity
"""

import asyncio
import json
import sys
import traceback
import requests
import time
import threading
import statistics
import psutil
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class PerformanceLoadTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "performance_tests": {},
            "load_tests": {},
            "stress_tests": {},
            "memory_tests": {},
            "concurrency_tests": {},
            "summary": {}
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
        # Test configuration
        self.test_config = {
            "light_load": {"users": 5, "requests_per_user": 10, "duration": 30},
            "medium_load": {"users": 20, "requests_per_user": 25, "duration": 60},
            "heavy_load": {"users": 50, "requests_per_user": 50, "duration": 120},
            "stress_test": {"users": 100, "requests_per_user": 100, "duration": 180}
        }
        
        # Critical endpoints for performance testing
        self.performance_endpoints = {
            "/health": {"method": "GET", "timeout": 5, "expected_ms": 100},
            "/api/v1/hexaco-test/questions": {"method": "GET", "timeout": 10, "expected_ms": 500},
            "/api/v1/tests/holland/questions": {"method": "GET", "timeout": 10, "expected_ms": 500},
            "/api/v1/jobs": {"method": "GET", "timeout": 15, "expected_ms": 1000},
            "/api/v1/school-programs": {"method": "GET", "timeout": 15, "expected_ms": 1000},
            "/api/v1/vector-search": {"method": "POST", "timeout": 20, "expected_ms": 2000}
        }
    
    def test_single_endpoint_performance(self, endpoint: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test performance of a single endpoint"""
        method = config.get("method", "GET")
        timeout = config.get("timeout", 10)
        expected_ms = config.get("expected_ms", 1000)
        
        response_times = []
        status_codes = []
        errors = []
        
        # Run multiple requests to get statistical data
        num_requests = 20
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=timeout)
                elif method == "POST":
                    # Use minimal test payload
                    payload = {"test": True, "query": "performance test"}
                    response = requests.post(f"{self.backend_url}{endpoint}", json=payload, timeout=timeout)
                else:
                    response = requests.request(method, f"{self.backend_url}{endpoint}", timeout=timeout)
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                # Small delay between requests
                time.sleep(0.1)
                
            except requests.exceptions.Timeout:
                errors.append(f"Request {i+1}: Timeout")
                response_times.append(timeout * 1000)  # Record timeout as max time
            except requests.exceptions.ConnectionError:
                errors.append(f"Request {i+1}: Connection error")
                return {
                    "endpoint": endpoint,
                    "status": "CONNECTION_ERROR",
                    "error": "Backend server not running"
                }
            except Exception as e:
                errors.append(f"Request {i+1}: {str(e)}")
        
        # Calculate statistics
        if response_times:
            stats = {
                "min_ms": min(response_times),
                "max_ms": max(response_times),
                "avg_ms": statistics.mean(response_times),
                "median_ms": statistics.median(response_times),
                "p95_ms": self._calculate_percentile(response_times, 95),
                "p99_ms": self._calculate_percentile(response_times, 99),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
            
            # Performance evaluation
            performance_grade = self._evaluate_performance(stats["avg_ms"], expected_ms)
            consistency_grade = self._evaluate_consistency(stats["std_dev"], stats["avg_ms"])
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status": "COMPLETED",
                "requests_sent": num_requests,
                "successful_requests": len([code for code in status_codes if code < 500]),
                "error_count": len(errors),
                "statistics": stats,
                "performance_grade": performance_grade,
                "consistency_grade": consistency_grade,
                "meets_expectations": stats["avg_ms"] <= expected_ms,
                "errors": errors[:5]  # First 5 errors only
            }
        else:
            result = {
                "endpoint": endpoint,
                "status": "FAILED",
                "error": "No successful requests"
            }
        
        return result
    
    def test_all_endpoint_performance(self):
        """Test performance of all critical endpoints"""
        print("⚡ Testing individual endpoint performance...")
        
        endpoint_results = {}
        
        for endpoint, config in self.performance_endpoints.items():
            print(f"   Testing {config['method']} {endpoint}...")
            result = self.test_single_endpoint_performance(endpoint, config)
            endpoint_results[endpoint] = result
            
            if result.get("status") == "COMPLETED":
                avg_ms = result["statistics"]["avg_ms"]
                grade = result["performance_grade"]
                print(f"     Result: {avg_ms:.1f}ms avg (Grade: {grade})")
            else:
                print(f"     Result: {result.get('status', 'UNKNOWN')}")
        
        self.results["performance_tests"]["individual_endpoints"] = endpoint_results
        return endpoint_results
    
    def test_concurrent_load(self, test_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test concurrent load on the system"""
        users = config["users"]
        requests_per_user = config["requests_per_user"]
        duration = config["duration"]
        
        print(f"   Running {test_name}: {users} users, {requests_per_user} req/user, {duration}s duration...")
        
        # Metrics collection
        start_time = time.time()
        all_response_times = []
        all_status_codes = []
        errors = []
        requests_sent = 0
        
        # Monitor system resources during test
        initial_memory = psutil.virtual_memory().percent
        initial_cpu = psutil.cpu_percent(interval=1)
        
        def user_simulation(user_id: int) -> List[float]:
            """Simulate a single user making requests"""
            user_response_times = []
            user_start = time.time()
            
            for request_num in range(requests_per_user):
                if time.time() - user_start > duration:
                    break
                
                try:
                    # Test the health endpoint for load testing
                    request_start = time.time()
                    response = requests.get(f"{self.backend_url}/health", timeout=10)
                    response_time = (time.time() - request_start) * 1000
                    
                    user_response_times.append(response_time)
                    all_status_codes.append(response.status_code)
                    
                    # Random delay between requests (0.1 to 0.5 seconds)
                    delay = 0.1 + (request_num % 5) * 0.1
                    time.sleep(delay)
                    
                except Exception as e:
                    errors.append(f"User {user_id}, Request {request_num}: {str(e)}")
            
            return user_response_times
        
        # Run concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=users) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(users)]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    user_times = future.result()
                    all_response_times.extend(user_times)
                    requests_sent += len(user_times)
                except Exception as e:
                    errors.append(f"User thread error: {str(e)}")
        
        # Final system metrics
        final_memory = psutil.virtual_memory().percent
        final_cpu = psutil.cpu_percent(interval=1)
        total_duration = time.time() - start_time
        
        # Calculate load test statistics
        if all_response_times:
            load_stats = {
                "total_requests": requests_sent,
                "total_duration_s": total_duration,
                "requests_per_second": requests_sent / total_duration if total_duration > 0 else 0,
                "avg_response_ms": statistics.mean(all_response_times),
                "median_response_ms": statistics.median(all_response_times),
                "p95_response_ms": self._calculate_percentile(all_response_times, 95),
                "p99_response_ms": self._calculate_percentile(all_response_times, 99),
                "min_response_ms": min(all_response_times),
                "max_response_ms": max(all_response_times),
                "error_rate": len(errors) / (requests_sent + len(errors)) * 100 if (requests_sent + len(errors)) > 0 else 0,
                "successful_requests": len([code for code in all_status_codes if code < 500]),
                "system_impact": {
                    "memory_change_percent": final_memory - initial_memory,
                    "cpu_usage_initial": initial_cpu,
                    "cpu_usage_final": final_cpu
                }
            }
            
            # Evaluate load test performance
            load_grade = self._evaluate_load_performance(load_stats)
            
            result = {
                "test_name": test_name,
                "config": config,
                "status": "COMPLETED",
                "statistics": load_stats,
                "load_grade": load_grade,
                "errors_sample": errors[:10],  # First 10 errors
                "system_stable": load_stats["error_rate"] < 5.0 and final_memory < 90
            }
        else:
            result = {
                "test_name": test_name,
                "config": config,
                "status": "FAILED",
                "error": "No successful requests during load test"
            }
        
        return result
    
    def test_memory_usage_patterns(self):
        """Test memory usage patterns during normal operations"""
        print("🧠 Testing memory usage patterns...")
        
        try:
            # Monitor memory for different operation types
            memory_tests = {}
            
            # Baseline memory
            baseline_memory = psutil.virtual_memory().percent
            
            # Test 1: Multiple API calls
            memory_before = psutil.virtual_memory().percent
            for i in range(50):
                try:
                    requests.get(f"{self.backend_url}/health", timeout=5)
                    time.sleep(0.1)
                except:
                    pass
            memory_after = psutil.virtual_memory().percent
            
            memory_tests["api_calls"] = {
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_change": memory_after - memory_before,
                "test_description": "50 API calls to health endpoint"
            }
            
            # Test 2: Data-heavy endpoints
            memory_before = psutil.virtual_memory().percent
            try:
                requests.get(f"{self.backend_url}/api/v1/jobs", timeout=10)
                requests.get(f"{self.backend_url}/api/v1/hexaco-test/questions", timeout=10)
                requests.get(f"{self.backend_url}/api/v1/school-programs", timeout=10)
            except:
                pass
            memory_after = psutil.virtual_memory().percent
            
            memory_tests["data_heavy"] = {
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_change": memory_after - memory_before,
                "test_description": "Data-heavy endpoint requests"
            }
            
            # Overall assessment
            max_memory_change = max([test.get("memory_change", 0) for test in memory_tests.values()])
            current_memory = psutil.virtual_memory().percent
            
            result = {
                "baseline_memory_percent": baseline_memory,
                "current_memory_percent": current_memory,
                "tests": memory_tests,
                "max_memory_change": max_memory_change,
                "memory_grade": self._evaluate_memory_usage(current_memory, max_memory_change),
                "memory_stable": current_memory < 85 and max_memory_change < 10
            }
            
        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "memory_stable": False
            }
        
        self.results["memory_tests"] = result
        return result
    
    def test_stress_scenarios(self):
        """Test system behavior under stress"""
        print("💪 Testing stress scenarios...")
        
        stress_results = {}
        
        # Stress Test 1: Rapid fire requests
        print("   Testing rapid fire requests...")
        rapid_fire_start = time.time()
        rapid_fire_errors = 0
        rapid_fire_times = []
        
        for i in range(100):
            try:
                start = time.time()
                response = requests.get(f"{self.backend_url}/health", timeout=2)
                response_time = (time.time() - start) * 1000
                rapid_fire_times.append(response_time)
                
                if response.status_code >= 500:
                    rapid_fire_errors += 1
            except:
                rapid_fire_errors += 1
        
        rapid_fire_duration = time.time() - rapid_fire_start
        
        stress_results["rapid_fire"] = {
            "requests_sent": 100,
            "errors": rapid_fire_errors,
            "duration_s": rapid_fire_duration,
            "avg_response_ms": statistics.mean(rapid_fire_times) if rapid_fire_times else 0,
            "requests_per_second": 100 / rapid_fire_duration if rapid_fire_duration > 0 else 0,
            "error_rate": rapid_fire_errors / 100 * 100,
            "survived_stress": rapid_fire_errors < 20
        }
        
        # Stress Test 2: Large payload (if applicable)
        print("   Testing large payload handling...")
        try:
            large_payload = {"data": "x" * 10000, "test": True}  # 10KB payload
            start = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/vector-search",
                json=large_payload,
                timeout=15
            )
            response_time = (time.time() - start) * 1000
            
            stress_results["large_payload"] = {
                "payload_size_kb": len(json.dumps(large_payload)) / 1024,
                "response_time_ms": response_time,
                "status_code": response.status_code,
                "handled_successfully": response.status_code < 500,
                "within_timeout": response_time < 15000
            }
            
        except Exception as e:
            stress_results["large_payload"] = {
                "status": "ERROR",
                "error": str(e),
                "handled_successfully": False
            }
        
        self.results["stress_tests"] = stress_results
        return stress_results
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate the nth percentile of a dataset"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _evaluate_performance(self, avg_ms: float, expected_ms: float) -> str:
        """Evaluate performance grade based on response time"""
        if avg_ms <= expected_ms * 0.5:
            return "A"
        elif avg_ms <= expected_ms:
            return "B"
        elif avg_ms <= expected_ms * 1.5:
            return "C"
        elif avg_ms <= expected_ms * 2:
            return "D"
        else:
            return "F"
    
    def _evaluate_consistency(self, std_dev: float, avg_ms: float) -> str:
        """Evaluate consistency grade based on standard deviation"""
        if avg_ms == 0:
            return "N/A"
        
        coefficient_of_variation = (std_dev / avg_ms) * 100
        
        if coefficient_of_variation <= 10:
            return "A"
        elif coefficient_of_variation <= 20:
            return "B"
        elif coefficient_of_variation <= 30:
            return "C"
        elif coefficient_of_variation <= 50:
            return "D"
        else:
            return "F"
    
    def _evaluate_load_performance(self, stats: Dict[str, Any]) -> str:
        """Evaluate load test performance"""
        error_rate = stats.get("error_rate", 100)
        avg_response = stats.get("avg_response_ms", 10000)
        p95_response = stats.get("p95_response_ms", 10000)
        
        # Grade based on multiple factors
        grade_points = 0
        
        # Error rate scoring (40 points max)
        if error_rate <= 1:
            grade_points += 40
        elif error_rate <= 3:
            grade_points += 30
        elif error_rate <= 5:
            grade_points += 20
        elif error_rate <= 10:
            grade_points += 10
        
        # Average response time scoring (30 points max)
        if avg_response <= 500:
            grade_points += 30
        elif avg_response <= 1000:
            grade_points += 20
        elif avg_response <= 2000:
            grade_points += 10
        elif avg_response <= 5000:
            grade_points += 5
        
        # P95 response time scoring (30 points max)
        if p95_response <= 1000:
            grade_points += 30
        elif p95_response <= 2000:
            grade_points += 20
        elif p95_response <= 5000:
            grade_points += 10
        elif p95_response <= 10000:
            grade_points += 5
        
        # Convert to letter grade
        if grade_points >= 90:
            return "A"
        elif grade_points >= 80:
            return "B"
        elif grade_points >= 70:
            return "C"
        elif grade_points >= 60:
            return "D"
        else:
            return "F"
    
    def _evaluate_memory_usage(self, current_memory: float, max_change: float) -> str:
        """Evaluate memory usage grade"""
        if current_memory >= 95:
            return "F"
        elif current_memory >= 90:
            return "D"
        elif current_memory >= 80:
            return "C"
        elif current_memory >= 70:
            return "B"
        else:
            return "A"
    
    def generate_summary(self):
        """Generate comprehensive performance testing summary"""
        performance_tests = self.results.get("performance_tests", {})
        load_tests = self.results.get("load_tests", {})
        stress_tests = self.results.get("stress_tests", {})
        memory_tests = self.results.get("memory_tests", {})
        
        # Analyze individual endpoint performance
        endpoint_results = performance_tests.get("individual_endpoints", {})
        endpoint_grades = [result.get("performance_grade", "F") for result in endpoint_results.values() 
                          if result.get("status") == "COMPLETED"]
        
        avg_response_times = [result["statistics"]["avg_ms"] for result in endpoint_results.values() 
                             if result.get("status") == "COMPLETED"]
        
        # Analyze load test results
        load_test_results = load_tests
        load_grades = [result.get("load_grade", "F") for result in load_test_results.values() 
                      if result.get("status") == "COMPLETED"]
        
        # System stability analysis
        memory_stable = memory_tests.get("memory_stable", False)
        stress_survived = all(test.get("survived_stress", False) for test in stress_tests.values() 
                             if "survived_stress" in test)
        
        summary = {
            "endpoint_performance": {
                "total_endpoints_tested": len(endpoint_results),
                "successful_tests": len([r for r in endpoint_results.values() if r.get("status") == "COMPLETED"]),
                "average_response_time_ms": statistics.mean(avg_response_times) if avg_response_times else 0,
                "performance_grades": endpoint_grades,
                "overall_performance_grade": self._calculate_overall_grade(endpoint_grades)
            },
            "load_test_performance": {
                "tests_completed": len([r for r in load_test_results.values() if r.get("status") == "COMPLETED"]),
                "load_grades": load_grades,
                "overall_load_grade": self._calculate_overall_grade(load_grades),
                "max_concurrent_users_tested": max([r.get("config", {}).get("users", 0) for r in load_test_results.values()], default=0)
            },
            "system_stability": {
                "memory_stable": memory_stable,
                "stress_test_survived": stress_survived,
                "current_memory_usage": memory_tests.get("current_memory_percent", 0),
                "system_healthy": memory_stable and stress_survived
            },
            "performance_bottlenecks": self._identify_bottlenecks(endpoint_results, load_test_results),
            "recommendations": []
        }
        
        # Generate recommendations
        if summary["endpoint_performance"]["overall_performance_grade"] in ["D", "F"]:
            summary["recommendations"].append("🐌 Optimize slow API endpoints - response times are too high")
        
        if summary["load_test_performance"]["overall_load_grade"] in ["D", "F"]:
            summary["recommendations"].append("⚡ Improve system capacity - load tests showing poor performance")
        
        if not memory_stable:
            summary["recommendations"].append("🧠 Investigate memory usage - potential memory leaks detected")
        
        if not stress_survived:
            summary["recommendations"].append("💪 Improve error handling under stress conditions")
        
        if summary["system_stability"]["current_memory_usage"] > 80:
            summary["recommendations"].append("📊 System memory usage is high - consider scaling")
        
        if summary["endpoint_performance"]["average_response_time_ms"] > 1000:
            summary["recommendations"].append("🚀 Overall API performance needs optimization")
        
        if (summary["endpoint_performance"]["overall_performance_grade"] in ["A", "B"] and 
            summary["load_test_performance"]["overall_load_grade"] in ["A", "B"] and
            summary["system_stability"]["system_healthy"]):
            summary["recommendations"].append("✅ System performance is excellent!")
        
        self.results["summary"] = summary
        return summary
    
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
    
    def _identify_bottlenecks(self, endpoint_results: Dict, load_results: Dict) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check for slow endpoints
        for endpoint, result in endpoint_results.items():
            if result.get("status") == "COMPLETED":
                avg_ms = result["statistics"]["avg_ms"]
                if avg_ms > 2000:
                    bottlenecks.append(f"Slow endpoint: {endpoint} ({avg_ms:.1f}ms avg)")
        
        # Check for high error rates in load tests
        for test_name, result in load_results.items():
            if result.get("status") == "COMPLETED":
                error_rate = result["statistics"]["error_rate"]
                if error_rate > 10:
                    bottlenecks.append(f"High error rate in {test_name}: {error_rate:.1f}%")
        
        return bottlenecks
    
    def save_results(self):
        """Save performance test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_load_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Performance and load test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_performance_tests(self):
        """Run complete performance and load testing suite"""
        print("🚀 Starting Comprehensive Performance and Load Testing...")
        print("=" * 70)
        
        # Test 1: Individual Endpoint Performance
        print("1. Testing individual endpoint performance...")
        endpoint_performance = self.test_all_endpoint_performance()
        
        # Test 2: Light Load Test
        print("2. Running light load test...")
        light_load = self.test_concurrent_load("light_load", self.test_config["light_load"])
        self.results["load_tests"]["light_load"] = light_load
        
        # Test 3: Medium Load Test
        print("3. Running medium load test...")
        medium_load = self.test_concurrent_load("medium_load", self.test_config["medium_load"])
        self.results["load_tests"]["medium_load"] = medium_load
        
        # Test 4: Memory Usage Patterns
        print("4. Testing memory usage patterns...")
        memory_usage = self.test_memory_usage_patterns()
        
        # Test 5: Stress Scenarios
        print("5. Testing stress scenarios...")
        stress_results = self.test_stress_scenarios()
        
        # Test 6: Heavy Load Test (if previous tests passed)
        if (light_load.get("load_grade", "F") not in ["F"] and 
            medium_load.get("load_grade", "F") not in ["F"]):
            print("6. Running heavy load test...")
            heavy_load = self.test_concurrent_load("heavy_load", self.test_config["heavy_load"])
            self.results["load_tests"]["heavy_load"] = heavy_load
        else:
            print("6. Skipping heavy load test due to previous failures...")
            self.results["load_tests"]["heavy_load"] = {"status": "SKIPPED", "reason": "Previous load tests failed"}
        
        # Generate Summary
        print("7. Generating performance summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 70)
        print("🚀 PERFORMANCE AND LOAD TESTING SUMMARY")
        print("=" * 70)
        
        print(f"📊 Endpoint Performance:")
        print(f"   Endpoints Tested: {summary['endpoint_performance']['total_endpoints_tested']}")
        print(f"   Average Response Time: {summary['endpoint_performance']['average_response_time_ms']:.1f}ms")
        print(f"   Overall Grade: {summary['endpoint_performance']['overall_performance_grade']}")
        
        print(f"\n⚡ Load Test Performance:")
        print(f"   Tests Completed: {summary['load_test_performance']['tests_completed']}")
        print(f"   Max Concurrent Users: {summary['load_test_performance']['max_concurrent_users_tested']}")
        print(f"   Overall Load Grade: {summary['load_test_performance']['overall_load_grade']}")
        
        print(f"\n🛡️ System Stability:")
        print(f"   Memory Stable: {'✅ YES' if summary['system_stability']['memory_stable'] else '❌ NO'}")
        print(f"   Stress Test Survived: {'✅ YES' if summary['system_stability']['stress_test_survived'] else '❌ NO'}")
        print(f"   Memory Usage: {summary['system_stability']['current_memory_usage']:.1f}%")
        print(f"   System Healthy: {'✅ YES' if summary['system_stability']['system_healthy'] else '❌ NO'}")
        
        if summary["performance_bottlenecks"]:
            print(f"\n🔍 Performance Bottlenecks:")
            for bottleneck in summary["performance_bottlenecks"]:
                print(f"   • {bottleneck}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = PerformanceLoadTester()
    
    try:
        # Run performance tests
        results = asyncio.run(tester.run_comprehensive_performance_tests())
        
        # Exit code based on results
        summary = results["summary"]
        overall_performance = summary["endpoint_performance"]["overall_performance_grade"]
        overall_load = summary["load_test_performance"]["overall_load_grade"]
        system_healthy = summary["system_stability"]["system_healthy"]
        
        if overall_performance in ["A", "B"] and overall_load in ["A", "B"] and system_healthy:
            sys.exit(0)  # Excellent
        elif overall_performance in ["A", "B", "C"] and overall_load in ["A", "B", "C"]:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ Performance and load testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()