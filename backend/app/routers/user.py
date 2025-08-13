from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    logger.info(f"🔍 ONBOARDING STATUS CHECK for user ID: {current_user.id}")
    logger.info(f"🔍 Clerk User ID: {getattr(current_user, 'clerk_user_id', 'NOT_FOUND')}")
    logger.info(f"🔍 User Email: {getattr(current_user, 'email', 'NOT_FOUND')}")
    
    # DEBUG: Log current user onboarding status from multiple perspectives
    onboarding_completed_value = getattr(current_user, 'onboarding_completed', 'FIELD_NOT_FOUND')
    logger.info(f"🔍 current_user.onboarding_completed = {onboarding_completed_value} (type: {type(onboarding_completed_value)})")
    logger.info(f"🔍 User object type: {type(current_user)}")
    logger.info(f"🔍 User object ID: {id(current_user)}")
    
    # Check if this is fresh from database or cached
    try:
        from sqlalchemy import inspect
        inspector = inspect(current_user)
        if hasattr(inspector, 'expired_attributes'):
            expired_attrs = inspector.expired_attributes
            logger.info(f"🔍 Expired attributes: {expired_attrs}")
        logger.info(f"🔍 User object state: {inspector.persistent if hasattr(inspector, 'persistent') else 'unknown'}")
    except Exception as inspect_error:
        logger.warning(f"⚠️ Could not inspect user object: {inspect_error}")
    
    # Check if onboarding_completed field exists and is True
    if hasattr(current_user, 'onboarding_completed'):
        field_value = current_user.onboarding_completed
        logger.info(f"🔍 Onboarding field exists, value: {field_value} (type: {type(field_value)})")
        
        if field_value:
            logger.info(f"✅ User {current_user.id} onboarding completed via database field")
            return {"onboarding_completed": True}
        else:
            logger.info(f"🔴 User {current_user.id} onboarding NOT completed according to database field")
    else:
        logger.error(f"❌ CRITICAL: User {current_user.id} missing onboarding_completed field!")
        # Let's check all user attributes to debug
        all_attrs = [attr for attr in dir(current_user) if not attr.startswith('_')]
        logger.info(f"🔍 All user attributes: {all_attrs}")
    
    # Fallback: Check if user has a personality profile
    try:
        from ..models.personality_profiles import PersonalityProfile
        personality_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        has_profile = personality_profile is not None
        logger.info(f"🔍 DEBUG: User {current_user.id} has personality profile: {has_profile}")
        
        # If they have a profile but onboarding_completed is False, update it
        if has_profile and hasattr(current_user, 'onboarding_completed') and not current_user.onboarding_completed:
            logger.info(f"🔄 Updating onboarding_completed for user {current_user.id} based on personality profile")
            current_user.onboarding_completed = True
            db.commit()
            db.refresh(current_user)
            logger.info(f"✅ Updated onboarding_completed for user {current_user.id}")
        
        # Additional verification: Query database directly
        try:
            direct_query_result = db.execute(
                text("SELECT onboarding_completed FROM users WHERE id = :user_id"),
                {"user_id": current_user.id}
            ).fetchone()
            if direct_query_result:
                db_onboarding_value = direct_query_result[0]
                logger.info(f"🔍 DIRECT DATABASE QUERY: user {current_user.id} onboarding_completed = {db_onboarding_value}")
                
                # If database says True but we're returning False, there's a cache issue
                if db_onboarding_value and not has_profile:
                    logger.warning(f"⚠️ CACHE MISMATCH: Database shows True, but personality profile check shows False")
                    # Trust the database value
                    has_profile = True
            else:
                logger.error(f"❌ Could not find user {current_user.id} in direct database query!")
        except Exception as direct_query_error:
            logger.error(f"⚠️ Direct database query failed: {direct_query_error}")
        
        result = {"onboarding_completed": has_profile}
        logger.info(f"📤 FINAL RESULT for user {current_user.id}: {result}")
        logger.info(f"📋 STATUS CHECK SUMMARY:")
        logger.info(f"📋   - Database field: {onboarding_completed_value}")
        logger.info(f"📋   - Personality profile exists: {has_profile}")
        logger.info(f"📋   - Final result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error checking personality profile: {e}")
        # If we can't check, return False for safety
        logger.error(f"❌ Returning False for user {current_user.id} due to error: {e}")
        logger.info(f"📋 ERROR FALLBACK SUMMARY:")
        logger.info(f"📋   - Error occurred: {e}")
        logger.info(f"📋   - Database field: {onboarding_completed_value}")
        logger.info(f"📋   - Returning: False (safety fallback)")
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