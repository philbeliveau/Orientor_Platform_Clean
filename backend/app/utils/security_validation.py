"""
Security Validation Utilities for Orientor Platform
==================================================

This module provides security validation functions to ensure
proper configuration and prevent common security vulnerabilities.
"""

import os
import logging
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class SecurityIssue:
    def __init__(self, level: SecurityLevel, message: str, recommendation: str = ""):
        self.level = level
        self.message = message
        self.recommendation = recommendation
        
    def __str__(self):
        return f"[{self.level.value}] {self.message}"

class SecurityValidator:
    """Production security validation for Orientor Platform"""
    
    def __init__(self):
        self.issues: List[SecurityIssue] = []
        self.is_production = os.getenv("ENVIRONMENT") == "production" or os.getenv("RAILWAY_ENVIRONMENT") == "production"
    
    def validate_all(self) -> Tuple[bool, List[SecurityIssue]]:
        """Run all security validations"""
        self.issues.clear()
        
        # Critical validations
        self._validate_clerk_configuration()
        self._validate_secrets_configuration()
        self._validate_database_security()
        self._validate_cors_configuration()
        
        # Additional validations
        self._validate_environment_variables()
        self._validate_api_keys()
        
        # Determine if deployment should be blocked
        critical_issues = [issue for issue in self.issues if issue.level == SecurityLevel.CRITICAL]
        is_secure = len(critical_issues) == 0
        
        return is_secure, self.issues
    
    def _validate_clerk_configuration(self):
        """Validate Clerk authentication configuration"""
        clerk_secret = os.getenv("CLERK_SECRET_KEY")
        clerk_publishable = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
        clerk_domain = os.getenv("NEXT_PUBLIC_CLERK_DOMAIN")
        
        if not clerk_secret:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "CLERK_SECRET_KEY is not configured",
                "Set CLERK_SECRET_KEY environment variable with your Clerk secret key"
            ))
        elif clerk_secret.startswith("sk_test_") and self.is_production:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "Using test Clerk secret key in production",
                "Replace with production Clerk secret key (sk_live_*)"
            ))
        
        if not clerk_publishable:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is not configured",
                "Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY environment variable"
            ))
        elif clerk_publishable.startswith("pk_test_") and self.is_production:
            self.issues.append(SecurityIssue(
                SecurityLevel.HIGH,
                "Using test Clerk publishable key in production",
                "Replace with production Clerk publishable key (pk_live_*)"
            ))
            
        if not clerk_domain:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "NEXT_PUBLIC_CLERK_DOMAIN is not configured",
                "Set NEXT_PUBLIC_CLERK_DOMAIN environment variable"
            ))
        elif not (clerk_domain.endswith('.clerk.accounts.dev') or clerk_domain.endswith('.clerk.com')):
            self.issues.append(SecurityIssue(
                SecurityLevel.MEDIUM,
                f"Unusual Clerk domain format: {clerk_domain}",
                "Verify Clerk domain is correct"
            ))
    
    def _validate_secrets_configuration(self):
        """Validate secret keys and sensitive configuration"""
        secret_key = os.getenv("SECRET_KEY")
        
        if not secret_key:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "SECRET_KEY is not configured",
                "Set a strong SECRET_KEY environment variable"
            ))
        elif secret_key == "development-secret-key-replace-in-production":
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "Using default SECRET_KEY in production",
                "Generate and set a strong, unique SECRET_KEY"
            ))
        elif len(secret_key) < 32:
            self.issues.append(SecurityIssue(
                SecurityLevel.HIGH,
                f"SECRET_KEY is too short ({len(secret_key)} chars)",
                "Use a SECRET_KEY of at least 32 characters"
            ))
    
    def _validate_database_security(self):
        """Validate database connection security"""
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # Check for insecure database connections
            if database_url.startswith("postgresql://") and "localhost" not in database_url and "sslmode" not in database_url:
                self.issues.append(SecurityIssue(
                    SecurityLevel.HIGH,
                    "Database connection may not be using SSL",
                    "Add ?sslmode=require to your DATABASE_URL for production"
                ))
            
            # Check for default passwords
            if "password" in database_url.lower() or "123456" in database_url:
                self.issues.append(SecurityIssue(
                    SecurityLevel.CRITICAL,
                    "Database URL contains weak or default password",
                    "Use a strong, unique database password"
                ))
    
    def _validate_cors_configuration(self):
        """Validate CORS security settings"""
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        
        if "*" in allowed_origins and self.is_production:
            self.issues.append(SecurityIssue(
                SecurityLevel.CRITICAL,
                "CORS allows all origins (*) in production",
                "Restrict ALLOWED_ORIGINS to specific domains"
            ))
        elif not allowed_origins and self.is_production:
            self.issues.append(SecurityIssue(
                SecurityLevel.HIGH,
                "ALLOWED_ORIGINS not configured for production",
                "Set specific allowed origins for CORS"
            ))
    
    def _validate_environment_variables(self):
        """Validate critical environment variables"""
        critical_vars = [
            "DATABASE_URL",
            "OPENAI_API_KEY",
            "CLERK_SECRET_KEY",
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"
        ]
        
        for var in critical_vars:
            value = os.getenv(var)
            if not value:
                self.issues.append(SecurityIssue(
                    SecurityLevel.HIGH if var != "CLERK_SECRET_KEY" else SecurityLevel.CRITICAL,
                    f"Required environment variable {var} is not set",
                    f"Set {var} environment variable"
                ))
            elif value.startswith("REPLACE_WITH_") or value.startswith("your_") or value == "sk-REPLACE":
                self.issues.append(SecurityIssue(
                    SecurityLevel.CRITICAL,
                    f"Environment variable {var} contains placeholder value",
                    f"Replace {var} with actual production value"
                ))
    
    def _validate_api_keys(self):
        """Validate API key formats and security"""
        api_keys = {
            "OPENAI_API_KEY": "sk-",
            "ANTHROPIC_API_KEY": "sk-ant-",
            "PINECONE_API_KEY": None  # No standard prefix
        }
        
        for key_name, expected_prefix in api_keys.items():
            key_value = os.getenv(key_name)
            if key_value:
                if expected_prefix and not key_value.startswith(expected_prefix):
                    self.issues.append(SecurityIssue(
                        SecurityLevel.MEDIUM,
                        f"{key_name} has unexpected format",
                        f"Verify {key_name} is correct"
                    ))
                elif len(key_value) < 20:
                    self.issues.append(SecurityIssue(
                        SecurityLevel.MEDIUM,
                        f"{key_name} appears to be too short",
                        f"Verify {key_name} is complete and correct"
                    ))

def validate_production_security() -> Dict[str, any]:
    """
    Comprehensive security validation for production deployment
    
    Returns:
        dict: Security validation results
    """
    validator = SecurityValidator()
    is_secure, issues = validator.validate_all()
    
    # Categorize issues by severity
    critical = [str(issue) for issue in issues if issue.level == SecurityLevel.CRITICAL]
    high = [str(issue) for issue in issues if issue.level == SecurityLevel.HIGH]
    medium = [str(issue) for issue in issues if issue.level == SecurityLevel.MEDIUM]
    low = [str(issue) for issue in issues if issue.level == SecurityLevel.LOW]
    
    result = {
        "is_secure": is_secure,
        "deployment_safe": is_secure,
        "total_issues": len(issues),
        "issues": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "recommendations": [issue.recommendation for issue in issues if issue.recommendation]
    }
    
    # Log results
    if is_secure:
        logger.info("✅ Security validation passed - deployment safe")
    else:
        logger.error(f"🚨 Security validation failed - {len(critical)} critical issues found")
        for issue in critical:
            logger.error(f"  {issue}")
    
    return result

if __name__ == "__main__":
    # Run validation when executed directly
    results = validate_production_security()
    
    if results["deployment_safe"]:
        print("✅ Security validation passed")
        exit(0)
    else:
        print("❌ Security validation failed")
        print(f"Critical issues: {len(results['issues']['critical'])}")
        for issue in results['issues']['critical']:
            print(f"  - {issue}")
        exit(1)