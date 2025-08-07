"""
Router Migration and Standardization System
==========================================

This module provides automated router migration to the unified secure authentication system.
It handles:
1. Updating import statements to use standardized secure authentication
2. Converting legacy authentication patterns
3. Validating router compatibility
4. Providing rollback mechanisms

SECURITY IMPROVEMENTS:
- Standardized authentication across all 41+ routers  
- Consistent error handling and logging
- Integrated caching and performance optimization
- Rollback support for zero-downtime deployment
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# MIGRATION CONFIGURATION
# ============================================================================

@dataclass
class RouterMigrationConfig:
    """Configuration for router migration process"""
    backup_enabled: bool = True
    backup_directory: str = "router_backups"
    dry_run: bool = False
    validate_imports: bool = True
    update_tests: bool = True
    create_migration_log: bool = True

@dataclass
class RouterInfo:
    """Information about a router file"""
    file_path: str
    current_import: str
    auth_pattern: str
    needs_migration: bool
    complexity_score: int
    dependencies: List[str]

# ============================================================================
# AUTHENTICATION PATTERNS
# ============================================================================

class AuthPatterns:
    """Authentication patterns for router standardization"""
    
    # Target pattern - what we want all routers to use
    SECURE_INTEGRATED = {
        "import": "from app.utils.secure_auth_integration import get_current_user_secure_integrated as get_current_user",
        "dependency": "current_user: User = Depends(get_current_user)",
        "description": "Secure integrated authentication with full optimization"
    }
    
    # Rollback pattern - fallback for compatibility
    ROLLBACK_COMPATIBLE = {
        "import": "from app.utils.secure_auth_integration import get_current_user_with_rollback as get_current_user", 
        "dependency": "current_user: User = Depends(get_current_user)",
        "description": "Secure authentication with automatic rollback support"
    }
    
    # Legacy patterns that need to be updated
    LEGACY_PATTERNS = [
        {
            "pattern": r"from app\.utils\.clerk_auth import get_current_user_with_db_sync as get_current_user",
            "type": "clerk_db_sync",
            "description": "Clerk with database sync (current standard)"
        },
        {
            "pattern": r"from app\.utils\.clerk_auth import get_current_user",
            "type": "clerk_direct",
            "description": "Direct Clerk import"
        },
        {
            "pattern": r"def get_current_user\(.*token.*oauth2_scheme.*\)",
            "type": "legacy_jwt",
            "description": "Legacy JWT implementation"
        },
        {
            "pattern": r"from app\.utils\.optimized_clerk_auth import",
            "type": "optimized_clerk",
            "description": "Optimized Clerk authentication"
        }
    ]

# ============================================================================
# ROUTER ANALYZER
# ============================================================================

class RouterAnalyzer:
    """Analyzes router files to determine migration requirements"""
    
    def __init__(self, router_directory: str = "backend/app/routers"):
        self.router_directory = Path(router_directory)
        self.analyzed_routers: Dict[str, RouterInfo] = {}
    
    def analyze_all_routers(self) -> Dict[str, RouterInfo]:
        """Analyze all router files in the directory"""
        router_files = list(self.router_directory.glob("*.py"))
        router_files = [f for f in router_files if f.name != "__init__.py"]
        
        logger.info(f"🔍 Analyzing {len(router_files)} router files")
        
        for router_file in router_files:
            try:
                router_info = self._analyze_router_file(router_file)
                self.analyzed_routers[router_file.name] = router_info
            except Exception as e:
                logger.error(f"Failed to analyze {router_file.name}: {str(e)}")
        
        return self.analyzed_routers
    
    def _analyze_router_file(self, file_path: Path) -> RouterInfo:
        """Analyze a single router file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect current authentication pattern
        current_import = self._detect_auth_import(content)
        auth_pattern = self._classify_auth_pattern(current_import)
        needs_migration = self._needs_migration(auth_pattern, content)
        complexity_score = self._calculate_complexity(content)
        dependencies = self._extract_dependencies(content)
        
        return RouterInfo(
            file_path=str(file_path),
            current_import=current_import,
            auth_pattern=auth_pattern,
            needs_migration=needs_migration,
            complexity_score=complexity_score,
            dependencies=dependencies
        )
    
    def _detect_auth_import(self, content: str) -> str:
        """Detect the current authentication import statement"""
        # Look for authentication-related imports
        import_patterns = [
            r"from app\.utils\.clerk_auth import .*get_current_user.*",
            r"from app\.utils\.optimized_clerk_auth import .*",
            r"from app\.utils\.secure_auth import .*",
            r"def get_current_user\(.*\):"
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                return matches[0]
        
        return "none_detected"
    
    def _classify_auth_pattern(self, import_statement: str) -> str:
        """Classify the authentication pattern type"""
        for legacy_pattern in AuthPatterns.LEGACY_PATTERNS:
            if re.search(legacy_pattern["pattern"], import_statement):
                return legacy_pattern["type"]
        
        if "secure_auth_integration" in import_statement:
            return "secure_integrated"
        
        return "unknown"
    
    def _needs_migration(self, auth_pattern: str, content: str) -> bool:
        """Determine if the router needs migration"""
        if auth_pattern == "secure_integrated":
            return False  # Already using target pattern
        
        if auth_pattern == "unknown":
            # Check if it has any authentication at all
            return "Depends(get_current_user)" in content or "current_user:" in content
        
        return True
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate complexity score (1-10) based on various factors"""
        score = 1
        
        # Lines of code
        lines = len(content.split('\n'))
        if lines > 500:
            score += 3
        elif lines > 200:
            score += 2
        elif lines > 100:
            score += 1
        
        # Number of endpoints
        endpoint_count = len(re.findall(r"@router\.(get|post|put|delete|patch)", content))
        if endpoint_count > 10:
            score += 2
        elif endpoint_count > 5:
            score += 1
        
        # Complex authentication patterns
        if "oauth2_scheme" in content:
            score += 2
        if "JWT" in content or "jwt" in content:
            score += 1
        
        # Database operations
        if ".query(" in content or ".filter(" in content:
            score += 1
        
        return min(score, 10)
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies (imports) from the file"""
        dependencies = []
        
        # Find all import statements
        import_matches = re.findall(r"^from ([\w\.]+) import", content, re.MULTILINE)
        dependencies.extend(import_matches)
        
        import_matches = re.findall(r"^import ([\w\.]+)", content, re.MULTILINE)
        dependencies.extend(import_matches)
        
        return list(set(dependencies))

# ============================================================================
# ROUTER MIGRATOR
# ============================================================================

class RouterMigrator:
    """Handles the actual migration of router files"""
    
    def __init__(self, config: RouterMigrationConfig):
        self.config = config
        self.migration_log: List[str] = []
        
    def migrate_all_routers(self, router_info: Dict[str, RouterInfo]) -> Dict[str, Any]:
        """Migrate all routers that need migration"""
        results = {
            "successful_migrations": [],
            "failed_migrations": [],
            "skipped_routers": [],
            "total_routers": len(router_info)
        }
        
        # Create backup directory if needed
        if self.config.backup_enabled:
            backup_dir = Path(self.config.backup_directory)
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_path = backup_dir / f"migration_{timestamp}"
            self.backup_path.mkdir()
        
        for router_name, info in router_info.items():
            try:
                if not info.needs_migration:
                    results["skipped_routers"].append(router_name)
                    self._log(f"✅ {router_name}: Already using secure authentication")
                    continue
                
                success = self._migrate_single_router(info)
                if success:
                    results["successful_migrations"].append(router_name)
                    self._log(f"✅ {router_name}: Successfully migrated")
                else:
                    results["failed_migrations"].append(router_name)
                    self._log(f"❌ {router_name}: Migration failed")
                    
            except Exception as e:
                results["failed_migrations"].append(router_name)
                self._log(f"❌ {router_name}: Migration error - {str(e)}")
        
        # Save migration log
        if self.config.create_migration_log:
            self._save_migration_log()
        
        return results
    
    def _migrate_single_router(self, router_info: RouterInfo) -> bool:
        """Migrate a single router file"""
        file_path = Path(router_info.file_path)
        
        # Create backup if enabled
        if self.config.backup_enabled:
            backup_file = self.backup_path / file_path.name
            shutil.copy2(file_path, backup_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Apply migration transformations
            migrated_content = self._apply_migration_transforms(original_content, router_info)
            
            if self.config.dry_run:
                self._log(f"DRY RUN: Would update {file_path.name}")
                return True
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(migrated_content)
            
            # Validate the migration if requested
            if self.config.validate_imports:
                validation_result = self._validate_migration(file_path)
                if not validation_result:
                    # Rollback on validation failure
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate {file_path.name}: {str(e)}")
            return False
    
    def _apply_migration_transforms(self, content: str, router_info: RouterInfo) -> str:
        """Apply migration transformations to router content"""
        migrated_content = content
        
        # 1. Update import statements
        migrated_content = self._update_auth_imports(migrated_content, router_info)
        
        # 2. Update function signatures if needed
        migrated_content = self._update_function_signatures(migrated_content, router_info)
        
        # 3. Add error handling improvements
        migrated_content = self._add_error_handling(migrated_content, router_info)
        
        # 4. Add migration comment
        migration_comment = f"""
# ============================================================================
# AUTHENTICATION MIGRATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================================
# This file has been automatically migrated to use the unified secure 
# authentication system with integrated caching and security optimizations.
# 
# Previous pattern: {router_info.auth_pattern}
# Current pattern: secure_integrated
# Migration complexity: {router_info.complexity_score}/10
# ============================================================================

"""
        # Add comment at the top after any existing docstrings
        if '"""' in migrated_content:
            # Find the end of the module docstring
            docstring_end = migrated_content.find('"""', migrated_content.find('"""') + 3) + 3
            migrated_content = migrated_content[:docstring_end] + migration_comment + migrated_content[docstring_end:]
        else:
            migrated_content = migration_comment + migrated_content
        
        return migrated_content
    
    def _update_auth_imports(self, content: str, router_info: RouterInfo) -> str:
        """Update authentication import statements"""
        # Remove old imports
        old_import_patterns = [
            r"from app\.utils\.clerk_auth import.*get_current_user.*\n",
            r"from app\.utils\.optimized_clerk_auth import.*\n",
            r"from app\.utils\.secure_auth import.*\n"
        ]
        
        for pattern in old_import_patterns:
            content = re.sub(pattern, "", content, flags=re.MULTILINE)
        
        # Add new secure import
        new_import = AuthPatterns.SECURE_INTEGRATED["import"]
        
        # Find a good place to insert the import (after other app imports)
        import_insertion_point = content.find("from ..") 
        if import_insertion_point == -1:
            import_insertion_point = content.find("from fastapi")
        
        if import_insertion_point != -1:
            # Find the end of the current import block
            lines = content.split('\n')
            insert_line = 0
            for i, line in enumerate(lines):
                if line.startswith(('from ', 'import ')) and 'fastapi' in line:
                    insert_line = i + 1
                elif insert_line > 0 and not line.startswith(('from ', 'import ')) and line.strip():
                    break
                    
            lines.insert(insert_line, new_import)
            content = '\n'.join(lines)
        else:
            # Add at the beginning if no good insertion point found
            content = new_import + "\n\n" + content
        
        return content
    
    def _update_function_signatures(self, content: str, router_info: RouterInfo) -> str:
        """Update function signatures to use standardized authentication"""
        # This handles legacy JWT authentication patterns
        if router_info.auth_pattern == "legacy_jwt":
            # Replace legacy JWT function definitions
            legacy_pattern = r"def get_current_user\(token: str = Depends\(oauth2_scheme\), db: Session = Depends\(get_db\)\):[^}]*?return user"
            if re.search(legacy_pattern, content, re.DOTALL):
                # Remove the entire legacy function and replace with import
                content = re.sub(legacy_pattern, "", content, flags=re.DOTALL)
                self._log("Removed legacy JWT authentication function")
        
        return content
    
    def _add_error_handling(self, content: str, router_info: RouterInfo) -> str:
        """Add improved error handling for authentication"""
        # This is a placeholder for additional error handling improvements
        # In a full implementation, this would add try-catch blocks and
        # standardized error responses
        return content
    
    def _validate_migration(self, file_path: Path) -> bool:
        """Validate that the migration was successful"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that the new import is present
            if "secure_auth_integration" not in content:
                self._log(f"Validation failed: Missing secure auth import in {file_path.name}")
                return False
            
            # Check for syntax errors by attempting to parse
            import ast
            try:
                ast.parse(content)
            except SyntaxError as e:
                self._log(f"Validation failed: Syntax error in {file_path.name}: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            self._log(f"Validation error for {file_path.name}: {str(e)}")
            return False
    
    def _log(self, message: str) -> None:
        """Add message to migration log"""
        self.migration_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        logger.info(message)
    
    def _save_migration_log(self) -> None:
        """Save migration log to file"""
        if hasattr(self, 'backup_path'):
            log_file = self.backup_path / "migration_log.txt"
        else:
            log_file = Path("migration_log.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("Router Migration Log\n")
            f.write("===================\n\n")
            f.write(f"Migration started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for log_entry in self.migration_log:
                f.write(log_entry + "\n")

# ============================================================================
# MIGRATION ORCHESTRATOR
# ============================================================================

class MigrationOrchestrator:
    """Orchestrates the complete router migration process"""
    
    def __init__(self, router_directory: str = "backend/app/routers"):
        self.router_directory = router_directory
        self.analyzer = RouterAnalyzer(router_directory)
    
    def execute_migration(self, config: Optional[RouterMigrationConfig] = None) -> Dict[str, Any]:
        """Execute the complete migration process"""
        if config is None:
            config = RouterMigrationConfig()
        
        migrator = RouterMigrator(config)
        
        logger.info("🚀 Starting router migration to secure authentication system")
        
        # Step 1: Analyze all routers
        router_info = self.analyzer.analyze_all_routers()
        
        # Step 2: Generate migration plan
        migration_plan = self._generate_migration_plan(router_info)
        
        # Step 3: Execute migration
        if not config.dry_run:
            migration_results = migrator.migrate_all_routers(router_info)
        else:
            migration_results = self._simulate_migration(router_info)
        
        # Step 4: Generate migration report
        report = self._generate_migration_report(router_info, migration_results, migration_plan)
        
        logger.info("✅ Router migration completed")
        
        return report
    
    def _generate_migration_plan(self, router_info: Dict[str, RouterInfo]) -> Dict[str, Any]:
        """Generate a migration plan based on router analysis"""
        plan = {
            "total_routers": len(router_info),
            "routers_needing_migration": 0,
            "migration_by_complexity": {"low": [], "medium": [], "high": []},
            "migration_by_pattern": {},
            "estimated_time_minutes": 0
        }
        
        for router_name, info in router_info.items():
            if info.needs_migration:
                plan["routers_needing_migration"] += 1
                
                # Classify by complexity
                if info.complexity_score <= 3:
                    plan["migration_by_complexity"]["low"].append(router_name)
                elif info.complexity_score <= 6:
                    plan["migration_by_complexity"]["medium"].append(router_name)
                else:
                    plan["migration_by_complexity"]["high"].append(router_name)
                
                # Group by pattern
                if info.auth_pattern not in plan["migration_by_pattern"]:
                    plan["migration_by_pattern"][info.auth_pattern] = []
                plan["migration_by_pattern"][info.auth_pattern].append(router_name)
        
        # Estimate migration time (rough estimates)
        plan["estimated_time_minutes"] = (
            len(plan["migration_by_complexity"]["low"]) * 2 +
            len(plan["migration_by_complexity"]["medium"]) * 5 +
            len(plan["migration_by_complexity"]["high"]) * 10
        )
        
        return plan
    
    def _simulate_migration(self, router_info: Dict[str, RouterInfo]) -> Dict[str, Any]:
        """Simulate migration for dry run"""
        return {
            "successful_migrations": [name for name, info in router_info.items() if info.needs_migration],
            "failed_migrations": [],
            "skipped_routers": [name for name, info in router_info.items() if not info.needs_migration],
            "total_routers": len(router_info)
        }
    
    def _generate_migration_report(self, router_info: Dict[str, RouterInfo], 
                                 migration_results: Dict[str, Any], 
                                 migration_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        return {
            "migration_plan": migration_plan,
            "migration_results": migration_results,
            "router_analysis": {
                name: {
                    "auth_pattern": info.auth_pattern,
                    "complexity_score": info.complexity_score,
                    "needs_migration": info.needs_migration,
                    "migration_status": self._get_migration_status(name, migration_results)
                }
                for name, info in router_info.items()
            },
            "summary": {
                "total_routers": len(router_info),
                "successful_migrations": len(migration_results["successful_migrations"]),
                "failed_migrations": len(migration_results["failed_migrations"]),
                "skipped_routers": len(migration_results["skipped_routers"]),
                "success_rate": len(migration_results["successful_migrations"]) / 
                              max(1, len(migration_results["successful_migrations"]) + len(migration_results["failed_migrations"])) * 100
            }
        }
    
    def _get_migration_status(self, router_name: str, migration_results: Dict[str, Any]) -> str:
        """Get migration status for a specific router"""
        if router_name in migration_results["successful_migrations"]:
            return "migrated"
        elif router_name in migration_results["failed_migrations"]:
            return "failed"
        elif router_name in migration_results["skipped_routers"]:
            return "skipped"
        else:
            return "unknown"

# ============================================================================
# CLI INTERFACE AND UTILITIES
# ============================================================================

def quick_migration(dry_run: bool = True, backup_enabled: bool = True) -> Dict[str, Any]:
    """Quick migration with default settings"""
    config = RouterMigrationConfig(
        dry_run=dry_run,
        backup_enabled=backup_enabled,
        validate_imports=True,
        create_migration_log=True
    )
    
    orchestrator = MigrationOrchestrator()
    return orchestrator.execute_migration(config)

def get_migration_status() -> Dict[str, Any]:
    """Get current migration status without making changes"""
    analyzer = RouterAnalyzer()
    router_info = analyzer.analyze_all_routers()
    
    status = {
        "total_routers": len(router_info),
        "secure_integrated": 0,
        "needs_migration": 0,
        "patterns": {}
    }
    
    for info in router_info.values():
        if info.auth_pattern == "secure_integrated":
            status["secure_integrated"] += 1
        elif info.needs_migration:
            status["needs_migration"] += 1
            
        if info.auth_pattern not in status["patterns"]:
            status["patterns"][info.auth_pattern] = 0
        status["patterns"][info.auth_pattern] += 1
    
    return status

if __name__ == "__main__":
    # Example usage
    print("Router Migration System")
    print("======================")
    
    # Get current status
    status = get_migration_status()
    print(f"Current status: {status['secure_integrated']}/{status['total_routers']} routers using secure authentication")
    
    # Run dry run migration
    print("\nRunning dry run migration...")
    results = quick_migration(dry_run=True)
    print(f"Migration plan: {results['summary']}")