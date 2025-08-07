"""
Unified Authentication Configuration System
==========================================

This module provides centralized configuration for all authentication and caching layers:
- Authentication caching (Phase 1-3)
- Database optimization (Phase 4-5) 
- Performance monitoring integration
- Security validation and compliance
- Feature flags for rollback mechanisms
- Production deployment configuration
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION ENUMS AND TYPES
# ============================================================================

class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class CacheStrategy(Enum):
    """Caching strategy options"""
    AGGRESSIVE = "aggressive"  # Maximum caching for performance
    BALANCED = "balanced"     # Balance between performance and freshness
    CONSERVATIVE = "conservative"  # Minimal caching for data consistency
    DISABLED = "disabled"     # No caching (emergency mode)

class SecurityLevel(Enum):
    """Security configuration levels"""
    MAXIMUM = "maximum"       # All security features enabled
    HIGH = "high"            # Most security features enabled
    STANDARD = "standard"    # Standard security features
    BASIC = "basic"          # Minimal security (development only)

# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class ClerkConfiguration:
    """Clerk authentication service configuration"""
    secret_key: str
    publishable_key: str
    domain: str
    api_url: str = "https://api.clerk.com/v1"
    jwks_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.jwks_url:
            self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        
        # Validate configuration
        if not self.secret_key or self.secret_key.startswith("REPLACE_WITH"):
            raise ValueError("Invalid Clerk secret key configuration")
        
        if not self.publishable_key or self.publishable_key.startswith("REPLACE_WITH"):
            raise ValueError("Invalid Clerk publishable key configuration")
        
        if not self.domain or "None" in self.domain:
            raise ValueError("Invalid Clerk domain configuration")

@dataclass
class CacheConfiguration:
    """Caching system configuration"""
    strategy: CacheStrategy = CacheStrategy.BALANCED
    request_cache_enabled: bool = True
    jwt_validation_cache_ttl: int = 300  # 5 minutes
    jwks_cache_ttl: int = 7200  # 2 hours
    background_refresh_enabled: bool = True
    cleanup_interval: int = 3600  # 1 hour
    max_cache_size_mb: int = 100
    encryption_enabled: bool = True
    
    def get_ttl_for_strategy(self, cache_type: str) -> int:
        """Get TTL based on strategy and cache type"""
        base_ttls = {
            "jwt_validation": self.jwt_validation_cache_ttl,
            "jwks": self.jwks_cache_ttl,
            "request": 0  # Request cache doesn't use TTL
        }
        
        base_ttl = base_ttls.get(cache_type, 300)
        
        if self.strategy == CacheStrategy.AGGRESSIVE:
            return base_ttl * 2
        elif self.strategy == CacheStrategy.CONSERVATIVE:
            return max(base_ttl // 2, 60)  # Minimum 1 minute
        elif self.strategy == CacheStrategy.DISABLED:
            return 0
        else:  # BALANCED
            return base_ttl

@dataclass
class SecurityConfiguration:
    """Security configuration settings"""
    level: SecurityLevel = SecurityLevel.HIGH
    use_full_sha256_keys: bool = True
    sanitize_error_messages: bool = True
    store_plaintext_tokens: bool = False
    cache_encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    rate_limiting_enabled: bool = True
    cors_restricted: bool = True
    https_only: bool = True
    
    def is_production_ready(self) -> bool:
        """Check if security configuration is production ready"""
        return (
            self.level in [SecurityLevel.HIGH, SecurityLevel.MAXIMUM] and
            self.use_full_sha256_keys and
            self.sanitize_error_messages and
            not self.store_plaintext_tokens and
            self.cache_encryption_enabled
        )

@dataclass
class DatabaseConfiguration:
    """Database optimization configuration"""
    connection_pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour
    query_cache_enabled: bool = True
    slow_query_threshold: float = 1.0  # seconds
    connection_retries: int = 3
    prepared_statements_enabled: bool = True
    
    def get_connection_url_params(self) -> Dict[str, Any]:
        """Get database connection URL parameters"""
        return {
            "pool_size": self.connection_pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle
        }

@dataclass
class MonitoringConfiguration:
    """Performance monitoring configuration"""
    enabled: bool = True
    metrics_retention_hours: int = 24
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "response_time_p95_ms": 500,
        "error_rate_percent": 5.0,
        "cache_hit_rate_min": 0.7,
        "security_incidents_per_hour": 10,
        "rollback_events_per_day": 5
    })
    dashboard_enabled: bool = True
    export_metrics: bool = False
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    detailed_logging: bool = False

@dataclass
class FeatureFlagsConfiguration:
    """Feature flags configuration"""
    auth_caching: bool = True
    jwt_validation_cache: bool = True
    jwks_background_refresh: bool = True
    database_optimization: bool = True
    performance_monitoring: bool = True
    secure_error_handling: bool = True
    cache_encryption: bool = True
    legacy_compatibility: bool = False
    experimental_features: bool = False
    rollback_enabled: bool = True
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary for easy access"""
        return {
            "ENABLE_AUTH_CACHING": self.auth_caching,
            "ENABLE_JWT_VALIDATION_CACHE": self.jwt_validation_cache,
            "ENABLE_JWKS_BACKGROUND_REFRESH": self.jwks_background_refresh,
            "ENABLE_DATABASE_OPTIMIZATION": self.database_optimization,
            "ENABLE_PERFORMANCE_MONITORING": self.performance_monitoring,
            "ENABLE_SECURE_ERROR_HANDLING": self.secure_error_handling,
            "ENABLE_CACHE_ENCRYPTION": self.cache_encryption,
            "ENABLE_LEGACY_COMPATIBILITY": self.legacy_compatibility,
            "ENABLE_EXPERIMENTAL_FEATURES": self.experimental_features,
            "ENABLE_ROLLBACK": self.rollback_enabled
        }

# ============================================================================
# UNIFIED CONFIGURATION CLASS
# ============================================================================

class UnifiedAuthConfig:
    """
    Unified configuration system integrating all authentication and caching layers.
    Provides centralized configuration management with environment-specific settings.
    """
    
    def __init__(self, environment: Optional[DeploymentEnvironment] = None):
        self.environment = environment or self._detect_environment()
        
        # Load configurations
        self.clerk = self._load_clerk_config()
        self.cache = self._load_cache_config()
        self.security = self._load_security_config()
        self.database = self._load_database_config()
        self.monitoring = self._load_monitoring_config()
        self.feature_flags = self._load_feature_flags()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"🔧 Unified authentication configuration loaded for {self.environment.value}")
    
    def _detect_environment(self) -> DeploymentEnvironment:
        """Detect deployment environment from environment variables"""
        env_name = os.getenv("DEPLOYMENT_ENVIRONMENT", "development").lower()
        
        try:
            return DeploymentEnvironment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', defaulting to development")
            return DeploymentEnvironment.DEVELOPMENT
    
    def _load_clerk_config(self) -> ClerkConfiguration:
        """Load Clerk configuration from environment"""
        return ClerkConfiguration(
            secret_key=os.getenv("CLERK_SECRET_KEY", ""),
            publishable_key=os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", ""),
            domain=os.getenv("NEXT_PUBLIC_CLERK_DOMAIN", "")
        )
    
    def _load_cache_config(self) -> CacheConfiguration:
        """Load cache configuration from environment"""
        strategy_name = os.getenv("CACHE_STRATEGY", "balanced").lower()
        try:
            strategy = CacheStrategy(strategy_name)
        except ValueError:
            logger.warning(f"Unknown cache strategy '{strategy_name}', using balanced")
            strategy = CacheStrategy.BALANCED
        
        return CacheConfiguration(
            strategy=strategy,
            request_cache_enabled=self._get_bool_env("REQUEST_CACHE_ENABLED", True),
            jwt_validation_cache_ttl=int(os.getenv("JWT_CACHE_TTL", "300")),
            jwks_cache_ttl=int(os.getenv("JWKS_CACHE_TTL", "7200")),
            background_refresh_enabled=self._get_bool_env("BACKGROUND_REFRESH_ENABLED", True),
            cleanup_interval=int(os.getenv("CACHE_CLEANUP_INTERVAL", "3600")),
            max_cache_size_mb=int(os.getenv("MAX_CACHE_SIZE_MB", "100")),
            encryption_enabled=self._get_bool_env("CACHE_ENCRYPTION_ENABLED", True)
        )
    
    def _load_security_config(self) -> SecurityConfiguration:
        """Load security configuration from environment"""
        level_name = os.getenv("SECURITY_LEVEL", "high").lower()
        try:
            level = SecurityLevel(level_name)
        except ValueError:
            logger.warning(f"Unknown security level '{level_name}', using high")
            level = SecurityLevel.HIGH
        
        return SecurityConfiguration(
            level=level,
            use_full_sha256_keys=self._get_bool_env("USE_FULL_SHA256_KEYS", True),
            sanitize_error_messages=self._get_bool_env("SANITIZE_ERROR_MESSAGES", True),
            store_plaintext_tokens=self._get_bool_env("STORE_PLAINTEXT_TOKENS", False),
            cache_encryption_enabled=self._get_bool_env("CACHE_ENCRYPTION_ENABLED", True),
            audit_logging_enabled=self._get_bool_env("AUDIT_LOGGING_ENABLED", True),
            rate_limiting_enabled=self._get_bool_env("RATE_LIMITING_ENABLED", True),
            cors_restricted=self._get_bool_env("CORS_RESTRICTED", True),
            https_only=self._get_bool_env("HTTPS_ONLY", self.environment == DeploymentEnvironment.PRODUCTION)
        )
    
    def _load_database_config(self) -> DatabaseConfiguration:
        """Load database configuration from environment"""
        return DatabaseConfiguration(
            connection_pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            query_cache_enabled=self._get_bool_env("QUERY_CACHE_ENABLED", True),
            slow_query_threshold=float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0")),
            connection_retries=int(os.getenv("DB_CONNECTION_RETRIES", "3")),
            prepared_statements_enabled=self._get_bool_env("PREPARED_STATEMENTS_ENABLED", True)
        )
    
    def _load_monitoring_config(self) -> MonitoringConfiguration:
        """Load monitoring configuration from environment"""
        # Parse alert thresholds from environment
        default_thresholds = {
            "response_time_p95_ms": 500,
            "error_rate_percent": 5.0,
            "cache_hit_rate_min": 0.7,
            "security_incidents_per_hour": 10,
            "rollback_events_per_day": 5
        }
        
        thresholds_json = os.getenv("ALERT_THRESHOLDS")
        if thresholds_json:
            try:
                custom_thresholds = json.loads(thresholds_json)
                default_thresholds.update(custom_thresholds)
            except json.JSONDecodeError:
                logger.warning("Invalid ALERT_THRESHOLDS JSON, using defaults")
        
        return MonitoringConfiguration(
            enabled=self._get_bool_env("MONITORING_ENABLED", True),
            metrics_retention_hours=int(os.getenv("METRICS_RETENTION_HOURS", "24")),
            alert_thresholds=default_thresholds,
            dashboard_enabled=self._get_bool_env("DASHBOARD_ENABLED", True),
            export_metrics=self._get_bool_env("EXPORT_METRICS", False),
            metrics_endpoint=os.getenv("METRICS_ENDPOINT", "/metrics"),
            health_check_endpoint=os.getenv("HEALTH_CHECK_ENDPOINT", "/health"),
            detailed_logging=self._get_bool_env("DETAILED_LOGGING", False)
        )
    
    def _load_feature_flags(self) -> FeatureFlagsConfiguration:
        """Load feature flags configuration from environment"""
        return FeatureFlagsConfiguration(
            auth_caching=self._get_bool_env("ENABLE_AUTH_CACHING", True),
            jwt_validation_cache=self._get_bool_env("ENABLE_JWT_VALIDATION_CACHE", True),
            jwks_background_refresh=self._get_bool_env("ENABLE_JWKS_BACKGROUND_REFRESH", True),
            database_optimization=self._get_bool_env("ENABLE_DATABASE_OPTIMIZATION", True),
            performance_monitoring=self._get_bool_env("ENABLE_PERFORMANCE_MONITORING", True),
            secure_error_handling=self._get_bool_env("ENABLE_SECURE_ERROR_HANDLING", True),
            cache_encryption=self._get_bool_env("ENABLE_CACHE_ENCRYPTION", True),
            legacy_compatibility=self._get_bool_env("ENABLE_LEGACY_COMPATIBILITY", False),
            experimental_features=self._get_bool_env("ENABLE_EXPERIMENTAL_FEATURES", False),
            rollback_enabled=self._get_bool_env("ENABLE_ROLLBACK", True)
        )
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable with default"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration"""
        issues = []
        
        # Validate Clerk configuration
        try:
            # This will raise ValueError if invalid
            pass  # Validation happens in ClerkConfiguration.__post_init__
        except ValueError as e:
            issues.append(f"Clerk configuration: {str(e)}")
        
        # Validate security for production
        if self.environment == DeploymentEnvironment.PRODUCTION:
            if not self.security.is_production_ready():
                issues.append("Security configuration is not production ready")
            
            if self.feature_flags.experimental_features:
                issues.append("Experimental features should not be enabled in production")
            
            if self.cache.strategy == CacheStrategy.DISABLED:
                issues.append("Caching should not be disabled in production")
        
        # Log issues
        if issues:
            for issue in issues:
                logger.error(f"🚨 Configuration issue: {issue}")
            
            if self.environment == DeploymentEnvironment.PRODUCTION:
                raise ValueError("Production deployment blocked due to configuration issues")
            else:
                logger.warning("Configuration issues detected but continuing in non-production environment")
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment variables that should be set based on current configuration"""
        env_vars = {}
        
        # Feature flags
        env_vars.update(self.feature_flags.to_dict())
        
        # Cache configuration
        env_vars.update({
            "CACHE_STRATEGY": self.cache.strategy.value,
            "JWT_CACHE_TTL": str(self.cache.jwt_validation_cache_ttl),
            "JWKS_CACHE_TTL": str(self.cache.jwks_cache_ttl)
        })
        
        # Security configuration
        env_vars.update({
            "SECURITY_LEVEL": self.security.level.value,
            "USE_FULL_SHA256_KEYS": str(self.security.use_full_sha256_keys).lower(),
            "SANITIZE_ERROR_MESSAGES": str(self.security.sanitize_error_messages).lower()
        })
        
        return env_vars
    
    def get_deployment_checklist(self) -> Dict[str, Any]:
        """Get deployment readiness checklist"""
        checklist = {
            "environment": self.environment.value,
            "ready_for_deployment": True,
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Security checks
        if not self.security.is_production_ready() and self.environment == DeploymentEnvironment.PRODUCTION:
            checklist["critical_issues"].append("Security configuration is not production ready")
            checklist["ready_for_deployment"] = False
        
        # Performance checks
        if self.cache.strategy == CacheStrategy.DISABLED:
            if self.environment == DeploymentEnvironment.PRODUCTION:
                checklist["critical_issues"].append("Caching is disabled in production")
                checklist["ready_for_deployment"] = False
            else:
                checklist["warnings"].append("Caching is disabled")
        
        # Feature flag checks
        if self.feature_flags.experimental_features and self.environment == DeploymentEnvironment.PRODUCTION:
            checklist["warnings"].append("Experimental features enabled in production")
        
        # Database checks
        if self.database.connection_pool_size < 10 and self.environment == DeploymentEnvironment.PRODUCTION:
            checklist["recommendations"].append("Consider increasing database connection pool size for production")
        
        return checklist
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration for documentation or debugging"""
        config_export = {
            "environment": self.environment.value,
            "cache": {
                "strategy": self.cache.strategy.value,
                "request_cache_enabled": self.cache.request_cache_enabled,
                "jwt_validation_cache_ttl": self.cache.jwt_validation_cache_ttl,
                "jwks_cache_ttl": self.cache.jwks_cache_ttl,
                "background_refresh_enabled": self.cache.background_refresh_enabled,
                "encryption_enabled": self.cache.encryption_enabled
            },
            "security": {
                "level": self.security.level.value,
                "use_full_sha256_keys": self.security.use_full_sha256_keys,
                "sanitize_error_messages": self.security.sanitize_error_messages,
                "store_plaintext_tokens": self.security.store_plaintext_tokens,
                "cache_encryption_enabled": self.security.cache_encryption_enabled
            },
            "database": {
                "connection_pool_size": self.database.connection_pool_size,
                "max_overflow": self.database.max_overflow,
                "query_cache_enabled": self.database.query_cache_enabled
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "dashboard_enabled": self.monitoring.dashboard_enabled,
                "metrics_endpoint": self.monitoring.metrics_endpoint
            },
            "feature_flags": self.feature_flags.to_dict()
        }
        
        if include_secrets:
            config_export["clerk"] = {
                "domain": self.clerk.domain,
                "api_url": self.clerk.api_url,
                "jwks_url": self.clerk.jwks_url
                # Note: secrets are not included even when include_secrets=True for security
            }
        
        return config_export

# ============================================================================
# GLOBAL CONFIGURATION INSTANCE
# ============================================================================

# Global configuration instance
_global_config: Optional[UnifiedAuthConfig] = None

def get_auth_config() -> UnifiedAuthConfig:
    """Get the global authentication configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = UnifiedAuthConfig()
    return _global_config

def reload_auth_config(environment: Optional[DeploymentEnvironment] = None) -> UnifiedAuthConfig:
    """Reload the global authentication configuration"""
    global _global_config
    _global_config = UnifiedAuthConfig(environment)
    return _global_config

# Configuration shortcuts for easy access
def get_clerk_config() -> ClerkConfiguration:
    """Get Clerk configuration"""
    return get_auth_config().clerk

def get_cache_config() -> CacheConfiguration:
    """Get cache configuration"""
    return get_auth_config().cache

def get_security_config() -> SecurityConfiguration:
    """Get security configuration"""
    return get_auth_config().security

def get_database_config() -> DatabaseConfiguration:
    """Get database configuration"""
    return get_auth_config().database

def get_monitoring_config() -> MonitoringConfiguration:
    """Get monitoring configuration"""
    return get_auth_config().monitoring

def get_feature_flags() -> FeatureFlagsConfiguration:
    """Get feature flags configuration"""
    return get_auth_config().feature_flags

# ============================================================================
# CONFIGURATION VALIDATION UTILITIES
# ============================================================================

async def validate_runtime_config() -> Dict[str, Any]:
    """Validate configuration at runtime"""
    config = get_auth_config()
    validation_result = {
        "valid": True,
        "issues": [],
        "warnings": []
    }
    
    # Test Clerk connectivity
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(config.clerk.jwks_url)
            if response.status_code != 200:
                validation_result["issues"].append(f"Cannot reach Clerk JWKS endpoint: {response.status_code}")
                validation_result["valid"] = False
    except Exception as e:
        validation_result["issues"].append(f"Clerk connectivity test failed: {str(e)}")
        validation_result["valid"] = False
    
    # Test cache functionality if enabled
    if config.feature_flags.auth_caching:
        try:
            from ..utils.auth_cache import RequestCache
            cache = RequestCache()
            cache.set("test", "value")
            if cache.get("test") != "value":
                validation_result["issues"].append("Cache functionality test failed")
                validation_result["valid"] = False
        except Exception as e:
            validation_result["issues"].append(f"Cache test failed: {str(e)}")
            validation_result["valid"] = False
    
    return validation_result

def create_environment_template(environment: DeploymentEnvironment) -> str:
    """Create .env template for specific environment"""
    config = UnifiedAuthConfig(environment)
    
    template_lines = [
        f"# Authentication Configuration for {environment.value.upper()}",
        f"DEPLOYMENT_ENVIRONMENT={environment.value}",
        "",
        "# Clerk Configuration",
        "CLERK_SECRET_KEY=your_clerk_secret_key_here",
        "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here", 
        "NEXT_PUBLIC_CLERK_DOMAIN=your-domain.clerk.accounts.dev",
        "",
        "# Security Configuration",
        f"SECURITY_LEVEL={config.security.level.value}",
        f"USE_FULL_SHA256_KEYS={str(config.security.use_full_sha256_keys).lower()}",
        f"SANITIZE_ERROR_MESSAGES={str(config.security.sanitize_error_messages).lower()}",
        f"CACHE_ENCRYPTION_ENABLED={str(config.security.cache_encryption_enabled).lower()}",
        "",
        "# Cache Configuration",
        f"CACHE_STRATEGY={config.cache.strategy.value}",
        f"JWT_CACHE_TTL={config.cache.jwt_validation_cache_ttl}",
        f"JWKS_CACHE_TTL={config.cache.jwks_cache_ttl}",
        "",
        "# Feature Flags"
    ]
    
    # Add feature flags
    for key, value in config.feature_flags.to_dict().items():
        template_lines.append(f"{key}={str(value).lower()}")
    
    return "\n".join(template_lines)