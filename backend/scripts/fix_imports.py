#!/usr/bin/env python3

import os
import re

# Files that need fixing
ROUTER_FILES = [
    "backend/app/routers/chat.py",
    "backend/app/routers/users.py", 
    "backend/app/routers/jobs.py",
    "backend/app/routers/onboarding.py"
]

# Simple find/replace patterns
FIXES = [
    # Fix inconsistent imports
    (
        r"from app\.utils\.clerk_auth import get_current_user\b",
        "from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user"
    ),
    (
        r"from \.\.utils\.clerk_auth import get_current_user\b", 
        "from ..utils.clerk_auth import get_current_user_with_db_sync as get_current_user"
    )
]

def fix_file(file_path: str) -> bool:
    """Fix imports in a single file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
        
    print(f"🔧 Fixing {file_path}...")
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        for pattern, replacement in FIXES:
            content = re.sub(pattern, replacement, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed {file_path}")
            return True
        else:
            print(f"ℹ️ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all router imports"""
    print("🚀 Fixing backend router imports...")
    
    fixed_count = 0
    for file_path in ROUTER_FILES:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count}/{len(ROUTER_FILES)} files")
    print("🎉 Import standardization complete!")

if __name__ == "__main__":
    main()