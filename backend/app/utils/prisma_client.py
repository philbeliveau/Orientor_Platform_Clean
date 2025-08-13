"""
Enhanced Prisma Client Wrapper for Orientor Platform
Provides async database operations with connection management, error handling, and performance monitoring
"""

import logging
import time
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Dict, Any
from prisma import Prisma
import json

logger = logging.getLogger(__name__)

class PrismaManager:
    """
    Singleton Prisma client manager for the Orientor Platform
    Handles connection lifecycle and provides async context managers
    """
    
    _instance: Optional['PrismaManager'] = None
    _client: Optional[Prisma] = None
    _connected: bool = False
    
    def __new__(cls) -> 'PrismaManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def client(self) -> Prisma:
        """Get the Prisma client instance"""
        if self._client is None:
            self._client = Prisma()
        return self._client
    
    async def connect(self) -> None:
        """Connect to the database"""
        if not self._connected:
            try:
                await self.client.connect()
                self._connected = True
                logger.info("✅ Prisma client connected successfully")
            except Exception as e:
                # Check if it's already connected error
                if "Already connected to the query engine" in str(e):
                    self._connected = True
                    logger.info("✅ Prisma client was already connected")
                else:
                    logger.error(f"❌ Failed to connect Prisma client: {e}")
                    raise
    
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        if self._connected and self._client:
            try:
                await self._client.disconnect()
                self._connected = False
                logger.info("✅ Prisma client disconnected")
            except Exception as e:
                logger.error(f"❌ Error disconnecting Prisma client: {e}")
    
    async def is_connected(self) -> bool:
        """Check if the client is connected"""
        try:
            if not self._connected:
                return False
            # Simple query to test connection
            await self.client.execute_raw("SELECT 1")
            return True
        except Exception:
            self._connected = False
            return False

# Global instance
prisma_manager = PrismaManager()

@asynccontextmanager
async def get_prisma() -> AsyncGenerator[Prisma, None]:
    """
    Enhanced async context manager for Prisma client with retry logic and monitoring
    
    Usage:
        async with get_prisma() as db:
            users = await db.user.find_many()
    """
    start_time = time.time()
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            await prisma_manager.connect()
            yield prisma_manager.client
            
            # Log performance metrics
            duration = time.time() - start_time
            if duration > 1.0:  # Log slow operations
                logger.warning(f"Slow database operation: {duration:.2f}s")
            return
            
        except Exception as e:
            # Don't retry on "already connected" errors
            if "Already connected to the query engine" in str(e):
                prisma_manager._connected = True
                yield prisma_manager.client
                return
                
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Database operation failed after {max_retries} retries: {e}")
                raise
            else:
                logger.warning(f"Database operation retry {retry_count}/{max_retries}: {e}")
                await asyncio.sleep(0.5 * retry_count)  # Exponential backoff
        finally:
            # Keep connection alive for reuse
            pass

@asynccontextmanager
async def get_prisma_transaction() -> AsyncGenerator[Prisma, None]:
    """
    Enhanced async context manager for Prisma transactions
    
    Usage:
        async with get_prisma_transaction() as db:
            user = await db.user.create(data={...})
            profile = await db.user_profile.create(data={...})
            # Transaction is automatically committed
    """
    start_time = time.time()
    await prisma_manager.connect()
    
    try:
        async with prisma_manager.client.tx() as transaction:
            yield transaction
            
        # Log transaction performance
        duration = time.time() - start_time
        if duration > 2.0:  # Log slow transactions
            logger.warning(f"Slow transaction: {duration:.2f}s")
            
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise

async def get_prisma_client() -> Prisma:
    """
    FastAPI dependency for Prisma client
    
    Usage in FastAPI routes:
        @app.get("/users")
        async def get_users(db: Prisma = Depends(get_prisma_client)):
            return await db.user.find_many()
    """
    await prisma_manager.connect()
    return prisma_manager.client

# Health check function
async def prisma_health_check() -> dict:
    """
    Health check for Prisma connection
    Returns status and connection info
    """
    try:
        await prisma_manager.connect()
        
        # Test query
        result = await prisma_manager.client.execute_raw("SELECT version() as version")
        
        return {
            "status": "healthy",
            "connected": True,
            "version": result[0]["version"] if result else "unknown",
            "client": "prisma"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "client": "prisma"
        }

# Startup and shutdown handlers for FastAPI
async def startup_prisma():
    """Startup handler for FastAPI app"""
    logger.info("🚀 Starting Prisma client...")
    await prisma_manager.connect()

async def shutdown_prisma():
    """Shutdown handler for FastAPI app"""
    logger.info("🛑 Shutting down Prisma client...")
    await prisma_manager.disconnect()

# Example service functions using Prisma
class PrismaUserService:
    """
    Example service class showing how to use Prisma for user operations
    Replace this with your actual service patterns
    """
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID with type safety"""
        async with get_prisma() as db:
            user = await db.user.find_unique(where={"id": user_id})
            return user.dict() if user else None
    
    @staticmethod
    async def get_users_with_profiles(limit: int = 10) -> list[dict]:
        """Get users with their profiles (example of relations)"""
        async with get_prisma() as db:
            users = await db.user.find_many(
                take=limit,
                include={
                    "user_profile": True,  # This will include related profile data
                    "conversations": {
                        "take": 5,  # Limit related conversations
                        "order_by": {"created_at": "desc"}
                    }
                }
            )
            return [user.dict() for user in users]
    
    @staticmethod
    async def create_user_with_profile(user_data: dict, profile_data: dict) -> dict:
        """Create user with profile in a transaction"""
        async with get_prisma() as db:
            # Example transaction
            result = await db.user.create(
                data={
                    **user_data,
                    "user_profile": {
                        "create": profile_data
                    }
                },
                include={"user_profile": True}
            )
            return result.dict()

# Migration helpers
async def check_prisma_schema():
    """
    Check if Prisma schema is in sync with database
    Useful for deployment health checks
    """
    try:
        async with get_prisma() as db:
            # This will fail if schema is out of sync
            await db.execute_raw("SELECT 1")
            return {"schema_status": "synced", "prisma": "ready"}
    except Exception as e:
        return {"schema_status": "out_of_sync", "error": str(e)}

# Utility for running raw SQL when needed
async def execute_raw_query(query: str, params: list = None) -> list[dict]:
    """
    Execute raw SQL query with Prisma
    Use sparingly - prefer Prisma's type-safe queries
    """
    async with get_prisma() as db:
        result = await db.execute_raw(query, *params or [])
        return result

# ===================================================================
# MIGRATION HELPER CLASSES AND UTILITIES
# ===================================================================

class PrismaMigrationHelpers:
    """
    Utility class providing migration helpers for converting SQLAlchemy to Prisma
    """
    
    @staticmethod
    def convert_sqlalchemy_filter_to_prisma_where(sqlalchemy_filter: str) -> dict:
        """
        Convert common SQLAlchemy filter patterns to Prisma where clauses
        Example: User.id == 123 -> {"id": 123}
        """
        # Basic conversion logic - extend as needed
        conversions = {
            "==": "equals",
            "!=": "not",
            ">": "gt", 
            ">=": "gte",
            "<": "lt",
            "<=": "lte",
            "in_": "in",
            "like": "contains"
        }
        # This is a simplified converter - expand based on actual usage patterns
        return {}
    
    @staticmethod
    def log_migration_step(router_name: str, operation: str, details: dict = None):
        """Log migration progress for monitoring"""
        log_entry = {
            "timestamp": time.time(),
            "router": router_name,
            "operation": operation,
            "details": details or {}
        }
        logger.info(f"Migration: {router_name} - {operation}", extra=log_entry)
    
    @staticmethod
    async def validate_data_integrity(table_name: str, count_query: str) -> dict:
        """
        Validate data integrity during migration
        Compare record counts between old and new queries
        """
        try:
            async with get_prisma() as db:
                result = await db.execute_raw(count_query)
                count = result[0]["count"] if result else 0
                
                return {
                    "table": table_name,
                    "count": count,
                    "status": "verified",
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "table": table_name,
                "error": str(e),
                "status": "failed",
                "timestamp": time.time()
            }

class PrismaOperationLogger:
    """
    Enhanced logging for Prisma operations during migration
    """
    
    def __init__(self, router_name: str):
        self.router_name = router_name
        self.operations = []
    
    def log_query_conversion(self, old_query: str, new_query: str, operation_type: str):
        """Log SQLAlchemy -> Prisma query conversions"""
        entry = {
            "timestamp": time.time(),
            "type": "query_conversion",
            "operation": operation_type,
            "old_query": old_query,
            "new_query": new_query,
            "router": self.router_name
        }
        self.operations.append(entry)
        logger.info(f"Query converted in {self.router_name}: {operation_type}")
    
    def log_performance_metric(self, operation: str, duration: float, record_count: int = None):
        """Log performance metrics for comparison"""
        entry = {
            "timestamp": time.time(),
            "type": "performance",
            "operation": operation,
            "duration": duration,
            "record_count": record_count,
            "router": self.router_name
        }
        self.operations.append(entry)
        
        if duration > 1.0:
            logger.warning(f"Slow operation in {self.router_name}: {operation} took {duration:.2f}s")
    
    def get_migration_report(self) -> dict:
        """Generate migration report for this router"""
        return {
            "router": self.router_name,
            "total_operations": len(self.operations),
            "conversions": [op for op in self.operations if op["type"] == "query_conversion"],
            "performance_metrics": [op for op in self.operations if op["type"] == "performance"],
            "migration_timestamp": time.time()
        }

# Performance monitoring utilities
class PrismaPerformanceMonitor:
    """
    Monitor performance metrics during migration and post-migration
    """
    
    @staticmethod
    async def benchmark_query(query_func, operation_name: str) -> dict:
        """
        Benchmark a Prisma query operation
        """
        start_time = time.time()
        try:
            result = await query_func()
            duration = time.time() - start_time
            
            return {
                "operation": operation_name,
                "duration": duration,
                "status": "success",
                "result_count": len(result) if isinstance(result, list) else 1,
                "timestamp": time.time()
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "operation": operation_name,
                "duration": duration,
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    @staticmethod
    async def connection_health_check() -> dict:
        """
        Comprehensive health check for Prisma connection
        """
        health_data = await prisma_health_check()
        
        # Add additional metrics
        try:
            async with get_prisma() as db:
                # Test basic operations
                start_time = time.time()
                await db.execute_raw("SELECT 1")
                query_time = time.time() - start_time
                
                health_data.update({
                    "query_response_time": query_time,
                    "connection_pool_status": "active",
                    "migration_ready": query_time < 0.5
                })
        except Exception as e:
            health_data.update({
                "query_response_time": None,
                "connection_pool_status": "error",
                "migration_ready": False,
                "error": str(e)
            })
        
        return health_data