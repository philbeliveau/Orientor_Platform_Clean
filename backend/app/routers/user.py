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

from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.models import User, UserProfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get user profile - Clerk authenticated"""


    logger.info(f"Getting profile for user ID: {current_user.id}")
    
    return {
        "id": current_user.id,
        "clerk_id": current_user.clerk_user_id,
        "email": current_user.email,
        "profile": current_user.profile if hasattr(current_user, 'profile') else None,
        "onboarding_completed": current_user.onboarding_completed
    }

@router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    STANDARDIZED onboarding status check - matches onboarding router format
    """
    logger.info(f"🔍 User router: Getting onboarding status for user ID: {current_user.id}")
    
    try:
        # SIMPLIFIED: Single source of truth - database field
        onboarding_completed = getattr(current_user, 'onboarding_completed', False)
        logger.info(f"📊 User {current_user.id} onboarding_completed: {onboarding_completed}")
        
        # FALLBACK FIX: If database field is False, check personality profile and fix if needed
        if not onboarding_completed:
            personality_profile = await db.personality_profiles.find_first(
                where={'user_id': current_user.id}
            )
            
            if personality_profile:
                logger.info(f"🔧 Fixing onboarding_completed for user {current_user.id} - has profile but field is False")
                await db.users.update(
                    where={'id': current_user.id},
                    data={'onboarding_completed': True}
                )
                onboarding_completed = True
        
        # STANDARDIZED RESPONSE: Match onboarding router format exactly
        return {
            "onboarding_completed": onboarding_completed,
            "has_started": onboarding_completed,  # If completed, they must have started
            "is_complete": onboarding_completed,
            "message": "Onboarding completed" if onboarding_completed else "Onboarding needed"
        }
        
    except Exception as e:
        logger.error(f"Error in user router onboarding status check: {str(e)}")
        # Safe fallback
        return {
            "onboarding_completed": False,
            "has_started": False,
            "is_complete": False,
            "message": "Error checking status - assuming onboarding needed"
        }

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return {
        "id": current_user.id,
        "clerk_user_id": current_user.clerk_user_id,
        "email": current_user.email,
        "onboarding_completed": current_user.onboarding_completed,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }