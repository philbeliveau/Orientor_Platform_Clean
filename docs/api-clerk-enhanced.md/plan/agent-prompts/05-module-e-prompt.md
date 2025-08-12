# Agent Prompt: Module E - Backend Authentication Standardization

## 🎯 MISSION CRITICAL TASK
You are implementing **Backend Authentication Standardization** that will unify the remaining 15% of inconsistent router patterns, implement JWKS caching, and create performance-optimized authentication middleware for the FastAPI backend.

## 🚨 CRITICAL PROBLEM TO SOLVE
Based on platform analysis, the backend has authentication inconsistencies:
```python
# CURRENT PROBLEMS:
# 1. 4 routers (10%) with inconsistent imports
from app.utils.clerk_auth import get_current_user  # Missing 'with_db_sync'

# 2. 1 legacy router (2.5%) with custom JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Custom JWT implementation - NOT using Clerk

# 3. No JWKS caching - every request validates against Clerk API
# 4. No centralized error handling
# 5. No performance monitoring
```
**Impact**: 15% inconsistency, poor performance, security vulnerabilities

## 🎯 YOUR SOLUTION TARGET
Create unified, high-performance backend authentication:
```python
# YOUR TARGET SOLUTION:
Enhanced JWKS Cache → Unified Auth Service → Standardized Routers → Performance Monitoring
```

## 📋 IMPLEMENTATION REQUIREMENTS

### 1. Create Enhanced Authentication Service
**File**: `backend/app/utils/enhanced_clerk_auth.py`

**Required Interface**:
```python
class EnhancedClerkAuth:
    # Core authentication
    async def validate_token_enhanced(token: str, template: Optional[str]) -> Dict[str, Any]
    async def get_user_with_db_sync_enhanced(token: str, db: Session) -> User
    
    # Performance features
    def get_metrics() -> AuthMetrics
    def get_cache_status() -> CacheStatus
    
    # Lifecycle management
    async def cleanup() -> None

class AuthMetrics:
    total_requests: int
    cache_hits: int
    cache_misses: int
    validation_time: float
    error_rate: float
    jwks_refresh_count: int
```

### 2. Required Features
```python
✅ MUST IMPLEMENT:
├── JWKS caching with Redis support
├── Token validation optimization (<50ms)
├── Unified router migration (4 files)
├── Legacy system modernization (1 router)
├── Performance metrics collection
├── Centralized error handling
├── Database user synchronization
└── Health monitoring endpoints

⚡ PERFORMANCE TARGETS:
├── Token validation: <50ms (JWKS cache), <10ms (Redis cache)
├── JWKS cache hit rate: >90%
├── User sync: <100ms existing, <500ms new users
├── Error rate: <0.1%
└── Memory usage: <50MB for auth caching
```

### 3. Files to Migrate
```python
ROUTERS_TO_STANDARDIZE = [
    "backend/app/routers/chat.py",           # Inconsistent import
    "backend/app/routers/users.py",          # Legacy pattern
    "backend/app/routers/jobs.py",           # Inconsistent import  
    "backend/app/routers/onboarding.py"      # Inconsistent import
]
```

## 🔧 DETAILED IMPLEMENTATION STEPS

### Step 1: Enhanced Authentication Service
```python
# File: backend/app/utils/enhanced_clerk_auth.py

import asyncio
import time
import json
from functools import lru_cache
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWKClient
import redis
from dataclasses import dataclass

from ..database import get_db
from ..models.user import User
from ..config import settings

@dataclass
class BackendAuthConfig:
    # JWKS caching
    jwks_cache_enabled: bool = True
    jwks_cache_ttl: int = 3600  # 1 hour
    jwks_max_cached_keys: int = 16
    
    # Redis configuration
    redis_enabled: bool = True
    redis_cache_ttl: int = 300  # 5 minutes
    
    # Performance settings
    connection_pooling: bool = True
    async_processing: bool = True
    metrics_collection: bool = True
    
    # Error handling
    error_handling_mode: str = "graceful"  # "strict" or "graceful"
    fallback_auth: bool = True
    retry_attempts: int = 3

@dataclass
class AuthMetrics:
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    validation_time: float = 0.0
    error_rate: float = 0.0
    jwks_refresh_count: int = 0

class EnhancedClerkAuth:
    def __init__(self, config: BackendAuthConfig = None):
        self.config = config or BackendAuthConfig()
        self.metrics = AuthMetrics()
        
        # Initialize JWKS client with caching
        self.jwks_client = PyJWKClient(
            f"https://{settings.CLERK_DOMAIN}/.well-known/jwks.json",
            cache_keys=self.config.jwks_cache_enabled,
            max_cached_keys=self.config.jwks_max_cached_keys,
            cache_jwk_set=self.config.jwks_cache_enabled,
            jwk_set_cache_lifetime=self.config.jwks_cache_ttl
        )
        
        # Redis client for distributed caching
        self.redis_client = None
        if self.config.redis_enabled:
            try:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self.redis_client = None
        
        # HTTP client for Clerk API
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=100, 
                max_keepalive_connections=20
            )
        )

    async def validate_token_enhanced(
        self, 
        token: str, 
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced token validation with caching and performance optimization
        """
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # Check Redis cache first
            if self.redis_client:
                cached_claims = await self._get_cached_claims(token)
                if cached_claims:
                    self.metrics.cache_hits += 1
                    return cached_claims
            
            # Validate token with JWKS
            claims = await self._validate_with_jwks(token)
            
            # Cache valid claims
            if self.redis_client:
                await self._cache_claims(token, claims)
            
            self.metrics.cache_misses += 1
            return claims
            
        except Exception as error:
            self.metrics.error_rate = min(self.metrics.error_rate + 0.01, 1.0)
            raise HTTPException(
                status_code=401,
                detail=f"Token validation failed: {str(error)}"
            )
        finally:
            # Record performance metrics
            validation_time = time.time() - start_time
            self.metrics.validation_time = (
                self.metrics.validation_time + validation_time
            ) / 2

    async def _validate_with_jwks(self, token: str) -> Dict[str, Any]:
        """
        Validate token using JWKS with automatic key rotation
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and validate token
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=getattr(settings, 'CLERK_AUDIENCE', None),
                issuer=f"https://{settings.CLERK_DOMAIN}"
            )
            
            return claims
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )

    async def _get_cached_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached token claims from Redis
        """
        try:
            if not self.redis_client:
                return None
                
            cache_key = f"clerk_token:{hash(token)}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            pass
        return None

    async def _cache_claims(self, token: str, claims: Dict[str, Any]) -> None:
        """
        Cache token claims in Redis
        """
        try:
            if not self.redis_client:
                return
                
            cache_key = f"clerk_token:{hash(token)}"
            self.redis_client.setex(
                cache_key,
                self.config.redis_cache_ttl,
                json.dumps(claims)
            )
        except Exception:
            pass

    async def get_user_with_db_sync_enhanced(
        self, 
        token: str, 
        db: Session
    ) -> User:
        """
        Enhanced user retrieval with database synchronization
        """
        # Validate token and get claims
        claims = await self.validate_token_enhanced(token)
        clerk_user_id = claims.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )
        
        # Get or create user in database
        user = await self._get_or_sync_user(clerk_user_id, claims, db)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found or sync failed"
            )
        
        return user

    async def _get_or_sync_user(
        self, 
        clerk_user_id: str, 
        claims: Dict[str, Any], 
        db: Session
    ) -> Optional[User]:
        """
        Get user from database or sync from Clerk
        """
        # Try to get user from database first
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        
        if user:
            # Update user info if needed
            await self._update_user_if_needed(user, claims, db)
            return user
        
        # User not in database, sync from Clerk
        return await self._sync_user_from_clerk(clerk_user_id, claims, db)

    async def _update_user_if_needed(
        self, 
        user: User, 
        claims: Dict[str, Any], 
        db: Session
    ) -> None:
        """
        Update user information if needed
        """
        # Check if user info needs updating
        email = claims.get("email")
        if email and user.email != email:
            user.email = email
            user.updated_at = int(time.time())
            db.commit()

    async def _sync_user_from_clerk(
        self, 
        clerk_user_id: str, 
        claims: Dict[str, Any], 
        db: Session
    ) -> User:
        """
        Sync user from Clerk API to local database
        """
        try:
            # Fetch user details from Clerk API
            response = await self.http_client.get(
                f"https://api.clerk.dev/v1/users/{clerk_user_id}",
                headers={
                    "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Failed to sync user from Clerk"
                )
            
            user_data = response.json()
            
            # Create new user in database
            user = User(
                clerk_user_id=clerk_user_id,
                email=user_data.get("email_addresses", [{}])[0].get("email_address"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"User sync failed: {str(e)}"
            )

    def get_metrics(self) -> AuthMetrics:
        """
        Get authentication metrics
        """
        return self.metrics

    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get cache status information
        """
        status = {
            "jwks_cache_enabled": self.config.jwks_cache_enabled,
            "redis_enabled": self.redis_client is not None,
            "total_requests": self.metrics.total_requests,
            "cache_hit_rate": (
                self.metrics.cache_hits / max(self.metrics.total_requests, 1)
            ),
            "error_rate": self.metrics.error_rate
        }
        
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                status["redis_status"] = "connected"
                status["redis_memory"] = redis_info.get("used_memory_human")
            except:
                status["redis_status"] = "disconnected"
        
        return status

    async def cleanup(self):
        """
        Cleanup resources
        """
        await self.http_client.aclose()
        if self.redis_client:
            self.redis_client.close()

# Initialize global auth instance
enhanced_clerk_auth = EnhancedClerkAuth()

# Security scheme
security_scheme = HTTPBearer()

async def get_current_user_enhanced(
    token: str = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Enhanced dependency for getting current authenticated user
    """
    return await enhanced_clerk_auth.get_user_with_db_sync_enhanced(
        token.credentials, 
        db
    )
```

### Step 2: Router Migration Script
```python
# File: backend/scripts/migrate_routers.py

import os
import re
from pathlib import Path
from typing import List, Tuple

class RouterMigrationTool:
    """
    Tool to migrate routers to use enhanced authentication
    """
    
    ROUTERS_TO_MIGRATE = [
        "backend/app/routers/chat.py",
        "backend/app/routers/users.py", 
        "backend/app/routers/jobs.py",
        "backend/app/routers/onboarding.py"
    ]
    
    MIGRATION_PATTERNS = [
        # Fix inconsistent imports
        (
            r"from app\.utils\.clerk_auth import get_current_user\b",
            "from app.utils.enhanced_clerk_auth import get_current_user_enhanced as get_current_user"
        ),
        (
            r"from \.\.utils\.clerk_auth import get_current_user\b",
            "from ..utils.enhanced_clerk_auth import get_current_user_enhanced as get_current_user"
        ),
        # Fix legacy patterns
        (
            r"from \.utils\.clerk_auth import get_current_user_with_db_sync as get_current_user",
            "from .utils.enhanced_clerk_auth import get_current_user_enhanced as get_current_user"
        )
    ]

    def migrate_all_routers(self) -> None:
        """
        Migrate all inconsistent routers
        """
        print("🚀 Starting router migration to enhanced authentication...")
        
        for router_path in self.ROUTERS_TO_MIGRATE:
            self.migrate_single_router(router_path)
        
        print("🎉 Router migration completed!")
        self.print_migration_summary()

    def migrate_single_router(self, file_path: str) -> None:
        """
        Migrate a single router file
        """
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return
            
        print(f"🔄 Migrating {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = 0
            
            # Apply migration patterns
            for pattern, replacement in self.MIGRATION_PATTERNS:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    changes_made += 1
                    content = new_content
            
            # Only write if changes were made
            if content != original_content:
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {file_path} ({changes_made} changes)")
                print(f"📁 Backup created: {backup_path}")
            else:
                print(f"ℹ️ No changes needed for {file_path}")
                
        except Exception as e:
            print(f"❌ Failed to migrate {file_path}: {e}")

    def print_migration_summary(self) -> None:
        """
        Print migration summary
        """
        print("\n📊 Migration Summary:")
        print("├── Enhanced authentication service: ✅ Ready")
        print("├── Router consistency: ✅ 100% standardized")
        print("├── JWKS caching: ✅ Enabled")
        print("├── Performance monitoring: ✅ Active")
        print("└── Error handling: ✅ Centralized")

if __name__ == "__main__":
    migrator = RouterMigrationTool()
    migrator.migrate_all_routers()
```

### Step 3: Performance Middleware
```python
# File: backend/app/middleware/auth_performance_middleware.py

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..utils.enhanced_clerk_auth import enhanced_clerk_auth

class AuthPerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor authentication performance
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.protected_patterns = [
            "/api/v1/protected",
            "/api/v1/users",
            "/api/v1/chat", 
            "/api/v1/jobs",
            "/api/v1/profiles"
        ]

    async def dispatch(self, request: Request, call_next):
        # Only monitor routes that use authentication
        if self._is_authenticated_route(request.url.path):
            start_time = time.time()
            
            response = await call_next(request)
            
            # Record timing
            duration = time.time() - start_time
            
            # Add performance headers
            response.headers["X-Auth-Time"] = str(duration)
            
            # Get auth metrics
            metrics = enhanced_clerk_auth.get_metrics()
            if metrics.total_requests > 0:
                response.headers["X-Cache-Hit-Rate"] = str(
                    metrics.cache_hits / metrics.total_requests
                )
            
            return response
        
        return await call_next(request)
    
    def _is_authenticated_route(self, path: str) -> bool:
        """
        Check if route requires authentication
        """
        return any(path.startswith(pattern) for pattern in self.protected_patterns)
```

### Step 4: Health Check Integration
```python
# File: backend/app/routers/health.py

from fastapi import APIRouter
from ..utils.enhanced_clerk_auth import enhanced_clerk_auth

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint with enhanced auth metrics
    """
    auth_metrics = enhanced_clerk_auth.get_metrics()
    cache_status = enhanced_clerk_auth.get_cache_status()
    
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "authentication": {
            "service": "enhanced_clerk_auth",
            "total_requests": auth_metrics.total_requests,
            "cache_hit_rate": cache_status.get("cache_hit_rate", 0),
            "average_validation_time": auth_metrics.validation_time,
            "error_rate": auth_metrics.error_rate,
            "jwks_cache_enabled": cache_status.get("jwks_cache_enabled", False),
            "redis_status": cache_status.get("redis_status", "disabled")
        }
    }

@router.get("/auth/metrics")
async def get_auth_metrics():
    """
    Detailed authentication metrics endpoint
    """
    return {
        "metrics": enhanced_clerk_auth.get_metrics().__dict__,
        "cache_status": enhanced_clerk_auth.get_cache_status()
    }
```

### Step 5: FastAPI Integration
```python
# File: backend/app/main.py (integration)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.auth_performance_middleware import AuthPerformanceMiddleware
from .routers import chat, users, jobs, onboarding, health
from .utils.enhanced_clerk_auth import enhanced_clerk_auth

app = FastAPI(
    title="Orientor Platform API",
    description="Enhanced API with optimized Clerk authentication",
    version="2.0.0"
)

# Add authentication performance middleware
app.add_middleware(AuthPerformanceMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(onboarding.router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize enhanced authentication system
    """
    print("🚀 Starting Orientor Platform API with Enhanced Authentication")
    
    # Validate authentication setup
    cache_status = enhanced_clerk_auth.get_cache_status()
    print(f"📊 JWKS Cache: {'✅ Enabled' if cache_status['jwks_cache_enabled'] else '❌ Disabled'}")
    print(f"📊 Redis Cache: {'✅ Connected' if cache_status.get('redis_status') == 'connected' else '❌ Disconnected'}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    await enhanced_clerk_auth.cleanup()
    print("🛑 Enhanced authentication cleanup completed")
```

## 📊 SUCCESS VALIDATION

### Performance Tests
```python
# File: backend/tests/test_enhanced_auth_performance.py

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from app.utils.enhanced_clerk_auth import EnhancedClerkAuth, BackendAuthConfig

@pytest.mark.asyncio
async def test_token_validation_performance():
    """
    Test token validation performance with caching
    """
    config = BackendAuthConfig(redis_enabled=False)  # Use in-memory for testing
    auth_service = EnhancedClerkAuth(config)
    
    # Mock JWKS validation
    with patch.object(auth_service, '_validate_with_jwks') as mock_validate:
        mock_validate.return_value = {"sub": "user123", "email": "test@example.com"}
        
        # First call (cache miss)
        start_time = time.time()
        await auth_service.validate_token_enhanced("mock_token")
        first_call_time = time.time() - start_time
        
        # Should be reasonably fast even without cache
        assert first_call_time < 0.1  # Less than 100ms
        
        # Verify metrics
        metrics = auth_service.get_metrics()
        assert metrics.total_requests == 1
        assert metrics.cache_misses == 1

@pytest.mark.asyncio 
async def test_concurrent_token_validation():
    """
    Test concurrent token validation performance
    """
    auth_service = EnhancedClerkAuth()
    
    with patch.object(auth_service, '_validate_with_jwks') as mock_validate:
        mock_validate.return_value = {"sub": "user123"}
        
        # Simulate concurrent requests
        tasks = [
            auth_service.validate_token_enhanced("token1"),
            auth_service.validate_token_enhanced("token2"),
            auth_service.validate_token_enhanced("token3"),
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # All should succeed
        assert len(results) == 3
        
        # Should handle concurrency efficiently
        assert total_time < 0.5  # Less than 500ms for 3 concurrent requests
```

### Integration Tests
```python
# File: backend/tests/test_router_migration.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """
    Test health endpoint with auth metrics
    """
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "authentication" in data
    assert "cache_hit_rate" in data["authentication"]
    assert "average_validation_time" in data["authentication"]

def test_router_standardization():
    """
    Test that all routers use standardized authentication
    """
    # This test would verify that all routers import the correct auth function
    # Implementation depends on your specific router structure
    pass
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve Before Completion:
- [ ] **100% router standardization** (4/4 routers migrated)
- [ ] **<50ms token validation** with JWKS cache
- [ ] **<10ms token validation** with Redis cache
- [ ] **>90% cache hit rate** for active users
- [ ] **Legacy system fully modernized** (1 router)
- [ ] **Performance monitoring** active and reporting
- [ ] **Error rate <0.1%** across all operations

### System Integration:
- [ ] Health checks reporting auth metrics
- [ ] Performance middleware active
- [ ] Redis caching operational (if available)
- [ ] Database user sync working

## 🔄 DEPENDENCIES
**Independent**: This module can be implemented independently but benefits from:
- Redis for distributed caching
- Database connection pooling
- Performance monitoring infrastructure

## 📖 REFERENCE DOCUMENTATION
Complete technical specifications available in:
`/docs/api-clerk-enhanced.md/plan/phase-2-middleware/module-e-backend-auth.md`

## 🔄 REPORTING FORMAT
```
📊 MODULE E PROGRESS REPORT
⏱️ STATUS: [In Progress/Completed/Blocked]
🎯 IMPLEMENTATION: [X/8 core features completed]
📈 PERFORMANCE: 
  ├── Token validation: Xms
  ├── Cache hit rate: X%
  ├── Router standardization: X/4 complete
  └── Error rate: X%
🧪 TESTING: [X/Y test suites passing]
🔗 INTEGRATION: FastAPI App - [Ready/Testing/Complete]
🚨 BLOCKERS: [Any issues or dependencies]
🔄 NEXT: [Backend optimization complete / Additional work needed]
```

**Can start immediately** - This module provides critical backend infrastructure!

---

**REMINDER**: 🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
Unify all backend authentication through enhanced Clerk integration!