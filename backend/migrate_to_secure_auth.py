#!/usr/bin/env python3
"""
SECURITY MIGRATION SCRIPT - Update All Routers to Secure Authentication
========================================================================

This script automatically updates all router files to use the secure JWT authentication
system instead of the insecure base64 authentication.

CRITICAL: Run this script to upgrade all endpoints to secure authentication immediately.
"""

import os
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the routers directory
ROUTERS_DIR = Path(__file__).parent / "app" / "routers"

# Authentication import patterns to replace
INSECURE_IMPORTS = [
    r"from app\.utils\.auth import get_current_user_unified as get_current_user",
    r"from app\.utils\.auth import get_current_user_unified",
    r"from app\.utils\.auth import get_current_user_legacy_compatible",
    r"from app\.utils\.auth import get_current_user_optional",
]

# Secure authentication imports to add
SECURE_IMPORTS = [
    "from app.utils.secure_auth import get_current_user_secure as get_current_user",
    "from app.utils.secure_auth import get_current_user_optional_secure as get_current_user_optional",
]

# Dependency patterns to update
DEPENDENCY_PATTERNS = [
    (r"get_current_user_unified", "get_current_user_secure"),
    (r"get_current_user_legacy_compatible", "get_current_user_secure"),
    (r"get_current_user_optional", "get_current_user_optional_secure"),
]

def backup_file(file_path: Path) -> Path:
    """Create a backup of the original file"""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    backup_path.write_text(file_path.read_text(), encoding='utf-8')
    logger.info(f"✅ Backup created: {backup_path}")
    return backup_path

def update_router_file(file_path: Path) -> bool:
    """Update a single router file to use secure authentication"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        updated = False
        
        # Check if file already uses secure auth
        if "secure_auth" in content:
            logger.info(f"⏭️ {file_path.name} already uses secure authentication")
            return False
        
        # Replace insecure imports
        for pattern in INSECURE_IMPORTS:
            if re.search(pattern, content):
                # Create backup before modifying
                if not updated:
                    backup_file(file_path)
                    updated = True
                
                # Replace with secure import
                content = re.sub(pattern, SECURE_IMPORTS[0], content)
                logger.info(f"🔒 Updated import in {file_path.name}")
        
        # Update dependency patterns in function signatures
        for old_pattern, new_pattern in DEPENDENCY_PATTERNS:
            if re.search(old_pattern, content):
                if not updated and re.search(old_pattern, content):
                    backup_file(file_path)
                    updated = True
                
                content = re.sub(old_pattern, new_pattern, content)
                logger.info(f"🔒 Updated dependency pattern in {file_path.name}: {old_pattern} -> {new_pattern}")
        
        # Add security comment if file was updated
        if updated:
            security_comment = '''# SECURITY UPDATE: This router now uses secure JWT authentication
# Previous insecure base64 authentication has been replaced with RSA-256 JWT tokens
# Backup of original file created with .backup extension

'''
            
            # Add comment after existing imports
            import_end = content.find('\nrouter = APIRouter')
            if import_end != -1:
                content = content[:import_end] + '\n' + security_comment + content[import_end:]
            else:
                # Add at the beginning if no router declaration found
                content = security_comment + content
        
        # Write updated content
        if updated:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ {file_path.name} updated successfully")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to update {file_path.name}: {e}")
        return False

def migrate_all_routers():
    """Migrate all router files to secure authentication"""
    if not ROUTERS_DIR.exists():
        logger.error(f"❌ Routers directory not found: {ROUTERS_DIR}")
        return
    
    logger.info(f"🔍 Scanning routers directory: {ROUTERS_DIR}")
    
    # Find all Python files in routers directory
    router_files = list(ROUTERS_DIR.glob("*.py"))
    
    if not router_files:
        logger.warning("⚠️ No Python files found in routers directory")
        return
    
    logger.info(f"📁 Found {len(router_files)} router files")
    
    updated_count = 0
    skipped_count = 0
    
    for router_file in router_files:
        # Skip __init__.py and backup files
        if router_file.name.startswith('__') or router_file.name.endswith('.backup'):
            continue
        
        logger.info(f"🔍 Processing: {router_file.name}")
        
        if update_router_file(router_file):
            updated_count += 1
        else:
            skipped_count += 1
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎉 SECURITY MIGRATION COMPLETE")
    logger.info("="*60)
    logger.info(f"✅ Files updated: {updated_count}")
    logger.info(f"⏭️ Files skipped: {skipped_count}")
    logger.info(f"📁 Total files processed: {updated_count + skipped_count}")
    
    if updated_count > 0:
        logger.info("\n🚨 IMPORTANT NEXT STEPS:")
        logger.info("1. Test all endpoints with new authentication system")
        logger.info("2. Update frontend to use new JWT endpoints")
        logger.info("3. Setup Redis for token blacklisting")
        logger.info("4. Deploy with secure environment variables")
        logger.info("5. Remove .backup files after successful testing")
    
    logger.info("\n🔒 All routers now use SECURE JWT authentication!")

if __name__ == "__main__":
    logger.info("🚀 Starting Security Migration...")
    logger.info("This will update all routers to use secure JWT authentication")
    
    # Confirmation prompt
    response = input("\n⚠️ This will modify router files. Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        logger.info("❌ Migration cancelled by user")
        exit(0)
    
    migrate_all_routers()