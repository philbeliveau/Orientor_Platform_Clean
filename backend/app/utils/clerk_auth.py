"""
Clerk authentication utilities for FastAPI backend
"""
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import clerk_backend_api as clerk
from clerk_backend_api.models import ClerkErrors
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
            session = clerk_client.sessions.verify_token(token)
            
            if not session or not hasattr(session, 'user_id'):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Get user information
            user = clerk_client.users.get(user_id=session.user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Safely extract email address
            email = None
            if user.email_addresses and len(user.email_addresses) > 0:
                email = user.email_addresses[0].email_address
            
            # Return user data in the format expected by the app
            return {
                "id": user.id,
                "email": email,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "username": user.username or "",
                "clerk_user_id": user.id,
                "session_id": session.id if hasattr(session, 'id') else None
            }
            
        except ClerkErrors as e:
            logger.error(f"Clerk API error: {e}")
            if hasattr(e, 'status_code'):
                if e.status_code == 401 or e.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                elif e.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Authentication service error"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification failed"
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

def create_clerk_user_in_db(user_data: Dict[str, Any], db) -> Dict[str, Any]:
    """
    Create or update user in local database based on Clerk user data
    This function should be called when a new user signs up via Clerk
    """
    from sqlalchemy.orm import Session
    from ..models.user import User
    
    try:
        # Check if user already exists by clerk_user_id
        existing_user = db.query(User).filter(User.clerk_user_id == user_data["id"]).first()
        
        if existing_user:
            # Update existing user
            existing_user.email = user_data.get("email", existing_user.email)
            db.commit()
            db.refresh(existing_user)
            logger.info(f"Updated existing user with Clerk ID: {user_data['id']}")
            return {
                "id": existing_user.id,
                "email": existing_user.email,
                "clerk_user_id": existing_user.clerk_user_id,
                "created_at": existing_user.created_at,
                "onboarding_completed": existing_user.onboarding_completed
            }
        else:
            # Create new user
            new_user = User(
                email=user_data.get("email", ""),
                clerk_user_id=user_data["id"],
                hashed_password=None,  # Clerk handles authentication
                onboarding_completed=False
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Created new user with Clerk ID: {user_data['id']}")
            
            return {
                "id": new_user.id,
                "email": new_user.email,
                "clerk_user_id": new_user.clerk_user_id,
                "created_at": new_user.created_at,
                "onboarding_completed": new_user.onboarding_completed
            }
            
    except Exception as e:
        logger.error(f"Error creating/updating user in database: {e}")
        db.rollback()
        raise e

# Health check for Clerk service
async def clerk_health_check() -> Dict[str, str]:
    """
    Check if Clerk service is accessible
    """
    try:
        # Check if Clerk secret key is configured
        if not os.getenv("CLERK_SECRET_KEY"):
            logger.warning("CLERK_SECRET_KEY not configured")
            return {"status": "unhealthy", "service": "clerk", "error": "CLERK_SECRET_KEY not configured"}
        
        # Try to access Clerk API with a lightweight operation
        # Using users endpoint to verify API connectivity
        clerk_client.users.list()
        return {"status": "healthy", "service": "clerk"}
    except Exception as e:
        logger.error(f"Clerk health check failed: {e}")
        return {"status": "unhealthy", "service": "clerk", "error": str(e)}