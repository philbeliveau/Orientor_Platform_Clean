"""
Cache Integration Module
========================

This module provides integration between the authentication caching system
and the rest of the application, including performance monitoring, 
FastAPI startup/shutdown events, and router compatibility.
"""

import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .auth_cache import (
    start_cache_maintenance,
    stop_cache_maintenance,
    CacheMetrics,
    cache_health_check,
    get_current_user_cached,
    get_request_cache,
    get_jwks_cache,
    RequestCache
)
from .database import get_db
from ..models.user import User

logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI LIFECYCLE INTEGRATION
# ============================================================================

@asynccontextmanager
async def cache_lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for cache system.
    Handles initialization and cleanup of cache components.
    """
    logger.info("🚀 Starting authentication cache system...")
    
    try:
        # Initialize JWKS cache with pre-fetch
        jwks_cache = get_jwks_cache()
        await jwks_cache.get_jwks()
        logger.info("✅ JWKS cache initialized and pre-populated")
        
        # Start background maintenance tasks
        await start_cache_maintenance()
        logger.info("✅ Cache maintenance tasks started")
        
        # Log initial cache statistics
        stats = CacheMetrics.get_all_stats()
        logger.info(f"📊 Initial cache statistics: {stats}")
        
        # Yield control to the application
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize cache system: {str(e)}")
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down authentication cache system...")
        
        try:
            await stop_cache_maintenance()
            logger.info("✅ Cache maintenance tasks stopped")
            
            # Log final statistics
            final_stats = CacheMetrics.get_all_stats()
            logger.info(f"📊 Final cache statistics: {final_stats}")
            
        except Exception as e:
            logger.error(f"⚠️ Error during cache system shutdown: {str(e)}")

# ============================================================================
# PERFORMANCE MONITORING INTEGRATION
# ============================================================================

class CachePerformanceMonitor:
    """
    Integration with the performance monitoring system.
    Provides cache metrics for the performance dashboard.
    """
    
    @staticmethod
    async def get_performance_metrics() -> Dict[str, Any]:
        """
        Get cache performance metrics in a format compatible 
        with the performance monitoring system.
        """
        try:
            # Get comprehensive cache statistics
            cache_stats = CacheMetrics.get_all_stats()
            
            # Get cache health status
            health_status = await cache_health_check()
            
            # Format for performance monitoring
            return {
                "cache_system": {
                    "status": health_status.get("status", "unknown"),
                    "components": {
                        "jwt_validation": {
                            "hit_rate": cache_stats.get("jwt_validation_cache", {}).get("hit_rate", 0),
                            "size": cache_stats.get("jwt_validation_cache", {}).get("size", 0),
                            "memory_usage_kb": cache_stats.get("jwt_validation_cache", {}).get("memory_usage_kb", 0)
                        },
                        "jwks": {
                            "cache_valid": cache_stats.get("jwks_cache", {}).get("cache_valid", False),
                            "refresh_in_progress": cache_stats.get("jwks_cache", {}).get("refresh_in_progress", False),
                            "background_refreshes": cache_stats.get("jwks_cache", {}).get("background_refreshes", 0),
                            "fallback_uses": cache_stats.get("jwks_cache", {}).get("fallback_uses", 0)
                        }
                    },
                    "overall_health": health_status.get("status") == "healthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache performance metrics: {str(e)}")
            return {
                "cache_system": {
                    "status": "error",
                    "error": str(e)
                }
            }
    
    @staticmethod
    async def cleanup_and_optimize() -> Dict[str, Any]:
        """
        Perform cache cleanup and optimization operations.
        Returns statistics about the operations performed.
        """
        try:
            # Cleanup expired entries
            cleanup_results = CacheMetrics.cleanup_expired_entries()
            
            # Get updated statistics
            stats_after = CacheMetrics.get_all_stats()
            
            return {
                "cleanup_performed": True,
                "entries_cleaned": cleanup_results,
                "current_stats": stats_after
            }
            
        except Exception as e:
            logger.error(f"Error during cache cleanup and optimization: {str(e)}")
            return {
                "cleanup_performed": False,
                "error": str(e)
            }

# ============================================================================
# ROUTER COMPATIBILITY LAYER
# ============================================================================

class CachedAuthDependencies:
    """
    Provides cached authentication dependencies that are compatible
    with existing router patterns while offering improved performance.
    """
    
    @staticmethod
    async def get_current_user_optimized(
        credentials: HTTPAuthorizationCredentials,
        db: Session,
        request_cache: Optional[RequestCache] = None
    ) -> Dict[str, Any]:
        """
        Optimized user authentication with full caching integration.
        Can be used as a drop-in replacement for get_current_user.
        """
        if request_cache is None:
            request_cache = get_request_cache()
        
        return await get_current_user_cached(credentials, db, request_cache)
    
    @staticmethod
    async def get_current_user_with_db_sync_optimized(
        credentials: HTTPAuthorizationCredentials,
        db: Session,
        request_cache: Optional[RequestCache] = None
    ) -> User:
        """
        Optimized database user sync with full caching integration.
        Can be used as a drop-in replacement for get_current_user_with_db_sync.
        """
        # Import here to avoid circular dependencies
        from .clerk_auth import create_clerk_user_in_db
        
        if request_cache is None:
            request_cache = get_request_cache()
        
        try:
            # Get Clerk user data using cached authentication
            clerk_user_data = await get_current_user_cached(credentials, db, request_cache)
            
            # Check if we have the database user ID cached
            db_user_cache_key = f"db_user:{clerk_user_data['id']}"
            cached_user = request_cache.get(db_user_cache_key)
            
            if cached_user is not None:
                logger.debug("🎯 Database user cache hit in optimized function")
                return cached_user
            
            # Sync/create user in local database
            user_data = create_clerk_user_in_db(clerk_user_data["clerk_data"], db)
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to sync user with database"
                )
            
            # Return SQLAlchemy User object
            user = db.query(User).filter(User.id == user_data["id"]).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database after sync"
                )
            
            # Cache the database user for this request
            request_cache.set(db_user_cache_key, user)
            logger.debug("💾 Database user cached in optimized function")
                
            return user
            
        except Exception as e:
            logger.error(f"Optimized user authentication with DB sync error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

# ============================================================================
# MIGRATION UTILITIES
# ============================================================================

class CacheMigrationHelper:
    """
    Helper utilities for migrating existing routers to use the new caching system.
    """
    
    @staticmethod
    def create_cached_dependency(original_dependency):
        """
        Create a cached version of an existing authentication dependency.
        
        Args:
            original_dependency: The original FastAPI dependency function
            
        Returns:
            A new dependency function that includes caching
        """
        async def cached_wrapper(
            credentials: HTTPAuthorizationCredentials = Depends(original_dependency.__wrapped__ if hasattr(original_dependency, '__wrapped__') else original_dependency),
            db: Session = Depends(get_db),
            request_cache: RequestCache = Depends(get_request_cache)
        ):
            # If the original dependency is get_current_user_with_db_sync, use our optimized version
            if hasattr(original_dependency, '__name__') and 'db_sync' in original_dependency.__name__:
                return await CachedAuthDependencies.get_current_user_with_db_sync_optimized(
                    credentials, db, request_cache
                )
            else:
                return await CachedAuthDependencies.get_current_user_optimized(
                    credentials, db, request_cache
                )
        
        return cached_wrapper
    
    @staticmethod
    def get_migration_stats() -> Dict[str, Any]:
        """
        Get statistics about cache usage to help evaluate migration effectiveness.
        """
        return {
            "cache_stats": CacheMetrics.get_all_stats(),
            "recommendations": {
                "migrate_heavy_routes": "Routes with high authentication frequency should be migrated first",
                "monitor_memory": "Monitor memory usage after migration to ensure optimal cache sizes",
                "background_refresh": "JWKS background refresh reduces authentication latency"
            }
        }

# ============================================================================
# HEALTH CHECK INTEGRATION
# ============================================================================

async def comprehensive_auth_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check that includes both legacy and cached authentication systems.
    Suitable for use in application health endpoints.
    """
    try:
        # Get cache system health
        cache_health = await cache_health_check()
        
        # Get performance metrics
        perf_metrics = await CachePerformanceMonitor.get_performance_metrics()
        
        # Get legacy Clerk health (for compatibility)
        from .clerk_auth import clerk_health_check
        clerk_health = await clerk_health_check()
        
        # Combine all health information
        overall_status = "healthy"
        if cache_health.get("status") != "healthy" or clerk_health.get("status") != "healthy":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": cache_health.get("timestamp"),
            "authentication_system": {
                "cache_system": cache_health,
                "performance_metrics": perf_metrics,
                "clerk_integration": clerk_health
            },
            "recommendations": _get_health_recommendations(cache_health, perf_metrics)
        }
        
    except Exception as e:
        logger.error(f"Comprehensive auth health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def _get_health_recommendations(cache_health: Dict[str, Any], perf_metrics: Dict[str, Any]) -> list:
    """Generate health recommendations based on current system status"""
    recommendations = []
    
    # Check cache hit rates
    jwt_cache = perf_metrics.get("cache_system", {}).get("components", {}).get("jwt_validation", {})
    hit_rate = jwt_cache.get("hit_rate", 0)
    
    if hit_rate < 0.7:
        recommendations.append("JWT validation hit rate is below 70% - consider increasing cache TTL")
    
    # Check JWKS fallback usage
    jwks_cache = perf_metrics.get("cache_system", {}).get("components", {}).get("jwks", {})
    fallback_uses = jwks_cache.get("fallback_uses", 0)
    
    if fallback_uses > 0:
        recommendations.append("JWKS fallback cache has been used - check network connectivity")
    
    # Check overall health
    if cache_health.get("status") == "degraded":
        recommendations.append("Cache system is in degraded state - review component health")
    
    if not recommendations:
        recommendations.append("Authentication cache system is operating optimally")
    
    return recommendations

# ============================================================================
# EXPORT INTERFACES
# ============================================================================

# Main exports for application integration
__all__ = [
    # Lifecycle management
    "cache_lifespan",
    
    # Performance monitoring
    "CachePerformanceMonitor",
    
    # Router compatibility
    "CachedAuthDependencies",
    
    # Migration utilities
    "CacheMigrationHelper",
    
    # Health checks
    "comprehensive_auth_health_check",
]