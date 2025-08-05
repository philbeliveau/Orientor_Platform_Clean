"""
Clerk authentication utilities for FastAPI backend
"""
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import clerk_backend_api as clerk
from clerk_backend_api.exceptions import ClerkAPIError
import logging

logger = logging.getLogger(__name__)

# Initialize Clerk client
clerk_client = clerk.Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

# Security scheme for extracting Bearer token
security = HTTPBearer()

async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify Clerk JWT token and return user information
    """
    try:
        token = credentials.credentials
        
        # Verify the token with Clerk
        try:
            # Use the Sessions API to verify the token
            session = clerk_client.sessions.verify_session_token(token)
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Get user information
            user = clerk_client.users.get_user(user_id=session.user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Return user data in the format expected by the app
            return {
                "id": user.id,
                "email": user.email_addresses[0].email_address if user.email_addresses else None,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "clerk_user_id": user.id,
                "session_id": session.id
            }
            
        except ClerkAPIError as e:
            logger.error(f"Clerk API error: {e}")
            if e.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service error"
                )
                
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

async def get_current_user(user_data: Dict[str, Any] = Depends(verify_clerk_token)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    Compatible with existing code that expects user data
    """
    return user_data

async def get_current_user_id(user_data: Dict[str, Any] = Depends(verify_clerk_token)) -> str:
    """
    Dependency to get current user ID only
    """
    return user_data["id"]

def create_clerk_user_in_db(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or update user in local database based on Clerk user data
    This function should be called when a new user signs up via Clerk
    """
    # TODO: Implement database user creation/update logic
    # This would sync Clerk user data with your local user table
    pass

# Health check for Clerk service
async def clerk_health_check() -> Dict[str, str]:
    """
    Check if Clerk service is accessible
    """
    try:
        # Try to get organization list as a health check
        # This is a lightweight operation that verifies API connectivity
        clerk_client.organizations.list_organizations(limit=1)
        return {"status": "healthy", "service": "clerk"}
    except Exception as e:
        logger.error(f"Clerk health check failed: {e}")
        return {"status": "unhealthy", "service": "clerk", "error": str(e)}