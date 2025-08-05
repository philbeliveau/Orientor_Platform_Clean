# COMPREHENSIVE SECURITY TESTING SUITE
# ====================================
# 
# This test suite validates the secure authentication system
# and ensures all security vulnerabilities have been fixed.
# 
# Tests include:
# ✅ JWT token generation and validation
# ✅ Password hashing security
# ✅ Authentication endpoint security
# ✅ Rate limiting protection
# ✅ Token blacklisting
# ✅ Security headers validation

import pytest
import json
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.database import Base, get_db
from app.utils.secure_auth import SecureAuthManager, hash_password, verify_password
from app.models.user import User
import jwt
from datetime import datetime, timedelta, timezone
import redis
from unittest.mock import Mock, patch

# Test Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_secure_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestSecureAuthentication:
    """Test suite for secure authentication system"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        # Create test app with secure authentication
        from main_deploy_secure import app
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        
        # Create test auth manager
        self.auth_manager = SecureAuthManager()
        
        # Clear test database
        db = TestingSessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()

    def test_password_hashing_security(self):
        """Test password hashing with bcrypt"""
        password = "SecurePassword123!"
        
        # Test password hashing
        hashed = hash_password(password)
        
        # Verify hash properties
        assert hashed != password  # Not plaintext
        assert len(hashed) > 50  # Bcrypt hash length
        assert hashed.startswith('$2b$')  # Bcrypt format
        
        # Test password verification
        assert verify_password(password, hashed) == True
        assert verify_password("WrongPassword", hashed) == False
        
        # Test different passwords produce different hashes
        hashed2 = hash_password(password)
        assert hashed != hashed2  # Salt ensures uniqueness

    def test_jwt_token_security(self):
        """Test JWT token generation and validation"""
        user_id = 123
        email = "test@example.com"
        
        # Generate access token
        access_token = self.auth_manager.create_access_token(user_id, email)
        
        # Verify token structure
        assert isinstance(access_token, str)
        assert len(access_token) > 100  # JWT tokens are long
        assert access_token.count('.') == 2  # JWT has 3 parts
        
        # Verify token content
        payload = self.auth_manager.verify_token(access_token)
        assert payload['sub'] == str(user_id)
        assert payload['email'] == email
        assert payload['token_type'] == 'access'
        assert 'exp' in payload  # Expiration
        assert 'jti' in payload  # JWT ID

    def test_secure_user_registration(self):
        """Test secure user registration endpoint"""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        
        # Verify successful registration
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert "password" not in data["user"]  # No password in response
        
        # Verify tokens are present and different
        assert len(data["access_token"]) > 100
        assert len(data["refresh_token"]) > 100
        assert data["access_token"] != data["refresh_token"]

    def test_secure_user_login(self):
        """Test secure user login endpoint"""
        # First register a user
        register_data = {
            "email": "logintest@example.com",
            "password": "SecurePass123!"
        }
        self.client.post("/api/auth/register", json=register_data)
        
        # Test login
        login_data = {
            "email": "logintest@example.com",
            "password": "SecurePass123!"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        # Verify successful login
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == login_data["email"]

    def test_invalid_login_security(self):
        """Test security with invalid login attempts"""
        # Register user first
        register_data = {
            "email": "security@example.com",
            "password": "SecurePass123!"
        }
        self.client.post("/api/auth/register", json=register_data)
        
        # Test wrong password
        login_data = {
            "email": "security@example.com",
            "password": "WrongPassword123!"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        # Verify security response
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_rate_limiting_protection(self):
        """Test rate limiting for login attempts"""
        # Register user first
        register_data = {
            "email": "ratelimit@example.com",
            "password": "SecurePass123!"
        }
        self.client.post("/api/auth/register", json=register_data)
        
        # Make multiple failed login attempts
        login_data = {
            "email": "ratelimit@example.com",
            "password": "WrongPassword123!"
        }
        
        # First 5 attempts should return 401
        for i in range(5):
            response = self.client.post("/api/auth/login", json=login_data)
            assert response.status_code == 401
        
        # 6th attempt should trigger rate limiting
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 429
        assert "Too many login attempts" in response.json()["detail"]

    def test_token_refresh_security(self):
        """Test token refresh functionality"""
        # Register and get tokens
        register_data = {
            "email": "refresh@example.com",
            "password": "SecurePass123!"
        }
        register_response = self.client.post("/api/auth/register", json=register_data)
        tokens = register_response.json()
        
        # Test token refresh
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = self.client.post("/api/auth/refresh", json=refresh_data)
        
        # Verify successful refresh
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        
        # Verify new token is different
        assert data["access_token"] != tokens["access_token"]

    def test_protected_endpoint_security(self):
        """Test protected endpoint access"""
        # Register and get tokens
        register_data = {
            "email": "protected@example.com",
            "password": "SecurePass123!"
        }
        register_response = self.client.post("/api/auth/register", json=register_data)
        tokens = register_response.json()
        
        # Test access without token
        response = self.client.get("/api/auth/me")
        assert response.status_code == 401
        
        # Test access with valid token
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = self.client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == register_data["email"]

    def test_logout_security(self):
        """Test secure logout with token blacklisting"""
        # Register and get tokens
        register_data = {
            "email": "logout@example.com",
            "password": "SecurePass123!"
        }
        register_response = self.client.post("/api/auth/register", json=register_data)
        tokens = register_response.json()
        
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Test logout
        response = self.client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # Verify token is blacklisted (should fail to access protected endpoint)
        response = self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    def test_password_strength_validation(self):
        """Test password strength requirements"""
        weak_passwords = [
            "weak",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123"  # No special characters
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": f"weak{len(weak_password)}@example.com",
                "password": weak_password
            }
            
            response = self.client.post("/api/auth/register", json=user_data)
            assert response.status_code == 422  # Validation error

    def test_security_headers(self):
        """Test security headers in responses"""
        response = self.client.get("/health")
        
        # Verify security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_cors_security_configuration(self):
        """Test CORS security configuration"""
        # Test OPTIONS request (preflight)
        response = self.client.options("/api/auth/login")
        
        # Verify CORS headers are present but restrictive
        assert "Access-Control-Allow-Origin" in response.headers
        # Should not be wildcard (*) in production
        assert response.headers["Access-Control-Allow-Origin"] != "*"

    def test_token_expiration_security(self):
        """Test that tokens have proper expiration"""
        user_id = 123
        email = "test@example.com"
        
        # Generate token
        token = self.auth_manager.create_access_token(user_id, email)
        payload = self.auth_manager.verify_token(token)
        
        # Verify expiration is set and reasonable
        exp_timestamp = payload['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Token should expire in the future but not too far
        assert exp_datetime > now
        assert exp_datetime < now + timedelta(hours=1)  # Should be 30 minutes

    def test_security_status_endpoint(self):
        """Test security status reporting"""
        response = self.client.get("/api/security/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify security configuration
        assert "authentication_method" in data
        assert "security_level" in data
        assert "cors_origins" in data
        assert "security_headers" in data
        assert data["security_headers"] == "enabled"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])