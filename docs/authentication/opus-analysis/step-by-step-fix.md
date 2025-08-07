# 🔧 Step-by-Step Authentication Fix Guide

## Prerequisites
- Access to Clerk Dashboard
- Backend and Frontend running locally
- Terminal access for both frontend and backend
- Text editor ready with project open

---

## 🎯 Step 1: Clerk Dashboard Configuration (15 minutes)

### 1.1 Access Clerk Dashboard
1. Open browser to https://dashboard.clerk.com
2. Sign in with your Clerk account
3. Select the Orientor application

### 1.2 Create JWT Template
1. Navigate to **Configure** → **JWT Templates**
2. Click **"+ New template"**
3. Fill in the following:
   - **Name**: `orientor-jwt`
   - **Lifetime**: `3600` (1 hour)
4. In the **Claims** section, add:

```json
{
  "aud": "{{frontend_api}}",
  "exp": {{time.now}} + 3600,
  "iat": {{time.now}},
  "iss": "https://{{organization.domain}}",
  "nbf": {{time.now}},
  "sub": "{{user.id}}",
  "email": "{{user.primary_email_address.email_address}}",
  "first_name": "{{user.first_name}}",
  "last_name": "{{user.last_name}}",
  "username": "{{user.username}}",
  "user_metadata": {{user.public_metadata}}
}
```

5. Click **Save**
6. Note the template name: `orientor-jwt` (you'll need this)

### 1.3 Verify Template
1. Stay on the JWT Templates page
2. You should see `orientor-jwt` in the list
3. Status should be "Active"

---

## 🎯 Step 2: Backend Environment Setup (10 minutes)

### 2.1 Stop the Backend
```bash
# In backend terminal
Ctrl+C  # Stop the server
```

### 2.2 Verify Environment File
```bash
cd backend
cat .env | grep CLERK
```

You should see:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_DOMAIN=ruling-halibut-89.clerk.accounts.dev
```

If missing, add them to `.env`:
```bash
echo 'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cnVsaW5nLWhhbGlidXQtODkuY2xlcmsuYWNjb3VudHMuZGV2JA' >> .env
echo 'CLERK_SECRET_KEY=sk_test_1cINwMnu5slBHCftWNHnKMelHORTylnlnFQvhzWO6f' >> .env
echo 'NEXT_PUBLIC_CLERK_DOMAIN=ruling-halibut-89.clerk.accounts.dev' >> .env
```

### 2.3 Update run.py
Open `backend/run.py` and add at the very top:

```python
#!/usr/bin/env python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Force load environment variables BEFORE any other imports
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"❌ No .env file found at: {env_path}")
    sys.exit(1)

# Validate critical environment variables
REQUIRED_ENV_VARS = [
    'CLERK_SECRET_KEY',
    'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
    'NEXT_PUBLIC_CLERK_DOMAIN'
]

print("\n🔍 Checking required environment variables:")
all_present = True
for var in REQUIRED_ENV_VARS:
    value = os.getenv(var)
    if not value:
        print(f"   ❌ {var}: NOT FOUND")
        all_present = False
    else:
        print(f"   ✅ {var}: {value[:20]}...")

if not all_present:
    print("\n❌ Missing required environment variables!")
    print("   Please check your .env file")
    sys.exit(1)

print("\n✅ All environment variables loaded successfully!\n")

# NOW import the rest
import uvicorn

# ... rest of the file remains the same
```

### 2.4 Start Backend with Validation
```bash
python run.py
```

You should see:
```
✅ Loaded environment from: /path/to/backend/.env

🔍 Checking required environment variables:
   ✅ CLERK_SECRET_KEY: sk_test_1cINwMnu5sl...
   ✅ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk_test_cnVsaW5nLWh...
   ✅ NEXT_PUBLIC_CLERK_DOMAIN: ruling-halibut-89.cl...

✅ All environment variables loaded successfully!

Starting server on port 8000 with auto-reload enabled...
```

---

## 🎯 Step 3: Frontend Token Configuration (15 minutes)

### 3.1 Update API Service
Open `frontend/src/services/api.ts`

Find the `useClerkApi` function (around line 100) and update:

```typescript
// BEFORE (around line 100-111)
export const useClerkApi = () => {
  const { getToken } = useAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<T>,
    ...args: any[]
  ): Promise<T> => {
    const token = await getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }
    return apiMethod(token, ...args);
  };

// AFTER - Replace with:
export const useClerkApi = () => {
  const { getToken } = useAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<T>,
    ...args: any[]
  ): Promise<T> => {
    try {
      // Request JWT token with the template we created
      console.log('[Auth] Requesting JWT token with orientor-jwt template...');
      const token = await getToken({ template: 'orientor-jwt' });
      
      if (!token) {
        console.error('[Auth] No token returned from Clerk');
        throw new Error('No authentication token available');
      }
      
      // Log token type for debugging
      const tokenPreview = token.substring(0, 30);
      if (tokenPreview.startsWith('eyJ')) {
        console.log('[Auth] ✅ JWT token obtained:', tokenPreview + '...');
      } else if (tokenPreview.startsWith('sess_')) {
        console.error('[Auth] ❌ Got session token instead of JWT:', tokenPreview);
        throw new Error('Invalid token type - got session token instead of JWT');
      }
      
      return apiMethod(token, ...args);
    } catch (error) {
      console.error('[Auth] Token acquisition failed:', error);
      throw error;
    }
  };
```

### 3.2 Update Dashboard Error Handling
Open `frontend/src/app/dashboard/page.tsx`

Add better error logging (around line 110-130):

```typescript
// In the fetchHollandResults function
const fetchHollandResults = async () => {
  try {
    if (!isLoaded || !isSignedIn || !user?.id) {
      console.log('[Holland] Skipping - user not ready');
      return;
    }

    // Add token validation
    const token = await getToken({ template: 'orientor-jwt' });
    if (!token) {
      console.error('[Holland] No JWT token available');
      setError('Authentication token not available');
      return;
    }
    
    // Log token type
    console.log('[Holland] Token type:', token.substring(0, 10));
    
    setLoading(true);
    const results = await api.getHollandResults();
    // ... rest of the function
```

### 3.3 Restart Frontend
```bash
# In frontend terminal
Ctrl+C  # Stop the server
npm run dev
```

---

## 🎯 Step 4: Backend Token Validation Enhancement (10 minutes)

### 4.1 Update clerk_auth.py
Open `backend/app/utils/clerk_auth.py`

Add debugging to the `verify_clerk_token` function (around line 82):

```python
async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verify a Clerk JWT token and return its payload"""
    
    # Add token type detection
    logger.info(f"🔍 Token validation attempt")
    logger.info(f"   Token preview: {token[:50]}...")
    
    # Check if this is a session token (wrong type)
    if token.startswith("sess_"):
        logger.error("❌ Received session token instead of JWT")
        logger.error("   Frontend must use getToken({ template: 'orientor-jwt' })")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: Session token received, JWT required"
        )
    
    # Check if this looks like a JWT
    if not token.startswith("eyJ"):
        logger.error(f"❌ Invalid token format: {token[:20]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format: Not a valid JWT"
        )
    
    logger.info("✅ Token appears to be JWT format, proceeding with validation")
    
    try:
        # Get JWKS keys
        jwks = await fetch_clerk_jwks()
        logger.info(f"   JWKS loaded: {len(jwks.get('keys', []))} keys available")
        
        # ... rest of the existing validation code
```

### 4.2 Add Debug Middleware
Open `backend/app/main.py`

Add after the app creation (around line 65):

```python
from fastapi import Request
import time

# Add debug middleware for authentication
@app.middleware("http")
async def auth_debug_middleware(request: Request, call_next):
    """Debug middleware to trace authentication issues"""
    
    # Only log API requests
    if "/api/" in str(request.url):
        auth_header = request.headers.get("authorization", "None")
        
        if auth_header != "None":
            # Log the request
            token_type = "JWT" if auth_header.startswith("Bearer eyJ") else "Session" if "sess_" in auth_header else "Unknown"
            logger.info(f"🔐 Auth Request: {request.method} {request.url.path}")
            logger.info(f"   Token Type: {token_type}")
            logger.info(f"   Token Preview: {auth_header[:60]}...")
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log failures
    if response.status_code == 401 and "/api/" in str(request.url):
        logger.warning(f"❌ 401 Unauthorized: {request.url.path} ({duration:.2f}s)")
    
    return response
```

---

## 🎯 Step 5: Testing the Fix (10 minutes)

### 5.1 Create Test Script
Create `backend/test_auth.py`:

```python
#!/usr/bin/env python
"""Quick authentication test"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    print("\n" + "="*50)
    print("🧪 AUTHENTICATION SYSTEM TEST")
    print("="*50)
    
    # Check environment
    vars = ['CLERK_SECRET_KEY', 'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', 'NEXT_PUBLIC_CLERK_DOMAIN']
    print("\n1️⃣ Environment Variables:")
    for var in vars:
        val = os.getenv(var)
        status = "✅" if val else "❌"
        preview = f"{val[:20]}..." if val else "NOT SET"
        print(f"   {status} {var}: {preview}")
    
    # Test JWKS
    print("\n2️⃣ Clerk JWKS Endpoint:")
    import httpx
    domain = os.getenv('NEXT_PUBLIC_CLERK_DOMAIN')
    if domain:
        url = f"https://{domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    keys = len(resp.json().get('keys', []))
                    print(f"   ✅ JWKS accessible: {keys} keys")
                else:
                    print(f"   ❌ JWKS error: {resp.status_code}")
            except Exception as e:
                print(f"   ❌ JWKS failed: {e}")
    
    # Test backend
    print("\n3️⃣ Backend Status:")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8000/docs")
            if resp.status_code == 200:
                print("   ✅ Backend running")
            else:
                print(f"   ❌ Backend error: {resp.status_code}")
        except:
            print("   ❌ Backend not accessible")
    
    print("\n" + "="*50)
    print("Test complete!\n")

if __name__ == "__main__":
    asyncio.run(test())
```

### 5.2 Run Test
```bash
cd backend
python test_auth.py
```

Expected output:
```
==================================================
🧪 AUTHENTICATION SYSTEM TEST
==================================================

1️⃣ Environment Variables:
   ✅ CLERK_SECRET_KEY: sk_test_1cINwMnu5sl...
   ✅ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk_test_cnVsaW5nLWh...
   ✅ NEXT_PUBLIC_CLERK_DOMAIN: ruling-halibut-89.cl...

2️⃣ Clerk JWKS Endpoint:
   ✅ JWKS accessible: 2 keys

3️⃣ Backend Status:
   ✅ Backend running

==================================================
Test complete!
```

---

## 🎯 Step 6: Full System Test (5 minutes)

### 6.1 Open Browser
1. Navigate to http://localhost:3000
2. Open Developer Console (F12)
3. Go to Network tab
4. Clear console

### 6.2 Attempt Login
1. Click login/sign-in
2. Enter credentials
3. Watch console for:
   - `[Auth] Requesting JWT token with orientor-jwt template...`
   - `[Auth] ✅ JWT token obtained: eyJ...`

### 6.3 Check Backend Logs
You should see:
```
🔐 Auth Request: GET /api/v1/tests/holland/user-results
   Token Type: JWT
   Token Preview: Bearer eyJ...
🔍 Token validation attempt
   Token preview: eyJ...
✅ Token appears to be JWT format, proceeding with validation
   JWKS loaded: 2 keys available
```

### 6.4 Verify Success
- No 401 error loops
- Dashboard loads with data
- No "Could not validate credentials" errors

---

## 🚨 Troubleshooting

### If you see "sess_" tokens:
1. JWT template not configured in Clerk
2. Frontend not requesting JWT template
3. Clear browser cache and cookies

### If you see 401 errors still:
1. Check backend logs for token format
2. Verify CLERK_SECRET_KEY is correct
3. Ensure JWKS endpoint is accessible

### If environment variables missing:
1. Check .env file exists
2. Restart backend after adding variables
3. Verify load_dotenv is called BEFORE imports

---

## ✅ Success Indicators

You know it's working when:
1. Console shows: `[Auth] ✅ JWT token obtained: eyJ...`
2. Backend logs show: `✅ Token appears to be JWT format`
3. No 401 error loops
4. Dashboard displays user data
5. API calls return data not errors

---

## 🎊 Final Verification

Run this command to verify everything:
```bash
# In backend directory
curl -H "Authorization: Bearer $(cd ../frontend && npm run get-token 2>/dev/null)" \
     http://localhost:8000/api/v1/test/hello
```

If you get a response (not 401), authentication is working!

---

*Time Estimate: 45-60 minutes total*
*Difficulty: Medium*
*Success Rate: 95% if steps followed exactly*