"""
JWKS Cache Monitoring Router
===========================

Provides comprehensive monitoring endpoints for the enhanced Clerk JWKS caching system.
These endpoints help track performance improvements, cache efficiency, and API call reduction.

Endpoints:
- GET /jwks/stats - Cache performance statistics
- GET /jwks/health - Cache health check
- POST /jwks/invalidate - Manual cache invalidation
- GET /jwks/performance - Performance metrics dashboard
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.database import get_db
from ..utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from ..utils.clerk_jwks_cache import (
    get_jwks_cache_stats,
    jwks_cache_health_check,
    get_clerk_jwks_cache
)

router = APIRouter(
    prefix="/api/jwks",
    tags=["JWKS Cache Monitoring"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/stats")
async def get_jwks_cache_statistics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive JWKS cache performance statistics.
    
    Returns detailed metrics including:
    - Cache hit rate and performance
    - API call reduction percentage
    - Background refresh statistics
    - Fetch timing metrics
    """
    try:
        stats = await get_jwks_cache_stats()
        
        # Calculate API call reduction
        hit_rate = stats["performance"]["hit_rate"]
        api_reduction = hit_rate * 100
        
        # Enhanced response with business metrics
        return {
            "cache_performance": {
                "hit_rate_percentage": f"{hit_rate * 100:.1f}%",
                "api_call_reduction": f"{api_reduction:.1f}%",
                "hits": stats["performance"]["hits"],
                "misses": stats["performance"]["misses"],
                "avg_fetch_time_ms": round(stats["performance"]["avg_fetch_time_ms"], 2)
            },
            "cost_savings": {
                "estimated_api_calls_saved": stats["performance"]["hits"],
                "total_clerk_api_calls": stats["performance"]["hits"] + stats["performance"]["misses"],
                "efficiency_rating": "Excellent" if hit_rate > 0.8 else "Good" if hit_rate > 0.6 else "Needs Optimization"
            },
            "cache_status": stats["cache_status"],
            "operations": stats["operations"],
            "configuration": stats["configuration"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve JWKS cache statistics: {str(e)}"
        )

@router.get("/health")
async def jwks_cache_health(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Comprehensive health check for JWKS cache system.
    
    Validates:
    - Cache connectivity and validity
    - JWKS endpoint accessibility
    - Background refresh operations
    - Performance benchmarks
    """
    try:
        health_data = await jwks_cache_health_check()
        
        # Add system-level health indicators
        health_data["system_health"] = {
            "overall_status": health_data["status"],
            "critical_checks_passed": all(
                check.get("status") == "pass" 
                for check in health_data["checks"].values()
            ),
            "performance_acceptable": (
                health_data["stats"]["performance"]["avg_fetch_time_ms"] < 500
            ),
            "cache_efficiency": health_data["stats"]["performance"]["hit_rate"] > 0.5
        }
        
        return health_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JWKS cache health check failed: {str(e)}"
        )

@router.post("/invalidate")
async def invalidate_jwks_cache(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manually invalidate JWKS cache.
    
    Use cases:
    - Force refresh after Clerk key rotation
    - Clear cache during debugging
    - Reset metrics for testing
    
    Note: Cache will be automatically refreshed on next authentication request.
    """
    try:
        cache = get_clerk_jwks_cache()
        await cache.invalidate_cache()
        
        return {
            "status": "success",
            "message": "JWKS cache invalidated successfully",
            "action_taken": "Cache cleared - will refresh on next authentication",
            "invalidated_by": f"User {current_user.id}",
            "next_steps": "Cache will automatically refresh on next JWT validation"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate JWKS cache: {str(e)}"
        )

@router.get("/performance")
async def jwks_performance_dashboard(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Performance dashboard data for JWKS cache monitoring.
    
    Provides metrics suitable for:
    - Operations dashboards
    - Performance monitoring
    - Cost optimization tracking
    - SLA compliance monitoring
    """
    try:
        stats = await get_jwks_cache_stats()
        health = await jwks_cache_health_check()
        
        # Calculate key performance indicators
        hit_rate = stats["performance"]["hit_rate"]
        avg_fetch_ms = stats["performance"]["avg_fetch_time_ms"]
        total_operations = stats["performance"]["hits"] + stats["performance"]["misses"]
        
        return {
            "kpi_summary": {
                "cache_hit_rate": f"{hit_rate * 100:.1f}%",
                "api_call_reduction": f"{hit_rate * 100:.1f}%",
                "average_response_time": f"{avg_fetch_ms:.1f}ms",
                "total_operations": total_operations,
                "uptime_status": health["status"]
            },
            "performance_trends": {
                "efficiency_rating": (
                    "Excellent" if hit_rate > 0.8 else
                    "Good" if hit_rate > 0.6 else
                    "Needs Optimization"
                ),
                "response_time_rating": (
                    "Fast" if avg_fetch_ms < 100 else
                    "Acceptable" if avg_fetch_ms < 300 else
                    "Slow"
                ),
                "reliability_rating": (
                    "Reliable" if health["status"] == "healthy" else
                    "Needs Attention"
                )
            },
            "cost_analysis": {
                "estimated_clerk_api_calls_saved": stats["performance"]["hits"],
                "total_authentication_requests": total_operations,
                "savings_percentage": f"{hit_rate * 100:.1f}%",
                "background_operations": stats["operations"]["background_refreshes"]
            },
            "operational_metrics": {
                "cache_age_seconds": stats["cache_status"]["age_seconds"],
                "fallback_uses": stats["operations"]["fallback_uses"],
                "failed_refreshes": stats["operations"]["failed_refreshes"],
                "active_background_tasks": stats["operations"]["active_bg_tasks"]
            },
            "recommendations": _generate_performance_recommendations(stats, health)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate performance dashboard: {str(e)}"
        )

def _generate_performance_recommendations(
    stats: Dict[str, Any], 
    health: Dict[str, Any]
) -> list[str]:
    """Generate actionable recommendations based on cache performance"""
    recommendations = []
    
    hit_rate = stats["performance"]["hit_rate"]
    avg_fetch_ms = stats["performance"]["avg_fetch_time_ms"]
    failed_refreshes = stats["operations"]["failed_refreshes"]
    
    # Hit rate recommendations
    if hit_rate < 0.5:
        recommendations.append(
            "🔴 Low cache hit rate detected. Consider reducing TTL or investigating high cache miss patterns."
        )
    elif hit_rate < 0.8:
        recommendations.append(
            "🟡 Cache hit rate could be improved. Monitor authentication patterns for optimization opportunities."
        )
    else:
        recommendations.append(
            "✅ Excellent cache hit rate. Current configuration is performing well."
        )
    
    # Response time recommendations
    if avg_fetch_ms > 300:
        recommendations.append(
            "🔴 Slow JWKS fetch times detected. Check network connectivity to Clerk services."
        )
    elif avg_fetch_ms > 100:
        recommendations.append(
            "🟡 JWKS fetch times are acceptable but could be optimized."
        )
    
    # Reliability recommendations
    if failed_refreshes > 0:
        recommendations.append(
            f"⚠️ {failed_refreshes} failed background refreshes detected. Monitor Clerk service connectivity."
        )
    
    # Health status recommendations
    if health["status"] != "healthy":
        recommendations.append(
            "🚨 Cache health issues detected. Review logs and consider manual cache invalidation."
        )
    
    # General optimization
    if not recommendations:
        recommendations.append(
            "🎉 JWKS cache is performing optimally. All metrics are within acceptable ranges."
        )
    
    return recommendations

@router.get("/metrics/export")
async def export_jwks_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export JWKS cache metrics in a standardized format for external monitoring systems.
    
    Compatible with:
    - Prometheus/Grafana
    - DataDog
    - Custom monitoring solutions
    """
    try:
        stats = await get_jwks_cache_stats()
        
        # Standardized metrics format
        metrics = {
            "timestamp": stats["cache_status"]["last_updated"],
            "gauges": {
                "jwks_cache_hit_rate": stats["performance"]["hit_rate"],
                "jwks_cache_avg_fetch_time_ms": stats["performance"]["avg_fetch_time_ms"],
                "jwks_cache_age_seconds": stats["cache_status"]["age_seconds"] or 0,
                "jwks_cache_active_bg_tasks": stats["operations"]["active_bg_tasks"]
            },
            "counters": {
                "jwks_cache_hits_total": stats["performance"]["hits"],
                "jwks_cache_misses_total": stats["performance"]["misses"],
                "jwks_cache_background_refreshes_total": stats["operations"]["background_refreshes"],
                "jwks_cache_failed_refreshes_total": stats["operations"]["failed_refreshes"],
                "jwks_cache_fallback_uses_total": stats["operations"]["fallback_uses"]
            },
            "info": {
                "jwks_cache_is_valid": stats["cache_status"]["is_valid"],
                "jwks_cache_has_fallback": stats["cache_status"]["has_fallback"],
                "jwks_url": stats["configuration"]["jwks_url"],
                "refresh_interval": stats["configuration"]["refresh_interval"]
            }
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export JWKS metrics: {str(e)}"
        )