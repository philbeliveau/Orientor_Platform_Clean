"""
Optimized Clerk Authentication with Database Session Caching (Phase 4-5)
=========================================================================

This module provides high-performance Clerk authentication that integrates
with the database session caching system to achieve 80-90% database load reduction
while maintaining data consistency and proper user session management.

Key Features:
1. Integration with database session caching (15-minute TTL)
2. Smart database sync with change detection
3. Optimized database connection pooling
4. Comprehensive cache invalidation strategies
5. Performance monitoring and metrics
6. Fallback mechanisms for cache failures

Performance Targets:
- 80-90% reduction in database queries for user authentication
- Sub-100ms authentication response times (cache hits)
- Intelligent sync detection to minimize database writes
- Automatic cache invalidation on user data changes
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.database import get_db
from .database_session_cache import (
    database_session_manager,
    get_user_session_cached,
    UserSessionData
)
from .auth_cache import (
    get_current_user_cached,
    get_request_cache,
    RequestCache
)
from ..performance.auth_metrics import performance_monitor, measure_performance

logger = logging.getLogger(__name__)
security = HTTPBearer()

# ============================================================================
# HIGH-PERFORMANCE AUTHENTICATED USER RETRIEVAL
# ============================================================================

async def get_current_user_optimized(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    request_cache: RequestCache = Depends(get_request_cache)
) -> Dict[str, Any]:
    """
    Get current authenticated user with maximum performance optimization.
    
    This function combines:
    1. Request-level caching (Phase 1)
    2. JWT validation caching (Phase 2) 
    3. JWKS caching (Phase 3)
    4. Database session caching (Phase 4)
    5. Smart database sync (Phase 5)
    
    Performance: <50ms for cache hits, <200ms for cache misses
    Database Load Reduction: 80-90%
    """
    async with measure_performance("optimized_user_auth", {"phase": "4-5"}):
        # Phase 1-3: Use existing cached authentication
        clerk_user_data = await get_current_user_cached(credentials, db, request_cache)
        
        # Phase 4-5: Database session caching with smart sync
        session_data = await get_user_session_cached(clerk_user_data["clerk_data"], db)
        
        # Enhance response with session data
        optimized_response = {
            **clerk_user_data,
            "database_user_id": session_data.user_id,
            "session_data": session_data.to_dict(),
            "cache_performance": {
                "session_cached": True,
                "db_sync_skipped": session_data.db_synced,
                "last_sync": session_data.last_clerk_sync.isoformat() if session_data.last_clerk_sync else None
            }
        }
        
        return optimized_response

async def get_current_user_sqlalchemy_optimized(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user as SQLAlchemy User object with database optimization.
    
    This function is optimized for legacy routers that expect a User object,
    but uses the new caching system for maximum performance.
    
    Returns:
        User: SQLAlchemy User object with optimized retrieval
    """
    async with measure_performance("optimized_user_sqlalchemy", {"phase": "4-5"}):
        # Get optimized user data
        request_cache = get_request_cache()
        clerk_user_data = await get_current_user_cached(credentials, db, request_cache)
        
        # Use database session cache
        session_data = await get_user_session_cached(clerk_user_data["clerk_data"], db)
        
        # Check if we have the SQLAlchemy user cached in request cache
        user_cache_key = f"sqlalchemy_user:{session_data.user_id}"
        cached_user = request_cache.get(user_cache_key)
        
        if cached_user is not None:
            logger.debug("🎯 SQLAlchemy user cache hit")
            return cached_user
        
        # Fetch SQLAlchemy User object
        user = db.query(User).filter(User.id == session_data.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        
        # Cache the SQLAlchemy user for this request
        request_cache.set(user_cache_key, user)
        logger.debug("💾 SQLAlchemy user cached")
        
        return user

async def get_user_id_optimized(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    """
    Get just the user ID with maximum performance optimization.
    Useful for operations that only need the user ID.
    
    Returns:
        int: Database user ID
    """
    async with measure_performance("optimized_user_id", {"phase": "4-5"}):
        request_cache = get_request_cache()
        clerk_user_data = await get_current_user_cached(credentials, db, request_cache)
        
        # Use database session cache to get user ID
        session_data = await get_user_session_cached(clerk_user_data["clerk_data"], db)
        
        return session_data.user_id

# ============================================================================
# CACHE MANAGEMENT AND INVALIDATION
# ============================================================================

async def invalidate_user_session_cache(clerk_user_id: str) -> bool:
    """
    Invalidate cached user session data.
    Should be called when user data is updated externally.
    
    Args:
        clerk_user_id: Clerk user ID to invalidate
        
    Returns:
        bool: True if cache was invalidated, False if not found
    """
    try:
        result = database_session_manager.invalidate_user_session(clerk_user_id)
        if result:
            logger.info(f"🗑️ User session cache invalidated: {clerk_user_id}")
        else:
            logger.debug(f"⚠️ User session not found in cache: {clerk_user_id}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to invalidate user session cache: {e}")
        return False

async def refresh_user_session_cache(
    clerk_user_id: str,
    db: Session,
    force_database_sync: bool = True
) -> Optional[UserSessionData]:
    """
    Force refresh of user session cache by fetching latest data from Clerk and database.
    
    Args:
        clerk_user_id: Clerk user ID to refresh
        db: Database session
        force_database_sync: Force database synchronization
        
    Returns:
        UserSessionData: Refreshed session data or None if failed
    """
    try:
        # First invalidate existing cache
        database_session_manager.invalidate_user_session(clerk_user_id)
        
        # Fetch fresh data from Clerk API
        import os
        import httpx
        
        clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        if not clerk_secret_key:
            raise ValueError("CLERK_SECRET_KEY not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.clerk.com/v1/users/{clerk_user_id}",
                headers={
                    "Authorization": f"Bearer {clerk_secret_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            clerk_user_data = response.json()
        
        # Force sync with database
        session_data = await database_session_manager.get_or_create_user_session(
            clerk_user_data, db, force_refresh=force_database_sync
        )
        
        logger.info(f"🔄 User session cache refreshed: {clerk_user_id}")
        return session_data
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh user session cache: {e}")
        return None

# ============================================================================
# BULK OPERATIONS FOR PERFORMANCE
# ============================================================================

async def preload_user_sessions(
    clerk_user_ids: list[str],
    db: Session,
    max_concurrent: int = 5
) -> Dict[str, Optional[UserSessionData]]:
    """
    Preload multiple user sessions for bulk operations.
    Useful for endpoints that need to process multiple users.
    
    Args:
        clerk_user_ids: List of Clerk user IDs to preload
        db: Database session
        max_concurrent: Maximum concurrent preload operations
        
    Returns:
        Dict mapping clerk_user_id to UserSessionData (or None if failed)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results = {}
    
    async def preload_single_user(clerk_user_id: str):
        async with semaphore:
            try:
                # Check if already cached
                cached_session = database_session_manager.session_cache.get_user_session(clerk_user_id)
                if cached_session:
                    return clerk_user_id, cached_session
                
                # Fetch from Clerk API
                import os
                import httpx
                
                clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://api.clerk.com/v1/users/{clerk_user_id}",
                        headers={
                            "Authorization": f"Bearer {clerk_secret_key}",
                            "Content-Type": "application/json"
                        }
                    )
                    response.raise_for_status()
                    clerk_user_data = response.json()
                
                # Cache the session
                session_data = await get_user_session_cached(clerk_user_data, db)
                return clerk_user_id, session_data
                
            except Exception as e:
                logger.error(f"Failed to preload user session {clerk_user_id}: {e}")
                return clerk_user_id, None
    
    # Execute preload operations concurrently
    tasks = [preload_single_user(user_id) for user_id in clerk_user_ids]
    completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect results
    for result in completed_tasks:
        if isinstance(result, Exception):
            logger.error(f"Preload task failed: {result}")
            continue
        
        if isinstance(result, tuple) and len(result) == 2:
            clerk_user_id, session_data = result
            results[clerk_user_id] = session_data
    
    logger.info(f"🔄 Preloaded {len(results)} user sessions")
    return results

# ============================================================================
# PERFORMANCE MONITORING AND HEALTH CHECKS
# ============================================================================

async def get_authentication_performance_stats() -> Dict[str, Any]:
    """
    Get comprehensive authentication performance statistics.
    
    Returns:
        Dict containing performance metrics across all caching layers
    """
    try:
        # Get database session manager stats
        db_stats = database_session_manager.get_comprehensive_stats()
        
        # Get auth cache performance summary
        from ..utils.auth_cache import CacheMetrics
        cache_stats = CacheMetrics.get_all_stats()
        
        # Get performance monitor summary
        perf_summary = performance_monitor.analyze_bottlenecks()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'database_optimization': db_stats,
            'authentication_caches': cache_stats,
            'performance_analysis': perf_summary,
            'overall_status': 'optimal' if db_stats['cache_statistics']['hit_rate'] > 0.8 else 'degraded'
        }
    except Exception as e:
        logger.error(f"Failed to get authentication performance stats: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'overall_status': 'error'
        }

async def authentication_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for the optimized authentication system.
    
    Returns:
        Dict containing health status of all components
    """
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {},
        'performance_summary': {}
    }
    
    try:
        # Check database session manager health
        db_health = await database_session_manager.health_check()
        health['components']['database_session_manager'] = db_health
        
        if db_health['status'] != 'healthy':
            health['status'] = 'degraded'
        
        # Check auth cache health
        from ..utils.auth_cache import cache_health_check
        cache_health = await cache_health_check()
        health['components']['auth_cache'] = cache_health
        
        if cache_health['status'] != 'healthy':
            health['status'] = 'degraded'
        
        # Performance summary
        stats = await get_authentication_performance_stats()
        health['performance_summary'] = {
            'database_hit_rate': stats.get('database_optimization', {}).get('cache_statistics', {}).get('hit_rate', 0),
            'database_load_reduction': stats.get('database_optimization', {}).get('cache_efficiency', {}).get('database_load_reduction', 0),
            'total_operations': stats.get('database_optimization', {}).get('total_operations', 0)
        }
        
    except Exception as e:
        logger.error(f"Authentication health check failed: {e}")
        health['status'] = 'unhealthy'
        health['error'] = str(e)
    
    return health

# ============================================================================
# STARTUP AND SHUTDOWN HOOKS
# ============================================================================

async def startup_optimized_authentication():
    """Initialize optimized authentication system"""
    from .database_session_cache import startup_database_optimization
    
    try:
        # Start database optimization services
        await startup_database_optimization()
        
        # Set performance monitoring phase
        performance_monitor.set_phase("phase_4_5_database_optimization")
        
        logger.info("🚀 Optimized authentication system startup complete")
        
        # Log initial performance status
        stats = await get_authentication_performance_stats()
        logger.info(f"📊 Initial performance status: {stats.get('overall_status', 'unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start optimized authentication system: {e}")
        raise

async def shutdown_optimized_authentication():
    """Cleanup optimized authentication system"""
    from .database_session_cache import shutdown_database_optimization
    
    try:
        # Stop database optimization services
        await shutdown_database_optimization()
        
        # Generate final performance report
        final_stats = await get_authentication_performance_stats()
        logger.info(f"📈 Final performance statistics: {final_stats}")
        
        logger.info("⏹️ Optimized authentication system shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during optimized authentication shutdown: {e}")

# ============================================================================
# UTILITY FUNCTIONS FOR EASY INTEGRATION
# ============================================================================

def get_database_user_id_from_session(session_data: UserSessionData) -> int:
    """Extract database user ID from session data"""
    return session_data.user_id

def is_session_data_fresh(session_data: UserSessionData, max_age_minutes: int = 15) -> bool:
    """Check if session data is fresh enough"""
    if not session_data.cached_at:
        return False
    
    age = datetime.now() - session_data.cached_at
    return age.total_seconds() < (max_age_minutes * 60)

# ============================================================================
# EXPORT INTERFACES
# ============================================================================

# Main exports for use by routers and services
__all__ = [
    # High-performance authentication functions
    'get_current_user_optimized',
    'get_current_user_sqlalchemy_optimized',
    'get_user_id_optimized',
    
    # Cache management
    'invalidate_user_session_cache',
    'refresh_user_session_cache',
    'preload_user_sessions',
    
    # Performance monitoring
    'get_authentication_performance_stats',
    'authentication_health_check',
    
    # Startup/shutdown hooks
    'startup_optimized_authentication',
    'shutdown_optimized_authentication',
    
    # Utility functions
    'get_database_user_id_from_session',
    'is_session_data_fresh'
]