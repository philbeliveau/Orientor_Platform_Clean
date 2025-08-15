#!/usr/bin/env python3
"""
Frontend Component Testing Suite
Tests React components, authentication hooks, error handling, and UI functionality
"""

import asyncio
import json
import sys
import traceback
import subprocess
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class FrontendComponentTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "component_analysis": {},
            "auth_patterns": {},
            "error_handling": {},
            "performance": {},
            "summary": {}
        }
        self.frontend_path = Path(__file__).parent.parent / "frontend"
        self.src_path = self.frontend_path / "src"
        
        # Critical components to analyze
        self.critical_components = [
            "src/app/space/page.tsx",
            "src/app/hexaco-test/page.tsx", 
            "src/app/tests/hexaco/page.tsx",
            "src/app/dashboard/page.tsx",
            "src/app/chat/page.tsx",
            "src/components/SpaceCard.tsx",
            "src/components/EnhancedClassesCard.tsx"
        ]
    
    def test_frontend_structure(self):
        """Test frontend project structure and critical files"""
        try:
            structure_results = {}
            
            # Check if frontend directory exists
            if not self.frontend_path.exists():
                return {
                    "status": "FAIL",
                    "error": "Frontend directory not found",
                    "frontend_path": str(self.frontend_path)
                }
            
            # Check package.json
            package_json = self.frontend_path / "package.json"
            if package_json.exists():
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                structure_results["package_json"] = {
                    "exists": True,
                    "name": package_data.get("name", "unknown"),
                    "dependencies": {
                        "react": package_data.get("dependencies", {}).get("react"),
                        "next": package_data.get("dependencies", {}).get("next"),
                        "@clerk/nextjs": package_data.get("dependencies", {}).get("@clerk/nextjs"),
                        "axios": package_data.get("dependencies", {}).get("axios")
                    },
                    "scripts": list(package_data.get("scripts", {}).keys())
                }
            else:
                structure_results["package_json"] = {"exists": False}
            
            # Check src directory structure
            if self.src_path.exists():
                structure_results["src_structure"] = {
                    "exists": True,
                    "app_dir": (self.src_path / "app").exists(),
                    "components_dir": (self.src_path / "components").exists(),
                    "utils_dir": (self.src_path / "utils").exists()
                }
            else:
                structure_results["src_structure"] = {"exists": False}
            
            # Check for Next.js config files
            nextjs_files = ["next.config.js", "next.config.mjs", "tailwind.config.js", "tsconfig.json"]
            structure_results["config_files"] = {}
            for config_file in nextjs_files:
                config_path = self.frontend_path / config_file
                structure_results["config_files"][config_file] = config_path.exists()
            
            result = {
                "status": "PASS",
                "structure": structure_results,
                "frontend_path": str(self.frontend_path)
            }
            
        except Exception as e:
            result = {
                "status": "FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        self.results["tests"]["frontend_structure"] = result
        return result["status"] == "PASS"
    
    def analyze_component_files(self):
        """Analyze critical component files for common issues"""
        component_results = {}
        
        for component_path in self.critical_components:
            full_path = self.frontend_path / component_path
            
            analysis = {
                "path": component_path,
                "exists": full_path.exists(),
                "issues": [],
                "auth_patterns": {},
                "error_handling": {},
                "performance_patterns": {}
            }
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Analyze authentication patterns
                    analysis["auth_patterns"] = self._analyze_auth_patterns(content)
                    
                    # Analyze error handling
                    analysis["error_handling"] = self._analyze_error_handling(content)
                    
                    # Analyze performance patterns
                    analysis["performance_patterns"] = self._analyze_performance_patterns(content)
                    
                    # Check for common issues
                    analysis["issues"] = self._check_common_issues(content, component_path)
                    
                    # File stats
                    analysis["stats"] = {
                        "lines": len(content.split('\n')),
                        "size_bytes": len(content.encode('utf-8')),
                        "imports_count": len(re.findall(r'^import\s+', content, re.MULTILINE)),
                        "functions_count": len(re.findall(r'(?:const|function)\s+\w+\s*=|function\s+\w+', content))
                    }
                    
                except Exception as e:
                    analysis["error"] = str(e)
                    analysis["issues"].append(f"Failed to read file: {str(e)}")
            else:
                analysis["issues"].append("File does not exist")
            
            component_results[component_path] = analysis
        
        self.results["component_analysis"] = component_results
        return component_results
    
    def _analyze_auth_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze authentication patterns in component"""
        patterns = {
            "useAuth_import": "import { useAuth" in content,
            "useUser_import": "import { useUser" in content,
            "getToken_usage": "getToken" in content,
            "localStorage_access_token": "localStorage.getItem('access_token')" in content,
            "wrong_login_redirect": "router.push('/login')" in content,
            "correct_signin_redirect": "router.push('/sign-in')" in content,
            "auth_loading_check": "isLoaded" in content,
            "signin_check": "isSignedIn" in content,
            "user_object_usage": "user." in content
        }
        
        # Count occurrences
        for pattern_name, pattern_found in patterns.items():
            if isinstance(pattern_found, bool) and pattern_found:
                # Count actual occurrences for boolean patterns
                if pattern_name == "getToken_usage":
                    patterns[f"{pattern_name}_count"] = len(re.findall(r'getToken\s*\(', content))
                elif pattern_name == "localStorage_access_token":
                    patterns[f"{pattern_name}_count"] = len(re.findall(r"localStorage\.getItem\s*\(\s*['\"]access_token['\"]", content))
        
        # Check for proper auth flow
        patterns["has_auth_flow"] = patterns["useAuth_import"] and patterns["getToken_usage"]
        patterns["has_issues"] = patterns["localStorage_access_token"] or patterns["wrong_login_redirect"]
        
        return patterns
    
    def _analyze_error_handling(self, content: str) -> Dict[str, Any]:
        """Analyze error handling patterns"""
        patterns = {
            "try_catch_blocks": len(re.findall(r'try\s*{', content)),
            "catch_blocks": len(re.findall(r'catch\s*\(', content)),
            "error_state_management": "error" in content and ("useState" in content or "Error" in content),
            "axios_error_handling": "axios" in content and ("catch" in content or "error" in content),
            "401_error_handling": "401" in content,
            "loading_states": "loading" in content or "isLoading" in content,
            "defensive_programming": "?." in content,  # Optional chaining
            "null_checks": " && " in content and ("null" in content or "undefined" in content)
        }
        
        # Check for specific error patterns that might cause crashes
        dangerous_patterns = {
            "forEach_on_undefined": re.search(r'\.forEach\s*\(', content) and not re.search(r'Array\.isArray\s*\(', content),
            "direct_property_access": re.search(r'\w+\.\w+\s*(?:&&|\|\|)', content),
            "unguarded_api_responses": "response.data" in content and not ("response.data?" in content or "response?.data" in content)
        }
        
        patterns["dangerous_patterns"] = dangerous_patterns
        patterns["error_safety_score"] = self._calculate_error_safety_score(patterns)
        
        return patterns
    
    def _analyze_performance_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze performance-related patterns"""
        patterns = {
            "useEffect_hooks": len(re.findall(r'useEffect\s*\(', content)),
            "useState_hooks": len(re.findall(r'useState\s*\(', content)),
            "useMemo_hooks": len(re.findall(r'useMemo\s*\(', content)),
            "useCallback_hooks": len(re.findall(r'useCallback\s*\(', content)),
            "api_calls": len(re.findall(r'(?:axios\.|fetch\(|request\()', content)),
            "inline_functions": len(re.findall(r'onClick=\{.*=>', content)),
            "console_logs": len(re.findall(r'console\.log\s*\(', content)),
            "heavy_operations": "JSON.parse" in content or "JSON.stringify" in content
        }
        
        # Performance warnings
        warnings = []
        if patterns["inline_functions"] > 5:
            warnings.append("Many inline functions in JSX - consider useCallback")
        if patterns["useEffect_hooks"] > 10:
            warnings.append("Many useEffect hooks - consider optimization")
        if patterns["console_logs"] > 0:
            warnings.append("Console.log statements found - remove for production")
        
        patterns["performance_warnings"] = warnings
        patterns["optimization_score"] = self._calculate_optimization_score(patterns)
        
        return patterns
    
    def _check_common_issues(self, content: str, file_path: str) -> List[str]:
        """Check for common React/TypeScript issues"""
        issues = []
        
        # Authentication issues
        if "getToken" in content and "import { useAuth" not in content:
            issues.append("Uses getToken() without importing useAuth from @clerk/nextjs")
        
        if "localStorage.getItem('access_token')" in content:
            issues.append("Uses localStorage for token instead of Clerk authentication")
        
        if "router.push('/login')" in content:
            issues.append("Redirects to /login instead of /sign-in")
        
        # Error handling issues
        if ".forEach(" in content and not ("Array.isArray" in content or "?." in content):
            issues.append("Potential forEach error - no array check or optional chaining")
        
        if "response.data" in content and not ("response.data?" in content or "response?.data" in content):
            issues.append("Direct access to response.data without null checks")
        
        # TypeScript issues
        if file_path.endswith('.tsx') and "any" in content:
            issues.append("Uses 'any' type - consider more specific typing")
        
        # Performance issues
        if content.count("useEffect") > 10:
            issues.append("Many useEffect hooks - consider optimization")
        
        if "console.log" in content:
            issues.append("Contains console.log statements")
        
        # Security issues
        if "dangerouslySetInnerHTML" in content:
            issues.append("Uses dangerouslySetInnerHTML - potential XSS risk")
        
        return issues
    
    def _calculate_error_safety_score(self, patterns: Dict[str, Any]) -> int:
        """Calculate error safety score (0-100)"""
        score = 100
        
        # Deduct points for dangerous patterns
        dangerous = patterns.get("dangerous_patterns", {})
        for pattern, exists in dangerous.items():
            if exists:
                score -= 20
        
        # Add points for good practices
        if patterns.get("try_catch_blocks", 0) > 0:
            score += 10
        if patterns.get("defensive_programming"):
            score += 15
        if patterns.get("loading_states"):
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_optimization_score(self, patterns: Dict[str, Any]) -> int:
        """Calculate optimization score (0-100)"""
        score = 100
        
        # Deduct points for performance issues
        if patterns.get("inline_functions", 0) > 5:
            score -= 20
        if patterns.get("console_logs", 0) > 0:
            score -= 10
        if patterns.get("useEffect_hooks", 0) > 10:
            score -= 15
        
        # Add points for optimizations
        if patterns.get("useMemo_hooks", 0) > 0:
            score += 10
        if patterns.get("useCallback_hooks", 0) > 0:
            score += 10
        
        return max(0, min(100, score))
    
    def test_typescript_configuration(self):
        """Test TypeScript configuration and compilation"""
        try:
            # Check tsconfig.json
            tsconfig_path = self.frontend_path / "tsconfig.json"
            if not tsconfig_path.exists():
                return {
                    "status": "FAIL",
                    "error": "tsconfig.json not found"
                }
            
            with open(tsconfig_path, 'r') as f:
                tsconfig_content = f.read()
            
            # Test TypeScript compilation (dry run)
            try:
                # Run tsc --noEmit to check for type errors
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit"],
                    cwd=self.frontend_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                typescript_result = {
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                    "tsconfig_exists": True,
                    "compilation_successful": result.returncode == 0,
                    "type_errors": result.stderr if result.returncode != 0 else None,
                    "stdout": result.stdout if result.stdout else None
                }
                
            except subprocess.TimeoutExpired:
                typescript_result = {
                    "status": "TIMEOUT",
                    "error": "TypeScript compilation timeout"
                }
            except FileNotFoundError:
                typescript_result = {
                    "status": "SKIP",
                    "error": "TypeScript not installed or not in PATH"
                }
            
        except Exception as e:
            typescript_result = {
                "status": "ERROR",
                "error": str(e)
            }
        
        self.results["tests"]["typescript_configuration"] = typescript_result
        return typescript_result.get("status") == "PASS"
    
    def test_build_process(self):
        """Test frontend build process"""
        try:
            # Test if we can run a build
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout for build
            )
            
            build_result = {
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "build_successful": result.returncode == 0,
                "return_code": result.returncode,
                "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0,
                "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0
            }
            
            if result.returncode != 0:
                build_result["error_output"] = result.stderr[:1000]  # First 1000 chars
            
            # Check if build directory was created
            build_dir = self.frontend_path / ".next"
            build_result["build_directory_created"] = build_dir.exists()
            
        except subprocess.TimeoutExpired:
            build_result = {
                "status": "TIMEOUT",
                "error": "Build process timeout after 2 minutes"
            }
        except FileNotFoundError:
            build_result = {
                "status": "SKIP",
                "error": "npm not found - Node.js not installed"
            }
        except Exception as e:
            build_result = {
                "status": "ERROR",
                "error": str(e)
            }
        
        self.results["tests"]["build_process"] = build_result
        return build_result.get("status") == "PASS"
    
    def generate_summary(self):
        """Generate comprehensive frontend testing summary"""
        tests = self.results.get("tests", {})
        components = self.results.get("component_analysis", {})
        
        # Count test results
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests.values() if test.get("status") == "PASS")
        
        # Analyze component health
        component_stats = {
            "total_components": len(components),
            "existing_components": sum(1 for comp in components.values() if comp.get("exists", False)),
            "components_with_auth_issues": 0,
            "components_with_errors": 0,
            "average_error_safety": 0,
            "average_optimization": 0
        }
        
        auth_issues_total = 0
        safety_scores = []
        optimization_scores = []
        
        for comp_path, comp_data in components.items():
            if comp_data.get("exists", False):
                # Count auth issues
                auth_patterns = comp_data.get("auth_patterns", {})
                if auth_patterns.get("has_issues", False):
                    component_stats["components_with_auth_issues"] += 1
                    auth_issues_total += 1
                
                # Count general issues
                issues = comp_data.get("issues", [])
                if issues:
                    component_stats["components_with_errors"] += 1
                
                # Collect scores
                error_handling = comp_data.get("error_handling", {})
                performance = comp_data.get("performance_patterns", {})
                
                if "error_safety_score" in error_handling:
                    safety_scores.append(error_handling["error_safety_score"])
                if "optimization_score" in performance:
                    optimization_scores.append(performance["optimization_score"])
        
        if safety_scores:
            component_stats["average_error_safety"] = sum(safety_scores) / len(safety_scores)
        if optimization_scores:
            component_stats["average_optimization"] = sum(optimization_scores) / len(optimization_scores)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "frontend_structure_ok": tests.get("frontend_structure", {}).get("status") == "PASS",
            "typescript_ok": tests.get("typescript_configuration", {}).get("status") == "PASS",
            "build_ok": tests.get("build_process", {}).get("status") == "PASS",
            "component_stats": component_stats,
            "auth_health": {
                "components_with_auth_issues": component_stats["components_with_auth_issues"],
                "total_auth_issues": auth_issues_total,
                "auth_patterns_clean": auth_issues_total == 0
            },
            "code_quality": {
                "average_error_safety": component_stats["average_error_safety"],
                "average_optimization": component_stats["average_optimization"],
                "safety_grade": self._get_grade(component_stats["average_error_safety"]),
                "performance_grade": self._get_grade(component_stats["average_optimization"])
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if not summary["frontend_structure_ok"]:
            summary["recommendations"].append("🏗️ Fix frontend project structure issues")
        
        if not summary["typescript_ok"]:
            summary["recommendations"].append("📝 Fix TypeScript configuration and type errors")
        
        if not summary["build_ok"]:
            summary["recommendations"].append("🔨 Fix build process issues")
        
        if summary["auth_health"]["components_with_auth_issues"] > 0:
            summary["recommendations"].append(f"🔐 Fix authentication issues in {summary['auth_health']['components_with_auth_issues']} components")
        
        if summary["code_quality"]["safety_grade"] in ["D", "F"]:
            summary["recommendations"].append("⚠️ Improve error handling and safety patterns")
        
        if summary["code_quality"]["performance_grade"] in ["D", "F"]:
            summary["recommendations"].append("🚀 Optimize performance patterns")
        
        if summary["test_pass_rate"] >= 90:
            summary["recommendations"].append("✅ Frontend health is excellent!")
        elif summary["test_pass_rate"] >= 70:
            summary["recommendations"].append("✅ Frontend health is good")
        
        self.results["summary"] = summary
        return summary
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def save_results(self):
        """Save frontend test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"frontend_component_test_results_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Frontend component test results saved to: {filepath}")
        return filepath
    
    async def run_comprehensive_frontend_tests(self):
        """Run complete frontend component testing suite"""
        print("⚛️ Starting Comprehensive Frontend Component Testing...")
        print("=" * 60)
        
        # Test 1: Frontend Structure
        print("1. Testing frontend structure...")
        structure_ok = self.test_frontend_structure()
        print(f"   Result: {'✅ PASS' if structure_ok else '❌ FAIL'}")
        
        # Test 2: Component Analysis
        print("2. Analyzing critical components...")
        components = self.analyze_component_files()
        existing_components = sum(1 for comp in components.values() if comp.get("exists", False))
        print(f"   Result: {existing_components}/{len(components)} components found")
        
        # Test 3: TypeScript Configuration
        print("3. Testing TypeScript configuration...")
        typescript_ok = self.test_typescript_configuration()
        print(f"   Result: {'✅ PASS' if typescript_ok else '❌ FAIL'}")
        
        # Test 4: Build Process
        print("4. Testing build process...")
        build_ok = self.test_build_process()
        print(f"   Result: {'✅ PASS' if build_ok else '❌ FAIL'}")
        
        # Generate Summary
        print("5. Generating summary...")
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("⚛️ FRONTEND COMPONENT TESTING SUMMARY")
        print("=" * 60)
        print(f"Test Pass Rate: {summary['passed_tests']}/{summary['total_tests']} ({summary['test_pass_rate']:.1f}%)")
        print(f"Frontend Structure: {'✅ OK' if summary['frontend_structure_ok'] else '❌ BROKEN'}")
        print(f"TypeScript: {'✅ OK' if summary['typescript_ok'] else '❌ BROKEN'}")
        print(f"Build Process: {'✅ OK' if summary['build_ok'] else '❌ BROKEN'}")
        
        print(f"\n📦 Component Health:")
        print(f"   Components Found: {summary['component_stats']['existing_components']}/{summary['component_stats']['total_components']}")
        print(f"   Auth Issues: {summary['auth_health']['components_with_auth_issues']} components")
        print(f"   Error Safety: {summary['code_quality']['average_error_safety']:.1f}/100 (Grade: {summary['code_quality']['safety_grade']})")
        print(f"   Performance: {summary['code_quality']['average_optimization']:.1f}/100 (Grade: {summary['code_quality']['performance_grade']})")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"• {rec}")
        
        # Save results
        filepath = self.save_results()
        
        return self.results

def main():
    """Main execution function"""
    tester = FrontendComponentTester()
    
    try:
        # Run frontend tests
        results = asyncio.run(tester.run_comprehensive_frontend_tests())
        
        # Exit code based on results
        summary = results["summary"]
        if summary["test_pass_rate"] >= 90 and summary["code_quality"]["safety_grade"] in ["A", "B"]:
            sys.exit(0)  # Excellent
        elif summary["test_pass_rate"] >= 70:
            sys.exit(1)  # Good but could be better
        else:
            sys.exit(2)  # Needs attention
            
    except Exception as e:
        print(f"❌ Frontend component testing failed: {str(e)}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()