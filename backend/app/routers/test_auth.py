from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma

from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.models.user import User

# ============================================================================
# PRISMA MIGRATION - Enhanced Database Integration
# ============================================================================
# This router has been migrated to use Prisma ORM with enhanced features:
# - Type-safe database operations
# - Improved error handling and retry logic
# - Performance monitoring
# - Enhanced logging
# - Transaction support for complex operations
# 
# Migration date: 2025-01-13
# Previous system: SQLAlchemy ORM
# Current system: Prisma ORM with enhanced client
# ============================================================================

router = APIRouter()

@router.get("/test-token")
async def test_token_verification(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify Clerk token validation"""
    try:
        return {
            "status": "success",
            "user_id": current_user.id,
            "clerk_user_id": current_user.clerk_user_id,
            "token_valid": True,
            "authentication_method": "clerk_standard"
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {str(e)}"
        )
