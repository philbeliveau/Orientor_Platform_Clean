"""
Deployment Validation and Rollback System
=========================================

This module provides comprehensive deployment validation, smoke tests, and rollback mechanisms
for the integrated authentication optimization system.

Features:
- Pre-deployment validation checks
- Comprehensive smoke tests
- Zero-downtime rollback mechanisms
- Health monitoring and alerting
- Production readiness verification
- Configuration validation
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json
import traceback

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

@dataclass
class ValidationConfig:
    """Configuration for deployment validation"""
    timeout_seconds: int = 300  # 5 minutes
    max_retries: int = 3
    retry_delay_seconds: int = 5
    critical_failure_threshold: int = 1
    warning_failure_threshold: int = 3
    health_check_interval: int = 30
    enable_rollback: bool = True
    rollback_timeout: int = 120
    validate_external_services: bool = True
    run_load_tests: bool = False

@dataclass
class ValidationResult:
    """Result of a validation check"""
    name: str
    success: bool
    message: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None
    severity: str = "error"  # error, warning, info

@dataclass
class DeploymentHealth:
    """Overall deployment health status"""
    status: str  # healthy, degraded, unhealthy
    validations: List[ValidationResult]
    critical_failures: int
    warning_failures: int
    total_checks: int
    deployment_safe: bool
    rollback_required: bool

# ============================================================================
# VALIDATION CHECKS
# ============================================================================

class ValidationChecks:
    """Collection of validation checks for deployment readiness"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.start_time = None
        
    async def run_all_checks(self) -> DeploymentHealth:
        """Run all validation checks and return overall health status"""
        self.start_time = time.time()
        validations = []
        
        logger.info("🔍 Starting comprehensive deployment validation")
        
        # Core system checks
        validations.append(await self._check_configuration_security())
        validations.append(await self._check_authentication_system())
        validations.append(await self._check_database_connectivity())
        validations.append(await self._check_cache_functionality())
        validations.append(await self._check_encryption_system())
        
        # External service checks
        if self.config.validate_external_services:
            validations.append(await self._check_clerk_connectivity())
            validations.append(await self._check_external_apis())
        
        # Performance and security checks
        validations.append(await self._check_response_times())
        validations.append(await self._check_security_features())
        validations.append(await self._check_feature_flags())
        
        # Integration checks
        validations.append(await self._check_router_integration())
        validations.append(await self._check_monitoring_system())
        
        # Load testing (if enabled)
        if self.config.run_load_tests:
            validations.append(await self._check_load_performance())
        
        # Analyze results
        health = self._analyze_validation_results(validations)
        
        # Log summary
        duration = time.time() - self.start_time
        logger.info(f"✅ Validation completed in {duration:.2f}s - Status: {health.status}")
        
        return health
    
    async def _check_configuration_security(self) -> ValidationResult:
        """Validate security configuration"""
        start_time = time.time()
        
        try:
            from ..config.unified_auth_config import get_auth_config
            config = get_auth_config()
            
            issues = []
            
            # Check security level
            if config.security.level.value not in ["high", "maximum"]:
                issues.append(f"Security level is {config.security.level.value}, should be high or maximum")
            
            # Check critical security settings
            if config.security.store_plaintext_tokens:
                issues.append("Plaintext token storage is enabled - SECURITY RISK")
            
            if not config.security.use_full_sha256_keys:
                issues.append("Not using full SHA-256 cache keys - SECURITY RISK")
            
            if not config.security.sanitize_error_messages:
                issues.append("Error message sanitization is disabled")
            
            # Check encryption
            if not config.security.cache_encryption_enabled:
                issues.append("Cache encryption is disabled")
            
            # Check environment variables
            required_vars = ["CLERK_SECRET_KEY", "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "NEXT_PUBLIC_CLERK_DOMAIN"]
            missing_vars = [var for var in required_vars if not os.getenv(var) or os.getenv(var).startswith("REPLACE_WITH")]
            
            if missing_vars:
                issues.append(f"Missing or placeholder environment variables: {missing_vars}")
            
            success = len(issues) == 0
            message = "Security configuration validated" if success else f"Security issues found: {'; '.join(issues)}"
            severity = "error" if not success else "info"
            
            return ValidationResult(
                name="Configuration Security",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"issues": issues, "config_summary": config.export_config(include_secrets=False)},
                severity=severity
            )
            
        except Exception as e:
            return ValidationResult(
                name="Configuration Security",
                success=False,
                message=f"Configuration security check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_authentication_system(self) -> ValidationResult:
        """Validate authentication system functionality"""
        start_time = time.time()
        
        try:
            from ..utils.secure_auth_integration import secure_auth_system
            
            # Run health check on authentication system
            health_check = await secure_auth_system.health_check()
            
            success = health_check["status"] == "healthy"
            details = health_check
            
            if success:
                message = "Authentication system is healthy"
            else:
                message = f"Authentication system issues: {health_check.get('status', 'unknown')}"
            
            return ValidationResult(
                name="Authentication System",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details=details,
                severity="error" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Authentication System",
                success=False,
                message=f"Authentication system check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_database_connectivity(self) -> ValidationResult:
        """Validate database connectivity and performance"""
        start_time = time.time()
        
        try:
            from ..utils.database import get_db
            from ..models.user import User
            
            # Test database connection and query performance
            with get_db() as db:
                # Simple query to test connectivity
                query_start = time.time()
                user_count = db.query(User).count()
                query_time = (time.time() - query_start) * 1000
                
                # Test write operation (if safe)
                if os.getenv("DEPLOYMENT_ENVIRONMENT") != "production":
                    test_user = User(email=f"test_{int(time.time())}@example.com", clerk_user_id=f"test_{int(time.time())}")
                    db.add(test_user)
                    db.flush()  # Test write without committing
                    db.rollback()  # Clean up
                
                success = query_time < 1000  # Query should complete in under 1 second
                message = f"Database accessible, {user_count} users, query time: {query_time:.2f}ms"
                severity = "error" if query_time > 2000 else "warning" if query_time > 500 else "info"
                
                return ValidationResult(
                    name="Database Connectivity",
                    success=success,
                    message=message,
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"user_count": user_count, "query_time_ms": query_time},
                    severity=severity
                )
                
        except Exception as e:
            return ValidationResult(
                name="Database Connectivity",
                success=False,
                message=f"Database connectivity check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_cache_functionality(self) -> ValidationResult:
        """Validate caching system functionality"""
        start_time = time.time()
        
        try:
            from ..utils.auth_cache import RequestCache, TTLCache
            
            issues = []
            
            # Test request cache
            try:
                cache = RequestCache()
                test_key = f"test_key_{int(time.time())}"
                test_value = f"test_value_{int(time.time())}"
                
                cache.set(test_key, test_value)
                retrieved = cache.get(test_key)
                
                if retrieved != test_value:
                    issues.append("Request cache set/get failed")
            except Exception as e:
                issues.append(f"Request cache error: {str(e)}")
            
            # Test TTL cache
            try:
                ttl_cache = TTLCache(default_ttl=60)
                test_key = f"ttl_test_{int(time.time())}"
                test_value = {"test": "data"}
                
                ttl_cache.set(test_key, test_value)
                retrieved = ttl_cache.get(test_key)
                
                if retrieved != test_value:
                    issues.append("TTL cache set/get failed")
                
                # Test TTL expiration (with very short TTL)
                ttl_cache.set(test_key + "_expire", test_value, ttl=1)
                await asyncio.sleep(1.1)
                expired_value = ttl_cache.get(test_key + "_expire")
                
                if expired_value is not None:
                    issues.append("TTL cache expiration not working")
                    
            except Exception as e:
                issues.append(f"TTL cache error: {str(e)}")
            
            success = len(issues) == 0
            message = "Cache functionality validated" if success else f"Cache issues: {'; '.join(issues)}"
            
            return ValidationResult(
                name="Cache Functionality",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"issues": issues},
                severity="error" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Cache Functionality",
                success=False,
                message=f"Cache functionality check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_encryption_system(self) -> ValidationResult:
        """Validate encryption system functionality"""
        start_time = time.time()
        
        try:
            from ..utils.secure_auth_integration import secure_data_handler
            
            # Test encryption/decryption
            test_data = {
                "user_id": 12345,
                "email": "test@example.com",
                "sensitive_info": "This should be encrypted"
            }
            
            # Encrypt data
            encrypted = secure_data_handler.encrypt_sensitive_data(test_data)
            
            # Decrypt data
            decrypted = secure_data_handler.decrypt_sensitive_data(encrypted)
            
            success = decrypted == test_data
            message = "Encryption system validated" if success else "Encryption/decryption mismatch"
            
            return ValidationResult(
                name="Encryption System",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"test_data": test_data, "encrypted_length": len(encrypted)},
                severity="error" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Encryption System",
                success=False,
                message=f"Encryption system check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_clerk_connectivity(self) -> ValidationResult:
        """Validate Clerk service connectivity"""
        start_time = time.time()
        
        try:
            from ..config.unified_auth_config import get_clerk_config
            clerk_config = get_clerk_config()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test JWKS endpoint
                response = await client.get(clerk_config.jwks_url)
                
                if response.status_code == 200:
                    jwks_data = response.json()
                    key_count = len(jwks_data.get("keys", []))
                    
                    success = key_count > 0
                    message = f"Clerk JWKS accessible, {key_count} keys available"
                else:
                    success = False
                    message = f"Clerk JWKS request failed: {response.status_code}"
                
                return ValidationResult(
                    name="Clerk Connectivity",
                    success=success,
                    message=message,
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"jwks_url": clerk_config.jwks_url, "response_code": response.status_code},
                    severity="error" if not success else "info"
                )
                
        except Exception as e:
            return ValidationResult(
                name="Clerk Connectivity",
                success=False,
                message=f"Clerk connectivity check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_external_apis(self) -> ValidationResult:
        """Validate external API connectivity"""
        start_time = time.time()
        
        try:
            # Test basic HTTP connectivity
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_urls = [
                    "https://httpbin.org/status/200",  # Test HTTP connectivity
                    "https://jsonplaceholder.typicode.com/posts/1"  # Test JSON API
                ]
                
                results = {}
                for url in test_urls:
                    try:
                        response = await client.get(url)
                        results[url] = {"status": response.status_code, "success": response.status_code == 200}
                    except Exception as e:
                        results[url] = {"status": "error", "success": False, "error": str(e)}
                
                successful_tests = sum(1 for r in results.values() if r["success"])
                total_tests = len(results)
                
                success = successful_tests == total_tests
                message = f"External API connectivity: {successful_tests}/{total_tests} tests passed"
                severity = "error" if successful_tests == 0 else "warning" if successful_tests < total_tests else "info"
                
                return ValidationResult(
                    name="External APIs",
                    success=success,
                    message=message,
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"test_results": results},
                    severity=severity
                )
                
        except Exception as e:
            return ValidationResult(
                name="External APIs",
                success=False,
                message=f"External API check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="warning"  # External API failures are warnings, not critical
            )
    
    async def _check_response_times(self) -> ValidationResult:
        """Validate system response times"""
        start_time = time.time()
        
        try:
            from ..utils.secure_auth_integration import secure_auth_system
            
            # Test authentication performance
            performance_results = {}
            
            # Simulate authentication operations
            for i in range(5):
                op_start = time.time()
                
                # Test cache operations
                from ..utils.auth_cache import RequestCache
                cache = RequestCache()
                cache.set(f"perf_test_{i}", {"data": f"value_{i}"})
                retrieved = cache.get(f"perf_test_{i}")
                
                op_time = (time.time() - op_start) * 1000
                performance_results[f"cache_operation_{i}"] = op_time
            
            avg_response_time = sum(performance_results.values()) / len(performance_results)
            max_response_time = max(performance_results.values())
            
            success = avg_response_time < 100  # Average under 100ms
            
            if avg_response_time < 50:
                message = f"Excellent response times: avg {avg_response_time:.2f}ms"
                severity = "info"
            elif avg_response_time < 100:
                message = f"Good response times: avg {avg_response_time:.2f}ms"
                severity = "info"
            elif avg_response_time < 200:
                message = f"Acceptable response times: avg {avg_response_time:.2f}ms"
                severity = "warning"
            else:
                message = f"Slow response times: avg {avg_response_time:.2f}ms"
                severity = "error"
                
            return ValidationResult(
                name="Response Times",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "individual_results": performance_results
                },
                severity=severity
            )
            
        except Exception as e:
            return ValidationResult(
                name="Response Times",
                success=False,
                message=f"Response time check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="warning"
            )
    
    async def _check_security_features(self) -> ValidationResult:
        """Validate security features are working"""
        start_time = time.time()
        
        try:
            from ..utils.secure_auth_integration import sanitize_error_message, generate_secure_cache_key
            
            security_tests = {}
            
            # Test error sanitization
            test_error = "Database connection failed with password=secret123 and user=admin"
            sanitized = sanitize_error_message(test_error)
            security_tests["error_sanitization"] = {
                "passed": "password" not in sanitized and "secret123" not in sanitized,
                "original": test_error,
                "sanitized": sanitized
            }
            
            # Test secure cache keys
            test_token = "test_jwt_token_12345"
            secure_key = generate_secure_cache_key(test_token)
            security_tests["cache_key_security"] = {
                "passed": len(secure_key) > 32,  # Should be full hash, not truncated
                "key_length": len(secure_key),
                "key_sample": secure_key[:20] + "..."
            }
            
            # Test feature flags
            from ..utils.secure_auth_integration import feature_flags
            security_tests["feature_flags"] = {
                "passed": feature_flags.is_enabled("ENABLE_SECURE_ERROR_HANDLING"),
                "flags": feature_flags.flags
            }
            
            passed_tests = sum(1 for test in security_tests.values() if test["passed"])
            total_tests = len(security_tests)
            
            success = passed_tests == total_tests
            message = f"Security features: {passed_tests}/{total_tests} tests passed"
            
            return ValidationResult(
                name="Security Features",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"test_results": security_tests},
                severity="error" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Security Features",
                success=False,
                message=f"Security features check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_feature_flags(self) -> ValidationResult:
        """Validate feature flags configuration"""
        start_time = time.time()
        
        try:
            from ..config.unified_auth_config import get_feature_flags
            flags = get_feature_flags()
            
            flag_status = flags.to_dict()
            
            # Check for production-appropriate settings
            issues = []
            environment = os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
            
            if environment == "production":
                if flag_status.get("ENABLE_EXPERIMENTAL_FEATURES", False):
                    issues.append("Experimental features enabled in production")
                
                if not flag_status.get("ENABLE_AUTH_CACHING", True):
                    issues.append("Authentication caching disabled in production")
                
                if not flag_status.get("ENABLE_SECURE_ERROR_HANDLING", True):
                    issues.append("Secure error handling disabled in production")
            
            success = len(issues) == 0
            message = "Feature flags validated" if success else f"Flag issues: {'; '.join(issues)}"
            
            return ValidationResult(
                name="Feature Flags",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"flags": flag_status, "issues": issues, "environment": environment},
                severity="error" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Feature Flags",
                success=False,
                message=f"Feature flags check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="error"
            )
    
    async def _check_router_integration(self) -> ValidationResult:
        """Validate router integration status"""
        start_time = time.time()
        
        try:
            from ..utils.router_migration import get_migration_status
            
            status = get_migration_status()
            
            migration_percentage = (status["secure_integrated"] / status["total_routers"]) * 100 if status["total_routers"] > 0 else 0
            
            success = migration_percentage >= 90  # At least 90% of routers should be migrated
            
            if migration_percentage >= 95:
                message = f"Excellent router integration: {migration_percentage:.1f}% migrated"
                severity = "info"
            elif migration_percentage >= 90:
                message = f"Good router integration: {migration_percentage:.1f}% migrated"
                severity = "info"
            elif migration_percentage >= 75:
                message = f"Partial router integration: {migration_percentage:.1f}% migrated"
                severity = "warning"
            else:
                message = f"Poor router integration: {migration_percentage:.1f}% migrated"
                severity = "error"
            
            return ValidationResult(
                name="Router Integration",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    "migration_percentage": migration_percentage,
                    "migrated_routers": status["secure_integrated"],
                    "total_routers": status["total_routers"],
                    "patterns": status["patterns"]
                },
                severity=severity
            )
            
        except Exception as e:
            return ValidationResult(
                name="Router Integration",
                success=False,
                message=f"Router integration check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="warning"
            )
    
    async def _check_monitoring_system(self) -> ValidationResult:
        """Validate monitoring system functionality"""
        start_time = time.time()
        
        try:
            from ..utils.secure_auth_integration import auth_monitor
            
            # Test monitoring system
            dashboard_data = auth_monitor.get_dashboard_data()
            
            success = "system_health" in dashboard_data and "feature_flags" in dashboard_data
            message = "Monitoring system operational" if success else "Monitoring system issues detected"
            
            return ValidationResult(
                name="Monitoring System",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details=dashboard_data,
                severity="warning" if not success else "info"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Monitoring System",
                success=False,
                message=f"Monitoring system check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="warning"
            )
    
    async def _check_load_performance(self) -> ValidationResult:
        """Validate system performance under load"""
        start_time = time.time()
        
        try:
            from ..utils.auth_cache import RequestCache
            
            # Simulate concurrent load
            async def simulate_request():
                cache = RequestCache()
                for i in range(10):
                    cache.set(f"load_test_{i}_{time.time()}", {"data": f"value_{i}"})
                    cache.get(f"load_test_{i}_{time.time()}")
                return time.time()
            
            # Run concurrent simulated requests
            tasks = [simulate_request() for _ in range(50)]
            results = await asyncio.gather(*tasks)
            
            total_time = max(results) - min(results)
            success = total_time < 5.0  # Should complete within 5 seconds
            
            message = f"Load test completed in {total_time:.2f}s"
            severity = "error" if total_time > 10 else "warning" if total_time > 5 else "info"
            
            return ValidationResult(
                name="Load Performance",
                success=success,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={"concurrent_requests": len(tasks), "total_time_seconds": total_time},
                severity=severity
            )
            
        except Exception as e:
            return ValidationResult(
                name="Load Performance",
                success=False,
                message=f"Load performance check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                severity="warning"
            )
    
    def _analyze_validation_results(self, validations: List[ValidationResult]) -> DeploymentHealth:
        """Analyze validation results and determine overall health"""
        critical_failures = sum(1 for v in validations if not v.success and v.severity == "error")
        warning_failures = sum(1 for v in validations if not v.success and v.severity == "warning")
        total_checks = len(validations)
        
        # Determine overall status
        if critical_failures > self.config.critical_failure_threshold:
            status = "unhealthy"
            deployment_safe = False
            rollback_required = True
        elif warning_failures > self.config.warning_failure_threshold:
            status = "degraded"
            deployment_safe = critical_failures == 0
            rollback_required = False
        else:
            status = "healthy"
            deployment_safe = True
            rollback_required = False
        
        return DeploymentHealth(
            status=status,
            validations=validations,
            critical_failures=critical_failures,
            warning_failures=warning_failures,
            total_checks=total_checks,
            deployment_safe=deployment_safe,
            rollback_required=rollback_required
        )

# ============================================================================
# SMOKE TESTS
# ============================================================================

class SmokeTests:
    """Comprehensive smoke tests for post-deployment validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def run_smoke_tests(self) -> Dict[str, Any]:
        """Run comprehensive smoke tests"""
        logger.info("🧪 Starting smoke tests")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        }
        
        # Run individual smoke tests
        test_results["tests"].append(await self._test_health_endpoint())
        test_results["tests"].append(await self._test_authentication_flow())
        test_results["tests"].append(await self._test_cache_performance())
        test_results["tests"].append(await self._test_error_handling())
        test_results["tests"].append(await self._test_security_headers())
        test_results["tests"].append(await self._test_database_operations())
        
        # Calculate summary
        test_results["summary"]["total"] = len(test_results["tests"])
        test_results["summary"]["passed"] = sum(1 for t in test_results["tests"] if t["success"])
        test_results["summary"]["failed"] = test_results["summary"]["total"] - test_results["summary"]["passed"]
        test_results["summary"]["success_rate"] = (test_results["summary"]["passed"] / test_results["summary"]["total"]) * 100
        
        logger.info(f"🧪 Smoke tests completed: {test_results['summary']['passed']}/{test_results['summary']['total']} passed")
        
        return test_results
    
    async def _test_health_endpoint(self) -> Dict[str, Any]:
        """Test health endpoint functionality"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                success = response.status_code == 200
                details = response.json() if success else {"error": f"Status {response.status_code}"}
                
                return {
                    "name": "Health Endpoint",
                    "success": success,
                    "details": details,
                    "response_time_ms": response.elapsed.total_seconds() * 1000 if hasattr(response, 'elapsed') else 0
                }
        except Exception as e:
            return {
                "name": "Health Endpoint",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _test_authentication_flow(self) -> Dict[str, Any]:
        """Test authentication flow (mock)"""
        try:
            # This would test with a real authentication token in actual deployment
            # For now, test the authentication system components
            from ..utils.secure_auth_integration import secure_auth_system
            
            health_check = await secure_auth_system.health_check()
            success = health_check["status"] == "healthy"
            
            return {
                "name": "Authentication Flow",
                "success": success,
                "details": health_check,
                "response_time_ms": 0
            }
        except Exception as e:
            return {
                "name": "Authentication Flow",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache performance"""
        try:
            from ..utils.auth_cache import RequestCache
            
            start_time = time.time()
            
            cache = RequestCache()
            
            # Test cache operations
            for i in range(100):
                cache.set(f"smoke_test_{i}", {"value": i})
            
            for i in range(100):
                value = cache.get(f"smoke_test_{i}")
                if value["value"] != i:
                    raise Exception(f"Cache integrity failed at key smoke_test_{i}")
            
            duration = (time.time() - start_time) * 1000
            success = duration < 100  # Should complete in under 100ms
            
            return {
                "name": "Cache Performance",
                "success": success,
                "details": {"duration_ms": duration, "operations": 200},
                "response_time_ms": duration
            }
        except Exception as e:
            return {
                "name": "Cache Performance",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and sanitization"""
        try:
            from ..utils.secure_auth_integration import sanitize_error_message
            
            # Test error sanitization
            sensitive_error = "Database connection failed with password=secret123"
            sanitized = sanitize_error_message(sensitive_error)
            
            success = "password" not in sanitized and "secret123" not in sanitized
            
            return {
                "name": "Error Handling",
                "success": success,
                "details": {
                    "original": sensitive_error,
                    "sanitized": sanitized,
                    "properly_sanitized": success
                },
                "response_time_ms": 0
            }
        except Exception as e:
            return {
                "name": "Error Handling",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _test_security_headers(self) -> Dict[str, Any]:
        """Test security headers (if accessible via HTTP)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                headers = response.headers
                security_headers = {
                    "X-Content-Type-Options": headers.get("x-content-type-options"),
                    "X-Frame-Options": headers.get("x-frame-options"),
                    "X-XSS-Protection": headers.get("x-xss-protection")
                }
                
                success = any(value is not None for value in security_headers.values())
                
                return {
                    "name": "Security Headers",
                    "success": success,
                    "details": {"headers": security_headers},
                    "response_time_ms": 0
                }
        except Exception as e:
            return {
                "name": "Security Headers",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _test_database_operations(self) -> Dict[str, Any]:
        """Test basic database operations"""
        try:
            from ..utils.database import get_db
            from ..models.user import User
            
            with get_db() as db:
                # Test read operation
                user_count = db.query(User).count()
                
                success = user_count >= 0  # Basic connectivity test
                
                return {
                    "name": "Database Operations",
                    "success": success,
                    "details": {"user_count": user_count},
                    "response_time_ms": 0
                }
        except Exception as e:
            return {
                "name": "Database Operations",
                "success": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }

# ============================================================================
# ROLLBACK SYSTEM
# ============================================================================

class RollbackManager:
    """Manages rollback mechanisms for zero-downtime deployment"""
    
    def __init__(self):
        self.rollback_history: List[Dict[str, Any]] = []
        
    async def execute_rollback(self, reason: str = "Manual rollback") -> Dict[str, Any]:
        """Execute comprehensive rollback"""
        logger.warning(f"🔄 Executing rollback: {reason}")
        
        rollback_result = {
            "start_time": datetime.now().isoformat(),
            "reason": reason,
            "steps": [],
            "success": True,
            "end_time": None
        }
        
        try:
            # Step 1: Disable advanced features
            rollback_result["steps"].append(await self._rollback_feature_flags())
            
            # Step 2: Switch to basic authentication
            rollback_result["steps"].append(await self._rollback_authentication())
            
            # Step 3: Clear caches
            rollback_result["steps"].append(await self._clear_caches())
            
            # Step 4: Verify rollback
            rollback_result["steps"].append(await self._verify_rollback())
            
        except Exception as e:
            rollback_result["success"] = False
            rollback_result["error"] = str(e)
            logger.error(f"Rollback failed: {str(e)}")
        
        rollback_result["end_time"] = datetime.now().isoformat()
        self.rollback_history.append(rollback_result)
        
        return rollback_result
    
    async def _rollback_feature_flags(self) -> Dict[str, Any]:
        """Rollback feature flags to safe defaults"""
        try:
            from ..utils.secure_auth_integration import feature_flags
            
            # Disable advanced features
            feature_flags.set_flag("ENABLE_AUTH_CACHING", False)
            feature_flags.set_flag("ENABLE_JWT_VALIDATION_CACHE", False)
            feature_flags.set_flag("ENABLE_JWKS_BACKGROUND_REFRESH", False)
            feature_flags.set_flag("ENABLE_EXPERIMENTAL_FEATURES", False)
            
            return {
                "step": "Feature Flags Rollback",
                "success": True,
                "message": "Advanced features disabled"
            }
        except Exception as e:
            return {
                "step": "Feature Flags Rollback",
                "success": False,
                "message": f"Failed: {str(e)}"
            }
    
    async def _rollback_authentication(self) -> Dict[str, Any]:
        """Rollback to basic authentication"""
        try:
            from ..utils.secure_auth_integration import secure_auth_system
            
            # Trigger rollback in authentication system
            secure_auth_system.rollback_to_basic_auth()
            
            return {
                "step": "Authentication Rollback",
                "success": True,
                "message": "Switched to basic authentication"
            }
        except Exception as e:
            return {
                "step": "Authentication Rollback",
                "success": False,
                "message": f"Failed: {str(e)}"
            }
    
    async def _clear_caches(self) -> Dict[str, Any]:
        """Clear all caches"""
        try:
            from ..utils.auth_cache import jwt_validation_cache
            
            # Clear JWT validation cache
            jwt_validation_cache.clear()
            
            return {
                "step": "Cache Clearing",
                "success": True,
                "message": "Caches cleared"
            }
        except Exception as e:
            return {
                "step": "Cache Clearing",
                "success": False,
                "message": f"Failed: {str(e)}"
            }
    
    async def _verify_rollback(self) -> Dict[str, Any]:
        """Verify rollback was successful"""
        try:
            # Run basic validation
            validator = ValidationChecks(ValidationConfig())
            basic_health = await validator._check_authentication_system()
            
            success = basic_health.success
            message = "Rollback verified" if success else "Rollback verification failed"
            
            return {
                "step": "Rollback Verification",
                "success": success,
                "message": message
            }
        except Exception as e:
            return {
                "step": "Rollback Verification",
                "success": False,
                "message": f"Failed: {str(e)}"
            }

# ============================================================================
# MAIN DEPLOYMENT VALIDATOR
# ============================================================================

class DeploymentValidator:
    """Main deployment validation orchestrator"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validator = ValidationChecks(self.config)
        self.smoke_tester = SmokeTests()
        self.rollback_manager = RollbackManager()
        
    async def validate_deployment(self) -> Dict[str, Any]:
        """Run complete deployment validation"""
        logger.info("🚀 Starting deployment validation")
        
        validation_report = {
            "start_time": datetime.now().isoformat(),
            "pre_deployment": None,
            "smoke_tests": None,
            "final_status": None,
            "rollback_executed": False,
            "end_time": None
        }
        
        try:
            # Pre-deployment validation
            logger.info("🔍 Running pre-deployment validation")
            health = await self.validator.run_all_checks()
            validation_report["pre_deployment"] = {
                "status": health.status,
                "deployment_safe": health.deployment_safe,
                "rollback_required": health.rollback_required,
                "critical_failures": health.critical_failures,
                "warning_failures": health.warning_failures,
                "total_checks": health.total_checks,
                "validations": [
                    {
                        "name": v.name,
                        "success": v.success,
                        "message": v.message,
                        "duration_ms": v.duration_ms,
                        "severity": v.severity
                    }
                    for v in health.validations
                ]
            }
            
            # Check if deployment should proceed
            if not health.deployment_safe:
                logger.error("❌ Deployment validation failed - deployment not safe")
                validation_report["final_status"] = "blocked"
                
                if health.rollback_required and self.config.enable_rollback:
                    logger.warning("🔄 Executing automatic rollback")
                    rollback_result = await self.rollback_manager.execute_rollback("Pre-deployment validation failed")
                    validation_report["rollback_executed"] = True
                    validation_report["rollback_result"] = rollback_result
                
                return validation_report
            
            # Run smoke tests
            logger.info("🧪 Running smoke tests")
            smoke_results = await self.smoke_tester.run_smoke_tests()
            validation_report["smoke_tests"] = smoke_results
            
            # Determine final status
            smoke_success_rate = smoke_results["summary"]["success_rate"]
            
            if smoke_success_rate >= 90:
                validation_report["final_status"] = "success"
                logger.info("✅ Deployment validation passed")
            elif smoke_success_rate >= 75:
                validation_report["final_status"] = "warning"
                logger.warning("⚠️ Deployment validation passed with warnings")
            else:
                validation_report["final_status"] = "failed"
                logger.error("❌ Deployment validation failed")
                
                if self.config.enable_rollback:
                    logger.warning("🔄 Executing automatic rollback due to smoke test failures")
                    rollback_result = await self.rollback_manager.execute_rollback("Smoke tests failed")
                    validation_report["rollback_executed"] = True
                    validation_report["rollback_result"] = rollback_result
            
        except Exception as e:
            validation_report["final_status"] = "error"
            validation_report["error"] = str(e)
            validation_report["traceback"] = traceback.format_exc()
            logger.error(f"Deployment validation error: {str(e)}")
            
            if self.config.enable_rollback:
                logger.warning("🔄 Executing emergency rollback")
                rollback_result = await self.rollback_manager.execute_rollback(f"Validation error: {str(e)}")
                validation_report["rollback_executed"] = True
                validation_result["rollback_result"] = rollback_result
        
        validation_report["end_time"] = datetime.now().isoformat()
        
        return validation_report
    
    async def manual_rollback(self, reason: str = "Manual rollback requested") -> Dict[str, Any]:
        """Execute manual rollback"""
        return await self.rollback_manager.execute_rollback(reason)

# ============================================================================
# UTILITIES AND CLI
# ============================================================================

async def quick_validation() -> Dict[str, Any]:
    """Quick deployment validation with default settings"""
    validator = DeploymentValidator()
    return await validator.validate_deployment()

async def production_validation() -> Dict[str, Any]:
    """Production deployment validation with strict settings"""
    config = ValidationConfig(
        timeout_seconds=600,  # 10 minutes
        critical_failure_threshold=0,  # No critical failures allowed
        warning_failure_threshold=2,   # Max 2 warnings
        validate_external_services=True,
        run_load_tests=True,
        enable_rollback=True
    )
    
    validator = DeploymentValidator(config)
    return await validator.validate_deployment()

if __name__ == "__main__":
    # Example usage
    async def main():
        print("Deployment Validation System")
        print("============================")
        
        # Run quick validation
        print("Running quick validation...")
        result = await quick_validation()
        
        print(f"Final Status: {result['final_status']}")
        if result.get('rollback_executed'):
            print("Rollback was executed")
        
        # Print summary
        if result.get('pre_deployment'):
            pre = result['pre_deployment']
            print(f"Pre-deployment: {pre['status']} ({pre['critical_failures']} critical, {pre['warning_failures']} warnings)")
        
        if result.get('smoke_tests'):
            smoke = result['smoke_tests']['summary']
            print(f"Smoke tests: {smoke['passed']}/{smoke['total']} passed ({smoke['success_rate']:.1f}%)")
    
    asyncio.run(main())