"""
Unified error handling utilities for Prisma database operations.
Provides consistent error handling patterns across the application.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException
from prisma.errors import (
    PrismaError,
    DataError,
    UniqueViolationError,
    ForeignKeyViolationError,
    RecordNotFoundError,
    ClientNotConnectedError,
    TransactionError
)

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database-related errors."""
    def __init__(self, message: str, error_code: str = "DB_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, "DB_CONNECTION_ERROR")


class DatabaseValidationError(DatabaseError):
    """Exception raised when database validation fails."""
    def __init__(self, message: str = "Database validation failed"):
        super().__init__(message, "DB_VALIDATION_ERROR")


class DatabaseOperationError(DatabaseError):
    """Exception raised when database operation fails."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DB_OPERATION_ERROR")


def handle_prisma_error(e: Exception, operation: str = "database operation") -> HTTPException:
    """
    Convert Prisma errors to appropriate HTTP exceptions with detailed logging.
    
    Args:
        e: The Prisma exception
        operation: Description of the operation that failed
        
    Returns:
        HTTPException: Appropriate HTTP exception for the error type
    """
    error_details = {
        "operation": operation,
        "error_type": type(e).__name__,
        "error_message": str(e)
    }

    if isinstance(e, UniqueViolationError):
        # Unique constraint violations
        logger.error(f"Unique constraint violation in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=409,
            detail=f"Duplicate record: {operation} failed due to existing data"
        )
    
    elif isinstance(e, ForeignKeyViolationError):
        # Foreign key constraint violations
        logger.error(f"Foreign key constraint violation in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=400,
            detail=f"Related record required for {operation}"
        )
    
    elif isinstance(e, RecordNotFoundError):
        # Record not found errors
        logger.error(f"Record not found in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=404,
            detail=f"Record not found for {operation}"
        )
    
    elif isinstance(e, ClientNotConnectedError):
        # Database connection errors
        logger.error(f"Database connection error in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=503,
            detail=f"Database connection error during {operation}"
        )
    
    elif isinstance(e, TransactionError):
        # Transaction errors
        logger.error(f"Transaction error in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=400,
            detail=f"Database transaction failed for {operation}"
        )
    
    elif isinstance(e, DataError):
        # Data validation errors
        logger.error(f"Data validation error in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=400,
            detail=f"Data validation error in {operation}: Invalid data format"
        )
    
    elif isinstance(e, PrismaError):
        # Generic Prisma errors
        logger.error(f"Prisma error in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=500,
            detail=f"Database error during {operation}"
        )
    
    else:
        # Generic exception handling
        logger.error(f"Unexpected error in {operation}: {str(e)}", extra=error_details)
        return HTTPException(
            status_code=500,
            detail=f"Unexpected error during {operation}: {str(e)}"
        )


def with_db_error_handling(operation_name: str):
    """
    Decorator for database operations that automatically handles Prisma errors.
    
    Args:
        operation_name: Human-readable name for the operation
        
    Usage:
        @with_db_error_handling("user creation")
        async def create_user(db: Prisma, user_data: dict):
            return await db.users.create(data=user_data)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise handle_prisma_error(e, operation_name)
        return wrapper
    return decorator


def log_database_operation(operation: str, user_id: Optional[str] = None, **kwargs):
    """
    Log database operations with structured logging for better monitoring.
    
    Args:
        operation: Name of the database operation
        user_id: Optional user ID for tracking
        **kwargs: Additional context data
    """
    log_data = {
        "operation": operation,
        "user_id": user_id,
        **kwargs
    }
    logger.info(f"Database operation: {operation}", extra=log_data)


# Common error response templates
ERROR_RESPONSES = {
    "user_not_found": {
        "message": "User not found",
        "code": "USER_NOT_FOUND",
        "status_code": 404
    },
    "session_expired": {
        "message": "Session has expired",
        "code": "SESSION_EXPIRED", 
        "status_code": 401
    },
    "assessment_not_found": {
        "message": "Assessment session not found",
        "code": "ASSESSMENT_NOT_FOUND",
        "status_code": 404
    },
    "onboarding_already_complete": {
        "message": "Onboarding has already been completed",
        "code": "ONBOARDING_COMPLETE",
        "status_code": 409
    },
    "database_connection": {
        "message": "Database connection failed",
        "code": "DB_CONNECTION_FAILED",
        "status_code": 503
    }
}


def get_error_response(error_key: str, custom_message: Optional[str] = None) -> HTTPException:
    """
    Get a standardized error response.
    
    Args:
        error_key: Key from ERROR_RESPONSES
        custom_message: Optional custom message override
        
    Returns:
        HTTPException: Standardized error response
    """
    error_template = ERROR_RESPONSES.get(error_key)
    if not error_template:
        return HTTPException(
            status_code=500,
            detail=f"Unknown error: {error_key}"
        )
    
    message = custom_message or error_template["message"]
    return HTTPException(
        status_code=error_template["status_code"],
        detail=message
    )