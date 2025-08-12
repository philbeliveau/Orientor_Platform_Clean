#!/usr/bin/env python3

import os
import re

ROUTER_FILES = [
    "backend/app/routers/chat.py",
    "backend/app/routers/users.py",
    "backend/app/routers/jobs.py", 
    "backend/app/routers/onboarding.py"
]

def verify_file(file_path: str) -> bool:
    """Verify imports are standardized"""
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for correct import pattern
    correct_pattern = r"from .*\.clerk_auth import get_current_user_with_db_sync as get_current_user"
    
    if re.search(correct_pattern, content):
        print(f"✅ {file_path} - Import is correct")
        return True
    else:
        print(f"❌ {file_path} - Import needs fixing")
        return False

def main():
    """Verify all imports are standardized"""
    print("🔍 Verifying backend router imports...")
    
    all_correct = True
    for file_path in ROUTER_FILES:
        if not verify_file(file_path):
            all_correct = False
    
    if all_correct:
        print("\n✅ All imports are standardized!")
    else:
        print("\n❌ Some imports still need fixing")

if __name__ == "__main__":
    main()