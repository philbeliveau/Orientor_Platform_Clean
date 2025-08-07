"""
Performance Monitoring Integration Utilities
==========================================

Integration utilities for embedding performance monitoring into the existing
authentication system without disrupting current functionality.

This module provides:
1. Decorators for instrumenting existing auth functions
2. Middleware integration for automatic monitoring
3. Performance-aware versions of key authentication utilities
4. Gradual migration helpers for existing code
"""

import asyncio
import functools
from typing import Callable, Any, Dict, Optional
from datetime import datetime
import logging
import inspect

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .auth_metrics import performance_monitor, measure_performance
from ..utils.clerk_auth import (
    verify_clerk_token,
    fetch_clerk_jwks,
    get_current_user,
    get_current_user_with_db_sync
)

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically monitor authentication performance"""
    
    def __init__(self, app: ASGIApp, enable_monitoring: bool = True):
        """
        Initialize performance monitoring middleware
        
        Args:
            app: ASGI application
            enable_monitoring: Whether to enable performance monitoring
        """
        super().__init__(app)
        self.enable_monitoring = enable_monitoring
        self.auth_routes = set()  # Track which routes use authentication
        
    async def dispatch(self, request: Request, call_next):
        """Process request and monitor authentication performance"""
        
        if not self.enable_monitoring:
            return await call_next(request)
        
        # Check if this request likely involves authentication
        is_auth_request = self._is_auth_request(request)
        
        if not is_auth_request:
            return await call_next(request)
        
        # Monitor the request with authentication context
        async with measure_performance(
            operation_name=f"auth_request_{request.method}_{request.url.path}",
            metadata={
                'method': request.method,
                'path': request.url.path,
                'user_agent': request.headers.get('user-agent', 'unknown'),
                'content_type': request.headers.get('content-type', 'unknown')
            }
        ):
            response = await call_next(request)
            
            # Add performance headers if successful
            if response.status_code < 400:
                response.headers["X-Auth-Performance-Monitored"] = "true"
                response.headers["X-Auth-Phase"] = performance_monitor.current_phase
            
            return response

    def _is_auth_request(self, request: Request) -> bool:
        """Determine if a request likely involves authentication"""
        
        # Check for Authorization header
        if 'authorization' in request.headers:
            return True
        
        # Check for known auth routes
        path = request.url.path
        auth_paths = [
            '/api/auth/',
            '/api/users/',
            '/api/profile',
            '/api/career',
            '/api/chat',
            '/api/recommendations'
        ]
        
        return any(path.startswith(auth_path) for auth_path in auth_paths)

def monitor_auth_operation(operation_name: str, 
                         cache_check_func: Optional[Callable] = None,
                         metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator to monitor authentication operations
    
    Args:
        operation_name: Name of the operation being monitored
        cache_check_func: Optional function to check if cache was hit
        metadata: Additional metadata to include
        
    Usage:
        @monitor_auth_operation('jwt_validation')
        async def my_jwt_function(token):
            return validate_jwt(token)
    """
    
    def decorator(func: Callable) -> Callable:
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract additional metadata from function context
            call_metadata = metadata.copy() if metadata else {}
            call_metadata.update({
                'function_name': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            
            result, metric = await performance_monitor.measure_operation(
                operation=operation_name,
                operation_func=func,
                *args,
                cache_check_func=cache_check_func,
                metadata=call_metadata,
                **kwargs
            )
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, we need to handle differently
            call_metadata = metadata.copy() if metadata else {}
            call_metadata.update({
                'function_name': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()),
                'sync_function': True
            })
            
            # Create a simple sync measurement
            import time
            start_time = time.perf_counter()
            success = False
            result = None
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = e
                success = False
                raise
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                from .auth_metrics import PerformanceMetric
                metric = PerformanceMetric(
                    timestamp=datetime.now(),
                    operation=operation_name,
                    duration_ms=duration_ms,
                    success=success,
                    phase=performance_monitor.current_phase,
                    cache_hit=False,  # Can't check cache easily in sync context
                    metadata=call_metadata
                )
                
                performance_monitor.metrics.append(metric)
                
                # Log performance
                status = "✅" if success else "❌"
                logger.info(f"{status} {operation_name}: {duration_ms:.2f}ms")
            
            return result
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Performance-monitored versions of key authentication functions
@monitor_auth_operation(
    'jwks_fetch',
    cache_check_func=lambda: performance_monitor.current_phase != 'baseline',
    metadata={'component': 'jwks_endpoint'}
)
async def monitored_fetch_clerk_jwks():
    """Performance-monitored version of JWKS fetching"""
    return await fetch_clerk_jwks()

@monitor_auth_operation(
    'jwt_validation', 
    metadata={'component': 'clerk_auth_utils'}
)
async def monitored_verify_clerk_token(token: str):
    """Performance-monitored version of JWT token verification"""
    return await verify_clerk_token(token)

@monitor_auth_operation(
    'user_auth_full',
    metadata={'component': 'auth_middleware', 'flow': 'complete'}
)
async def monitored_get_current_user(credentials, db):
    """Performance-monitored version of complete user authentication"""
    return await get_current_user(credentials, db)

@monitor_auth_operation(
    'user_auth_with_db_sync',
    metadata={'component': 'auth_middleware', 'includes_db': True}
)  
async def monitored_get_current_user_with_db_sync(credentials, db):
    """Performance-monitored version of user auth with database sync"""
    return await get_current_user_with_db_sync(credentials, db)

class PerformanceAwareAuthUtils:
    """
    Performance-aware wrapper for authentication utilities that can be gradually
    integrated into existing code without breaking changes
    """
    
    def __init__(self, enable_monitoring: bool = True, fallback_to_original: bool = True):
        """
        Initialize performance-aware auth utils
        
        Args:
            enable_monitoring: Whether to enable performance monitoring
            fallback_to_original: Whether to fallback to original functions on errors
        """
        self.enable_monitoring = enable_monitoring
        self.fallback_to_original = fallback_to_original
        
    async def fetch_clerk_jwks(self):
        """Fetch JWKS with optional performance monitoring"""
        if self.enable_monitoring:
            try:
                return await monitored_fetch_clerk_jwks()
            except Exception as e:
                if self.fallback_to_original:
                    logger.warning(f"Monitored JWKS fetch failed, falling back: {e}")
                    return await fetch_clerk_jwks()
                raise
        else:
            return await fetch_clerk_jwks()
    
    async def verify_clerk_token(self, token: str):
        """Verify JWT token with optional performance monitoring"""
        if self.enable_monitoring:
            try:
                return await monitored_verify_clerk_token(token)
            except Exception as e:
                if self.fallback_to_original:
                    logger.warning(f"Monitored JWT verification failed, falling back: {e}")
                    return await verify_clerk_token(token)
                raise
        else:
            return await verify_clerk_token(token)
    
    async def get_current_user(self, credentials, db):
        """Get current user with optional performance monitoring"""
        if self.enable_monitoring:
            try:
                return await monitored_get_current_user(credentials, db)
            except Exception as e:
                if self.fallback_to_original:
                    logger.warning(f"Monitored user auth failed, falling back: {e}")
                    return await get_current_user(credentials, db)
                raise
        else:
            return await get_current_user(credentials, db)

# Global performance-aware auth utils instance
perf_auth_utils = PerformanceAwareAuthUtils()

class AuthPerformanceProfiler:
    """
    Advanced profiler for detailed authentication performance analysis
    """
    
    def __init__(self):
        self.profiles = []
        self.active_profiles = {}
        
    async def start_profile(self, profile_name: str, context: Dict[str, Any] = None):
        """Start a new performance profile"""
        profile_id = f"{profile_name}_{datetime.now().timestamp()}"
        
        profile = {
            'id': profile_id,
            'name': profile_name,
            'start_time': datetime.now(),
            'context': context or {},
            'operations': [],
            'system_snapshot': await self._get_system_snapshot()
        }
        
        self.active_profiles[profile_id] = profile
        logger.info(f"🎯 Started performance profile: {profile_name}")
        
        return profile_id
    
    async def record_operation(self, profile_id: str, operation: str, duration_ms: float, 
                             success: bool, metadata: Dict[str, Any] = None):
        """Record an operation in an active profile"""
        if profile_id not in self.active_profiles:
            logger.warning(f"Profile {profile_id} not found")
            return
        
        profile = self.active_profiles[profile_id]
        profile['operations'].append({
            'operation': operation,
            'timestamp': datetime.now(),
            'duration_ms': duration_ms,
            'success': success,
            'metadata': metadata or {}
        })
    
    async def end_profile(self, profile_id: str) -> Dict[str, Any]:
        """End a performance profile and return analysis"""
        if profile_id not in self.active_profiles:
            logger.warning(f"Profile {profile_id} not found")
            return {}
        
        profile = self.active_profiles.pop(profile_id)
        profile['end_time'] = datetime.now()
        profile['total_duration'] = (profile['end_time'] - profile['start_time']).total_seconds() * 1000
        profile['end_system_snapshot'] = await self._get_system_snapshot()
        
        # Analyze operations
        operations = profile['operations']
        if operations:
            durations = [op['duration_ms'] for op in operations]
            profile['analysis'] = {
                'total_operations': len(operations),
                'successful_operations': sum(1 for op in operations if op['success']),
                'avg_operation_duration': sum(durations) / len(durations),
                'max_operation_duration': max(durations),
                'min_operation_duration': min(durations),
                'total_operation_time': sum(durations)
            }
        
        self.profiles.append(profile)
        logger.info(f"✅ Completed performance profile: {profile['name']} ({profile['total_duration']:.1f}ms)")
        
        return profile
    
    async def _get_system_snapshot(self) -> Dict[str, Any]:
        """Get current system resource snapshot"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {'timestamp': datetime.now().isoformat()}
    
    def get_profile_summary(self, profile_id: str) -> Dict[str, Any]:
        """Get summary of a completed profile"""
        profile = next((p for p in self.profiles if p['id'] == profile_id), None)
        if not profile:
            return {}
        
        return {
            'id': profile['id'],
            'name': profile['name'],
            'duration_ms': profile.get('total_duration', 0),
            'operations_count': len(profile['operations']),
            'success_rate': (profile.get('analysis', {}).get('successful_operations', 0) / 
                           len(profile['operations'])) if profile['operations'] else 0,
            'avg_operation_duration': profile.get('analysis', {}).get('avg_operation_duration', 0)
        }

# Global profiler instance
auth_profiler = AuthPerformanceProfiler()

# Context manager for easy profiling
class profile_auth_session:
    """Context manager for profiling complete authentication sessions"""
    
    def __init__(self, session_name: str, context: Dict[str, Any] = None):
        self.session_name = session_name
        self.context = context
        self.profile_id = None
    
    async def __aenter__(self):
        self.profile_id = await auth_profiler.start_profile(self.session_name, self.context)
        return self.profile_id
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.profile_id:
            profile = await auth_profiler.end_profile(self.profile_id)
            return profile

# Integration helpers for gradual migration

def create_performance_wrapper(original_func: Callable, 
                             operation_name: str,
                             enable_monitoring: bool = True) -> Callable:
    """
    Create a performance-monitoring wrapper for any function
    
    This is useful for gradually adding monitoring to existing functions
    without changing their signatures or behavior.
    """
    
    if not enable_monitoring:
        return original_func
    
    if inspect.iscoroutinefunction(original_func):
        @functools.wraps(original_func)
        async def async_wrapper(*args, **kwargs):
            async with measure_performance(
                operation_name=operation_name,
                metadata={
                    'function': original_func.__name__,
                    'module': original_func.__module__
                }
            ):
                return await original_func(*args, **kwargs)
        return async_wrapper
    
    else:
        @functools.wraps(original_func)
        def sync_wrapper(*args, **kwargs):
            import time
            start_time = time.perf_counter()
            success = False
            
            try:
                result = original_func(*args, **kwargs)
                success = True
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Simple logging for sync functions
                status = "✅" if success else "❌"
                logger.info(f"{status} {operation_name}: {duration_ms:.2f}ms")
        
        return sync_wrapper

# Quick setup functions for easy integration

def setup_performance_monitoring(app, enable_middleware: bool = True):
    """
    Quick setup function to add performance monitoring to a FastAPI app
    
    Args:
        app: FastAPI application instance
        enable_middleware: Whether to add the monitoring middleware
    """
    
    if enable_middleware:
        app.add_middleware(PerformanceMonitoringMiddleware)
        logger.info("📊 Performance monitoring middleware added")
    
    # Add dashboard routes
    from .dashboard import router
    app.include_router(router)
    logger.info("📈 Performance dashboard routes added")
    
    # Start system monitoring
    async def startup_monitoring():
        await performance_monitor.start_system_monitoring()
        logger.info("📊 Performance monitoring started")
    
    app.add_event_handler("startup", startup_monitoring)
    
    # Stop monitoring on shutdown
    def shutdown_monitoring():
        performance_monitor.stop_system_monitoring()
        logger.info("📊 Performance monitoring stopped")
    
    app.add_event_handler("shutdown", shutdown_monitoring)

def instrument_auth_functions():
    """
    Instrument existing authentication functions with performance monitoring
    
    This function patches the existing auth utility functions to add monitoring
    without requiring code changes throughout the application.
    """
    
    # Patch existing functions with monitored versions
    import sys
    from .. import utils
    
    # Get the auth module
    auth_module = utils.clerk_auth
    
    # Create monitored versions
    auth_module.fetch_clerk_jwks = create_performance_wrapper(
        auth_module.fetch_clerk_jwks, 
        'jwks_fetch'
    )
    
    auth_module.verify_clerk_token = create_performance_wrapper(
        auth_module.verify_clerk_token,
        'jwt_validation'
    )
    
    auth_module.get_current_user = create_performance_wrapper(
        auth_module.get_current_user,
        'user_auth_full'
    )
    
    auth_module.get_current_user_with_db_sync = create_performance_wrapper(
        auth_module.get_current_user_with_db_sync,
        'user_auth_with_db_sync'
    )
    
    logger.info("🔧 Authentication functions instrumented with performance monitoring")

# Export key components
__all__ = [
    'PerformanceMonitoringMiddleware',
    'monitor_auth_operation',
    'PerformanceAwareAuthUtils',
    'perf_auth_utils',
    'AuthPerformanceProfiler',
    'auth_profiler',
    'profile_auth_session',
    'create_performance_wrapper',
    'setup_performance_monitoring',
    'instrument_auth_functions'
]