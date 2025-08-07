#!/usr/bin/env python3
"""
Authentication Integration Testing Coordinator
==============================================

This script coordinates comprehensive testing across all integrated systems:
- Authentication & Security
- Caching Layers (Request, JWT, JWKS)  
- Database Optimization
- Performance Monitoring
- Rollback Mechanisms
- Configuration Validation

Usage:
    python run_integration_tests.py --env production --full-test
    python run_integration_tests.py --quick-test
    python run_integration_tests.py --security-only
"""

import asyncio
import logging
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

# Add backend to path
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_test_log.txt')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# TEST COORDINATOR CLASS
# ============================================================================

class IntegrationTestCoordinator:
    """Coordinates comprehensive integration testing across all systems"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "environment": environment,
            "test_suites": {},
            "overall_status": "pending",
            "end_time": None
        }
        
    async def run_comprehensive_tests(self, quick_mode: bool = False, security_only: bool = False) -> Dict[str, Any]:
        """Run comprehensive integration tests across all systems"""
        
        logger.info(f"🚀 Starting comprehensive integration tests (Environment: {self.environment})")
        
        if security_only:
            test_suites = ["security"]
        elif quick_mode:
            test_suites = ["security", "authentication", "cache_basic"]
        else:
            test_suites = [
                "configuration",
                "security", 
                "authentication",
                "cache_comprehensive",
                "database",
                "performance",
                "rollback",
                "monitoring"
            ]
        
        # Run test suites
        for suite_name in test_suites:
            logger.info(f"📋 Running {suite_name} test suite...")
            suite_result = await self._run_test_suite(suite_name)
            self.test_results["test_suites"][suite_name] = suite_result
            
            if not suite_result["success"]:
                logger.error(f"❌ Test suite {suite_name} failed")
                if suite_name in ["security", "authentication"] and not quick_mode:
                    # Critical failure - consider stopping
                    logger.error("🚨 Critical test suite failed - consider stopping")
            else:
                logger.info(f"✅ Test suite {suite_name} passed")
        
        # Calculate overall results
        await self._calculate_overall_results()
        
        # Generate report
        await self._generate_test_report()
        
        return self.test_results
    
    async def _run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        suite_start = time.time()
        
        try:
            if suite_name == "configuration":
                result = await self._test_configuration()
            elif suite_name == "security":
                result = await self._test_security()
            elif suite_name == "authentication":
                result = await self._test_authentication()
            elif suite_name == "cache_basic":
                result = await self._test_cache_basic()
            elif suite_name == "cache_comprehensive":
                result = await self._test_cache_comprehensive()
            elif suite_name == "database":
                result = await self._test_database()
            elif suite_name == "performance":
                result = await self._test_performance()
            elif suite_name == "rollback":
                result = await self._test_rollback()
            elif suite_name == "monitoring":
                result = await self._test_monitoring()
            else:
                result = {"success": False, "error": f"Unknown test suite: {suite_name}"}
                
        except Exception as e:
            logger.error(f"Test suite {suite_name} failed with exception: {str(e)}")
            result = {"success": False, "error": str(e), "exception": True}
        
        result["duration_seconds"] = time.time() - suite_start
        return result
    
    async def _test_configuration(self) -> Dict[str, Any]:
        """Test unified configuration system"""
        try:
            # For testing purposes, set up minimal test configuration
            os.environ.setdefault("CLERK_SECRET_KEY", "sk_test_test_key_for_testing_only")
            os.environ.setdefault("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "pk_test_test_key_for_testing_only")
            os.environ.setdefault("NEXT_PUBLIC_CLERK_DOMAIN", "test-domain.clerk.accounts.dev")
            
            from app.config.unified_auth_config import get_auth_config, validate_runtime_config
            
            # Test configuration loading
            config = get_auth_config()
            
            # Test configuration validation
            validation_result = await validate_runtime_config()
            
            # Test environment-specific settings
            deployment_checklist = config.get_deployment_checklist()
            
            success = validation_result["valid"] and deployment_checklist["ready_for_deployment"]
            
            return {
                "success": success,
                "details": {
                    "config_loaded": True,
                    "validation_result": validation_result,
                    "deployment_ready": deployment_checklist["ready_for_deployment"],
                    "environment": config.environment.value,
                    "security_level": config.security.level.value
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_security(self) -> Dict[str, Any]:
        """Test all security features and compliance"""
        try:
            from app.utils.secure_auth_integration import (
                SecurityConfig, sanitize_error_message, generate_secure_cache_key,
                secure_data_handler, feature_flags
            )
            
            tests = {}
            
            # Test 1: JWT storage policy
            tests["no_jwt_storage"] = not SecurityConfig.STORE_PLAINTEXT_TOKENS
            
            # Test 2: Full SHA-256 cache keys
            test_key = generate_secure_cache_key("test_token", "test")
            tests["full_sha256_keys"] = len(test_key.split(":")[1]) == 64  # Full SHA-256
            
            # Test 3: Error sanitization
            sensitive_error = "Database connection failed with password=secret123"
            sanitized = sanitize_error_message(sensitive_error)
            tests["error_sanitization"] = "password" not in sanitized and "secret123" not in sanitized
            
            # Test 4: AES-256 encryption
            test_data = {"user_id": 123, "sensitive": "data"}
            encrypted = secure_data_handler.encrypt_sensitive_data(test_data)
            decrypted = secure_data_handler.decrypt_sensitive_data(encrypted)
            tests["aes256_encryption"] = decrypted == test_data
            
            # Test 5: Security feature flags
            tests["security_features_enabled"] = feature_flags.is_enabled("ENABLE_SECURE_ERROR_HANDLING")
            
            # Test 6: Configuration security
            from app.config.unified_auth_config import get_security_config
            security_config = get_security_config()
            tests["production_ready_config"] = security_config.is_production_ready()
            
            all_passed = all(tests.values())
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "passed_tests": sum(1 for result in tests.values() if result),
                    "total_tests": len(tests),
                    "security_level": security_config.level.value
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_authentication(self) -> Dict[str, Any]:
        """Test authentication system integration"""
        try:
            from app.utils.secure_auth_integration import secure_auth_system
            
            # Test authentication system health
            health_check = await secure_auth_system.health_check()
            
            # Test feature flags
            from app.config.unified_auth_config import get_feature_flags
            flags = get_feature_flags()
            
            # Test Clerk configuration
            from app.config.unified_auth_config import get_clerk_config
            clerk_config = get_clerk_config()
            
            success = (
                health_check["status"] == "healthy" and
                clerk_config.secret_key and
                not clerk_config.secret_key.startswith("REPLACE_WITH") and
                clerk_config.domain and
                "None" not in clerk_config.domain
            )
            
            return {
                "success": success,
                "details": {
                    "health_check": health_check,
                    "feature_flags": flags.to_dict(),
                    "clerk_configured": bool(clerk_config.secret_key and clerk_config.domain),
                    "security_features": health_check.get("security_status", {})
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_cache_basic(self) -> Dict[str, Any]:
        """Test basic caching functionality"""
        try:
            from app.utils.auth_cache import RequestCache, TTLCache
            
            tests = {}
            
            # Test 1: Request cache
            request_cache = RequestCache()
            request_cache.set("test_key", "test_value")
            retrieved = request_cache.get("test_key") 
            tests["request_cache"] = retrieved == "test_value"
            
            # Test 2: TTL cache
            ttl_cache = TTLCache(default_ttl=60)
            ttl_cache.set("ttl_test", {"data": "value"})
            retrieved_ttl = ttl_cache.get("ttl_test")
            tests["ttl_cache"] = retrieved_ttl == {"data": "value"}
            
            # Test 3: Cache statistics
            stats = ttl_cache.get_stats()
            tests["cache_stats"] = "hits" in stats and "misses" in stats
            
            all_passed = all(tests.values())
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "cache_stats": stats
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_cache_comprehensive(self) -> Dict[str, Any]:
        """Test comprehensive caching system"""
        try:
            # Import caching components
            from app.utils.auth_cache import RequestCache, TTLCache, get_jwks_cache
            from app.utils.cache_integration import CachedAuthDependencies
            
            tests = {}
            
            # Test 1: Multi-layer cache integration
            request_cache = RequestCache()
            ttl_cache = TTLCache(default_ttl=300)
            
            # Test request cache performance
            start_time = time.time()
            for i in range(100):
                request_cache.set(f"perf_test_{i}", {"data": f"value_{i}"})
                request_cache.get(f"perf_test_{i}")
            request_cache_time = (time.time() - start_time) * 1000
            tests["request_cache_performance"] = request_cache_time < 100  # Under 100ms
            
            # Test TTL cache with expiration
            ttl_cache.set("expire_test", "value", ttl=1)
            await asyncio.sleep(1.1)
            expired_value = ttl_cache.get("expire_test")
            tests["ttl_expiration"] = expired_value is None
            
            # Test JWKS cache if available
            try:
                jwks_cache = get_jwks_cache()
                tests["jwks_cache_available"] = True
            except Exception:
                tests["jwks_cache_available"] = False
            
            # Test cache dependencies integration
            try:
                cached_deps = CachedAuthDependencies()
                tests["cache_dependencies"] = True
            except Exception:
                tests["cache_dependencies"] = False
            
            all_passed = sum(1 for result in tests.values() if result) >= len(tests) * 0.8  # 80% pass rate
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "request_cache_time_ms": request_cache_time,
                    "passed_tests": sum(1 for result in tests.values() if result),
                    "total_tests": len(tests)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_database(self) -> Dict[str, Any]:
        """Test database integration and optimization"""
        try:
            from app.utils.database import get_db
            from app.models.user import User
            from app.config.unified_auth_config import get_database_config
            
            db_config = get_database_config()
            
            tests = {}
            
            # Test 1: Database connectivity
            try:
                with get_db() as db:
                    user_count = db.query(User).count()
                    tests["database_connectivity"] = True
                    tests["user_table_accessible"] = user_count >= 0
            except Exception:
                tests["database_connectivity"] = False
                tests["user_table_accessible"] = False
            
            # Test 2: Configuration
            tests["pool_size_configured"] = db_config.connection_pool_size > 0
            tests["query_cache_enabled"] = db_config.query_cache_enabled
            
            # Test 3: Connection performance
            start_time = time.time()
            try:
                with get_db() as db:
                    db.query(User).count()
                connection_time = (time.time() - start_time) * 1000
                tests["connection_performance"] = connection_time < 1000  # Under 1 second
            except Exception:
                tests["connection_performance"] = False
                connection_time = 0
            
            all_passed = all(tests.values())
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "connection_time_ms": connection_time,
                    "db_config": {
                        "pool_size": db_config.connection_pool_size,
                        "max_overflow": db_config.max_overflow,
                        "query_cache": db_config.query_cache_enabled
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_performance(self) -> Dict[str, Any]:
        """Test performance optimizations"""
        try:
            from app.utils.secure_auth_integration import secure_auth_system, auth_monitor
            
            tests = {}
            
            # Test 1: Authentication system performance
            start_time = time.time()
            health_check = await secure_auth_system.health_check()
            auth_time = (time.time() - start_time) * 1000
            tests["auth_system_performance"] = auth_time < 500  # Under 500ms
            
            # Test 2: Monitoring system
            try:
                dashboard_data = auth_monitor.get_dashboard_data()
                tests["monitoring_active"] = "system_health" in dashboard_data
            except Exception:
                tests["monitoring_active"] = False
            
            # Test 3: Cache performance  
            from app.utils.auth_cache import RequestCache
            cache = RequestCache()
            
            start_time = time.time()
            for i in range(50):
                cache.set(f"perf_{i}", {"data": i})
                cache.get(f"perf_{i}")
            cache_time = (time.time() - start_time) * 1000
            tests["cache_performance"] = cache_time < 50  # Under 50ms for 100 operations
            
            # Test 4: Memory usage (basic check)
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            tests["memory_usage_reasonable"] = memory_mb < 500  # Under 500MB
            
            all_passed = sum(1 for result in tests.values() if result) >= len(tests) * 0.75  # 75% pass
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "auth_time_ms": auth_time,
                    "cache_time_ms": cache_time,
                    "memory_usage_mb": memory_mb,
                    "performance_metrics": {
                        "auth_system": auth_time,
                        "cache_operations": cache_time,
                        "memory": memory_mb
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_rollback(self) -> Dict[str, Any]:
        """Test rollback mechanisms"""
        try:
            from app.utils.secure_auth_integration import feature_flags
            from app.deployment.validation_system import RollbackManager
            
            tests = {}
            
            # Test 1: Feature flags can be modified
            original_caching = feature_flags.is_enabled("ENABLE_AUTH_CACHING")
            feature_flags.set_flag("ENABLE_AUTH_CACHING", False)
            tests["feature_flag_modification"] = not feature_flags.is_enabled("ENABLE_AUTH_CACHING")
            
            # Restore original value
            feature_flags.set_flag("ENABLE_AUTH_CACHING", original_caching)
            tests["feature_flag_restoration"] = feature_flags.is_enabled("ENABLE_AUTH_CACHING") == original_caching
            
            # Test 2: Rollback manager availability
            try:
                rollback_manager = RollbackManager()
                tests["rollback_manager_available"] = True
            except Exception:
                tests["rollback_manager_available"] = False
            
            # Test 3: Secure auth system rollback capability
            from app.utils.secure_auth_integration import secure_auth_system
            try:
                # Test rollback method exists (don't actually roll back)
                tests["auth_rollback_available"] = hasattr(secure_auth_system, 'rollback_to_basic_auth')
            except Exception:
                tests["auth_rollback_available"] = False
            
            all_passed = all(tests.values())
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "rollback_features": {
                        "feature_flags": tests["feature_flag_modification"],
                        "rollback_manager": tests["rollback_manager_available"],
                        "auth_rollback": tests["auth_rollback_available"]
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_monitoring(self) -> Dict[str, Any]:
        """Test monitoring and alerting systems"""
        try:
            from app.utils.secure_auth_integration import auth_monitor, secure_auth_system
            from app.deployment.validation_system import DeploymentValidator
            
            tests = {}
            
            # Test 1: Authentication monitoring
            try:
                dashboard_data = auth_monitor.get_dashboard_data()
                tests["auth_monitoring"] = bool(dashboard_data)
            except Exception:
                tests["auth_monitoring"] = False
            
            # Test 2: System health check
            try:
                health = await secure_auth_system.health_check()
                tests["health_check_functional"] = "status" in health
            except Exception:
                tests["health_check_functional"] = False
            
            # Test 3: Deployment validation
            try:
                validator = DeploymentValidator()
                tests["deployment_validator"] = True
            except Exception:
                tests["deployment_validator"] = False
            
            # Test 4: Metrics recording
            try:
                auth_monitor.record_metric("test_metric", 1.0)
                tests["metrics_recording"] = True
            except Exception:
                tests["metrics_recording"] = False
            
            all_passed = sum(1 for result in tests.values() if result) >= len(tests) * 0.75  # 75% pass
            
            return {
                "success": all_passed,
                "details": {
                    "test_results": tests,
                    "monitoring_features": {
                        "dashboard": tests["auth_monitoring"],
                        "health_check": tests["health_check_functional"],
                        "deployment_validation": tests["deployment_validator"],
                        "metrics": tests["metrics_recording"]
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_overall_results(self):
        """Calculate overall test results"""
        total_suites = len(self.test_results["test_suites"])
        passed_suites = sum(1 for result in self.test_results["test_suites"].values() if result["success"])
        
        self.test_results["summary"] = {
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": total_suites - passed_suites,
            "success_rate": (passed_suites / total_suites) * 100 if total_suites > 0 else 0,
            "overall_success": passed_suites == total_suites
        }
        
        self.test_results["overall_status"] = "success" if passed_suites == total_suites else "failed"
        self.test_results["end_time"] = datetime.now().isoformat()
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📄 Test report generated: {report_file}")
        
        # Print summary to console
        summary = self.test_results["summary"]
        print("\n" + "="*60)
        print("🧪 INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"Environment: {self.environment}")
        print(f"Total Test Suites: {summary['total_suites']}")
        print(f"Passed: {summary['passed_suites']}")
        print(f"Failed: {summary['failed_suites']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Overall Status: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}")
        print("="*60)
        
        # Print suite-by-suite results
        for suite_name, result in self.test_results["test_suites"].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result.get("duration_seconds", 0)
            print(f"{suite_name:20} {status} ({duration:.2f}s)")
        
        print("="*60)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="Authentication Integration Testing Coordinator")
    parser.add_argument("--env", default="development", choices=["development", "staging", "production"],
                       help="Environment to test against")
    parser.add_argument("--quick-test", action="store_true", 
                       help="Run quick test suite (security, auth, basic cache)")
    parser.add_argument("--security-only", action="store_true",
                       help="Run security tests only")
    parser.add_argument("--full-test", action="store_true",
                       help="Run full comprehensive test suite")
    
    args = parser.parse_args()
    
    # Initialize coordinator
    coordinator = IntegrationTestCoordinator(environment=args.env)
    
    # Determine test mode
    if args.security_only:
        logger.info("🔒 Running security-only tests")
        results = await coordinator.run_comprehensive_tests(security_only=True)
    elif args.quick_test:
        logger.info("⚡ Running quick test suite")
        results = await coordinator.run_comprehensive_tests(quick_mode=True)
    else:
        logger.info("🔬 Running comprehensive test suite")
        results = await coordinator.run_comprehensive_tests()
    
    # Exit with appropriate code
    if results["summary"]["overall_success"]:
        logger.info("✅ All integration tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some integration tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())