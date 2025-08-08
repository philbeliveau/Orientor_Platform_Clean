#!/bin/bash
# Authentication Critical Reminders Hook
# This hook validates authentication patterns in the codebase

echo "🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS"
echo "✅ Always use: const { getToken } = useAuth(); const token = await getToken();"
echo "❌ Never use: localStorage.getItem('access_token')"
echo "✅ Always redirect to: /sign-in"
echo "❌ Never redirect to: /login"
echo "🚨 IF YOU SEE NON-CLERK AUTH CODE, STOP AND FIX IT IMMEDIATELY"

# Check for problematic authentication patterns
if [ "$1" ]; then
    echo "📁 Checking file: $1"
    
    # Check for localStorage auth usage
    if grep -q "localStorage.getItem.*access_token" "$1" 2>/dev/null; then
        echo "❌ CRITICAL: Found localStorage.getItem('access_token') in $1"
        echo "🔧 FIX: Replace with 'const token = await getToken()' from useAuth()"
    fi
    
    # Check for wrong login redirects
    if grep -q "router.push.*'/login'" "$1" 2>/dev/null; then
        echo "❌ CRITICAL: Found redirect to /login in $1"
        echo "🔧 FIX: Replace with router.push('/sign-in')"
    fi
    
    # Check for correct Clerk usage
    if grep -q "useAuth.*getToken" "$1" 2>/dev/null; then
        echo "✅ GOOD: Found proper Clerk useAuth usage in $1"
    fi
fi

echo "────────────────────────────────────────────────────"