"""JWT Token Management with Refresh Token Support"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
import jwt
from pydantic import BaseModel
import secrets
from passlib.context import CryptContext
import redis
from functools import wraps
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
SECRET_KEY = "your-secret-key-from-env"  # Should be loaded from environment
ALGORITHM = "HS256"
REFRESH_TOKEN_SALT = "refresh-token-salt"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    roles: list[str]
    permissions: list[str]
    token_type: str
    exp: datetime
    iat: datetime
    jti: Optional[str] = None  # JWT ID for blacklisting


class TokenPair(BaseModel):
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class JWTManager:
    """Manages JWT tokens with refresh capability"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.blacklist_prefix = "blacklist:token:"
        self.refresh_prefix = "refresh:token:"
        
    def create_access_token(
        self, 
        user_id: str, 
        email: str, 
        roles: list[str],
        permissions: list[str]
    ) -> str:
        """Create an access token"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jti = secrets.token_urlsafe(16)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "token_type": "access",
            "exp": expire,
            "iat": now,
            "jti": jti
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        jti = secrets.token_urlsafe(32)
        
        payload = {
            "user_id": user_id,
            "token_type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": jti
        }
        
        token = jwt.encode(payload, SECRET_KEY + REFRESH_TOKEN_SALT, algorithm=ALGORITHM)
        
        # Store refresh token in Redis with expiration
        if self.redis_client:
            key = f"{self.refresh_prefix}{user_id}:{jti}"
            self.redis_client.setex(
                key,
                timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                token
            )
        
        return token
    
    def create_token_pair(
        self,
        user_id: str,
        email: str,
        roles: list[str],
        permissions: list[str]
    ) -> TokenPair:
        """Create both access and refresh tokens"""
        access_token = self.create_access_token(user_id, email, roles, permissions)
        refresh_token = self.create_refresh_token(user_id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    
    def verify_access_token(self, token: str) -> TokenData:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is blacklisted
            if self.redis_client and payload.get("jti"):
                if self.redis_client.exists(f"{self.blacklist_prefix}{payload['jti']}"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked"
                    )
            
            return TokenData(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def verify_refresh_token(self, token: str) -> Dict:
        """Verify and decode refresh token"""
        try:
            payload = jwt.decode(
                token, 
                SECRET_KEY + REFRESH_TOKEN_SALT, 
                algorithms=[ALGORITHM]
            )
            
            # Verify refresh token exists in Redis
            if self.redis_client:
                user_id = payload.get("user_id")
                jti = payload.get("jti")
                key = f"{self.refresh_prefix}{user_id}:{jti}"
                
                if not self.redis_client.exists(key):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh token"
                    )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def refresh_access_token(
        self, 
        refresh_token: str,
        user_data: Dict  # Should contain email, roles, permissions
    ) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_refresh_token(refresh_token)
        
        return self.create_access_token(
            user_id=payload["user_id"],
            email=user_data["email"],
            roles=user_data["roles"],
            permissions=user_data["permissions"]
        )
    
    def revoke_token(self, token: str, token_type: str = "access"):
        """Revoke a token by adding to blacklist"""
        if not self.redis_client:
            return
        
        try:
            if token_type == "access":
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            else:
                payload = jwt.decode(
                    token, 
                    SECRET_KEY + REFRESH_TOKEN_SALT, 
                    algorithms=[ALGORITHM]
                )
            
            jti = payload.get("jti")
            if jti:
                # Calculate remaining time until expiration
                exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
                now = datetime.now(timezone.utc)
                ttl = int((exp - now).total_seconds())
                
                if ttl > 0:
                    key = f"{self.blacklist_prefix}{jti}"
                    self.redis_client.setex(key, ttl, "revoked")
                    
                    # If refresh token, also delete from storage
                    if token_type == "refresh":
                        user_id = payload.get("user_id")
                        refresh_key = f"{self.refresh_prefix}{user_id}:{jti}"
                        self.redis_client.delete(refresh_key)
        except jwt.InvalidTokenError:
            pass
    
    def revoke_all_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        if not self.redis_client:
            return
        
        # Find and delete all refresh tokens for user
        pattern = f"{self.refresh_prefix}{user_id}:*"
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)


# Dependency injection
jwt_manager = JWTManager()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Get current user from JWT token"""
    token = credentials.credentials
    return jwt_manager.verify_access_token(token)


def require_permissions(*required_permissions: str):
    """Decorator to check permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user: TokenData = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permissions
            user_permissions = set(current_user.permissions)
            required = set(required_permissions)
            
            if not required.issubset(user_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {required - user_permissions}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_roles(*required_roles: str):
    """Decorator to check roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user: TokenData = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check roles
            user_roles = set(current_user.roles)
            required = set(required_roles)
            
            if not required.intersection(user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required roles: {required}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator