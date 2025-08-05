"""Rate limiting implementation for API endpoints"""
import time
from typing import Dict, Optional, Callable
from fastapi import Request, HTTPException, status
from functools import wraps
import redis
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """Token bucket rate limiter with Redis support"""
    
    def __init__(
        self, 
        max_requests: int, 
        window_seconds: int,
        redis_client: Optional[redis.Redis] = None,
        identifier_extractor: Optional[Callable] = None
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis_client
        self.identifier_extractor = identifier_extractor or self._default_identifier
        
        # In-memory fallback
        self.buckets: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    def _default_identifier(self, request: Request) -> str:
        """Default identifier extractor - uses IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        if self.redis_client:
            return self._check_redis(identifier)
        else:
            return await self._check_memory(identifier)
    
    def _check_redis(self, identifier: str) -> bool:
        """Check rate limit using Redis"""
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        request_count = self.redis_client.zcard(key)
        
        if request_count >= self.max_requests:
            return False
        
        # Add current request
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, self.window_seconds)
        
        return True
    
    async def _check_memory(self, identifier: str) -> bool:
        """Check rate limit using in-memory storage"""
        async with self.lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            # Remove old entries
            self.buckets[identifier] = [
                timestamp for timestamp in self.buckets[identifier]
                if timestamp > window_start
            ]
            
            # Check limit
            if len(self.buckets[identifier]) >= self.max_requests:
                return False
            
            # Add current request
            self.buckets[identifier].append(current_time)
            return True
    
    async def get_reset_time(self, identifier: str) -> Optional[datetime]:
        """Get time when rate limit resets"""
        if self.redis_client:
            key = f"rate_limit:{identifier}"
            oldest_timestamp = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_timestamp:
                reset_time = oldest_timestamp[0][1] + self.window_seconds
                return datetime.fromtimestamp(reset_time)
        else:
            async with self.lock:
                if identifier in self.buckets and self.buckets[identifier]:
                    oldest = min(self.buckets[identifier])
                    reset_time = oldest + self.window_seconds
                    return datetime.fromtimestamp(reset_time)
        return None


class AdvancedRateLimiter(RateLimiter):
    """Advanced rate limiter with multiple tiers"""
    
    def __init__(
        self,
        tiers: Dict[str, Dict[str, int]],
        redis_client: Optional[redis.Redis] = None,
        identifier_extractor: Optional[Callable] = None
    ):
        self.tiers = tiers
        self.redis_client = redis_client
        self.identifier_extractor = identifier_extractor or self._default_identifier
        self.limiters = {}
        
        # Create rate limiter for each tier
        for tier_name, config in tiers.items():
            self.limiters[tier_name] = RateLimiter(
                max_requests=config["max_requests"],
                window_seconds=config["window_seconds"],
                redis_client=redis_client,
                identifier_extractor=identifier_extractor
            )
    
    async def check_rate_limit(self, identifier: str, tier: str = "default") -> bool:
        """Check rate limit for specific tier"""
        if tier not in self.limiters:
            tier = "default"
        
        return await self.limiters[tier].check_rate_limit(identifier)


def rate_limit(limiter: RateLimiter):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            identifier = limiter.identifier_extractor(request)
            
            if not await limiter.check_rate_limit(identifier):
                reset_time = await limiter.get_reset_time(identifier)
                retry_after = int((reset_time - datetime.now()).total_seconds()) if reset_time else limiter.window_seconds
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(limiter.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time.timestamp())) if reset_time else ""
                    }
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Pre-configured rate limiters
default_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 req/min
strict_limiter = RateLimiter(max_requests=10, window_seconds=60)   # 10 req/min
auth_limiter = RateLimiter(max_requests=5, window_seconds=300)     # 5 req/5min

# Advanced rate limiter with tiers
tiered_limiter = AdvancedRateLimiter(
    tiers={
        "default": {"max_requests": 100, "window_seconds": 60},
        "premium": {"max_requests": 1000, "window_seconds": 60},
        "admin": {"max_requests": 10000, "window_seconds": 60}
    }
)


class RateLimitMiddleware:
    """FastAPI middleware for global rate limiting"""
    
    def __init__(
        self,
        app,
        limiter: RateLimiter,
        exclude_paths: Optional[list] = None
    ):
        self.app = app
        self.limiter = limiter
        self.exclude_paths = exclude_paths or ["/docs", "/openapi.json", "/health"]
    
    async def __call__(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Extract identifier
        identifier = self.limiter.identifier_extractor(request)
        
        # Check rate limit
        if not await self.limiter.check_rate_limit(identifier):
            reset_time = await self.limiter.get_reset_time(identifier)
            retry_after = int((reset_time - datetime.now()).total_seconds()) if reset_time else self.limiter.window_seconds
            
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time.timestamp())) if reset_time else ""
                }
            )
        
        response = await call_next(request)
        return response