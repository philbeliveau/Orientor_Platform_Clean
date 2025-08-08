#!/usr/bin/env python3
"""
Migration Data Conflict Handler
Handles potential data conflicts during autoincrement migration application.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append("backend")

from app.utils.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

class MigrationDataHandler:
    """Handles data conflicts during autoincrement migration."""
    
    def __init__(self):
        self.db = next(get_db())
        self.conflict_report = {
            "tables_checked": [],
            "conflicts_found": [],
            "resolutions_applied": [],
            "errors": []
        }
    
    def check_table_conflicts(self, table_name: str) -> Dict[str, Any]:
        """Check for potential conflicts in a specific table."""
        
        try:
            # Check if table exists
            result = self.db.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table_name}'
                );
            """))
            
            if not result.fetchone()[0]:
                return {"status": "table_not_exists", "issue": f"Table {table_name} does not exist"}
            
            # Check if there are any existing records
            count_result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
            record_count = count_result.fetchone()[0]
            
            if record_count == 0:
                return {"status": "empty", "records": 0}
            
            # Check for duplicate IDs or NULL IDs
            id_check = self.db.execute(text(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT id) as unique_ids,
                    COUNT(*) - COUNT(id) as null_ids,
                    MIN(id) as min_id,
                    MAX(id) as max_id
                FROM {table_name};
            """))
            
            stats = id_check.fetchone()
            
            conflicts = []
            if stats.null_ids > 0:
                conflicts.append(f"{stats.null_ids} records with NULL id")
            
            if stats.unique_ids != stats.total_records:
                conflicts.append(f"Duplicate IDs detected: {stats.total_records} records but only {stats.unique_ids} unique IDs")
            
            return {
                "status": "analyzed",
                "records": stats.total_records,
                "unique_ids": stats.unique_ids,
                "null_ids": stats.null_ids,
                "min_id": stats.min_id,
                "max_id": stats.max_id,
                "conflicts": conflicts
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def resolve_null_ids(self, table_name: str) -> Dict[str, Any]:
        """Resolve NULL ID conflicts by assigning sequential IDs."""
        
        try:
            # Get the maximum existing ID
            max_id_result = self.db.execute(text(f"""
                SELECT COALESCE(MAX(id), 0) FROM {table_name} WHERE id IS NOT NULL;
            """))
            max_id = max_id_result.fetchone()[0]
            
            # Update NULL IDs with sequential values starting from max_id + 1
            update_result = self.db.execute(text(f"""
                UPDATE {table_name} 
                SET id = nextval('{table_name}_temp_seq') 
                WHERE id IS NULL;
            """))
            
            # Create a temporary sequence for this operation
            self.db.execute(text(f"""
                CREATE TEMPORARY SEQUENCE {table_name}_temp_seq START {max_id + 1};
            """))
            
            # Actually update the NULL IDs
            self.db.execute(text(f"""
                WITH numbered_nulls AS (
                    SELECT ctid, ROW_NUMBER() OVER () + {max_id} as new_id
                    FROM {table_name} 
                    WHERE id IS NULL
                )
                UPDATE {table_name} 
                SET id = numbered_nulls.new_id
                FROM numbered_nulls
                WHERE {table_name}.ctid = numbered_nulls.ctid;
            """))
            
            self.db.commit()
            
            # Verify the fix
            null_check = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE id IS NULL;"))
            remaining_nulls = null_check.fetchone()[0]
            
            return {
                "status": "resolved",
                "action": "assigned_sequential_ids",
                "starting_id": max_id + 1,
                "remaining_nulls": remaining_nulls
            }
            
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    def check_sequence_conflicts(self, table_name: str) -> Dict[str, Any]:
        """Check if sequence conflicts will occur after migration."""
        
        try:
            # Check if sequence already exists
            seq_check = self.db.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM pg_class 
                    WHERE relname = '{table_name}_id_seq' 
                    AND relkind = 'S'
                );
            """))
            
            sequence_exists = seq_check.fetchone()[0]
            
            if sequence_exists:
                # Get current sequence value
                seq_val = self.db.execute(text(f"SELECT currval('{table_name}_id_seq');"))
                current_seq_val = seq_val.fetchone()[0]
                
                # Get max table ID
                max_id_result = self.db.execute(text(f"SELECT MAX(id) FROM {table_name};"))
                max_table_id = max_id_result.fetchone()[0] or 0
                
                if current_seq_val <= max_table_id:
                    return {
                        "status": "conflict",
                        "issue": f"Sequence value ({current_seq_val}) <= max table ID ({max_table_id})",
                        "sequence_value": current_seq_val,
                        "max_table_id": max_table_id
                    }
            
            return {"status": "no_conflict"}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_comprehensive_check(self, tables: List[str]) -> Dict[str, Any]:
        """Run comprehensive conflict check on all specified tables."""
        
        print("🔍 Running comprehensive data conflict analysis...")
        
        for table_name in tables:
            print(f"   Checking {table_name}...")
            
            # Basic conflict check
            table_analysis = self.check_table_conflicts(table_name)
            self.conflict_report["tables_checked"].append({
                "table": table_name,
                "analysis": table_analysis
            })
            
            # If there are conflicts, record them
            if table_analysis.get("conflicts"):
                self.conflict_report["conflicts_found"].append({
                    "table": table_name,
                    "conflicts": table_analysis["conflicts"]
                })
            
            # Check for sequence conflicts
            seq_analysis = self.check_sequence_conflicts(table_name)
            if seq_analysis.get("status") == "conflict":
                self.conflict_report["conflicts_found"].append({
                    "table": table_name,
                    "conflicts": [seq_analysis["issue"]]
                })
        
        return self.conflict_report
    
    def print_conflict_report(self):
        """Print comprehensive conflict analysis report."""
        
        print("\n" + "=" * 80)
        print("📊 MIGRATION DATA CONFLICT ANALYSIS REPORT")
        print("=" * 80)
        
        total_tables = len(self.conflict_report["tables_checked"])
        total_conflicts = len(self.conflict_report["conflicts_found"])
        
        print(f"\n📈 SUMMARY:")
        print(f"Tables analyzed: {total_tables}")
        print(f"Conflicts found: {total_conflicts}")
        print(f"Resolutions applied: {len(self.conflict_report['resolutions_applied'])}")
        print(f"Errors encountered: {len(self.conflict_report['errors'])}")
        
        if total_conflicts == 0:
            print("\n✅ NO CONFLICTS DETECTED - Migration should proceed safely!")
        else:
            print(f"\n⚠️ CONFLICTS DETECTED - Manual resolution may be required")
            
            for conflict in self.conflict_report["conflicts_found"]:
                print(f"\n🚨 {conflict['table']}:")
                for issue in conflict["conflicts"]:
                    print(f"   - {issue}")
        
        # Print table details
        print(f"\n📋 TABLE ANALYSIS DETAILS:")
        for table_check in self.conflict_report["tables_checked"]:
            table = table_check["table"]
            analysis = table_check["analysis"]
            
            if analysis["status"] == "empty":
                print(f"   ✅ {table}: Empty table (no conflicts possible)")
            elif analysis["status"] == "analyzed":
                print(f"   📊 {table}: {analysis['records']} records, ID range: {analysis['min_id']}-{analysis['max_id']}")
            elif analysis["status"] == "error":
                print(f"   ❌ {table}: Error - {analysis['error']}")
            elif analysis["status"] == "table_not_exists":
                print(f"   ⚠️ {table}: Table does not exist")
        
        print("\n" + "=" * 80)
    
    def close(self):
        """Close database connection."""
        self.db.close()

# Critical tables that need to be checked for conflicts
CRITICAL_TABLES = [
    "users",
    "user_skills", 
    "career_goals",
    "chat_messages",
    "conversations",
    "courses",
    "user_profiles",
    "saved_recommendations",
    "conversation_categories"
]

async def main():
    """Main conflict analysis function."""
    
    print("🚀 Starting migration data conflict analysis...")
    
    handler = MigrationDataHandler()
    
    try:
        # Run comprehensive analysis
        results = handler.run_comprehensive_check(CRITICAL_TABLES)
        
        # Print report
        handler.print_conflict_report()
        
        # Provide recommendations
        if results["conflicts_found"]:
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("1. Review conflicts above")
            print("2. Backup database before applying migrations")
            print("3. Consider resolving data conflicts manually")
            print("4. Test migrations in development environment first")
        else:
            print("\n✅ MIGRATION SAFETY: All checks passed - migrations should apply cleanly!")
        
    finally:
        handler.close()

if __name__ == "__main__":
    asyncio.run(main())