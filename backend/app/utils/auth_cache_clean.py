"""
Authentication Caching System - Clean Core Implementation
========================================================

This module contains only the essential caching components extracted from the
over-engineered auth_cache.py system:

- RequestCache: Per-request caching with FastAPI dependency injection
- TTLCache: Thread-safe cache with TTL support  
- JWKSCache: Clerk JWKS caching with background refresh (race condition fixed)
- JWT validation caching decorator and function

This provides real authentication performance improvements without unnecessary complexity.
"""

import os
import logging
import asyncio
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST-LEVEL CACHING WITH FASTAPI DEPENDENCY INJECTION
# ============================================================================

class RequestCache:
    """
    Request-scoped cache that lives for the duration of a single HTTP request.
    Uses FastAPI's dependency system for automatic lifecycle management.
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._request_id = id(self)
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from request cache"""
        self._access_times[key] = time.time()
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in request cache"""
        self._cache[key] = value
        self._access_times[key] = time.time()
        
    def clear(self) -> None:
        """Clear the request cache"""
        self._cache.clear()
        self._access_times.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
            "request_id": self._request_id,
            "last_access": max(self._access_times.values()) if self._access_times else 0
        }

def get_request_cache() -> RequestCache:
    """
    FastAPI dependency that provides a request-scoped cache.
    Each HTTP request gets its own cache instance.
    """
    return RequestCache()

# ============================================================================
# TTL CACHE WITH THREAD SAFETY
# ============================================================================

class TTLCache:
    """
    Thread-safe cache with TTL (Time To Live) support.
    Automatically evicts expired entries and provides cache statistics.
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, returns None if expired or not found"""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
                
            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                # Expired entry
                del self._cache[key]
                self._stats["evictions"] += 1
                self._stats["misses"] += 1
                return None
                
            self._stats["hits"] += 1
            entry["last_accessed"] = time.time()
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl
        
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
                "last_accessed": time.time()
            }
            self._stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if current_time > entry["expires_at"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats["evictions"] += 1
                
        if expired_keys:
            logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
            
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
            return {
                **self._stats,
                "size": len(self._cache),
                "hit_rate": hit_rate,
                "memory_usage_kb": self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """Rough estimate of memory usage in KB"""
        import sys
        total_size = 0
        for entry in self._cache.values():
            total_size += sys.getsizeof(entry["value"])
        return total_size / 1024

# Global JWT validation cache (5-minute TTL)
jwt_validation_cache = TTLCache(default_ttl=300)

# ============================================================================
# JWKS CACHE WITH BACKGROUND REFRESH (RACE CONDITION FIXED)
# ============================================================================

class JWKSCache:
    """
    Advanced JWKS cache with background refresh, fallback mechanisms,
    and comprehensive error handling. Fixed AsyncHttpxClientWrapper error.
    """
    
    def __init__(self, jwks_url: str, refresh_interval: int = 7200):  # 2 hours
        self.jwks_url = jwks_url
        self.refresh_interval = refresh_interval
        self._cache: Optional[Dict[str, Any]] = None
        self._last_updated: Optional[datetime] = None
        self._lock = threading.RLock()
        # FIXED: Use asyncio.Lock instead of boolean flag to prevent race conditions
        self._refresh_lock = None  # Will be initialized when first used
        self._fallback_cache: Optional[Dict[str, Any]] = None
        # FIXED: Track background tasks to prevent orphaned httpx clients
        self._background_tasks: Set[asyncio.Task] = set()
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "background_refreshes": 0,
            "failed_refreshes": 0,
            "fallback_uses": 0
        }
    
    def __del__(self):
        """Cleanup any remaining background tasks on garbage collection"""
        if hasattr(self, '_background_tasks'):
            for task in self._background_tasks.copy():
                if not task.done():
                    task.cancel()
    
    def _get_refresh_lock(self):
        """Get or create the asyncio refresh lock"""
        if self._refresh_lock is None:
            self._refresh_lock = asyncio.Lock()
        return self._refresh_lock
        
    async def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get JWKS with automatic refresh and fallback mechanisms.
        
        Args:
            force_refresh: Force a refresh even if cache is valid
            
        Returns:
            JWKS dictionary
            
        Raises:
            HTTPException: If JWKS cannot be retrieved and no fallback exists
        """
        with self._lock:
            # Check if we have valid cached data
            if not force_refresh and self._is_cache_valid():
                self._stats["cache_hits"] += 1
                logger.debug("🎯 JWKS cache hit")
                return self._cache
            
            self._stats["cache_misses"] += 1
        
        # FIXED: Proper task management instead of fire-and-forget
        refresh_lock = self._get_refresh_lock()
        if not refresh_lock.locked():
            # Create and track background task
            task = asyncio.create_task(self._refresh_jwks())
            self._background_tasks.add(task)
            # Clean up completed tasks
            task.add_done_callback(self._background_tasks.discard)
        
        # If we have any cached data (even if stale), return it while refresh happens
        if self._cache is not None:
            logger.debug("📋 Returning stale JWKS while refresh is in progress")
            return self._cache
        
        # No cache available, must fetch synchronously
        return await self._fetch_jwks_sync()
    
    def _is_cache_valid(self) -> bool:
        """Check if the current cache is still valid"""
        if self._cache is None or self._last_updated is None:
            return False
        
        age = datetime.now() - self._last_updated
        return age < timedelta(seconds=self.refresh_interval)
    
    async def _refresh_jwks(self) -> None:
        """Background task to refresh JWKS - RACE CONDITION FIXED"""
        refresh_lock = self._get_refresh_lock()
        async with refresh_lock:  # FIXED: Proper async lock
            try:
                logger.debug("🔄 Starting background JWKS refresh...")
                new_jwks = await self._fetch_jwks_from_url()
                
                with self._lock:
                    # Store old cache as fallback before updating
                    if self._cache is not None:
                        self._fallback_cache = self._cache.copy()
                    
                    self._cache = new_jwks
                    self._last_updated = datetime.now()
                    self._stats["background_refreshes"] += 1
                    
                logger.info("✅ JWKS background refresh completed successfully")
                
            except Exception as e:
                logger.error(f"❌ JWKS background refresh failed: {str(e)}")
                self._stats["failed_refreshes"] += 1
    
    async def _fetch_jwks_sync(self) -> Dict[str, Any]:
        """Synchronously fetch JWKS when no cache is available"""
        try:
            logger.debug("🔄 Fetching JWKS synchronously (no cache available)")
            jwks = await self._fetch_jwks_from_url()
            
            with self._lock:
                self._cache = jwks
                self._last_updated = datetime.now()
                
            return jwks
            
        except Exception as e:
            # Try to use fallback cache
            if self._fallback_cache is not None:
                logger.warning(f"⚠️ Using fallback JWKS cache due to fetch failure: {str(e)}")
                self._stats["fallback_uses"] += 1
                return self._fallback_cache
            
            logger.error(f"🚨 JWKS fetch failed with no fallback available: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to retrieve JWKS for token validation"
            )
    
    async def _fetch_jwks_from_url(self) -> Dict[str, Any]:
        """Fetch JWKS from the configured URL - FIXED: Proper context management"""
        timeout = httpx.Timeout(10.0, connect=5.0)  # 10s total, 5s connect
        
        # FIXED: Use proper async context manager to prevent _state attribute errors
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()
    
    async def cleanup(self) -> None:
        """Explicit cleanup method for graceful shutdown"""
        # Cancel all background tasks
        for task in self._background_tasks.copy():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._background_tasks.clear()
        logger.info("🧹 JWKS cache cleanup completed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        with self._lock:
            return {
                **self._stats,
                "cache_valid": self._is_cache_valid(),
                "last_updated": self._last_updated.isoformat() if self._last_updated else None,
                "has_fallback": self._fallback_cache is not None,
                "cache_age_seconds": (datetime.now() - self._last_updated).total_seconds() if self._last_updated else None,
                "active_background_tasks": len([t for t in self._background_tasks if not t.done()])
            }
    
    def invalidate(self) -> None:
        """Manually invalidate the cache"""
        with self._lock:
            self._cache = None
            self._last_updated = None
        logger.info("🗑️ JWKS cache manually invalidated")
# Global JWKS cache instance
_jwks_cache: Optional[JWKSCache] = None

def get_jwks_cache() -> JWKSCache:
    """Get or create the global JWKS cache instance"""
    global _jwks_cache
    
    if _jwks_cache is None:
        # Get JWKS URL from environment
        clerk_domain = os.getenv('NEXT_PUBLIC_CLERK_DOMAIN')
        if not clerk_domain:
            raise ValueError("NEXT_PUBLIC_CLERK_DOMAIN environment variable is required")
        
        jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
        _jwks_cache = JWKSCache(jwks_url, refresh_interval=7200)  # 2 hours
        
    return _jwks_cache

# ============================================================================
# JWT VALIDATION CACHING DECORATOR AND FUNCTION
# ============================================================================

def cached_jwt_validation(func):
    """
    Decorator that adds JWT validation caching with 5-minute TTL.
    Caches successful JWT validations to avoid repeated cryptographic operations.
    """
    @wraps(func)
    async def wrapper(token: str, *args, **kwargs):
        # Create cache key from token hash (for security)
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        cache_key = f"jwt_validation:{token_hash}"
        
        # Try to get from cache
        cached_result = jwt_validation_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"🎯 JWT validation cache hit")
            return cached_result
        
        try:
            # Call the actual validation function
            result = await func(token, *args, **kwargs)
            
            # Cache successful validation (5 minutes)
            jwt_validation_cache.set(cache_key, result, ttl=300)
            logger.debug(f"💾 JWT validation cached")
            
            return result
            
        except Exception as e:
            # Don't cache validation failures
            logger.debug(f"❌ JWT validation failed, not caching: {str(e)}")
            raise
            
    return wrapper

security = HTTPBearer()

@cached_jwt_validation
async def verify_clerk_token_cached(token: str) -> Dict[str, Any]:
    """
    Enhanced JWT verification with comprehensive caching.
    This function integrates all three phases of caching.
    """
    logger.debug(f"🔍 Token validation attempt with caching")
    
    # Basic token format validation
    if token.startswith("sess_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: Session token received, JWT required"
        )
    
    if not token.startswith("eyJ"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format: Not a valid JWT"
        )
    
    try:
        # Get JWKS with advanced caching
        jwks_cache = get_jwks_cache()
        jwks = await jwks_cache.get_jwks()
        
        # Decode token header to get kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header - missing key ID"
            )
        
        # Find the matching key
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signing key not found"
            )
        
        # Verify token
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "verify_iss": False,
                "verify_signature": True,
                "verify_exp": True,
                "verify_sub": False
            }
        )
        
        logger.debug(f"✅ Token validated for user with caching: {payload.get('sub')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during cached token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

# ============================================================================
# BASIC HEALTH CHECK
# ============================================================================

async def cache_health_check() -> Dict[str, Any]:
    """
    Simple health check for cache components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Test JWT validation cache
        jwt_stats = jwt_validation_cache.get_stats()
        health_status["components"]["jwt_validation_cache"] = {
            "status": "healthy",
            "stats": jwt_stats
        }
    except Exception as e:
        health_status["components"]["jwt_validation_cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    try:
        # Test JWKS cache
        jwks_cache = get_jwks_cache()
        jwks_stats = jwks_cache.get_stats()
        
        health_status["components"]["jwks_cache"] = {
            "status": "healthy",
            "stats": jwks_stats
        }
    except Exception as e:
        health_status["components"]["jwks_cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

# ============================================================================
# EXPORT INTERFACES
# ============================================================================

__all__ = [
    # Cache classes
    "RequestCache",
    "TTLCache", 
    "JWKSCache",
    
    # Main functions
    "verify_clerk_token_cached",
    "cached_jwt_validation",
    "get_request_cache",
    "get_jwks_cache",
    "cache_health_check",
    
    # Cache instances
    "jwt_validation_cache",
]