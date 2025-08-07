"""
Authentication Cache System Tests
=================================

Comprehensive tests for the three-phase authentication caching system:
- Phase 1: Request-level caching
- Phase 2: JWT validation cache with TTL
- Phase 3: JWKS optimization with background refresh

These tests ensure thread-safety, proper error handling, and performance characteristics.
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.utils.auth_cache import (
    RequestCache,
    TTLCache,
    JWKSCache,
    CacheMetrics,
    jwt_validation_cache,
    get_jwks_cache,
    get_request_cache,
    cached_jwt_validation,
    verify_clerk_token_cached,
    cache_health_check
)


class TestRequestCache:
    """Test Phase 1: Request-level caching"""
    
    def test_request_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = RequestCache()
        
        # Test set and get
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        # Test non-existent key
        assert cache.get("non_existent") is None
        
        # Test clear
        cache.clear()
        assert cache.get("test_key") is None
    
    def test_request_cache_stats(self):
        """Test cache statistics"""
        cache = RequestCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        assert "key1" in stats["keys"]
        assert "key2" in stats["keys"]
        assert stats["request_id"] == id(cache)
    
    def test_request_cache_access_times(self):
        """Test access time tracking"""
        cache = RequestCache()
        cache.set("test_key", "test_value")
        
        # Get the key multiple times
        cache.get("test_key")
        time.sleep(0.01)  # Small delay
        cache.get("test_key")
        
        stats = cache.get_stats()
        assert stats["last_access"] > 0


class TestTTLCache:
    """Test Phase 2: JWT validation cache with TTL"""
    
    def test_ttl_cache_basic_operations(self):
        """Test basic TTL cache operations"""
        cache = TTLCache(default_ttl=1)  # 1 second TTL
        
        # Test set and get
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        # Test expiration
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("test_key") is None
    
    def test_ttl_cache_custom_ttl(self):
        """Test custom TTL values"""
        cache = TTLCache(default_ttl=10)
        
        # Set with custom TTL
        cache.set("short_ttl", "value", ttl=1)
        cache.set("long_ttl", "value", ttl=5)
        
        # Check both values exist
        assert cache.get("short_ttl") == "value"
        assert cache.get("long_ttl") == "value"
        
        # Wait for short TTL to expire
        time.sleep(1.1)
        assert cache.get("short_ttl") is None
        assert cache.get("long_ttl") == "value"
    
    def test_ttl_cache_thread_safety(self):
        """Test thread safety of TTL cache"""
        cache = TTLCache(default_ttl=5)
        results = []
        
        def worker(thread_id):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                cache.set(key, f"value_{i}")
                retrieved = cache.get(key)
                results.append(retrieved == f"value_{i}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert all(results)
    
    def test_ttl_cache_cleanup(self):
        """Test expired entry cleanup"""
        cache = TTLCache(default_ttl=1)
        
        # Add entries with different TTLs
        cache.set("expire_soon", "value1", ttl=1)
        cache.set("expire_later", "value2", ttl=5)
        
        # Wait for first entry to expire
        time.sleep(1.1)
        
        # Cleanup should remove expired entry
        cleaned = cache.cleanup_expired()
        assert cleaned == 1
        
        # Check remaining entry
        assert cache.get("expire_soon") is None
        assert cache.get("expire_later") == "value2"
    
    def test_ttl_cache_stats(self):
        """Test cache statistics"""
        cache = TTLCache(default_ttl=5)
        
        # Generate some hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert stats["hit_rate"] == 2/3


class TestJWKSCache:
    """Test Phase 3: JWKS optimization with background refresh"""
    
    @pytest.fixture
    def mock_jwks_response(self):
        """Mock JWKS response"""
        return {
            "keys": [
                {
                    "kid": "test_key_id",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
    
    @pytest.fixture
    def jwks_cache(self, mock_jwks_response):
        """Create JWKS cache with mocked HTTP client"""
        cache = JWKSCache("https://test.clerk.dev/.well-known/jwks.json", refresh_interval=2)
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_jwks_response
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            yield cache
    
    @pytest.mark.asyncio
    async def test_jwks_cache_fetch(self, jwks_cache, mock_jwks_response):
        """Test JWKS fetching"""
        jwks = await jwks_cache.get_jwks()
        assert jwks == mock_jwks_response
        
        # Should use cached version on second call
        jwks2 = await jwks_cache.get_jwks()
        assert jwks2 == mock_jwks_response
    
    @pytest.mark.asyncio
    async def test_jwks_cache_force_refresh(self, jwks_cache, mock_jwks_response):
        """Test forced refresh"""
        # Initial fetch
        await jwks_cache.get_jwks()
        
        # Force refresh
        jwks = await jwks_cache.get_jwks(force_refresh=True)
        assert jwks == mock_jwks_response
    
    def test_jwks_cache_stats(self, jwks_cache):
        """Test JWKS cache statistics"""
        stats = jwks_cache.get_stats()
        
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "background_refreshes" in stats
        assert "failed_refreshes" in stats
        assert "fallback_uses" in stats
        assert "cache_valid" in stats
    
    def test_jwks_cache_invalidate(self, jwks_cache):
        """Test cache invalidation"""
        jwks_cache.invalidate()
        
        stats = jwks_cache.get_stats()
        assert not stats["cache_valid"]
        assert stats["last_updated"] is None


class TestCachedJWTValidation:
    """Test JWT validation caching decorator"""
    
    @pytest.mark.asyncio
    async def test_jwt_validation_caching(self):
        """Test JWT validation is cached"""
        # Mock validation function
        mock_validation_calls = []
        
        @cached_jwt_validation
        async def mock_verify_token(token):
            mock_validation_calls.append(token)
            return {"sub": "test_user", "exp": time.time() + 3600}
        
        # Call with same token multiple times
        token = "test_token_12345"
        result1 = await mock_verify_token(token)
        result2 = await mock_verify_token(token)
        
        # Should only call the actual function once
        assert len(mock_validation_calls) == 1
        assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_jwt_validation_error_not_cached(self):
        """Test that validation errors are not cached"""
        mock_validation_calls = []
        
        @cached_jwt_validation
        async def mock_verify_token(token):
            mock_validation_calls.append(token)
            raise ValueError("Invalid token")
        
        token = "invalid_token"
        
        # Call multiple times, should fail each time
        with pytest.raises(ValueError):
            await mock_verify_token(token)
        
        with pytest.raises(ValueError):
            await mock_verify_token(token)
        
        # Should call the function each time (no caching of errors)
        assert len(mock_validation_calls) == 2


class TestCacheMetrics:
    """Test cache metrics and monitoring"""
    
    def test_get_all_stats(self):
        """Test comprehensive statistics collection"""
        # Clear cache first
        jwt_validation_cache.clear()
        
        # Generate some activity
        jwt_validation_cache.set("test", "value")
        jwt_validation_cache.get("test")
        jwt_validation_cache.get("nonexistent")
        
        stats = CacheMetrics.get_all_stats()
        
        assert "timestamp" in stats
        assert "jwt_validation_cache" in stats
        assert stats["jwt_validation_cache"]["hits"] >= 1
        assert stats["jwt_validation_cache"]["misses"] >= 1
    
    def test_cleanup_expired_entries(self):
        """Test cleanup across all caches"""
        # Add expiring entries
        jwt_validation_cache.set("expire_test", "value", ttl=1)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Cleanup
        results = CacheMetrics.cleanup_expired_entries()
        
        assert "jwt_validation_cache" in results
        assert results["jwt_validation_cache"] >= 0


class TestCacheIntegration:
    """Test integration with authentication system"""
    
    @pytest.mark.asyncio
    async def test_cache_health_check(self):
        """Test comprehensive cache health check"""
        health = await cache_health_check()
        
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in health
        assert "components" in health
        
        # Should have JWT validation cache component
        assert "jwt_validation_cache" in health["components"]
    
    @pytest.mark.asyncio
    @patch('app.utils.auth_cache.get_jwks_cache')
    async def test_verify_clerk_token_cached_integration(self, mock_get_jwks_cache):
        """Test the full cached token verification"""
        # Mock JWKS cache
        mock_cache = Mock()
        mock_cache.get_jwks = AsyncMock(return_value={
            "keys": [{
                "kid": "test_kid",
                "kty": "RSA",
                "use": "sig",
                "n": "test_n",
                "e": "AQAB"
            }]
        })
        mock_get_jwks_cache.return_value = mock_cache
        
        # Mock JWT decoding
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.algorithms.RSAAlgorithm.from_jwk') as mock_from_jwk, \
             patch('jwt.decode') as mock_decode:
            
            mock_header.return_value = {"kid": "test_kid"}
            mock_from_jwk.return_value = "mock_key"
            mock_decode.return_value = {"sub": "test_user", "exp": time.time() + 3600}
            
            # Test token verification
            token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
            result = await verify_clerk_token_cached(token)
            
            assert result["sub"] == "test_user"


class TestPerformanceCharacteristics:
    """Test performance characteristics of the caching system"""
    
    def test_request_cache_performance(self):
        """Test request cache performance with many operations"""
        cache = RequestCache()
        
        start_time = time.time()
        
        # Perform many operations
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        for i in range(1000):
            cache.get(f"key_{i}")
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # Should complete quickly (adjust threshold as needed)
        assert operation_time < 1.0  # 1 second for 2000 operations
    
    def test_ttl_cache_memory_efficiency(self):
        """Test TTL cache memory usage tracking"""
        cache = TTLCache(default_ttl=60)
        
        # Add many entries
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}" * 100)  # Larger values
        
        stats = cache.get_stats()
        
        # Should track memory usage
        assert stats["memory_usage_kb"] > 0
        assert stats["size"] == 100
    
    def test_concurrent_access_performance(self):
        """Test performance under concurrent access"""
        cache = TTLCache(default_ttl=60)
        results = []
        
        def concurrent_worker():
            for i in range(50):
                cache.set(f"key_{threading.current_thread().ident}_{i}", f"value_{i}")
                result = cache.get(f"key_{threading.current_thread().ident}_{i}")
                results.append(result is not None)
        
        threads = []
        start_time = time.time()
        
        # Create multiple threads
        for _ in range(10):
            thread = threading.Thread(target=concurrent_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All operations should succeed
        assert all(results)
        
        # Should complete in reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max


if __name__ == "__main__":
    pytest.main([__file__, "-v"])