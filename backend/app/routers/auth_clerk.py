"""
Clerk-based authentication router for FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session

from ..utils.clerk_auth import get_current_user_with_db_sync as get_current_user, clerk_health_check, create_clerk_user_in_db
from ..utils.database import get_db
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information and sync with local database
    """
    try:
        # Automatically create/update user in local database
        local_user = create_clerk_user_in_db(current_user, db)
        
        return {
            "user": current_user,
            "local_user": local_user,
            "message": "Successfully authenticated with Clerk"
        }
    except Exception as e:
        logger.error(f"Error syncing user with database: {e}")
        # Still return Clerk user info even if database sync fails
        return {
            "user": current_user,
            "message": "Successfully authenticated with Clerk (database sync failed)",
            "warning": str(e)
        }

@router.get("/health")
async def auth_health():
    """
    Check authentication service health
    """
    clerk_status = await clerk_health_check()
    return {
        "status": "healthy" if clerk_status["status"] == "healthy" else "unhealthy",
        "authentication": "clerk",
        "clerk": clerk_status
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side handled by Clerk)
    """
    return {
        "message": "Logout handled by Clerk on client-side",
        "status": "success"
    }

# Test protected endpoint
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Test protected route to verify authentication
    """
    return {
        "message": f"Hello {getattr(current_user, 'first_name', 'User')}! This is a protected route.",
        "user_id": current_user["id"],
        "authenticated": True
    }