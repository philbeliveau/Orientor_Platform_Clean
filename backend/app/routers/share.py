from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session

from app.utils.secure_auth_integration import get_current_user_secure_integrated as get_current_user
from app.models import User
from app.utils.database import get_db
from app.services.share_service import ShareService
from app.schemas.share import (
    ShareOptions, ShareLink, ShareAnalytics, SharedConversationRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat/share",
    tags=["share"]
)

@router.post("/conversations/{conversation_id}", response_model=ShareLink)
async def create_share_link(
    conversation_id: int,
    options: ShareOptions = Body(ShareOptions()),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a share link for a conversation"""
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


    share_link = await ShareService.create_share_link(
        db, conversation_id, current_user.id, options
    )
    
    if not share_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return share_link

@router.get("/shared/{share_token}")
async def get_shared_conversation(
    share_token: str,
    request: SharedConversationRequest = Body(SharedConversationRequest()),
    db: Session = Depends(get_db)
):
    """Access a shared conversation"""
    result = await ShareService.get_shared_conversation(
        db, share_token, request.password
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found or expired"
        )
    
    if isinstance(result, dict) and result.get("error") == "invalid_password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"X-Requires-Password": "true"}
        )
    
    return result

@router.put("/shares/{share_id}")
async def update_share_settings(
    share_id: int,
    options: ShareOptions,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update share settings"""
    success = await ShareService.update_share_settings(
        db, share_id, current_user.id, options
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    return {"message": "Share settings updated successfully"}

@router.delete("/shares/{share_id}")
async def revoke_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a share link"""
    success = await ShareService.revoke_share(
        db, share_id, current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    return {"message": "Share revoked successfully"}

@router.get("/user/shares", response_model=List[Dict[str, Any]])
async def get_user_shares(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all shares created by the current user"""
    return await ShareService.get_user_shares(db, current_user.id)

@router.get("/shares/{share_id}/analytics", response_model=ShareAnalytics)
async def get_share_analytics(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a share"""
    analytics = await ShareService.get_share_analytics(
        db, share_id, current_user.id
    )
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    return analytics