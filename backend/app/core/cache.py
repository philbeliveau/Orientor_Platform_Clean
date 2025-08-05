"""
Redis caching layer for Orientor backend services.
Provides a unified caching interface with fallback to in-memory cache.
"""

import os
import json
import logging
from typing import Optional, Any, Dict, Union
from datetime import timedelta
import hashlib

try:
    import redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not installed. Falling back to in-memory cache.")

logger = logging.getLogger(__name__)

class CacheService:
    """
    Unified cache service with Redis primary and in-memory fallback.
    """
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        if REDIS_AVAILABLE:
            try:
                # Configure Redis connection
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except (RedisError, Exception) as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self.redis_client = None
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate a namespaced cache key."""
        return f"orientor:{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        return json.dumps(value)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage."""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Get value from cache. Tries Redis first, falls back to memory.
        """
        full_key = self._generate_key(namespace, key)
        
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(full_key)
                if value:
                    logger.debug(f"Cache hit (Redis): {full_key}")
                    return self._deserialize_value(value)
            except RedisError as e:
                logger.warning(f"Redis get error: {str(e)}")
        
        # Fallback to memory cache
        if full_key in self.memory_cache:
            cache_entry = self.memory_cache[full_key]
            # Check if expired
            import time
            if cache_entry['expiry'] > time.time():
                logger.debug(f"Cache hit (Memory): {full_key}")
                return cache_entry['value']
            else:
                # Clean up expired entry
                del self.memory_cache[full_key]
        
        logger.debug(f"Cache miss: {full_key}")
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Union[int, timedelta] = 3600,
        namespace: str = "default"
    ) -> bool:
        """
        Set value in cache with TTL (in seconds or timedelta).
        """
        full_key = self._generate_key(namespace, key)
        
        # Convert timedelta to seconds
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        
        # Try Redis first
        if self.redis_client:
            try:
                serialized = self._serialize_value(value)
                self.redis_client.setex(full_key, ttl, serialized)
                logger.debug(f"Cache set (Redis): {full_key}, TTL: {ttl}s")
                return True
            except RedisError as e:
                logger.warning(f"Redis set error: {str(e)}")
        
        # Fallback to memory cache
        import time
        self.memory_cache[full_key] = {
            'value': value,
            'expiry': time.time() + ttl
        }
        logger.debug(f"Cache set (Memory): {full_key}, TTL: {ttl}s")
        
        # Limit memory cache size
        if len(self.memory_cache) > 1000:
            self._cleanup_memory_cache()
        
        return True
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete value from cache.
        """
        full_key = self._generate_key(namespace, key)
        
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.delete(full_key)
            except RedisError as e:
                logger.warning(f"Redis delete error: {str(e)}")
        
        # Also delete from memory cache
        if full_key in self.memory_cache:
            del self.memory_cache[full_key]
        
        return True
    
    async def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        """
        pattern = self._generate_key(namespace, "*")
        count = 0
        
        # Clear from Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            except RedisError as e:
                logger.warning(f"Redis clear error: {str(e)}")
        
        # Clear from memory cache
        keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"orientor:{namespace}:")]
        for key in keys_to_delete:
            del self.memory_cache[key]
            count += 1
        
        return count
    
    def _cleanup_memory_cache(self):
        """
        Remove expired entries and oldest entries if cache is too large.
        """
        import time
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = [
            k for k, v in self.memory_cache.items() 
            if v['expiry'] <= current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # If still too large, remove oldest entries
        if len(self.memory_cache) > 800:
            sorted_keys = sorted(
                self.memory_cache.items(), 
                key=lambda x: x[1]['expiry']
            )
            for key, _ in sorted_keys[:200]:
                del self.memory_cache[key]
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        Useful for caching function results.
        """
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

# Global cache instance
cache = CacheService()