"""
Prisma Client Wrapper for Orientor Platform
Provides async database operations with connection management
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
from prisma import Prisma
from prisma.models import User  # This will be generated after introspection
import asyncio

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
    Async context manager for Prisma client
    
    Usage:
        async with get_prisma() as db:
            users = await db.user.find_many()
    """
    await prisma_manager.connect()
    try:
        yield prisma_manager.client
    except Exception as e:
        logger.error(f"Database operation error: {e}")
        raise
    finally:
        # Keep connection alive for reuse
        pass

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