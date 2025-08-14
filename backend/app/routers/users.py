from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from prisma import Prisma
from ..utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    hobbies: Optional[str] = None
    interests: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
# ============================================================================
# PRISMA MIGRATION - Enhanced Database Integration
# ============================================================================
# This router has been migrated to use Prisma ORM with enhanced features:
# - Type-safe database operations
# - Improved error handling and retry logic
# - Performance monitoring
# - Enhanced logging
# 
# Migration date: 2025-01-13
# Previous system: SQLAlchemy ORM
# Current system: Prisma ORM with enhanced client
# ============================================================================

    return current_user

@router.get("/{user_id}/profile", response_model=ProfileResponse)
async def read_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get profile information for a specific user."""
    # Initialize operation logger
    logger = PrismaOperationLogger("users")
    
    try:
        # Convert SQLAlchemy query to Prisma query
        profile = await db.user_profile.find_first(
            where={"user_id": user_id}
        )
        
        logger.log_query_conversion(
            f"db.query(UserProfile).filter(UserProfile.user_id == {user_id}).first()",
            f"db.user_profile.find_first(where={{\"user_id\": {user_id}}})",
            "profile_lookup"
        )
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_performance_metric("profile_lookup_error", 0, 0)
        raise HTTPException(status_code=500, detail="Internal server error")
