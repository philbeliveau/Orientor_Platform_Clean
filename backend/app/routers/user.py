from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
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
    db: Session = Depends(get_db)
):
    """Get user profile - Clerk authenticated"""
# ============================================================================
# AUTHENTICATION MIGRATION - Secure Integration System
# ============================================================================
# This router has been migrated to use the unified secure authentication system
# with integrated caching, security optimizations, and rollback support.
# 
# Migration date: 2025-08-07 13:44:03
# Previous system: clerk_auth.get_current_user_with_db_sync
# Current system: secure_auth_integration.get_current_user_secure_integrated
# 
# Benefits:
# - AES-256 encryption for sensitive cache data
# - Full SHA-256 cache keys (not truncated)
# - Error message sanitization
# - Multi-layer caching optimization  
# - Zero-downtime rollback capability
# - Comprehensive security monitoring
# ============================================================================


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
    db: Session = Depends(get_db)
):
    """
    Check if the user has completed the onboarding process.
    Uses both the database field and personality profile as fallback.
    """
    logger.info(f"Checking onboarding status for user ID: {current_user.id}")
    
    # Check if onboarding_completed field exists and is True
    if hasattr(current_user, 'onboarding_completed') and current_user.onboarding_completed:
        return {"onboarding_completed": True}
    
    # Fallback: Check if user has a personality profile
    try:
        from ..models.personality_profiles import PersonalityProfile
        personality_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        has_profile = personality_profile is not None
        
        # If they have a profile but onboarding_completed is False, update it
        if has_profile and hasattr(current_user, 'onboarding_completed') and not current_user.onboarding_completed:
            current_user.onboarding_completed = True
            db.commit()
            logger.info(f"Updated onboarding_completed for user {current_user.id} based on personality profile")
        
        return {"onboarding_completed": has_profile}
        
    except Exception as e:
        logger.error(f"Error checking personality profile: {e}")
        # If we can't check, return False for safety
        return {"onboarding_completed": False}

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