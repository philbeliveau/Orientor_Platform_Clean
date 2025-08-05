"""Authentication routes with refresh token support"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from .jwt_manager import jwt_manager, get_current_user, TokenData, TokenPair
from .rbac import rbac_manager, Role, Permission
from .rate_limiter import RateLimiter, rate_limit

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Rate limiters
login_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
refresh_limiter = RateLimiter(max_requests=10, window_seconds=3600)  # 10 refreshes per hour


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.post("/login", response_model=TokenResponse)
@rate_limit(login_limiter)
async def login(request: Request, login_data: LoginRequest):
    """
    Login endpoint with rate limiting
    
    Returns access and refresh tokens
    """
    # TODO: Implement actual user authentication
    # This is a placeholder - integrate with your user service
    
    # Mock user data - replace with actual database lookup
    user = {
        "id": "user123",
        "email": login_data.email,
        "roles": [Role.USER],
        "is_active": True
    }
    
    # Verify password (placeholder)
    # if not verify_password(login_data.password, user.password_hash):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid credentials"
    #     )
    
    # Get user permissions based on roles
    permissions = list(rbac_manager.get_user_permissions(user["roles"]))
    
    # Create token pair
    token_pair = jwt_manager.create_token_pair(
        user_id=user["id"],
        email=user["email"],
        roles=user["roles"],
        permissions=[p.value for p in permissions]
    )
    
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
        user={
            "id": user["id"],
            "email": user["email"],
            "roles": user["roles"],
            "permissions": [p.value for p in permissions]
        }
    )


@router.post("/refresh", response_model=TokenResponse)
@rate_limit(refresh_limiter)
async def refresh_token(request: Request, refresh_data: RefreshRequest):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = jwt_manager.verify_refresh_token(refresh_data.refresh_token)
    
    # TODO: Fetch current user data from database
    # This ensures we get the latest roles/permissions
    user = {
        "id": payload["user_id"],
        "email": "user@example.com",  # Fetch from DB
        "roles": [Role.USER],  # Fetch from DB
    }
    
    # Get current permissions
    permissions = list(rbac_manager.get_user_permissions(user["roles"]))
    
    # Create new access token
    new_access_token = jwt_manager.refresh_access_token(
        refresh_token=refresh_data.refresh_token,
        user_data={
            "email": user["email"],
            "roles": user["roles"],
            "permissions": [p.value for p in permissions]
        }
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_data.refresh_token,  # Return same refresh token
        expires_in=jwt_manager.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user["id"],
            "email": user["email"],
            "roles": user["roles"],
            "permissions": [p.value for p in permissions]
        }
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Logout endpoint - revokes tokens
    """
    # Revoke access token
    jwt_manager.revoke_token(credentials.credentials, token_type="access")
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_devices(current_user: TokenData = Depends(get_current_user)):
    """
    Logout from all devices - revokes all user tokens
    """
    jwt_manager.revoke_all_user_tokens(current_user.user_id)
    
    return {"message": "Successfully logged out from all devices"}


@router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    """
    Register new user
    """
    # TODO: Implement user registration
    # This should create user in database
    
    # Mock implementation
    new_user = {
        "id": "new_user_id",
        "email": register_data.email,
        "roles": [Role.USER],  # Default role
    }
    
    # Get permissions for default role
    permissions = list(rbac_manager.get_user_permissions(new_user["roles"]))
    
    # Create token pair
    token_pair = jwt_manager.create_token_pair(
        user_id=new_user["id"],
        email=new_user["email"],
        roles=new_user["roles"],
        permissions=[p.value for p in permissions]
    )
    
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
        user={
            "id": new_user["id"],
            "email": new_user["email"],
            "roles": new_user["roles"],
            "permissions": [p.value for p in permissions]
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user information from token
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "roles": current_user.roles,
        "permissions": current_user.permissions,
        "token_expires": current_user.exp
    }


@router.post("/verify")
async def verify_token(current_user: TokenData = Depends(get_current_user)):
    """
    Verify if token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "expires": current_user.exp
    }