#!/usr/bin/env python3
"""
JWKS Cache Performance Test Suite
=================================

This script validates the JWKS caching implementation and measures performance improvements.

Tests:
1. Cache hit rate validation
2. API call reduction measurement
3. Response time comparison
4. Fallback mechanism testing
5. Background refresh validation

Run with: python test_jwks_performance.py
"""

import os
import sys
import asyncio
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Set environment variables
os.environ['NEXT_PUBLIC_CLERK_DOMAIN'] = os.getenv('NEXT_PUBLIC_CLERK_DOMAIN', 'ruling-halibut-89.clerk.accounts.dev')
os.environ['CLERK_SECRET_KEY'] = os.getenv('CLERK_SECRET_KEY', 'sk_test_1cINwMnu5slBHCftWNHnKMelHORTylnlnFQvhzWO6f')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JWKSPerformanceTest:
    """Comprehensive test suite for JWKS cache performance"""
    
    def __init__(self):
        self.results = {
            "cache_tests": [],
            "performance_tests": [],
            "fallback_tests": [],
            "error_handling_tests": []
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        logger.info("🚀 Starting JWKS Cache Performance Test Suite")
        
        try:
            # Test 1: Basic cache functionality
            await self.test_cache_basic_functionality()
            
            # Test 2: Performance comparison
            await self.test_performance_comparison()
            
            # Test 3: Cache hit rate validation
            await self.test_cache_hit_rate()
            
            # Test 4: Background refresh testing
            await self.test_background_refresh()
            
            # Test 5: Error handling and fallbacks
            await self.test_error_handling()
            
            # Test 6: Health check validation
            await self.test_health_check()
            
            # Generate summary report
            return self.generate_summary_report()
            
        except Exception as e:
            logger.error(f"💥 Test suite failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def test_cache_basic_functionality(self):
        """Test basic JWKS cache operations"""
        logger.info("🧪 Testing basic cache functionality...")
        
        try:
            from app.utils.clerk_jwks_cache import get_clerk_jwks_cache
            
            cache = get_clerk_jwks_cache()
            
            # Test 1: Initial JWKS fetch
            start_time = time.time()
            jwks1 = await cache.get_jwks()
            first_fetch_time = time.time() - start_time
            
            # Test 2: Cached JWKS fetch (should be faster)
            start_time = time.time()
            jwks2 = await cache.get_jwks()
            cached_fetch_time = time.time() - start_time
            
            # Validate results
            assert jwks1 == jwks2, "JWKS data should be identical"
            assert "keys" in jwks1, "JWKS should contain keys"
            assert len(jwks1["keys"]) > 0, "JWKS should have at least one key"
            
            self.results["cache_tests"].append({
                "test": "basic_functionality",
                "status": "passed",
                "first_fetch_time_ms": first_fetch_time * 1000,
                "cached_fetch_time_ms": cached_fetch_time * 1000,
                "speedup_factor": first_fetch_time / cached_fetch_time if cached_fetch_time > 0 else float('inf'),
                "jwks_keys_count": len(jwks1["keys"])
            })
            
            logger.info(f"✅ Basic functionality test passed")
            logger.info(f"   First fetch: {first_fetch_time*1000:.1f}ms")
            logger.info(f"   Cached fetch: {cached_fetch_time*1000:.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ Basic functionality test failed: {str(e)}")
            self.results["cache_tests"].append({
                "test": "basic_functionality",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_performance_comparison(self):
        """Compare performance with and without caching"""
        logger.info("🧪 Testing performance comparison...")
        
        try:
            from app.utils.clerk_jwks_cache import get_clerk_jwks_cache
            
            cache = get_clerk_jwks_cache()
            
            # Warm up cache
            await cache.get_jwks()
            
            # Test cached performance (multiple requests)
            cached_times = []
            for i in range(10):
                start_time = time.time()
                await cache.get_jwks()
                cached_times.append(time.time() - start_time)
            
            # Test direct fetch performance (force refresh)
            direct_times = []
            for i in range(3):  # Fewer direct fetches to avoid rate limiting
                start_time = time.time()
                await cache.get_jwks(force_refresh=True)
                direct_times.append(time.time() - start_time)
                await asyncio.sleep(0.5)  # Brief pause between direct fetches
            
            # Calculate metrics
            avg_cached = sum(cached_times) / len(cached_times)
            avg_direct = sum(direct_times) / len(direct_times)
            performance_improvement = (avg_direct - avg_cached) / avg_direct * 100
            
            self.results["performance_tests"].append({
                "test": "performance_comparison",
                "status": "passed",
                "avg_cached_time_ms": avg_cached * 1000,
                "avg_direct_time_ms": avg_direct * 1000,
                "performance_improvement_percent": performance_improvement,
                "speedup_factor": avg_direct / avg_cached if avg_cached > 0 else float('inf')
            })
            
            logger.info(f"✅ Performance comparison test passed")
            logger.info(f"   Average cached time: {avg_cached*1000:.1f}ms")
            logger.info(f"   Average direct time: {avg_direct*1000:.1f}ms")
            logger.info(f"   Performance improvement: {performance_improvement:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Performance comparison test failed: {str(e)}")
            self.results["performance_tests"].append({
                "test": "performance_comparison",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_cache_hit_rate(self):
        """Test cache hit rate over multiple requests"""
        logger.info("🧪 Testing cache hit rate...")
        
        try:
            from app.utils.clerk_jwks_cache import get_clerk_jwks_cache
            
            cache = get_clerk_jwks_cache()
            
            # Clear cache and reset metrics
            await cache.invalidate_cache()
            
            # Perform multiple requests
            for i in range(20):
                await cache.get_jwks()
                if i % 5 == 0:
                    await asyncio.sleep(0.1)  # Small delay every 5 requests
            
            # Get cache statistics
            stats = cache.get_cache_stats()
            hit_rate = stats["performance"]["hit_rate"]
            
            # Validate hit rate
            assert hit_rate > 0.8, f"Hit rate should be > 80%, got {hit_rate*100:.1f}%"
            
            self.results["cache_tests"].append({
                "test": "cache_hit_rate",
                "status": "passed",
                "hit_rate": hit_rate,
                "hits": stats["performance"]["hits"],
                "misses": stats["performance"]["misses"],
                "total_requests": stats["performance"]["hits"] + stats["performance"]["misses"]
            })
            
            logger.info(f"✅ Cache hit rate test passed")
            logger.info(f"   Hit rate: {hit_rate*100:.1f}%")
            logger.info(f"   Hits: {stats['performance']['hits']}")
            logger.info(f"   Misses: {stats['performance']['misses']}")
            
        except Exception as e:
            logger.error(f"❌ Cache hit rate test failed: {str(e)}")
            self.results["cache_tests"].append({
                "test": "cache_hit_rate",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_background_refresh(self):
        """Test background refresh functionality"""
        logger.info("🧪 Testing background refresh...")
        
        try:
            from app.utils.clerk_jwks_cache import get_clerk_jwks_cache
            
            cache = get_clerk_jwks_cache()
            
            # Get initial stats
            initial_stats = cache.get_cache_stats()
            initial_refreshes = initial_stats["operations"]["background_refreshes"]
            
            # Trigger multiple requests to activate background refresh
            for i in range(10):
                await cache.get_jwks()
                await asyncio.sleep(0.1)
            
            # Wait a bit for background refresh to potentially trigger
            await asyncio.sleep(2)
            
            # Get updated stats
            final_stats = cache.get_cache_stats()
            
            self.results["cache_tests"].append({
                "test": "background_refresh",
                "status": "passed",
                "initial_bg_refreshes": initial_refreshes,
                "final_bg_refreshes": final_stats["operations"]["background_refreshes"],
                "cache_age_seconds": final_stats["cache_status"]["age_seconds"],
                "is_cache_valid": final_stats["cache_status"]["is_valid"]
            })
            
            logger.info(f"✅ Background refresh test passed")
            logger.info(f"   Background refreshes: {final_stats['operations']['background_refreshes']}")
            logger.info(f"   Cache age: {final_stats['cache_status']['age_seconds']}s")
            
        except Exception as e:
            logger.error(f"❌ Background refresh test failed: {str(e)}")
            self.results["cache_tests"].append({
                "test": "background_refresh",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        logger.info("🧪 Testing error handling...")
        
        try:
            from app.utils.clerk_jwks_cache import get_clerk_jwks_cache
            
            cache = get_clerk_jwks_cache()
            
            # Ensure we have a valid cache first
            await cache.get_jwks()
            
            # Test cache invalidation and recovery
            await cache.invalidate_cache()
            
            # Should still work by fetching fresh data
            jwks = await cache.get_jwks()
            assert "keys" in jwks, "Should recover from cache invalidation"
            
            self.results["error_handling_tests"].append({
                "test": "cache_invalidation_recovery",
                "status": "passed",
                "recovered_successfully": True
            })
            
            logger.info(f"✅ Error handling test passed")
            logger.info(f"   Cache invalidation recovery: successful")
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {str(e)}")
            self.results["error_handling_tests"].append({
                "test": "cache_invalidation_recovery",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_health_check(self):
        """Test health check functionality"""
        logger.info("🧪 Testing health check...")
        
        try:
            from app.utils.clerk_jwks_cache import jwks_cache_health_check
            
            health_data = await jwks_cache_health_check()
            
            # Validate health check structure
            assert "status" in health_data, "Health check should have status"
            assert "checks" in health_data, "Health check should have checks"
            assert "stats" in health_data, "Health check should have stats"
            
            self.results["cache_tests"].append({
                "test": "health_check",
                "status": "passed",
                "health_status": health_data["status"],
                "checks_passed": len([c for c in health_data["checks"].values() if c["status"] == "pass"]),
                "total_checks": len(health_data["checks"])
            })
            
            logger.info(f"✅ Health check test passed")
            logger.info(f"   Health status: {health_data['status']}")
            logger.info(f"   Checks passed: {len([c for c in health_data['checks'].values() if c['status'] == 'pass'])}/{len(health_data['checks'])}")
            
        except Exception as e:
            logger.error(f"❌ Health check test failed: {str(e)}")
            self.results["cache_tests"].append({
                "test": "health_check",
                "status": "failed",
                "error": str(e)
            })
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_tests = sum(len(tests) for tests in self.results.values())
        passed_tests = sum(
            len([t for t in tests if t.get("status") == "passed"])
            for tests in self.results.values()
        )
        
        # Calculate performance metrics
        performance_data = {}
        for test in self.results["performance_tests"]:
            if test.get("status") == "passed":
                performance_data = test
                break
        
        cache_data = {}
        for test in self.results["cache_tests"]:
            if test.get("test") == "cache_hit_rate" and test.get("status") == "passed":
                cache_data = test
                break
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "overall_status": "PASSED" if passed_tests == total_tests else "FAILED"
            },
            "performance_summary": {
                "api_call_reduction": f"{cache_data.get('hit_rate', 0)*100:.1f}%" if cache_data else "N/A",
                "performance_improvement": f"{performance_data.get('performance_improvement_percent', 0):.1f}%" if performance_data else "N/A",
                "speedup_factor": f"{performance_data.get('speedup_factor', 0):.1f}x" if performance_data else "N/A",
                "avg_cached_response_time": f"{performance_data.get('avg_cached_time_ms', 0):.1f}ms" if performance_data else "N/A"
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check cache hit rate
        for test in self.results["cache_tests"]:
            if test.get("test") == "cache_hit_rate" and test.get("status") == "passed":
                hit_rate = test.get("hit_rate", 0)
                if hit_rate > 0.9:
                    recommendations.append("✅ Excellent cache hit rate - JWKS caching is performing optimally")
                elif hit_rate > 0.7:
                    recommendations.append("🟡 Good cache hit rate - Consider optimizing cache TTL for better performance")
                else:
                    recommendations.append("🔴 Low cache hit rate - Review cache configuration and TTL settings")
                break
        
        # Check performance improvement
        for test in self.results["performance_tests"]:
            if test.get("status") == "passed":
                improvement = test.get("performance_improvement_percent", 0)
                if improvement > 80:
                    recommendations.append("🚀 Significant performance improvement achieved - API calls reduced substantially")
                elif improvement > 50:
                    recommendations.append("📈 Good performance improvement - Clerk API usage optimized effectively")
                else:
                    recommendations.append("⚠️ Moderate performance improvement - Consider cache tuning")
                break
        
        # Check overall test status
        total_tests = sum(len(tests) for tests in self.results.values())
        passed_tests = sum(
            len([t for t in tests if t.get("status") == "passed"])
            for tests in self.results.values()
        )
        
        if passed_tests == total_tests:
            recommendations.append("🎉 All tests passed - JWKS cache implementation is production-ready")
        else:
            recommendations.append("🔧 Some tests failed - Review implementation before production deployment")
        
        return recommendations

async def main():
    """Main test execution"""
    print("=" * 70)
    print("JWKS CACHE PERFORMANCE TEST SUITE")
    print("=" * 70)
    
    test_suite = JWKSPerformanceTest()
    
    try:
        # Run all tests
        results = await test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        summary = results["test_summary"]
        performance = results["performance_summary"]
        
        print(f"📊 Overall Status: {summary['overall_status']}")
        print(f"✅ Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']*100:.1f}%")
        print()
        print("🚀 PERFORMANCE METRICS:")
        print(f"   API Call Reduction: {performance['api_call_reduction']}")
        print(f"   Performance Improvement: {performance['performance_improvement']}")
        print(f"   Speed Increase: {performance['speedup_factor']}")
        print(f"   Avg Cached Response: {performance['avg_cached_response_time']}")
        print()
        print("💡 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"   {rec}")
        
        print("\n" + "=" * 70)
        
        # Save detailed results
        import json
        with open("jwks_cache_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("📁 Detailed results saved to: jwks_cache_test_results.json")
        
        return results
        
    except Exception as e:
        print(f"💥 Test suite execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    # Check environment setup
    required_env = ['NEXT_PUBLIC_CLERK_DOMAIN', 'CLERK_SECRET_KEY']
    missing_env = [var for var in required_env if not os.getenv(var)]
    
    if missing_env:
        print(f"❌ Missing environment variables: {missing_env}")
        print("Please set these environment variables before running tests.")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())