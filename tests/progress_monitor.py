#!/usr/bin/env python3
"""
Progress Monitoring Dashboard
Tracks standardization progress and validates fixes in real-time
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import requests

class ProgressMonitor:
    def __init__(self):
        self.baseline_file = None
        self.current_metrics = {}
        self.progress_log = []
        
    def load_baseline(self):
        """Load baseline metrics from latest validation results"""
        test_dir = Path(__file__).parent
        baseline_files = list(test_dir.glob("baseline_validation_results_*.json"))
        
        if baseline_files:
            # Get most recent baseline
            latest_baseline = max(baseline_files, key=lambda p: p.stat().st_mtime)
            with open(latest_baseline) as f:
                self.baseline_file = json.load(f)
            print(f"📊 Loaded baseline from: {latest_baseline.name}")
        else:
            print("⚠️  No baseline file found. Run baseline_validation_suite.py first.")
    
    def count_pattern_violations(self) -> Dict[str, int]:
        """Count current pattern violations"""
        violations = {}
        
        try:
            # Pattern 1: Function signature mismatches
            cmd = ["find", "./backend", "-name", "*.py", "-exec", "grep", "-l", "def.*db: Session", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            session_files = [f for f in result.stdout.strip().split('\n') if f]
            violations["function_signature_mismatches"] = len(session_files)
            
            # Pattern 2: SQLAlchemy execute calls
            cmd = ["find", "./backend", "-name", "*.py", "-exec", "grep", "-l", "db\\.execute\\|\\.execute(", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            execute_files = [f for f in result.stdout.strip().split('\n') if f]
            violations["sqlalchemy_execute_calls"] = len(execute_files)
            
            # Pattern 3: from_orm usage
            cmd = ["find", "./backend", "-name", "*.py", "-exec", "grep", "-l", "from_orm(", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            from_orm_files = [f for f in result.stdout.strip().split('\n') if f]
            violations["from_orm_patterns"] = len(from_orm_files)
            
            # Pattern 4: Frontend localStorage tokens
            cmd = ["find", "./frontend/src", "-name", "*.tsx", "-exec", "grep", "-l", "localStorage.getItem.*access_token", "{}", ";"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            localstorage_files = [f for f in result.stdout.strip().split('\n') if f and f != ""]
            violations["frontend_localstorage_tokens"] = len(localstorage_files)
            
        except Exception as e:
            violations["error"] = str(e)
        
        return violations
    
    def test_critical_functionality(self) -> Dict[str, Any]:
        """Test critical platform functionality"""
        tests = {}
        backend_url = "http://localhost:8000"
        
        # Test 1: Prisma connectivity
        try:
            from prisma import Prisma
            prisma = Prisma()
            tests["prisma_connectivity"] = {"status": "PASS", "message": "✅ Prisma import OK"}
        except Exception as e:
            tests["prisma_connectivity"] = {"status": "FAIL", "message": f"❌ {str(e)}"}
        
        # Test 2: Critical API endpoints
        endpoints = {
            "/health": "Health check",
            "/api/v1/hexaco-test/questions": "HEXACO questions",
        }
        
        for endpoint, description in endpoints.items():
            try:
                response = requests.get(f"{backend_url}{endpoint}", timeout=3)
                if response.status_code < 500:
                    tests[f"api_{endpoint.replace('/', '_')}"] = {
                        "status": "PASS", 
                        "code": response.status_code,
                        "description": description
                    }
                else:
                    tests[f"api_{endpoint.replace('/', '_')}"] = {
                        "status": "FAIL", 
                        "code": response.status_code,
                        "description": description
                    }
            except requests.exceptions.ConnectionError:
                tests[f"api_{endpoint.replace('/', '_')}"] = {
                    "status": "SKIP", 
                    "message": "Server not running",
                    "description": description
                }
            except Exception as e:
                tests[f"api_{endpoint.replace('/', '_')}"] = {
                    "status": "ERROR", 
                    "message": str(e),
                    "description": description
                }
        
        return tests
    
    def calculate_progress(self) -> Dict[str, Any]:
        """Calculate progress against baseline"""
        if not self.baseline_file:
            return {"error": "No baseline loaded"}
        
        current_violations = self.count_pattern_violations()
        baseline_patterns = self.baseline_file.get("patterns", {})
        
        progress = {}
        
        for pattern_name in ["function_signature_mismatches", "sqlalchemy_execute_calls"]:
            baseline_count = baseline_patterns.get(pattern_name, {}).get("count", 0)
            current_count = current_violations.get(pattern_name, 0)
            
            if baseline_count > 0:
                reduction = baseline_count - current_count
                percentage = (reduction / baseline_count) * 100
                progress[pattern_name] = {
                    "baseline": baseline_count,
                    "current": current_count,
                    "reduced": reduction,
                    "progress_percentage": round(percentage, 1)
                }
            else:
                progress[pattern_name] = {
                    "baseline": 0,
                    "current": current_count,
                    "progress_percentage": 100.0 if current_count == 0 else 0.0
                }
        
        # Calculate overall progress
        total_baseline = sum(p.get("baseline", 0) for p in progress.values())
        total_current = sum(p.get("current", 0) for p in progress.values())
        
        if total_baseline > 0:
            overall_progress = ((total_baseline - total_current) / total_baseline) * 100
        else:
            overall_progress = 100.0 if total_current == 0 else 0.0
        
        progress["overall"] = {
            "total_baseline_issues": total_baseline,
            "total_current_issues": total_current,
            "overall_progress_percentage": round(overall_progress, 1)
        }
        
        return progress
    
    def generate_status_report(self) -> str:
        """Generate current status report"""
        violations = self.count_pattern_violations()
        functionality = self.test_critical_functionality()
        progress = self.calculate_progress()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
🔍 STANDARDIZATION PROGRESS REPORT
Generated: {timestamp}
{"=" * 50}

📊 CURRENT PATTERN VIOLATIONS:
• Function Signature Mismatches: {violations.get('function_signature_mismatches', 'Unknown')}
• SQLAlchemy Execute Calls: {violations.get('sqlalchemy_execute_calls', 'Unknown')}
• from_orm Patterns: {violations.get('from_orm_patterns', 'Unknown')}
• Frontend localStorage Tokens: {violations.get('frontend_localstorage_tokens', 'Unknown')}

🎯 PROGRESS VS BASELINE:"""
        
        if "error" not in progress:
            for pattern, data in progress.items():
                if pattern != "overall":
                    report += f"\n• {pattern}: {data['baseline']} → {data['current']} ({data['progress_percentage']}% complete)"
            
            overall = progress["overall"]
            report += f"\n\n📈 OVERALL PROGRESS: {overall['overall_progress_percentage']}% complete"
            report += f"\n   Total Issues: {overall['total_baseline_issues']} → {overall['total_current_issues']}"
        
        report += f"\n\n🔧 FUNCTIONALITY TESTS:"
        for test_name, result in functionality.items():
            status = result.get("status", "UNKNOWN")
            if status == "PASS":
                report += f"\n• {test_name}: ✅ {status}"
            elif status == "FAIL":
                report += f"\n• {test_name}: ❌ {status}"
            elif status == "SKIP":
                report += f"\n• {test_name}: ⏸️  {status}"
            else:
                report += f"\n• {test_name}: ❓ {status}"
        
        return report
    
    def monitor_continuous(self, interval_seconds: int = 30):
        """Run continuous monitoring"""
        print("🚀 Starting continuous progress monitoring...")
        print(f"📡 Monitoring every {interval_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                report = self.generate_status_report()
                
                # Clear screen and show report
                print("\033[2J\033[H")  # Clear screen
                print(report)
                print(f"\n⏰ Next update in {interval_seconds} seconds...")
                
                # Log progress
                self.progress_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "violations": self.count_pattern_violations(),
                    "progress": self.calculate_progress()
                })
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n📊 Monitoring stopped. Saving progress log...")
            self.save_progress_log()
    
    def save_progress_log(self):
        """Save progress log to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"progress_log_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.progress_log, f, indent=2)
        
        print(f"Progress log saved to: {filepath}")
    
    def run_single_check(self):
        """Run single progress check"""
        self.load_baseline()
        report = self.generate_status_report()
        print(report)
        
        # Save current state
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"progress_snapshot_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "violations": self.count_pattern_violations(),
            "functionality": self.test_critical_functionality(),
            "progress": self.calculate_progress()
        }
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"\n📸 Snapshot saved to: {filepath}")
        return snapshot

def main():
    """Main execution"""
    import sys
    
    monitor = ProgressMonitor()
    monitor.load_baseline()
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        # Continuous monitoring mode
        interval = 30
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                pass
        monitor.monitor_continuous(interval)
    else:
        # Single check mode
        monitor.run_single_check()

if __name__ == "__main__":
    main()