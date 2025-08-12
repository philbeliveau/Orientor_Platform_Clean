# Agent Prompt: Module E - Backend Import Standardization (SIMPLIFIED)

## 🎯 MISSION: FIX INCONSISTENT IMPORTS
**Problem**: 4 backend routers have inconsistent auth imports
**Solution**: Simple find/replace to standardize imports  
**Complexity**: MINIMAL - Just fix import statements

## 🚨 WHAT WE'RE NOT DOING (Over-Engineering)
❌ Custom JWKS caching systems
❌ Redis integration
❌ Complex authentication classes
❌ Performance monitoring middleware
❌ Custom user synchronization
❌ Metrics collection systems

## ✅ WHAT WE'RE DOING (Simple & Effective)
✅ Fix 4 inconsistent import statements
✅ Ensure all routers use the same auth pattern
✅ Simple script to automate the fix

## 📋 CURRENT PROBLEM

Based on the platform analysis, these routers have inconsistent imports:

```python
# INCONSISTENT PATTERNS FOUND:

# 1. Missing 'with_db_sync' in import (4 routers)
from app.utils.clerk_auth import get_current_user  # ❌ WRONG

# 2. Should be (standardized pattern)  
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user  # ✅ CORRECT
```

## 🔧 SIMPLE SOLUTION

### Files to Fix:
```
backend/app/routers/chat.py
backend/app/routers/users.py  
backend/app/routers/jobs.py
backend/app/routers/onboarding.py
```

### Simple Fix Script
**File**: `backend/scripts/fix_imports.py`

```python
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
```

### Manual Verification
After running the script, verify the imports look like this:

```python
# ✅ CORRECT PATTERN (all routers should have this):
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi import Depends

@router.post("/some-endpoint")
async def some_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"user_id": current_user.clerk_user_id}
```

## 📊 VERIFICATION SCRIPT

**File**: `backend/scripts/verify_imports.py`

```python
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
```

## ✅ TESTING

### Simple Test
```python
# Test that imports work correctly
def test_router_imports():
    """Test that all routers can import auth correctly"""
    try:
        from app.routers import chat, users, jobs, onboarding
        print("✅ All router imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

# Run the test
if __name__ == "__main__":
    test_router_imports()
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve:
- [ ] **All 4 routers** use consistent import pattern
- [ ] **Script runs successfully** and fixes imports
- [ ] **No breaking changes** to existing functionality
- [ ] **All routers still work** after the fix

### Implementation Time: **30 MINUTES MAX**
- 10 minutes: Write the fix script
- 10 minutes: Run the script and verify  
- 10 minutes: Test that routers still work

## 🔄 DEPENDENCIES
**NONE** - This is just fixing imports

## 💡 WHY THIS MATTERS

### Current State:
- **85% of routers** use correct pattern ✅
- **15% of routers** use inconsistent pattern ❌
- **Confusing for developers** maintaining the code
- **Potential bugs** from inconsistent auth handling

### After Fix:
- **100% of routers** use correct pattern ✅
- **Consistent codebase** for easier maintenance
- **Clear pattern** for future development

## 📝 REPORTING FORMAT
```
📊 MODULE E - IMPORT STANDARDIZATION
⏱️ STATUS: [Complete/In Progress]
🎯 ROUTERS FIXED: X/4
✅ SCRIPT WORKS: [Yes/No]
🔄 ALL ROUTERS FUNCTIONAL: [Yes/No] 
⏰ TIME SPENT: X minutes (max 30)
```

**START ANYTIME** - This is independent and low-risk!

---

**REMEMBER**: 
- **Just fix the imports** - don't add complexity
- **Test that routers still work** after changes
- **Keep it simple** - find/replace is enough
- 🔐 **CLERK AUTHENTICATION ONLY**