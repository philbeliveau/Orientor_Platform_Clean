"""
Clerk Authentication Utilities
==============================

This module provides authentication utilities for Clerk integration,
including token verification, user session management, and database integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta

from ..models.user import User
from ..utils.database import get_db
from ..core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Clerk Configuration with Security Validation
CLERK_PUBLISHABLE_KEY = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_DOMAIN = os.getenv('NEXT_PUBLIC_CLERK_DOMAIN')

# Security Validation for Critical Configuration
if not CLERK_SECRET_KEY:
    logger.error("🚨 SECURITY: CLERK_SECRET_KEY is not configured - authentication will fail")
    raise ValueError("CLERK_SECRET_KEY environment variable is required")

if not CLERK_PUBLISHABLE_KEY:
    logger.error("🚨 SECURITY: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is not configured")
    raise ValueError("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY environment variable is required")

if not CLERK_DOMAIN:
    logger.error("🚨 SECURITY: NEXT_PUBLIC_CLERK_DOMAIN is not configured - JWKS validation will fail")
    raise ValueError("NEXT_PUBLIC_CLERK_DOMAIN environment variable is required")

# Validate Clerk domain format
if not CLERK_DOMAIN.endswith('.clerk.accounts.dev') and not CLERK_DOMAIN.endswith('.clerk.com'):
    logger.warning(f"⚠️ SECURITY: Unusual Clerk domain format: {CLERK_DOMAIN}")

CLERK_API_URL = f"https://api.clerk.com/v1"
CLERK_JWKS_URL = f"https://{CLERK_DOMAIN}/.well-known/jwks.json"

logger.info(f"✅ Clerk configuration validated successfully")
logger.info(f"📍 Clerk Domain: {CLERK_DOMAIN}")
logger.info(f"🔗 JWKS URL: {CLERK_JWKS_URL}")

# Cache for Clerk JWKS
CLERK_JWKS_CACHE = None
CLERK_JWKS_LAST_UPDATED = None

async def fetch_clerk_jwks() -> Dict:
    """Fetch Clerk JWKS keys with caching"""
    global CLERK_JWKS_CACHE, CLERK_JWKS_LAST_UPDATED
    
    # Use cached JWKS if recent (5 minute cache)
    if CLERK_JWKS_CACHE and CLERK_JWKS_LAST_UPDATED and \
       (datetime.now() - CLERK_JWKS_LAST_UPDATED) < timedelta(minutes=5):
        return CLERK_JWKS_CACHE
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(CLERK_JWKS_URL)
            response.raise_for_status()
            CLERK_JWKS_CACHE = response.json()
            CLERK_JWKS_LAST_UPDATED = datetime.now()
            return CLERK_JWKS_CACHE
    except Exception as e:
        logger.error(f"Failed to fetch Clerk JWKS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication tokens"
        )

async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verify a Clerk JWT token and return its payload"""
    try:
        # Get JWKS keys
        jwks = await fetch_clerk_jwks()
        
        # Decode token header to get kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header"
            )
        
        # Find the matching key
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No matching key found for token"
            )
        
        # Verify token
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLERK_PUBLISHABLE_KEY,
            issuer=f"https://{os.getenv('NEXT_PUBLIC_CLERK_DOMAIN')}"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from Clerk token.
    Creates/updates the user in local database if needed.
    """
    token = credentials.credentials
    
    try:
        # Verify Clerk token
        payload = await verify_clerk_token(token)
        
        # Extract user info from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get additional user info from Clerk API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CLERK_API_URL}/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            clerk_user = response.json()
        
        # Return combined user info
        return {
            "id": user_id,
            "email": clerk_user.get("email_addresses", [{}])[0].get("email_address"),
            "first_name": clerk_user.get("first_name"),
            "last_name": clerk_user.get("last_name"),
            "clerk_data": clerk_user,
            "__raw": token  # Include raw token for API forwarding
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Clerk API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch user details from Clerk"
        )
    except Exception as e:
        logger.error(f"User authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def clerk_health_check() -> Dict[str, Any]:
    """Check Clerk service health"""
    try:
        async with httpx.AsyncClient() as client:
            # Check JWKS endpoint
            jwks_response = await client.get(CLERK_JWKS_URL)
            jwks_response.raise_for_status()
            
            # Check API endpoint
            api_response = await client.get(
                f"{CLERK_API_URL}/health",
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
            )
            api_response.raise_for_status()
            
            return {
                "status": "healthy",
                "jwks": jwks_response.status_code == 200,
                "api": api_response.status_code == 200
            }
    except Exception as e:
        logger.error(f"Clerk health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def create_clerk_user_in_db(
    clerk_user: Dict[str, Any],
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Create or update a local database user record from Clerk user data.
    Returns the local user record if successful.
    """
    try:
        user_id = clerk_user.get("id")
        email = clerk_user.get("email")
        
        if not user_id or not email:
            logger.warning("Invalid Clerk user data for DB sync")
            return None
        
        # Check if user exists
        user = db.query(User).filter(User.clerk_user_id == user_id).first()
        
        if not user:
            # Create new user
            user = User(
                clerk_user_id=user_id,
                email=email,
                first_name=clerk_user.get("first_name", ""),
                last_name=clerk_user.get("last_name", ""),
                is_active=True
            )
            db.add(user)
        else:
            # Update existing user
            user.email = email
            user.first_name = clerk_user.get("first_name", user.first_name)
            user.last_name = clerk_user.get("last_name", user.last_name)
        
        db.commit()
        db.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "clerk_id": user.clerk_user_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to sync Clerk user with database: {str(e)}")
        return None

async def get_current_user_with_db_sync(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from Clerk token and return SQLAlchemy User object.
    This function bridges the gap between Clerk authentication and legacy router expectations.
    
    Returns:
        User: SQLAlchemy User object compatible with legacy routers
    """
    try:
        # Get Clerk user data
        clerk_user_data = await get_current_user(credentials, db)
        
        # Sync/create user in local database
        user_data = create_clerk_user_in_db(clerk_user_data["clerk_data"], db)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user with database"
            )
        
        # Return SQLAlchemy User object
        user = db.query(User).filter(User.id == user_data["id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database after sync"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"User authentication with DB sync error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_user_id_from_clerk_data(clerk_user_data: Dict[str, Any]) -> int:
    """
    Helper function to extract local database user ID from Clerk user data.
    Useful for routers that need the local database ID.
    """
    if "clerk_data" in clerk_user_data:
        # Get user by clerk_user_id
        clerk_id = clerk_user_data["id"]  # This is the Clerk ID
        from ..utils.database import get_db_session
        
        with get_db_session() as db:
            user = db.query(User).filter(User.clerk_user_id == clerk_id).first()
            return user.id if user else None
    return None
