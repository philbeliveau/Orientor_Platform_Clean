#!/bin/bash

# Complete Baseline Testing Suite
# Establishes comprehensive baseline before standardization fixes

echo "🚀 ORIENTOR PLATFORM BASELINE TESTING SUITE"
echo "=============================================="
echo "Purpose: Establish baseline metrics before standardization fixes"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status $BLUE "🔍 Checking prerequisites..."

if ! command_exists python; then
    print_status $RED "❌ Python not found. Please install Python."
    exit 1
fi

if ! command_exists node; then
    print_status $RED "❌ Node.js not found. Please install Node.js."
    exit 1
fi

print_status $GREEN "✅ Prerequisites check passed"
echo ""

# Set working directory to project root
cd "$(dirname "$0")/.."

# Step 1: Run baseline validation suite
print_status $BLUE "📊 Step 1: Running baseline validation suite..."
echo ""

if python tests/baseline_validation_suite.py; then
    print_status $GREEN "✅ Baseline validation completed"
else
    print_status $YELLOW "⚠️  Baseline validation completed with issues"
fi
echo ""

# Step 2: Test critical functionality
print_status $BLUE "🔧 Step 2: Testing critical functionality..."
echo ""

if python tests/critical_functionality_test.py; then
    print_status $GREEN "✅ Critical functionality tests passed"
else
    print_status $YELLOW "⚠️  Critical functionality tests completed with issues"
fi
echo ""

# Step 3: Check for pattern violations
print_status $BLUE "🔍 Step 3: Scanning for pattern violations..."
echo ""

# Function signature mismatches
function_count=$(find ./backend -name "*.py" -exec grep -l "def.*db: Session" {} \; 2>/dev/null | wc -l)
print_status $YELLOW "Function signature mismatches: $function_count files"

# SQLAlchemy execute calls
execute_count=$(find ./backend -name "*.py" -exec grep -l "db\.execute\|\.execute(" {} \; 2>/dev/null | wc -l)
print_status $YELLOW "SQLAlchemy execute calls: $execute_count files"

# from_orm patterns
from_orm_count=$(find ./backend -name "*.py" -exec grep -l "from_orm(" {} \; 2>/dev/null | wc -l)
print_status $YELLOW "from_orm patterns: $from_orm_count files"

# Frontend localStorage tokens
localstorage_count=$(find ./frontend/src -name "*.tsx" -exec grep -l "localStorage.getItem.*access_token" {} \; 2>/dev/null | wc -l)
if [ $localstorage_count -eq 0 ]; then
    print_status $GREEN "Frontend localStorage tokens: ✅ CLEAN"
else
    print_status $RED "Frontend localStorage tokens: $localstorage_count files"
fi

# Old login routes
old_routes_count=$(find ./frontend/src -name "*.tsx" -exec grep -l "router.push('/login')" {} \; 2>/dev/null | wc -l)
if [ $old_routes_count -eq 0 ]; then
    print_status $GREEN "Old login routes: ✅ CLEAN"
else
    print_status $RED "Old login routes: $old_routes_count files"
fi

echo ""

# Step 4: Generate summary
print_status $BLUE "📋 Step 4: Generating baseline summary..."
echo ""

total_p0_issues=$((function_count + execute_count))
total_issues=$((total_p0_issues + from_orm_count + localstorage_count + old_routes_count))

print_status $BLUE "📊 BASELINE SUMMARY:"
print_status $BLUE "==================="
echo "P0 Critical Issues: $total_p0_issues"
echo "• Function Signature Mismatches: $function_count"
echo "• SQLAlchemy Execute Calls: $execute_count"
echo ""
echo "P1/P2 Issues: $((total_issues - total_p0_issues))"
echo "• from_orm Patterns: $from_orm_count"
echo "• Frontend localStorage: $localstorage_count"
echo "• Old Login Routes: $old_routes_count"
echo ""
echo "Total Issues to Fix: $total_issues"
echo ""

# Health assessment
if [ $total_p0_issues -gt 50 ]; then
    health="CRITICAL"
    color=$RED
elif [ $total_p0_issues -gt 20 ]; then
    health="POOR" 
    color=$YELLOW
elif [ $total_p0_issues -gt 5 ]; then
    health="NEEDS_ATTENTION"
    color=$YELLOW
else
    health="GOOD"
    color=$GREEN
fi

print_status $color "Overall Health: $health"
echo ""

# Step 5: Generate recommendations
print_status $BLUE "📋 RECOMMENDATIONS:"
print_status $BLUE "=================="

if [ $total_p0_issues -gt 0 ]; then
    echo "🚨 URGENT: Fix $total_p0_issues P0 critical issues before proceeding"
fi

if [ $function_count -gt 0 ]; then
    echo "🔧 Priority 1: Fix function signature mismatches ($function_count files)"
fi

if [ $execute_count -gt 0 ]; then
    echo "🔧 Priority 2: Convert SQLAlchemy execute calls ($execute_count files)"
fi

if [ $localstorage_count -eq 0 ] && [ $old_routes_count -eq 0 ]; then
    echo "✅ Frontend authentication patterns are clean"
fi

echo ""

# Step 6: Save baseline results
print_status $BLUE "💾 Step 6: Saving baseline results..."

timestamp=$(date +"%Y%m%d_%H%M%S")
baseline_dir="tests/baseline_results_$timestamp"
mkdir -p "$baseline_dir"

# Create baseline summary file
cat > "$baseline_dir/baseline_summary.txt" << EOF
ORIENTOR PLATFORM BASELINE SUMMARY
Generated: $(date)

PATTERN VIOLATIONS:
• Function Signature Mismatches: $function_count files
• SQLAlchemy Execute Calls: $execute_count files  
• from_orm Patterns: $from_orm_count files
• Frontend localStorage Tokens: $localstorage_count files
• Old Login Routes: $old_routes_count files

TOTAL ISSUES: $total_issues
P0 CRITICAL: $total_p0_issues
OVERALL HEALTH: $health

RECOMMENDATIONS:
$(if [ $total_p0_issues -gt 0 ]; then echo "- URGENT: Fix $total_p0_issues P0 critical issues"; fi)
$(if [ $function_count -gt 0 ]; then echo "- Priority 1: Fix function signature mismatches"; fi)
$(if [ $execute_count -gt 0 ]; then echo "- Priority 2: Convert SQLAlchemy execute calls"; fi)
$(if [ $localstorage_count -eq 0 ] && [ $old_routes_count -eq 0 ]; then echo "- ✅ Frontend auth patterns clean"; fi)

NEXT STEPS:
1. Begin P0 Critical fixes with function signatures
2. Monitor progress with: python tests/progress_monitor.py
3. Validate fixes with: python tests/critical_functionality_test.py
4. Run full validation after each phase
EOF

# Copy test results to baseline directory
cp tests/baseline_validation_results_*.json "$baseline_dir/" 2>/dev/null || true
cp tests/critical_functionality_test_*.json "$baseline_dir/" 2>/dev/null || true

print_status $GREEN "✅ Baseline results saved to: $baseline_dir"
echo ""

# Step 7: Final instructions
print_status $BLUE "🎯 NEXT STEPS:"
print_status $BLUE "============="
echo "1. Start backend server: cd backend && python main.py"
echo "2. Start frontend server: cd frontend && npm run dev"
echo "3. Begin P0 Critical fixes starting with function signatures"
echo "4. Monitor progress: python tests/progress_monitor.py"
echo "5. Test after each fix: python tests/critical_functionality_test.py"
echo ""

print_status $GREEN "🚀 Baseline testing complete! Ready for standardization fixes."

# Exit with appropriate code based on health
if [ "$health" = "CRITICAL" ]; then
    exit 2
elif [ "$health" = "POOR" ] || [ "$health" = "NEEDS_ATTENTION" ]; then
    exit 1
else
    exit 0
fi