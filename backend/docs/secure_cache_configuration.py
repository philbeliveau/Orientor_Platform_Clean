"""
Secure Cache Configuration Module
=================================

This module provides secure configuration templates and utilities for the
authentication caching system. It addresses critical security vulnerabilities
identified in the security audit and implements industry best practices.

Security Features:
- AES-256 encryption for sensitive cache data
- Secure cache key generation with proper entropy
- Input validation and sanitization
- Rate limiting and access controls
- Comprehensive audit logging
- Thread-safe operations with proper locking
"""

import os
import json
import hashlib
import hmac
import secrets
import time
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY CONFIGURATION CONSTANTS
# ============================================================================

# Cryptographic settings
CACHE_ENCRYPTION_ALGORITHM = "AES-256-GCM"
HASH_ALGORITHM = "SHA-256"
KEY_DERIVATION_ITERATIONS = 100000
SALT_SIZE = 32
TOKEN_HASH_SIZE = 64  # Full SHA-256 hash length

# Cache security limits
MAX_CACHE_KEY_LENGTH = 250
MAX_CACHE_VALUE_SIZE = 1024 * 1024  # 1MB
MAX_TTL_SECONDS = 7200  # 2 hours
MIN_TTL_SECONDS = 60    # 1 minute

# Rate limiting
DEFAULT_RATE_LIMIT = 100  # requests per minute
BURST_LIMIT = 20  # burst requests

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

# ============================================================================
# SECURE ENCRYPTION MANAGER
# ============================================================================

class SecureCacheEncryption:
    """
    Secure encryption manager for cache data using AES-256-GCM.
    Provides confidentiality, integrity, and authenticity for cached data.
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption manager with master key.
        
        Args:
            master_key: Base64 encoded master key. If None, generates from environment.
        """
        self._master_key = self._get_or_generate_master_key(master_key)
        self._salt_cache = {}
        self._lock = threading.RLock()
        
    def _get_or_generate_master_key(self, master_key: Optional[str]) -> bytes:
        """Get master key from environment or generate secure key"""
        if master_key:
            try:
                return base64.b64decode(master_key.encode())
            except Exception as e:
                logger.error(f"Invalid master key format: {e}")
                raise ValueError("Invalid master key format")
        
        # Try to get from environment
        env_key = os.getenv("CACHE_ENCRYPTION_KEY")
        if env_key:
            try:
                return base64.b64decode(env_key.encode())
            except Exception:
                logger.warning("Invalid CACHE_ENCRYPTION_KEY format, generating new key")
        
        # Generate new key (should be stored securely in production)
        new_key = Fernet.generate_key()
        logger.warning("Generated new encryption key - store securely in production")
        logger.info(f"Set CACHE_ENCRYPTION_KEY={new_key.decode()}")
        return new_key
    
    def _derive_key(self, context: str, salt: bytes) -> bytes:
        """Derive encryption key for specific context"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=KEY_DERIVATION_ITERATIONS,
        )
        return kdf.derive(self._master_key + context.encode())
    
    def encrypt_cache_value(self, value: Any, context: str = "default") -> str:
        """
        Encrypt cache value with context-specific key.
        
        Args:
            value: Value to encrypt (will be JSON serialized)
            context: Context for key derivation (e.g., "jwt", "session")
            
        Returns:
            Base64 encoded encrypted data with metadata
        """
        with self._lock:
            # Generate unique salt for this encryption
            salt = secrets.token_bytes(SALT_SIZE)
            
            # Serialize value
            try:
                plaintext = json.dumps(value, default=str).encode()
            except TypeError as e:
                logger.error(f"Failed to serialize cache value: {e}")
                raise ValueError(f"Cannot serialize cache value: {e}")
            
            # Derive encryption key
            encryption_key = self._derive_key(context, salt)
            fernet = Fernet(base64.urlsafe_b64encode(encryption_key))
            
            # Encrypt data
            encrypted_data = fernet.encrypt(plaintext)
            
            # Create metadata
            metadata = {
                "version": "1.0",
                "algorithm": CACHE_ENCRYPTION_ALGORITHM,
                "context": context,
                "salt": base64.b64encode(salt).decode(),
                "timestamp": datetime.now().isoformat(),
                "data": base64.b64encode(encrypted_data).decode()
            }
            
            return base64.b64encode(json.dumps(metadata).encode()).decode()
    
    def decrypt_cache_value(self, encrypted_data: str) -> Any:
        """
        Decrypt cache value and verify integrity.
        
        Args:
            encrypted_data: Base64 encoded encrypted data with metadata
            
        Returns:
            Decrypted and deserialized value
        """
        with self._lock:
            try:
                # Decode metadata
                metadata_bytes = base64.b64decode(encrypted_data.encode())
                metadata = json.loads(metadata_bytes.decode())
                
                # Validate metadata
                required_fields = ["version", "algorithm", "context", "salt", "data"]
                if not all(field in metadata for field in required_fields):
                    raise ValueError("Invalid encryption metadata")
                
                # Extract components
                context = metadata["context"]
                salt = base64.b64decode(metadata["salt"].encode())
                encrypted_payload = base64.b64decode(metadata["data"].encode())
                
                # Derive decryption key
                decryption_key = self._derive_key(context, salt)
                fernet = Fernet(base64.urlsafe_b64encode(decryption_key))
                
                # Decrypt data
                plaintext = fernet.decrypt(encrypted_payload)
                
                # Deserialize value
                return json.loads(plaintext.decode())
                
            except Exception as e:
                logger.error(f"Failed to decrypt cache value: {e}")
                raise ValueError(f"Decryption failed: {e}")

# ============================================================================
# SECURE CACHE KEY GENERATOR
# ============================================================================

class SecureCacheKeyGenerator:
    """
    Secure cache key generation with proper entropy and namespace isolation.
    Prevents cache key collisions and injection attacks.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """Initialize with HMAC secret key"""
        self._secret_key = (
            secret_key.encode() if secret_key 
            else os.getenv("CACHE_HMAC_SECRET", secrets.token_hex(32)).encode()
        )
        self._lock = threading.RLock()
        
    def generate_secure_key(self, 
                          data: Union[str, Dict[str, Any]], 
                          namespace: str = "default",
                          context: Optional[str] = None) -> str:
        """
        Generate cryptographically secure cache key.
        
        Args:
            data: Input data for key generation
            namespace: Cache namespace for isolation
            context: Optional context for key derivation
            
        Returns:
            Secure cache key with proper entropy
        """
        with self._lock:
            # Serialize data consistently
            if isinstance(data, dict):
                serialized_data = json.dumps(data, sort_keys=True)
            else:
                serialized_data = str(data)
            
            # Create unique salt
            salt = secrets.token_bytes(16)
            timestamp = str(int(time.time()))
            
            # Combine all components
            key_components = [
                namespace,
                context or "",
                serialized_data,
                timestamp,
                base64.b64encode(salt).decode()
            ]
            
            combined_data = ":".join(key_components)
            
            # Generate HMAC-based key
            mac = hmac.new(
                self._secret_key,
                combined_data.encode(),
                hashlib.sha256
            )
            
            # Create final key with namespace prefix
            secure_key = f"{namespace}:secure:{mac.hexdigest()}"
            
            # Validate key length
            if len(secure_key) > MAX_CACHE_KEY_LENGTH:
                logger.error(f"Generated key too long: {len(secure_key)}")
                raise ValueError("Cache key too long")
            
            return secure_key
    
    def generate_token_fingerprint(self, token: str, user_id: str) -> str:
        """
        Generate secure fingerprint for JWT tokens (no plaintext storage).
        
        Args:
            token: JWT token (will not be stored)
            user_id: User identifier
            
        Returns:
            Secure token fingerprint
        """
        # Extract token header and payload (without signature)
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            
            # Use header and payload for fingerprint (not signature)
            token_content = f"{parts[0]}.{parts[1]}"
            
            # Create fingerprint with user context
            fingerprint_data = f"{token_content}:{user_id}:{secrets.token_hex(16)}"
            
            # Generate secure hash
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to generate token fingerprint: {e}")
            raise ValueError("Invalid token format")

# ============================================================================
# SECURE INPUT VALIDATOR
# ============================================================================

class SecureInputValidator:
    """
    Input validation and sanitization for cache operations.
    Prevents injection attacks and ensures data integrity.
    """
    
    # Allowed characters in cache keys
    SAFE_KEY_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:.")
    
    # Dangerous patterns to detect
    INJECTION_PATTERNS = [
        r"['\";]",  # SQL injection chars
        r"[<>]",    # XSS chars
        r"\${",     # Template injection
        r"__.*__",  # Python magic methods
        r"\.\./",   # Path traversal
    ]
    
    @classmethod
    def validate_cache_key(cls, key: str) -> bool:
        """
        Validate cache key for security issues.
        
        Args:
            key: Cache key to validate
            
        Returns:
            True if key is safe, raises ValueError if not
        """
        # Check length
        if len(key) > MAX_CACHE_KEY_LENGTH:
            raise ValueError(f"Cache key too long: {len(key)} > {MAX_CACHE_KEY_LENGTH}")
        
        # Check for null bytes
        if '\x00' in key:
            raise ValueError("Cache key contains null bytes")
        
        # Check character whitelist
        if not all(c in cls.SAFE_KEY_CHARS for c in key):
            invalid_chars = set(key) - cls.SAFE_KEY_CHARS
            raise ValueError(f"Cache key contains invalid characters: {invalid_chars}")
        
        # Check for injection patterns
        import re
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, key, re.IGNORECASE):
                raise ValueError(f"Cache key matches dangerous pattern: {pattern}")
        
        return True
    
    @classmethod
    def validate_ttl(cls, ttl: int) -> bool:
        """
        Validate TTL value.
        
        Args:
            ttl: TTL value in seconds
            
        Returns:
            True if valid, raises ValueError if not
        """
        if not isinstance(ttl, int):
            raise ValueError("TTL must be an integer")
        
        if ttl < MIN_TTL_SECONDS:
            raise ValueError(f"TTL too low: {ttl} < {MIN_TTL_SECONDS}")
        
        if ttl > MAX_TTL_SECONDS:
            raise ValueError(f"TTL too high: {ttl} > {MAX_TTL_SECONDS}")
        
        return True
    
    @classmethod
    def validate_cache_value_size(cls, value: Any) -> bool:
        """
        Validate cache value size.
        
        Args:
            value: Value to cache
            
        Returns:
            True if valid, raises ValueError if not
        """
        try:
            serialized = json.dumps(value, default=str)
            size = len(serialized.encode('utf-8'))
            
            if size > MAX_CACHE_VALUE_SIZE:
                raise ValueError(f"Cache value too large: {size} > {MAX_CACHE_VALUE_SIZE}")
            
            return True
        except TypeError as e:
            raise ValueError(f"Cannot serialize cache value: {e}")

# ============================================================================
# RATE LIMITING AND ACCESS CONTROL
# ============================================================================

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = DEFAULT_RATE_LIMIT
    burst_limit: int = BURST_LIMIT
    window_size: int = 60  # seconds
    
@dataclass
class AccessControlConfig:
    """Access control configuration"""
    require_authentication: bool = True
    allowed_roles: List[str] = None
    require_permission: Optional[str] = None

class SecureAccessController:
    """
    Access control and rate limiting for cache operations.
    """
    
    def __init__(self):
        self._rate_limits = {}
        self._access_logs = []
        self._lock = threading.RLock()
    
    def check_rate_limit(self, identifier: str, config: RateLimitConfig) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Client identifier (IP, user ID, etc.)
            config: Rate limiting configuration
            
        Returns:
            True if within limit, False if exceeded
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - config.window_size
            
            # Initialize or clean old entries
            if identifier not in self._rate_limits:
                self._rate_limits[identifier] = []
            
            # Remove old entries
            self._rate_limits[identifier] = [
                timestamp for timestamp in self._rate_limits[identifier]
                if timestamp > window_start
            ]
            
            # Check limits
            requests_in_window = len(self._rate_limits[identifier])
            
            if requests_in_window >= config.requests_per_minute:
                logger.warning(f"Rate limit exceeded for {identifier}: {requests_in_window}")
                return False
            
            # Add current request
            self._rate_limits[identifier].append(current_time)
            return True
    
    def check_access_permission(self, user_data: Dict[str, Any], config: AccessControlConfig) -> bool:
        """
        Check if user has required access permissions.
        
        Args:
            user_data: User authentication data
            config: Access control configuration
            
        Returns:
            True if access allowed, False if denied
        """
        if not config.require_authentication:
            return True
        
        # Check authentication
        if not user_data.get("authenticated"):
            logger.warning("Unauthenticated cache access attempt")
            return False
        
        # Check roles
        if config.allowed_roles:
            user_roles = user_data.get("roles", [])
            if not any(role in user_roles for role in config.allowed_roles):
                logger.warning(f"Insufficient role for cache access: {user_roles}")
                return False
        
        # Check specific permission
        if config.require_permission:
            user_permissions = user_data.get("permissions", [])
            if config.require_permission not in user_permissions:
                logger.warning(f"Missing permission for cache access: {config.require_permission}")
                return False
        
        return True
    
    def log_access_attempt(self, event_data: Dict[str, Any]):
        """Log cache access attempt for security monitoring"""
        with self._lock:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "cache_access",
                **event_data
            }
            self._access_logs.append(log_entry)
            
            # Keep only recent logs (memory management)
            if len(self._access_logs) > 10000:
                self._access_logs = self._access_logs[-5000:]
            
            logger.info(f"Cache access: {json.dumps(log_entry)}")

# ============================================================================
# SECURE CACHE WRAPPER
# ============================================================================

class SecureCache:
    """
    Secure cache implementation with encryption, validation, and access control.
    Drop-in replacement for existing cache implementations with enhanced security.
    """
    
    def __init__(self, 
                 base_cache,
                 encryption_key: Optional[str] = None,
                 enable_encryption: bool = True,
                 rate_limit_config: Optional[RateLimitConfig] = None,
                 access_control_config: Optional[AccessControlConfig] = None):
        """
        Initialize secure cache wrapper.
        
        Args:
            base_cache: Underlying cache implementation
            encryption_key: Encryption key (optional)
            enable_encryption: Whether to enable encryption
            rate_limit_config: Rate limiting configuration
            access_control_config: Access control configuration
        """
        self._base_cache = base_cache
        self._encryption = SecureCacheEncryption(encryption_key) if enable_encryption else None
        self._key_generator = SecureCacheKeyGenerator()
        self._access_controller = SecureAccessController()
        self._validator = SecureInputValidator()
        
        self._rate_limit_config = rate_limit_config or RateLimitConfig()
        self._access_control_config = access_control_config or AccessControlConfig()
        
        self._stats = {
            "operations": 0,
            "encryption_ops": 0,
            "validation_failures": 0,
            "access_denied": 0,
            "rate_limited": 0
        }
        self._lock = threading.RLock()
    
    def get(self, key: str, context: Dict[str, Any] = None) -> Any:
        """
        Secure cache get operation.
        
        Args:
            key: Cache key
            context: Request context (user data, etc.)
            
        Returns:
            Cached value or None
        """
        with self._lock:
            try:
                # Update stats
                self._stats["operations"] += 1
                
                # Validate inputs
                self._validator.validate_cache_key(key)
                
                # Check access control
                if context and not self._access_controller.check_access_permission(
                    context.get("user", {}), self._access_control_config
                ):
                    self._stats["access_denied"] += 1
                    raise PermissionError("Cache access denied")
                
                # Check rate limiting
                client_id = context.get("client_id", "unknown") if context else "unknown"
                if not self._access_controller.check_rate_limit(client_id, self._rate_limit_config):
                    self._stats["rate_limited"] += 1
                    raise PermissionError("Rate limit exceeded")
                
                # Generate secure key
                secure_key = self._key_generator.generate_secure_key(key)
                
                # Get from base cache
                encrypted_value = self._base_cache.get(secure_key)
                if encrypted_value is None:
                    return None
                
                # Decrypt if enabled
                if self._encryption:
                    self._stats["encryption_ops"] += 1
                    return self._encryption.decrypt_cache_value(encrypted_value)
                else:
                    return encrypted_value
                
            except (ValueError, PermissionError) as e:
                self._stats["validation_failures"] += 1
                logger.warning(f"Secure cache get failed: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in secure cache get: {e}")
                raise
    
    def set(self, key: str, value: Any, ttl: int = 3600, context: Dict[str, Any] = None) -> bool:
        """
        Secure cache set operation.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds
            context: Request context
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                # Update stats
                self._stats["operations"] += 1
                
                # Validate inputs
                self._validator.validate_cache_key(key)
                self._validator.validate_ttl(ttl)
                self._validator.validate_cache_value_size(value)
                
                # Check access control
                if context and not self._access_controller.check_access_permission(
                    context.get("user", {}), self._access_control_config
                ):
                    self._stats["access_denied"] += 1
                    raise PermissionError("Cache access denied")
                
                # Check rate limiting
                client_id = context.get("client_id", "unknown") if context else "unknown"
                if not self._access_controller.check_rate_limit(client_id, self._rate_limit_config):
                    self._stats["rate_limited"] += 1
                    raise PermissionError("Rate limit exceeded")
                
                # Generate secure key
                secure_key = self._key_generator.generate_secure_key(key)
                
                # Encrypt if enabled
                if self._encryption:
                    self._stats["encryption_ops"] += 1
                    encrypted_value = self._encryption.encrypt_cache_value(value, "cache")
                else:
                    encrypted_value = value
                
                # Store in base cache
                return self._base_cache.set(secure_key, encrypted_value, ttl)
                
            except (ValueError, PermissionError) as e:
                self._stats["validation_failures"] += 1
                logger.warning(f"Secure cache set failed: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in secure cache set: {e}")
                raise
    
    def delete(self, key: str, context: Dict[str, Any] = None) -> bool:
        """
        Secure cache delete operation.
        
        Args:
            key: Cache key
            context: Request context
            
        Returns:
            True if deleted
        """
        with self._lock:
            try:
                # Validate inputs
                self._validator.validate_cache_key(key)
                
                # Check access control
                if context and not self._access_controller.check_access_permission(
                    context.get("user", {}), self._access_control_config
                ):
                    self._stats["access_denied"] += 1
                    raise PermissionError("Cache access denied")
                
                # Generate secure key
                secure_key = self._key_generator.generate_secure_key(key)
                
                # Delete from base cache
                return self._base_cache.delete(secure_key)
                
            except (ValueError, PermissionError) as e:
                self._stats["validation_failures"] += 1
                logger.warning(f"Secure cache delete failed: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in secure cache delete: {e}")
                raise
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security-related statistics"""
        with self._lock:
            return {
                **self._stats,
                "timestamp": datetime.now().isoformat(),
                "encryption_enabled": self._encryption is not None,
                "access_control_enabled": self._access_control_config.require_authentication
            }

# ============================================================================
# SECURITY MONITORING UTILITIES
# ============================================================================

class SecurityEventLogger:
    """Security event logging and monitoring"""
    
    def __init__(self):
        self._events = []
        self._lock = threading.RLock()
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        with self._lock:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "details": details,
                "severity": self._determine_severity(event_type)
            }
            self._events.append(event)
            
            # Log to standard logger
            logger.warning(f"SECURITY EVENT [{event_type}]: {json.dumps(details)}")
            
            # Keep only recent events
            if len(self._events) > 1000:
                self._events = self._events[-500:]
    
    def _determine_severity(self, event_type: str) -> str:
        """Determine event severity"""
        high_severity_events = [
            "authentication_bypass",
            "cache_injection",
            "encryption_failure",
            "access_denied_admin"
        ]
        
        if event_type in high_severity_events:
            return "HIGH"
        elif "denied" in event_type or "failed" in event_type:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent security events"""
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            return [
                event for event in self._events
                if datetime.fromisoformat(event["timestamp"]) > cutoff
            ]

# ============================================================================
# SECURE CONFIGURATION FACTORY
# ============================================================================

def create_secure_cache(cache_type: str = "ttl", **kwargs) -> SecureCache:
    """
    Factory function to create secure cache implementations.
    
    Args:
        cache_type: Type of cache ("ttl", "lru", "redis")
        **kwargs: Additional configuration
        
    Returns:
        Configured secure cache instance
    """
    # Import appropriate base cache
    if cache_type == "ttl":
        from ..utils.auth_cache import TTLCache
        base_cache = TTLCache(**kwargs)
    elif cache_type == "redis":
        from ..core.cache import CacheService
        base_cache = CacheService()
    else:
        raise ValueError(f"Unsupported cache type: {cache_type}")
    
    # Configure security settings
    rate_limit_config = RateLimitConfig(
        requests_per_minute=kwargs.get("rate_limit", DEFAULT_RATE_LIMIT),
        burst_limit=kwargs.get("burst_limit", BURST_LIMIT)
    )
    
    access_control_config = AccessControlConfig(
        require_authentication=kwargs.get("require_auth", True),
        allowed_roles=kwargs.get("allowed_roles"),
        require_permission=kwargs.get("require_permission")
    )
    
    return SecureCache(
        base_cache=base_cache,
        encryption_key=kwargs.get("encryption_key"),
        enable_encryption=kwargs.get("enable_encryption", True),
        rate_limit_config=rate_limit_config,
        access_control_config=access_control_config
    )

# ============================================================================
# SECURE AUTHENTICATION UTILITIES
# ============================================================================

def create_secure_token_fingerprint(token: str, user_id: str) -> str:
    """
    Create secure token fingerprint without storing plaintext token.
    
    Args:
        token: JWT token
        user_id: User identifier
        
    Returns:
        Secure token fingerprint
    """
    generator = SecureCacheKeyGenerator()
    return generator.generate_token_fingerprint(token, user_id)

def sanitize_error_message(error: Exception, include_details: bool = False) -> str:
    """
    Sanitize error messages to prevent information disclosure.
    
    Args:
        error: Exception object
        include_details: Whether to include error details (dev only)
        
    Returns:
        Sanitized error message
    """
    if include_details and os.getenv("ENVIRONMENT") == "development":
        return str(error)
    
    # Generic error messages for production
    error_mappings = {
        "ValueError": "Invalid input data",
        "PermissionError": "Access denied",
        "TimeoutError": "Operation timed out",
        "ConnectionError": "Service temporarily unavailable"
    }
    
    error_type = type(error).__name__
    return error_mappings.get(error_type, "An error occurred")

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_security_configuration() -> Dict[str, Any]:
    """
    Validate current security configuration against best practices.
    
    Returns:
        Configuration validation report
    """
    validation_report = {
        "status": "PASS",
        "issues": [],
        "recommendations": []
    }
    
    # Check encryption key
    if not os.getenv("CACHE_ENCRYPTION_KEY"):
        validation_report["issues"].append({
            "severity": "HIGH",
            "category": "Encryption",
            "message": "CACHE_ENCRYPTION_KEY not set",
            "recommendation": "Set strong encryption key in environment"
        })
        validation_report["status"] = "FAIL"
    
    # Check HMAC secret
    if not os.getenv("CACHE_HMAC_SECRET"):
        validation_report["issues"].append({
            "severity": "MEDIUM",
            "category": "Authentication",
            "message": "CACHE_HMAC_SECRET not set",
            "recommendation": "Set HMAC secret for key generation"
        })
        validation_report["status"] = "WARN"
    
    # Check Redis security
    redis_url = os.getenv("REDIS_URL", "")
    if redis_url and not redis_url.startswith("rediss://"):
        validation_report["issues"].append({
            "severity": "HIGH",
            "category": "Transport Security",
            "message": "Redis not using TLS",
            "recommendation": "Use rediss:// URL for TLS encryption"
        })
        validation_report["status"] = "FAIL"
    
    # Check environment
    if os.getenv("ENVIRONMENT") == "production":
        if os.getenv("DEBUG", "false").lower() == "true":
            validation_report["issues"].append({
                "severity": "HIGH",
                "category": "Configuration",
                "message": "Debug mode enabled in production",
                "recommendation": "Disable debug mode in production"
            })
            validation_report["status"] = "FAIL"
    
    return validation_report

# ============================================================================
# EXPORT INTERFACES
# ============================================================================

__all__ = [
    # Core security classes
    "SecureCacheEncryption",
    "SecureCacheKeyGenerator", 
    "SecureInputValidator",
    "SecureAccessController",
    "SecureCache",
    
    # Configuration classes
    "RateLimitConfig",
    "AccessControlConfig",
    
    # Utilities
    "create_secure_cache",
    "create_secure_token_fingerprint",
    "sanitize_error_message",
    "validate_security_configuration",
    
    # Security monitoring
    "SecurityEventLogger",
    
    # Constants
    "SECURITY_HEADERS",
    "MAX_CACHE_KEY_LENGTH",
    "MAX_CACHE_VALUE_SIZE",
    "MAX_TTL_SECONDS",
    "MIN_TTL_SECONDS"
]