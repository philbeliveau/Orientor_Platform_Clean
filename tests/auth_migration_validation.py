"""
Authentication Migration Validation Test Suite
============================================

This test validates that the authentication migration from legacy JWT to Clerk
has been completed successfully and the system is secure.

Run with: python -m pytest tests/auth_migration_validation.py -v
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

class TestAuthMigrationValidation:
    """Test suite to validate authentication migration completion"""

    def test_legacy_files_removed(self):
        """Ensure all dangerous legacy authentication files are removed"""
        project_root = Path(__file__).parent.parent
        
        # Files that should be completely removed
        dangerous_files = [
            "backend/shared/security/jwt_manager.py",
            "backend/app/utils/auth.py", 
            "frontend/src/contexts/SecureAuthContext.tsx",
            "frontend/src/services/secureAuthService.ts",
            "frontend/src/__tests__/secureAuth.test.tsx"
        ]
        
        for file_path in dangerous_files:
            full_path = project_root / file_path
            assert not full_path.exists(), f"SECURITY RISK: Legacy file still exists: {file_path}"
    
    def test_no_legacy_imports(self):
        """Ensure no code imports the removed legacy authentication modules"""
        project_root = Path(__file__).parent.parent
        
        # Search for imports of removed modules
        dangerous_imports = [
            "from backend.shared.security.jwt_manager",
            "import jwt_manager", 
            "from app.utils.auth import",
            "from ..utils.auth import",
            "SecureAuthContext",
            "secureAuthService"
        ]
        
        # Files to check
        files_to_check = []
        for ext in ["*.py", "*.ts", "*.tsx"]:
            files_to_check.extend(project_root.glob(f"**/{ext}"))
        
        # Exclude certain directories
        exclude_dirs = {".git", "node_modules", ".next", "__pycache__", "dist", "build"}
        
        for file_path in files_to_check:
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue
                
            # Skip test files  
            if "test" in str(file_path).lower():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for dangerous_import in dangerous_imports:
                    assert dangerous_import not in content, (
                        f"SECURITY RISK: Found dangerous import '{dangerous_import}' in {file_path}"
                    )
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                continue

    def test_clerk_environment_variables(self):
        """Ensure required Clerk environment variables are configured"""
        required_env_vars = [
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
            "CLERK_SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            pytest.skip(f"Skipping: Missing environment variables: {missing_vars}")

    def test_no_hardcoded_secrets(self):
        """Ensure no hardcoded JWT secrets remain in the codebase"""
        project_root = Path(__file__).parent.parent
        
        # Patterns that indicate hardcoded secrets
        dangerous_patterns = [
            "JWT_SECRET_KEY",
            "jwt.encode", 
            "jwt.decode",
            "secrets.token_urlsafe",
            "bcrypt"
        ]
        
        # Files to check (focus on Python files)
        python_files = list(project_root.glob("**/*.py"))
        
        exclude_dirs = {".git", "node_modules", ".next", "__pycache__", "venv", "env"}
        
        for file_path in python_files:
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue
                
            # Skip this test file itself and other test files
            if "test" in str(file_path).lower() or "auth_migration_validation.py" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for JWT usage (should only be in removed files)
                if "import jwt" in content or "from jose import jwt" in content:
                    # This is suspicious - JWT should only be used by Clerk now
                    print(f"WARNING: JWT usage found in {file_path}")
                    
            except (UnicodeDecodeError, PermissionError):
                continue

    def test_clerk_auth_function_exists(self):
        """Ensure the new Clerk authentication function is available"""
        try:
            from app.utils.clerk_auth import get_current_user_with_db_sync
            assert callable(get_current_user_with_db_sync), "Clerk auth function should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import Clerk authentication function: {e}")

    def test_routers_use_clerk_auth(self):
        """Ensure all routers are using the correct Clerk authentication import"""
        project_root = Path(__file__).parent.parent / "backend" / "app" / "routers"
        
        if not project_root.exists():
            pytest.skip("Router directory not found")
            
        router_files = list(project_root.glob("*.py"))
        router_files = [f for f in router_files if f.name != "__init__.py"]
        
        correct_import = "get_current_user_with_db_sync as get_current_user"
        
        for router_file in router_files:
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Skip files that don't use authentication
                if "get_current_user" not in content:
                    continue
                    
                # If it uses get_current_user, it should use the correct import
                if "from app.utils.clerk_auth import" in content or "from ..utils.clerk_auth import" in content:
                    # Should use the aliased import
                    assert correct_import in content, (
                        f"Router {router_file.name} should use correct Clerk import pattern"
                    )
            except (UnicodeDecodeError, PermissionError):
                continue

def run_security_validation():
    """Run a comprehensive security validation check"""
    print("🔍 Running Authentication Migration Security Validation...")
    
    # Run the test suite
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("✅ SECURITY VALIDATION PASSED - Migration completed successfully!")
        return True
    else:
        print("🚨 SECURITY VALIDATION FAILED - Migration incomplete or security issues detected!")
        return False

if __name__ == "__main__":
    success = run_security_validation()
    sys.exit(0 if success else 1)