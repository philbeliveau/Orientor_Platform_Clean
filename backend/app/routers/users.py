from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..utils.database import get_db
from ..models import User, UserProfile
from ..utils.secure_auth_integration import get_current_user_secure_integrated as get_current_user

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
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information."""
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


    return current_user

@router.get("/{user_id}/profile", response_model=ProfileResponse)
def read_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile information for a specific user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile
