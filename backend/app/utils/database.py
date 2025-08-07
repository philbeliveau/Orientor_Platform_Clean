import logging
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import Optional, Dict, Any
from fastapi import HTTPException
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create Base class for models
Base = declarative_base()

# Global variables for database connection
engine: Optional[object] = None
SessionLocal: Optional[object] = None
database_connected = False

def create_database_engine():
    """Create database engine with optimized configuration for user session caching"""
    global engine
    
    try:
        database_url = settings.get_database_url
        logger.info(f"Attempting to connect to database with optimization...")
        
        # Optimized engine configuration for Phase 4-5 (Database optimization)
        # These settings are tuned for high-performance user session caching
        engine_kwargs = {
            "pool_size": 5,  # Moderate pool size optimized for caching workload
            "max_overflow": 10,  # Higher overflow for burst capacity
            "pool_timeout": 30,  # Longer timeout for better reliability
            "pool_recycle": 3600,  # 1 hour recycle (optimized for session cache TTL)
            "pool_pre_ping": True,  # Test connections before use
            "pool_reset_on_return": "commit",  # Clean connection state
            "connect_args": {
                "connect_timeout": 10,  # Connection timeout
                "options": "-c timezone=utc"  # Set timezone
            }
        }
        
        # Environment-specific optimizations
        if settings.is_railway:
            # Railway-specific optimizations for database session caching
            engine_kwargs.update({
                "pool_size": 3,  # Smaller pool for Railway limits
                "max_overflow": 7,  # Moderate overflow
                "pool_timeout": 20,  # Shorter timeout for Railway
                "pool_recycle": 7200,  # 2 hours for production stability
                "echo": False  # Disable SQL logging in production
            })
        elif settings.is_production:
            # Production optimizations
            engine_kwargs.update({
                "pool_size": 8,  # Larger pool for production load
                "max_overflow": 15,  # Higher burst capacity
                "pool_recycle": 7200,  # 2 hour recycle
                "echo": False  # Disable SQL logging
            })
        else:
            # Development optimizations
            engine_kwargs.update({
                "pool_size": 3,  # Smaller for development
                "max_overflow": 5,
                "echo": False  # Can be enabled for debugging
            })
        
        engine = create_engine(database_url, **engine_kwargs)
        
        # Log optimization settings
        logger.info("✅ Database engine created with optimized configuration:")
        logger.info(f"   Pool size: {engine_kwargs['pool_size']}")
        logger.info(f"   Max overflow: {engine_kwargs['max_overflow']}")
        logger.info(f"   Pool timeout: {engine_kwargs['pool_timeout']}s")
        logger.info(f"   Pool recycle: {engine_kwargs['pool_recycle']}s")
        logger.info(f"   Environment: {'Railway' if settings.is_railway else 'Production' if settings.is_production else 'Development'}")
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ Failed to create optimized database engine: {str(e)}")
        raise

def test_database_connection():
    """Test database connection and log information"""
    global database_connected
    
    if not engine:
        logger.error("Database engine not initialized")
        return False
    
    try:
        # Test the connection with timeout
        with engine.connect() as conn:
            # Set a statement timeout
            conn.execute(text("SET statement_timeout = '30s'"))
            
            # Basic connection test
            result = conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            
            if test_result[0] == 1:
                logger.info("✅ Database connection test successful")
                
                # Get database information
                try:
                    result = conn.execute(text("SELECT current_database(), current_user, version()"))
                    db_name, db_user, version = result.fetchone()
                    logger.info(f"Database: {db_name}")
                    logger.info(f"User: {db_user}")
                    logger.info(f"PostgreSQL version: {version[:50]}...")  # Truncate long version string
                    
                    # Check if tables exist (with limit)
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        LIMIT 10
                    """))
                    tables = [row[0] for row in result]
                    logger.info(f"Sample tables: {tables[:5]}...")  # Show first 5 tables
                    
                except Exception as info_error:
                    logger.warning(f"Could not get database info: {info_error}")
                
                database_connected = True
                return True
            
    except OperationalError as e:
        logger.error(f"❌ Database connection failed (Operational): {str(e)}")
        database_connected = False
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed (SQLAlchemy): {str(e)}")
        database_connected = False
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed (Unexpected): {str(e)}")
        database_connected = False
        return False

def initialize_database():
    """Initialize database connection"""
    global SessionLocal, engine
    
    try:
        # Create engine
        engine = create_database_engine()
        
        # Test connection
        if test_database_connection():
            # Create session factory
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("✅ Database initialization completed successfully")
            return True
        else:
            logger.warning("⚠️ Database connection test failed, but continuing...")
            # Create session factory anyway for graceful degradation
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return False
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        # Create a mock session factory for graceful degradation
        SessionLocal = None
        return False

def get_db():
    """Get database session with enhanced error handling and recovery"""
    global SessionLocal, engine
    
    # Initialize database on first access if not already done
    if not SessionLocal or not engine:
        logger.info("🔌 Initializing database on first access...")
        initialize_database()
    
    if not SessionLocal:
        logger.error("Database session factory not initialized")
        raise Exception("Database not available")
    
    db = None
    try:
        db = SessionLocal()
        # Test the connection before yielding
        db.execute(text("SELECT 1"))
        yield db
    except OperationalError as e:
        logger.error(f"Database operational error: {str(e)}")
        if db:
            db.rollback()
        # Try to reinitialize database connection
        try:
            logger.info("🔄 Attempting to reinitialize database connection...")
            initialize_database()
            if SessionLocal:
                db = SessionLocal()
                db.execute(text("SELECT 1"))
                yield db
            else:
                raise Exception("Database reinitialize failed")
        except Exception as reinit_error:
            logger.error(f"Database reinitialize failed: {str(reinit_error)}")
            raise HTTPException(
                status_code=503, 
                detail="Database service temporarily unavailable"
            )
    except SQLAlchemyError as e:
        logger.error(f"Database SQLAlchemy error: {str(e)}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database query error"
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions from endpoints without wrapping them
        logger.info(f"HTTPException from endpoint: {e.detail}")
        if db:
            db.rollback()
        raise e
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database session error: {str(e)}"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.warning(f"Error closing database session: {str(close_error)}")

def check_database_health():
    """Check if database is healthy"""
    global database_connected
    
    if not engine or not database_connected:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        database_connected = False
        return False

# Database initialization is now deferred to avoid caching issues
# The database will be initialized when first accessed
logger.info("📌 Database initialization deferred to avoid environment variable caching")

# ============================================================================
# DATABASE SESSION UTILITIES FOR OPTIMIZATION (Phase 4-5)
# ============================================================================

from contextlib import contextmanager, asynccontextmanager

@contextmanager
def get_db_session():
    """
    Context manager for database sessions with proper cleanup.
    Useful for services that need database access outside of FastAPI dependency injection.
    
    Usage:
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
    """
    db = None
    try:
        if not SessionLocal:
            initialize_database()
        
        if not SessionLocal:
            raise Exception("Database session factory not available")
        
        db = SessionLocal()
        yield db
    except Exception as e:
        if db:
            db.rollback()
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.warning(f"Error closing database session: {close_error}")

@asynccontextmanager
async def get_async_db_session():
    """
    Async context manager for database sessions.
    For use with async services and caching systems.
    
    Usage:
        async with get_async_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
    """
    db = None
    try:
        if not SessionLocal:
            initialize_database()
        
        if not SessionLocal:
            raise Exception("Database session factory not available")
        
        db = SessionLocal()
        # Test connection asynchronously
        await asyncio.create_task(_test_db_connection(db))
        yield db
    except Exception as e:
        if db:
            db.rollback()
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.warning(f"Error closing async database session: {close_error}")

async def _test_db_connection(db):
    """Test database connection asynchronously"""
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: db.execute(text("SELECT 1")))

def get_connection_pool_stats() -> Optional[Dict]:
    """
    Get current database connection pool statistics.
    Useful for monitoring and optimization.
    
    Returns:
        Dict with pool statistics or None if engine not available
    """
    if not engine or not hasattr(engine, 'pool'):
        return None
    
    pool = engine.pool
    
    try:
        return {
            'pool_size': pool.size(),
            'checked_in_connections': pool.checkedin(),
            'checked_out_connections': pool.checkedout(),
            'overflow_connections': pool.overflow(),
            'total_connections': pool.size() + pool.overflow(),
            'pool_timeout': getattr(pool, '_timeout', 'unknown'),
            'pool_recycle': getattr(pool, '_recycle', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting pool stats: {e}")
        return {'error': str(e)}

def optimize_database_for_caching():
    """
    Apply additional database optimizations specifically for user session caching.
    This function can be called after database initialization to tune performance.
    """
    if not engine:
        logger.warning("Cannot optimize database - engine not available")
        return False
    
    try:
        # Set connection pool events for monitoring
        from sqlalchemy import event
        
        @event.listens_for(engine, "connect")
        def set_session_optimizations(dbapi_connection, connection_record):
            """Set session-level optimizations when connections are created"""
            with dbapi_connection.cursor() as cursor:
                # Optimize for read-heavy workloads (user session caching)
                cursor.execute("SET SESSION statement_timeout = '30s'")
                cursor.execute("SET SESSION lock_timeout = '10s'")
                cursor.execute("SET SESSION idle_in_transaction_session_timeout = '60s'")
                
                # Optimize for faster reads
                cursor.execute("SET SESSION effective_cache_size = '256MB'")
                cursor.execute("SET SESSION random_page_cost = 1.1")  # SSD optimization
        
        logger.info("🔧 Database session optimizations applied")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply database optimizations: {e}")
        return False