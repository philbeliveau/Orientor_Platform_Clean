#!/usr/bin/env python3
"""
Model Autoincrement Fix Script
Systematically fixes all model files to add autoincrement=True to primary key definitions.
"""

import os
import re
from pathlib import Path

def fix_model_autoincrement():
    """Fix autoincrement in all model files."""
    
    models_dir = Path("backend/app/models")
    
    # Pattern to find Integer primary keys without autoincrement
    pattern = r'(\s+id\s*=\s*Column\(Integer.*?primary_key=True.*?)(\))'
    
    results = {
        "fixed_files": [],
        "already_correct": [],
        "errors": [],
        "total_fixes": 0
    }
    
    for model_file in models_dir.glob("*.py"):
        if model_file.name in ["__init__.py", "base.py"]:
            continue
            
        try:
            original_content = model_file.read_text()
            
            # Skip if file already has autoincrement or no primary keys
            if "autoincrement=True" in original_content or "primary_key=True" not in original_content:
                results["already_correct"].append(model_file.name)
                continue
            
            # Find and fix all Integer primary key definitions
            def replace_pk(match):
                full_match = match.group(0)
                if "autoincrement=True" in full_match:
                    return full_match  # Already has autoincrement
                
                # Insert autoincrement=True before the closing parenthesis
                prefix = match.group(1)
                if prefix.endswith(','):
                    return f"{prefix} autoincrement=True)"
                else:
                    return f"{prefix}, autoincrement=True)"
            
            # Apply the fix
            new_content = re.sub(pattern, replace_pk, original_content, flags=re.MULTILINE | re.DOTALL)
            
            if new_content != original_content:
                # Write the fixed content back
                model_file.write_text(new_content)
                
                # Count the number of fixes made
                fixes_count = len(re.findall(r'autoincrement=True\)', new_content))
                results["fixed_files"].append({
                    "file": model_file.name,
                    "fixes": fixes_count
                })
                results["total_fixes"] += fixes_count
                
                print(f"✅ Fixed {model_file.name} ({fixes_count} primary keys)")
            else:
                results["already_correct"].append(model_file.name)
                
        except Exception as e:
            results["errors"].append({
                "file": model_file.name,
                "error": str(e)
            })
            print(f"❌ Error fixing {model_file.name}: {e}")
    
    return results

def print_fix_report(results):
    """Print comprehensive fix report."""
    
    print("\n" + "=" * 80)
    print("🔧 MODEL AUTOINCREMENT FIX REPORT")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"Files fixed: {len(results['fixed_files'])}")
    print(f"Already correct: {len(results['already_correct'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"Total autoincrement fixes applied: {results['total_fixes']}")
    
    if results["fixed_files"]:
        print(f"\n✅ FIXED FILES ({len(results['fixed_files'])}):")
        for file_info in results["fixed_files"]:
            print(f"  - {file_info['file']} ({file_info['fixes']} primary keys)")
    
    if results["already_correct"]:
        print(f"\n✅ ALREADY CORRECT ({len(results['already_correct'])}):")
        for filename in results["already_correct"]:
            print(f"  - {filename}")
    
    if results["errors"]:
        print(f"\n❌ ERRORS ({len(results['errors'])}):")
        for error_info in results["errors"]:
            print(f"  - {error_info['file']}: {error_info['error']}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    print("🚀 Starting systematic model autoincrement fix...")
    results = fix_model_autoincrement()
    print_fix_report(results)
    
    if results["fixed_files"]:
        print(f"\n🎉 Successfully fixed {results['total_fixes']} primary keys in {len(results['fixed_files'])} model files!")
    else:
        print("\n✅ All models already have proper autoincrement configuration.")