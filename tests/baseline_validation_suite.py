#!/usr/bin/env python3
"""
Baseline Platform Validation Suite
Establishes current platform health metrics before standardization fixes
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
import subprocess
import requests
import os

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

class BaselineValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "patterns": {},
            "recommendations": []
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
    
    def test_prisma_connectivity(self):
        """Test if Prisma client can be imported and initialized"""
        try:
            # Test Prisma import
            from prisma import Prisma
            result = {
                "status": "PASS",
                "message": "Prisma client import successful",
                "details": "✅ Prisma connectivity confirmed"
            }
            
            # Try to create Prisma instance
            prisma = Prisma()
            result["prisma_instance"] = "✅ Prisma instance created"
            
        except Exception as e:
            result = {
                "status": "FAIL", 
                "message": f"Prisma connectivity failed: {str(e)}",
                "details": traceback.format_exc()
            }
        
        self.results["tests"]["prisma_connectivity"] = result
        return result["status"] == "PASS"
    
    def scan_pattern_violations(self):
        """Scan for critical pattern violations"""
        patterns = {}
        
        # Pattern 1: Function signature mismatches
        try:
            cmd = ["find", "./backend", "-name", "*.py", "-exec", "grep", "-l", "def.*db: Session", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            session_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            patterns["function_signature_mismatches"] = {
                "count": len([f for f in session_files if f]),
                "files": session_files,
                "severity": "P0_CRITICAL",
                "description": "Services expect SQLAlchemy Session but routers inject Prisma"
            }
        except Exception as e:
            patterns["function_signature_mismatches"] = {"error": str(e)}
        
        # Pattern 2: SQLAlchemy execute calls
        try:
            cmd = ["find", "./backend", "-name", "*.py", "-exec", "grep", "-l", "db\\.execute\\|\\.execute(", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            execute_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            patterns["sqlalchemy_execute_calls"] = {
                "count": len([f for f in execute_files if f]),
                "files": execute_files,
                "severity": "P0_CRITICAL", 
                "description": "SQLAlchemy execute() called on Prisma clients"
            }
        except Exception as e:
            patterns["sqlalchemy_execute_calls"] = {"error": str(e)}
        
        # Pattern 3: Frontend localStorage usage
        try:
            cmd = ["find", "./frontend/src", "-name", "*.tsx", "-exec", "grep", "-l", "localStorage.getItem.*access_token", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            localstorage_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            patterns["frontend_localstorage_tokens"] = {
                "count": len([f for f in localstorage_files if f and f != ""]),
                "files": [f for f in localstorage_files if f and f != ""],
                "severity": "P1_HIGH",
                "description": "Components using localStorage instead of Clerk tokens"
            }
        except Exception as e:
            patterns["frontend_localstorage_tokens"] = {"error": str(e)}
        
        # Pattern 4: Old login route redirects
        try:
            cmd = ["find", "./frontend/src", "-name", "*.tsx", "-exec", "grep", "-l", "router.push('/login')", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            old_route_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            patterns["old_login_routes"] = {
                "count": len([f for f in old_route_files if f and f != ""]),
                "files": [f for f in old_route_files if f and f != ""],
                "severity": "P1_HIGH",
                "description": "Components redirecting to /login instead of /sign-in"
            }
        except Exception as e:
            patterns["old_login_routes"] = {"error": str(e)}
        
        self.results["patterns"] = patterns
        return patterns
    
    def test_critical_endpoints(self):
        """Test critical API endpoints that are likely to break"""
        endpoints = {
            "/api/v1/hexaco-test/questions": "HEXACO test questions",
            "/health": "Health check endpoint",
            "/api/v1/users/me": "Current user profile",
        }
        
        endpoint_results = {}
        
        for endpoint, description in endpoints.items():
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                endpoint_results[endpoint] = {
                    "status": "PASS" if response.status_code < 500 else "FAIL",
                    "status_code": response.status_code,
                    "description": description,
                    "response_time": response.elapsed.total_seconds()
                }
            except requests.exceptions.ConnectionError:
                endpoint_results[endpoint] = {
                    "status": "SKIP",
                    "message": "Backend server not running",
                    "description": description
                }
            except Exception as e:
                endpoint_results[endpoint] = {
                    "status": "FAIL",
                    "message": str(e),
                    "description": description
                }
        
        self.results["tests"]["critical_endpoints"] = endpoint_results
        return endpoint_results
    
    def test_database_models(self):
        """Test if key database models can be imported"""
        models_to_test = [
            "app.models.user",
            "app.models.career_goal", 
            "app.models.saved_recommendation",
            "app.models.personality_profiles"
        ]
        
        model_results = {}
        
        for model_name in models_to_test:
            try:
                __import__(model_name)
                model_results[model_name] = {
                    "status": "PASS",
                    "message": "Model imported successfully"
                }
            except Exception as e:
                model_results[model_name] = {
                    "status": "FAIL",
                    "message": str(e)
                }
        
        self.results["tests"]["database_models"] = model_results
        return model_results
    
    def generate_summary(self):
        """Generate overall health summary"""
        patterns = self.results.get("patterns", {})
        
        # Count critical issues
        p0_issues = 0
        p1_issues = 0
        
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, dict) and "severity" in pattern_data:
                if pattern_data["severity"] == "P0_CRITICAL":
                    p0_issues += pattern_data.get("count", 0)
                elif pattern_data["severity"] == "P1_HIGH":
                    p1_issues += pattern_data.get("count", 0)
        
        # Assess overall health
        if p0_issues > 50:
            health_status = "CRITICAL"
        elif p0_issues > 20:
            health_status = "POOR"
        elif p0_issues > 5:
            health_status = "NEEDS_ATTENTION"
        else:
            health_status = "GOOD"
        
        summary = {
            "overall_health": health_status,
            "p0_critical_issues": p0_issues,
            "p1_high_issues": p1_issues,
            "total_issues": p0_issues + p1_issues,
            "prisma_connectivity": self.results["tests"].get("prisma_connectivity", {}).get("status", "UNKNOWN"),
            "recommendations": []
        }
        
        # Generate recommendations
        if p0_issues > 0:
            summary["recommendations"].append(f"URGENT: Fix {p0_issues} P0 critical issues before proceeding")
        
        if patterns.get("function_signature_mismatches", {}).get("count", 0) > 0:
            summary["recommendations"].append("Priority 1: Fix function signature mismatches")
        
        if patterns.get("sqlalchemy_execute_calls", {}).get("count", 0) > 0:
            summary["recommendations"].append("Priority 2: Convert SQLAlchemy execute calls to Prisma")
        
        if p1_issues == 0:
            summary["recommendations"].append("✅ Frontend authentication patterns look clean")
        
        self.results["summary"] = summary
        return summary
    
    def save_results(self):
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"baseline_validation_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {filepath}")
        return filepath
    
    async def run_full_validation(self):
        """Run complete baseline validation suite"""
        print("🔍 Starting Baseline Platform Validation...")
        print("=" * 50)
        
        # Test 1: Prisma Connectivity
        print("1. Testing Prisma connectivity...")
        prisma_ok = self.test_prisma_connectivity()
        print(f"   Result: {'✅ PASS' if prisma_ok else '❌ FAIL'}")
        
        # Test 2: Pattern Violations 
        print("2. Scanning for pattern violations...")
        patterns = self.scan_pattern_violations()
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, dict) and "count" in pattern_data:
                count = pattern_data["count"]
                severity = pattern_data.get("severity", "UNKNOWN")
                print(f"   {pattern_name}: {count} instances ({severity})")
        
        # Test 3: Critical Endpoints
        print("3. Testing critical endpoints...")
        endpoints = self.test_critical_endpoints()
        for endpoint, result in endpoints.items():
            status = result.get("status", "UNKNOWN")
            print(f"   {endpoint}: {status}")
        
        # Test 4: Database Models
        print("4. Testing database models...")
        models = self.test_database_models()
        for model, result in models.items():
            status = result.get("status", "UNKNOWN")
            print(f"   {model}: {status}")
        
        # Generate Summary
        print("5. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 50)
        print("📊 BASELINE VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Overall Health: {summary['overall_health']}")
        print(f"P0 Critical Issues: {summary['p0_critical_issues']}")
        print(f"P1 High Issues: {summary['p1_high_issues']}")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Prisma Connectivity: {summary['prisma_connectivity']}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    validator = BaselineValidator()
    
    try:
        # Run validation
        results = asyncio.run(validator.run_full_validation())
        
        # Exit code based on health
        health = results["summary"]["overall_health"]
        if health == "CRITICAL":
            sys.exit(2)
        elif health in ["POOR", "NEEDS_ATTENTION"]:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()