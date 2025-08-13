# Phase 1: Enhanced Dependency Infrastructure

**Duration**: 30 minutes  
**Priority**: High (Foundation for all other phases)

## 🎯 Objective

Enhance the existing Prisma infrastructure to support robust dependency injection and connection management across all FastAPI routers.

## 📋 Current Infrastructure Analysis

### Existing Components
```python
# backend/app/utils/prisma_client.py
class PrismaManager:
    """Singleton Prisma client manager"""
    # ✅ Already implemented
    
@asynccontextmanager
async def get_prisma() -> AsyncGenerator[Prisma, None]:
    """Basic async context manager"""
    # 🔄 Needs enhancement
```

### Issues to Address
1. **Limited error handling** in dependency injection
2. **No connection retry logic** for resilience
3. **Missing transaction support** utilities
4. **Lack of standardized logging** patterns
5. **No performance monitoring** hooks

## 🛠️ Implementation Tasks

### Task 1.1: Enhanced Dependency Function

**Update `get_prisma()` function:**

```python
@asynccontextmanager
async def get_prisma() -> AsyncGenerator[Prisma, None]:
    """
    Enhanced Prisma dependency with robust error handling and monitoring
    
    Usage:
        async def endpoint(db: Prisma = Depends(get_prisma)):
            users = await db.user.find_many()
    """
    start_time = time.time()
    await prisma_manager.connect()
    
    try:
        # Add connection health check
        await prisma_manager.client.execute_raw("SELECT 1")
        logger.debug("Prisma connection established successfully")
        
        yield prisma_manager.client
        
    except Exception as e:
        logger.error(f"Prisma operation failed: {e}")
        # Attempt connection recovery
        if not await prisma_manager.is_connected():
            logger.warning("Attempting Prisma reconnection...")
            await prisma_manager.connect()
        raise
    finally:
        execution_time = (time.time() - start_time) * 1000
        logger.debug(f"Prisma operation completed in {execution_time:.2f}ms")
```

### Task 1.2: Transaction Support Utilities

**Add transaction wrapper functions:**

```python
@asynccontextmanager
async def get_prisma_transaction() -> AsyncGenerator[Prisma, None]:
    """
    Prisma dependency with automatic transaction management
    
    Usage:
        async def endpoint(db: Prisma = Depends(get_prisma_transaction)):
            # All operations in this function are wrapped in a transaction
            await db.user.create(data=user_data)
            await db.profile.create(data=profile_data)
            # Auto-commit on success, auto-rollback on error
    """
    async with get_prisma() as client:
        async with client.tx() as transaction:
            yield transaction
```

### Task 1.3: Migration Helper Functions

**Create SQLAlchemy → Prisma conversion utilities:**

```python
class PrismaMigrationHelpers:
    """Utilities to ease SQLAlchemy to Prisma migration"""
    
    @staticmethod
    def convert_sqlalchemy_filter(filter_dict: dict) -> dict:
        """Convert SQLAlchemy filter patterns to Prisma where clauses"""
        pass
    
    @staticmethod
    def convert_relationships(includes: list) -> dict:
        """Convert SQLAlchemy joinedload to Prisma include syntax"""
        pass
    
    @staticmethod
    async def migrate_pagination(
        model, page: int, per_page: int, where: dict = None
    ):
        """Standardized pagination pattern for Prisma"""
        pass
```

### Task 1.4: Enhanced Logging and Monitoring

**Add structured logging:**

```python
class PrismaOperationLogger:
    """Structured logging for Prisma operations"""
    
    @staticmethod
    def log_query(operation: str, model: str, duration_ms: float):
        logger.info(
            f"Prisma {operation}",
            extra={
                "operation": operation,
                "model": model,
                "duration_ms": duration_ms,
                "component": "prisma_client"
            }
        )
    
    @staticmethod
    def log_error(operation: str, model: str, error: Exception):
        logger.error(
            f"Prisma {operation} failed",
            extra={
                "operation": operation,
                "model": model,
                "error": str(error),
                "component": "prisma_client"
            }
        )
```

## 📁 Files to Modify

### Primary File
- `backend/app/utils/prisma_client.py`

### Changes Required

1. **Import additions:**
```python
import time
from typing import AsyncGenerator, Optional, Dict, Any
from contextlib import asynccontextmanager
```

2. **Function enhancements:**
   - Enhanced `get_prisma()` with error handling
   - New `get_prisma_transaction()` function
   - Migration helper utilities
   - Logging and monitoring components

3. **New classes:**
   - `PrismaMigrationHelpers`
   - `PrismaOperationLogger`

## ✅ Success Criteria

1. **Enhanced dependency injection** with robust error handling
2. **Transaction support** for complex operations
3. **Migration utilities** to ease router conversion
4. **Comprehensive logging** for debugging and monitoring
5. **Connection resilience** with automatic retry logic

## 🧪 Testing

### Test Enhanced Dependencies
```python
# Test basic dependency injection
async def test_get_prisma():
    async with get_prisma() as db:
        result = await db.user.find_first()
        assert result is not None

# Test transaction support  
async def test_prisma_transaction():
    async with get_prisma_transaction() as db:
        user = await db.user.create(data={"email": "test@example.com"})
        profile = await db.profile.create(data={"user_id": user.id})
        # Both operations committed together
```

## 🔄 Next Steps

After completing Phase 1:
1. Verify enhanced infrastructure works correctly
2. Test transaction support with sample operations
3. Proceed to [Phase 2: Router Migration](./phase-2-migration.md)

---
**⚠️ Important**: Complete Phase 1 fully before proceeding to router migration. This infrastructure is the foundation for all subsequent phases.