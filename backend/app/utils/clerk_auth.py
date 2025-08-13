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
import jwt
from datetime import datetime, timedelta
from prisma import Prisma

from ..models.user import User
from ..utils.prisma_client import get_prisma_client
from ..core.config import settings
from .auth_cache_clean import (
    verify_clerk_token_cached,
    get_jwks_cache,
    cache_health_check
)

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

# Legacy JWKS cache - replaced by auth_cache.py
# These variables are maintained for backward compatibility but are no longer used
CLERK_JWKS_CACHE = None
CLERK_JWKS_LAST_UPDATED = None

async def fetch_clerk_jwks() -> Dict:
    """Fetch Clerk JWKS keys with advanced caching (Legacy wrapper)"""
    logger.info("🔄 Using legacy JWKS fetch - redirecting to advanced cache")
    jwks_cache = get_jwks_cache()
    return await jwks_cache.get_jwks()

async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verify a Clerk JWT token and return its payload (Legacy wrapper)"""
    logger.info("🔄 Using legacy token verification - redirecting to cached version")
    return await verify_clerk_token_cached(token)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_prisma_client)
) -> Dict[str, Any]:
    """
    Get current authenticated user from Clerk token (Legacy wrapper).
    Creates/updates the user in local database if needed.
    
    Note: This function now uses the advanced caching system from auth_cache.py
    """
    logger.info("🔄 Using legacy get_current_user - redirecting to cached version")
    from .auth_cache_clean import get_request_cache
    # Simple cached user fetching without over-engineering
    token = credentials.credentials
    
    # Use request cache for deduplication within same request
    request_cache = get_request_cache()
    cache_key = f"user_fetch:{hash(token)}"
    cached_result = request_cache.get(cache_key)
    
    if cached_result is not None:
        logger.debug("🎯 Request cache hit for user fetch")
        return cached_result
    
    try:
        # Verify token with caching
        payload = await verify_clerk_token_cached(token)
        
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
                f"https://api.clerk.com/v1/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            clerk_user = response.json()
        
        # Prepare user data
        user_data = {
            "id": user_id,
            "email": clerk_user.get("email_addresses", [{}])[0].get("email_address"),
            "first_name": clerk_user.get("first_name"),
            "last_name": clerk_user.get("last_name"),
            "clerk_data": clerk_user,
            "__raw": token
        }
        
        # Cache in request cache
        request_cache.set(cache_key, user_data)
        logger.debug("💾 User data cached in request cache")
        
        return user_data
        
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
    """Check Clerk service health with simple cache monitoring"""
    try:
        # Check JWKS endpoint through cache
        jwks_cache = get_jwks_cache()
        await jwks_cache.get_jwks()
        
        # Get basic cache health
        cache_health = await cache_health_check()
        
        return {
            "status": "healthy" if cache_health["status"] == "healthy" else "degraded",
            "clerk_jwks": "accessible",
            "cache_system": cache_health
        }
    except Exception as e:
        logger.error(f"Clerk health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def create_clerk_user_in_db(
    clerk_user_data: Dict[str, Any],
    db: Prisma
) -> Optional[Dict[str, Any]]:
    """
    Create or update user in local database from Clerk data
    Handles migration from old JWT users and ensures user profile creation
    """
    try:
        from ..models.user_profile import UserProfile  # Import here to avoid circular imports
        
        clerk_user_id = clerk_user_data.get("id")
        if not clerk_user_id:
            logger.error("No Clerk user ID in data")
            return None
        
        # Extract email - handle different Clerk response formats
        email = None
        if "email_addresses" in clerk_user_data:
            email_list = clerk_user_data.get("email_addresses", [])
            if email_list and len(email_list) > 0:
                email = email_list[0].get("email_address")
        elif "email" in clerk_user_data:
            email = clerk_user_data.get("email")
        
        if not email:
            logger.error(f"No email found for Clerk user {clerk_user_id}")
            return None
        
        # First try to find user by clerk_user_id
        existing_user = await db.users.find_first(where={"clerk_user_id": clerk_user_id})
        
        # Fallback to email lookup if not found by clerk_user_id
        if not existing_user:
            existing_user = await db.users.find_first(where={"email": email})
        
        if existing_user:
            # Update existing user with Clerk ID
            if not existing_user.clerk_user_id:
                logger.info(f"Migrating user {email} to Clerk ID {clerk_user_id}")
            
            # Update user info using Prisma
            existing_user = await db.users.update(
                where={"id": existing_user.id},
                data={
                    "clerk_user_id": clerk_user_id,
                    "first_name": clerk_user_data.get("first_name") or existing_user.first_name,
                    "last_name": clerk_user_data.get("last_name") or existing_user.last_name
                }
            )
            
            # Ensure user profile exists (AWAIT the coroutine)
            await ensure_user_profile_exists(existing_user, db)
            
            return {
                "id": existing_user.id,
                "email": existing_user.email,
                "clerk_user_id": existing_user.clerk_user_id
            }
        
        # Create new user
        logger.info(f"Creating new user from Clerk: {email}")
        new_user = await db.users.create(
            data={
                "clerk_user_id": clerk_user_id,
                "email": email,
                "first_name": clerk_user_data.get("first_name"),
                "last_name": clerk_user_data.get("last_name")
            }
        )
        
        # Create associated user profile
        await ensure_user_profile_exists(new_user, db)
        logger.info(f"✅ Created user and profile for {email} (ID: {new_user.id})")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "clerk_user_id": new_user.clerk_user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to create/update user in DB: {str(e)}")
        return None

async def ensure_user_profile_exists(user, db: Prisma) -> None:
    """
    Ensure a user profile exists for the given user.
    Creates one if it doesn't exist.
    """
    try:
        from ..models.user_profile import UserProfile  # Import here to avoid circular imports
        
        # Check if user profile already exists
        existing_profile = await db.user_profiles.find_first(where={"user_id": user.id})
        
        if not existing_profile:
            # Create new user profile
            logger.info(f"Creating user profile for user ID {user.id}")
            new_profile = await db.user_profiles.create(
                data={
                    "user_id": user.id,
                    "name": f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
                    # Set default values that won't cause issues
                    "age": None,
                    "sex": None,
                    "major": None,
                    "year": None,
                    "gpa": None,
                    "hobbies": None,
                    "country": None,
                    "state_province": None,
                    "unique_quality": None,
                    "story": None,
                    "favorite_movie": None,
                    "favorite_book": None,
                    "favorite_celebrities": None,
                    "learning_style": None,
                    "interests": None,
                    "job_title": None,
                    "industry": None,
                    "years_experience": None,
                    "education_level": None,
                    "career_goals": None,
                    "skills": [],  # Empty array for ARRAY(String)
                    "personal_analysis": None
                }
            )
            logger.info(f"✅ Created user profile for user ID {user.id}")
        else:
            logger.debug(f"User profile already exists for user ID {user.id}")
            
    except Exception as e:
        logger.error(f"Failed to create user profile for user ID {user.id}: {str(e)}")
        raise

async def get_current_user_with_db_sync(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_prisma_client)
) -> User:
    """
    Get current authenticated user from Clerk token and return SQLAlchemy User object.
    This function bridges the gap between Clerk authentication and legacy router expectations.
    
    Now uses the advanced caching system for improved performance.
    
    Returns:
        User: SQLAlchemy User object compatible with legacy routers
    """
    try:
        # Get Clerk user data using cached authentication
        from .auth_cache import get_request_cache, get_current_user_cached
        request_cache = get_request_cache()
        clerk_user_data = await get_current_user_cached(credentials, db, request_cache)
        
        # Check if we have the database user ID cached
        db_user_cache_key = f"db_user:{clerk_user_data['id']}"
        cached_user = request_cache.get(db_user_cache_key)
        
        if cached_user is not None:
            logger.debug("🎯 Database user cache hit")
            return cached_user
        
        # Sync/create user in local database
        user_data = await create_clerk_user_in_db(clerk_user_data["clerk_data"], db)
        
        if not user_data:
            logger.error("Failed to create user in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user with database"
            )
        
        # Return User object
        user = await db.users.find_first(where={"id": user_data["id"]})
        if not user:
            logger.error(f"User not found in database after sync: {user_data['id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database after sync"
            )
        
        # Verify clerk_user_id matches
        if user.clerk_user_id != clerk_user_data["id"]:
            logger.error(f"User ID mismatch: DB={user.clerk_user_id} vs Clerk={clerk_user_data['id']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID mismatch"
            )
        
        # Cache the database user for this request
        request_cache.set(db_user_cache_key, user)
        logger.debug(f"💾 Database user cached: {user.id}")
            
        return user
        
    except HTTPException:
        raise  # Re-raise existing HTTP exceptions
    except Exception as e:
        logger.error(f"User authentication with DB sync error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_user_id_from_clerk_data(clerk_user_data: Dict[str, Any]) -> int:
    """
    Helper function to extract local database user ID from Clerk user data.
    Useful for routers that need the local database ID.
    """
    if "clerk_data" in clerk_user_data:
        # Get user by clerk_user_id
        clerk_id = clerk_user_data["id"]  # This is the Clerk ID
        from ..utils.prisma_client import get_prisma
        
        async with get_prisma() as db:
            user = await db.users.find_first(where={"clerk_user_id": clerk_id})
            return user.id if user else None
    return None

async def get_database_user_id(clerk_user_id: str, db: Prisma) -> int:
    """
    Convert Clerk user ID to database user ID, ensuring user exists.
    
    Args:
        clerk_user_id: The Clerk user ID (string)
        db: Database session
        
    Returns:
        Integer database user ID
        
    Raises:
        HTTPException: If user not found in database
    """
    try:
        user = await db.users.find_first(where={"clerk_user_id": clerk_user_id})
        if not user:
            logger.error(f"User not found in database for Clerk ID: {clerk_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found in database for Clerk ID: {clerk_user_id}"
            )
        return user.id
    except Exception as e:
        logger.error(f"Error resolving Clerk user ID to database ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve user ID"
        )

async def get_database_user_id_sync(clerk_user_id: str) -> int:
    """
    Async version of get_database_user_id for services.
    
    Args:
        clerk_user_id: The Clerk user ID (string)
        
    Returns:
        Integer database user ID
        
    Raises:
        HTTPException: If user not found in database
    """
    try:
        from .prisma_client import get_prisma_client
        db = await get_prisma_client()
        user = await db.users.find_first(where={"clerk_user_id": clerk_user_id})
        if not user:
            logger.error(f"User not found in database for Clerk ID: {clerk_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found in database for Clerk ID: {clerk_user_id}"
            )
        return user.id
    except Exception as e:
        logger.error(f"Error resolving Clerk user ID to database ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve user ID"
        )
