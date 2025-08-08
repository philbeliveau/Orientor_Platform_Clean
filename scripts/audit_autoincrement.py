#!/usr/bin/env python3
"""
Database Autoincrement Audit Script
Systematically audits all SQLAlchemy models to identify missing autoincrement on primary keys.
"""

import os
import re
from pathlib import Path

def audit_model_files():
    """Audit all model files for autoincrement issues."""
    
    models_dir = Path("backend/app/models")
    
    results = {
        "broken_models": [],
        "correct_models": [],
        "special_cases": [],
        "total_files": 0
    }
    
    # Pattern to find primary key definitions
    pk_pattern = r'id\s*=\s*Column\(Integer.*?primary_key=True.*?\)'
    autoincrement_pattern = r'autoincrement=True'
    
    for model_file in models_dir.glob("*.py"):
        if model_file.name in ["__init__.py", "base.py"]:
            continue
            
        results["total_files"] += 1
        
        try:
            content = model_file.read_text()
            
            # Skip if no primary key found
            pk_matches = re.findall(pk_pattern, content, re.DOTALL)
            if not pk_matches:
                # Check for special cases like UUID or custom patterns
                if "primary_key=True" in content:
                    results["special_cases"].append({
                        "file": model_file.name,
                        "reason": "Non-Integer primary key or custom pattern"
                    })
                continue
            
            # Check each primary key definition
            for pk_match in pk_matches:
                if "autoincrement=True" in pk_match:
                    results["correct_models"].append({
                        "file": model_file.name,
                        "definition": pk_match.strip()
                    })
                else:
                    results["broken_models"].append({
                        "file": model_file.name,
                        "definition": pk_match.strip(),
                        "line": content[:content.find(pk_match)].count('\n') + 1
                    })
                    
        except Exception as e:
            print(f"Error reading {model_file.name}: {e}")
    
    return results

def print_audit_report(results):
    """Print comprehensive audit report."""
    
    print("=" * 80)
    print("🚨 DATABASE AUTOINCREMENT AUDIT REPORT")
    print("=" * 80)
    
    total = results["total_files"]
    broken = len(results["broken_models"])
    correct = len(results["correct_models"])
    special = len(results["special_cases"])
    
    print(f"\n📊 SUMMARY:")
    print(f"Total model files: {total}")
    print(f"❌ Broken (missing autoincrement): {broken}")
    print(f"✅ Correct (has autoincrement): {correct}")
    print(f"🔄 Special cases: {special}")
    print(f"🚨 Failure rate: {(broken/total)*100:.1f}%")
    
    if results["broken_models"]:
        print(f"\n❌ BROKEN MODELS ({len(results['broken_models'])}):")
        print("-" * 50)
        for model in results["broken_models"]:
            print(f"  {model['file']}:{model['line']}")
            print(f"    {model['definition']}")
            print()
    
    if results["correct_models"]:
        print(f"\n✅ CORRECT MODELS ({len(results['correct_models'])}):")
        print("-" * 50)
        for model in results["correct_models"]:
            print(f"  {model['file']}")
    
    if results["special_cases"]:
        print(f"\n🔄 SPECIAL CASES ({len(results['special_cases'])}):")
        print("-" * 50)
        for model in results["special_cases"]:
            print(f"  {model['file']}: {model['reason']}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    results = audit_model_files()
    print_audit_report(results)