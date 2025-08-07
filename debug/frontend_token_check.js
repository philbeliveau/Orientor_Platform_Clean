/*
Frontend Token Debugger
Check what tokens are available and being sent to backend
*/

console.log("🔍 FRONTEND TOKEN DEBUGGER");
console.log("=" * 30);

// 1. Check localStorage for Clerk tokens
console.log("\n1️⃣ LOCALSTORAGE TOKENS:");
console.log("-" * 20);

const clerkTokenKeys = [
    'clerk-db-jwt',
    '__clerk_jwt',
    '__clerk_session',
    '__clerk_user',
    'clerk_session'
];

clerkTokenKeys.forEach(key => {
    const value = localStorage.getItem(key);
    if (value) {
        const truncated = value.length > 50 ? value.substring(0, 50) + '...' : value;
        console.log(`✅ ${key}: ${truncated}`);
    } else {
        console.log(`❌ ${key}: Not found`);
    }
});

// 2. Check sessionStorage
console.log("\n2️⃣ SESSIONSTORAGE TOKENS:");
console.log("-" * 25);

clerkTokenKeys.forEach(key => {
    const value = sessionStorage.getItem(key);
    if (value) {
        const truncated = value.length > 50 ? value.substring(0, 50) + '...' : value;
        console.log(`✅ ${key}: ${truncated}`);
    } else {
        console.log(`❌ ${key}: Not found`);
    }
});

// 3. Check if Clerk is available
console.log("\n3️⃣ CLERK OBJECT CHECK:");
console.log("-" * 20);

if (typeof window !== 'undefined' && window.Clerk) {
    console.log("✅ Clerk object available");
    
    // Try to get session
    if (window.Clerk.session) {
        console.log("✅ Clerk session exists");
        console.log("Session ID:", window.Clerk.session.id);
        
        // Try to get token
        window.Clerk.session.getToken()
            .then(token => {
                if (token) {
                    console.log("✅ Token retrieved from Clerk session");
                    console.log("Token preview:", token.substring(0, 50) + "...");
                    
                    // Try to decode JWT header to check format
                    try {
                        const parts = token.split('.');
                        if (parts.length === 3) {
                            const header = JSON.parse(atob(parts[0]));
                            console.log("✅ Valid JWT format");
                            console.log("JWT Header:", header);
                        } else {
                            console.log("❌ Invalid JWT format - not 3 parts");
                        }
                    } catch (e) {
                        console.log("❌ Could not decode JWT header:", e.message);
                    }
                } else {
                    console.log("❌ No token from Clerk session");
                }
            })
            .catch(err => {
                console.log("❌ Error getting token from Clerk:", err);
            });
    } else {
        console.log("❌ No Clerk session");
    }
} else {
    console.log("❌ Clerk object not available");
}

// 4. Check current user
console.log("\n4️⃣ CLERK USER CHECK:");
console.log("-" * 18);

if (typeof window !== 'undefined' && window.Clerk && window.Clerk.user) {
    console.log("✅ Clerk user exists");
    console.log("User ID:", window.Clerk.user.id);
    console.log("Email:", window.Clerk.user.primaryEmailAddress?.emailAddress);
} else {
    console.log("❌ No Clerk user");
}

// 5. Network request simulation
console.log("\n5️⃣ NETWORK REQUEST TEST:");
console.log("-" * 22);

// Function to test API call with proper auth
async function testApiCall() {
    try {
        if (window.Clerk && window.Clerk.session) {
            const token = await window.Clerk.session.getToken();
            
            console.log("🔄 Testing API call with token...");
            
            const response = await fetch('http://localhost:8000/api/v1/tests/holland/user-results', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log("Response status:", response.status);
            
            if (response.status === 401) {
                console.log("❌ 401 Unauthorized - token is invalid or expired");
                console.log("Token being sent:", token ? token.substring(0, 50) + "..." : "No token");
            } else if (response.ok) {
                console.log("✅ API call successful");
                const data = await response.json();
                console.log("Response data:", data);
            } else {
                console.log(`⚠️ API call failed with status: ${response.status}`);
            }
        } else {
            console.log("❌ Cannot test API call - no Clerk session");
        }
    } catch (error) {
        console.log("❌ API call error:", error.message);
    }
}

// Run the test
testApiCall();

// 6. Instructions
console.log("\n6️⃣ DEBUGGING INSTRUCTIONS:");
console.log("-" * 25);
console.log("1. Open browser dev tools (F12)");
console.log("2. Go to Console tab");
console.log("3. Copy and paste this entire script");
console.log("4. Press Enter to run");
console.log("5. Check the output for token status");
console.log("6. Also check Network tab for actual HTTP requests");