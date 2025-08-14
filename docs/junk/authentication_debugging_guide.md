# Authentication Debugging Guide

## Problem Analysis: 403 Forbidden Errors

### Current Status
- ✅ **Backend API**: Running on localhost:8000
- ✅ **Frontend**: Running on localhost:3000  
- ✅ **Clerk Configuration**: Environment variables properly set
- ✅ **Authentication Endpoints**: Exist and configured correctly
- ❌ **JWT Token Flow**: Frontend → Backend token validation failing

### Root Cause Identification

The 403 Forbidden errors are occurring because:

1. **Backend Authentication**: Working correctly, properly rejects unauthenticated requests
2. **Frontend Token Generation**: May not be generating proper JWT tokens
3. **JWT Template**: May not be configured correctly in Clerk dashboard

### Failing Endpoints
- `GET /api/v1/career-goals/active` → 403 Forbidden  
- `GET /api/v1/courses/` → 403 Forbidden
- `GET /api/v1/avatar/me` → 403 Forbidden

### Authentication Flow Analysis

#### Expected Flow:
1. User signs in with Clerk → ✅ Working
2. Frontend requests JWT token using `getToken({ template: 'orientor-jwt' })` → ⚠️ May be failing
3. Frontend sends `Authorization: Bearer {jwt_token}` → ❓ Unknown if correct token
4. Backend validates JWT against Clerk JWKS → ❌ Failing with "Not authenticated"

## Debugging Steps

### Step 1: Check JWT Template Configuration

The backend expects a JWT template named `'orientor-jwt'`. Verify in Clerk Dashboard:

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)  
2. Navigate to **JWT Templates**
3. Ensure template named `orientor-jwt` exists with proper configuration:
   ```json
   {
     "aud": "orientor-api",
     "iss": "https://ruling-halibut-89.clerk.accounts.dev",
     "sub": "{{user.id}}"
   }
   ```

### Step 2: Test Frontend JWT Token Generation

Add debugging to frontend components:

```typescript
// In any component using authentication
import { useAuth } from '@clerk/nextjs';

const { getToken } = useAuth();

const testToken = async () => {
  try {
    const token = await getToken({ template: 'orientor-jwt' });
    console.log('JWT Token received:', token?.substring(0, 50) + '...');
    console.log('Token format valid:', token?.startsWith('eyJ'));
  } catch (error) {
    console.error('Token generation failed:', error);
  }
};
```

### Step 3: Verify Backend Token Validation

The backend has detailed logging. Check console output when making requests:

```
✅ Token validated for user: user_30sroat707tAa5bGyk4EprB2Ja8
❌ JWT validation failed: [specific error]
```

### Step 4: Check Network Requests

In browser Dev Tools → Network tab, verify:

1. **Authorization Header**: `Bearer eyJ...` format
2. **Token Length**: JWT tokens are typically 200+ characters
3. **Request Headers**: Include proper `Authorization` header

## Immediate Fixes

### Fix 1: Update Frontend Services

Ensure all services use the new Clerk authentication:

```typescript
// ❌ Old way (causing 403 errors):
const token = localStorage.getItem('access_token');

// ✅ New way (fixed):
import { useClerkToken } from '../utils/clerkAuth';
const { getAuthToken } = useClerkToken();
const token = await getAuthToken();
```

### Fix 2: Configure JWT Template

If JWT template doesn't exist, create it in Clerk Dashboard:

1. **Name**: `orientor-jwt`
2. **Custom Claims**:
   ```json
   {
     "userId": "{{user.id}}",
     "email": "{{user.primary_email_address.email_address}}"
   }
   ```

### Fix 3: Temporary Backend Fix

If JWT template configuration is problematic, temporarily modify backend validation:

```python
# In backend/app/utils/clerk_auth.py, line ~140
payload = jwt.decode(
    token,
    key,
    algorithms=["RS256"],
    options={
        "verify_aud": False,    # Skip audience verification  
        "verify_iss": False,    # Skip issuer verification
        "verify_signature": True,
        "verify_exp": True
    }
)
```

## Testing Protocol

### 1. Manual Test
```bash
# Test endpoint without auth (should return 403)
curl "http://localhost:8000/api/v1/career-goals/active"

# Expected: {"detail": "Not authenticated"}
```

### 2. Frontend Debug Test
Add to any component:
```typescript
const debugAuth = async () => {
  const { getAuthToken } = useClerkToken();
  try {
    const token = await getAuthToken();
    console.log('🔑 Token generated:', !!token);
    console.log('📏 Token length:', token?.length);
    console.log('✅ JWT format:', token?.startsWith('eyJ'));
  } catch (error) {
    console.error('🚨 Auth error:', error);
  }
};
```

### 3. API Test with Token
Once token is generated, test API call:
```typescript
const testAPI = async () => {
  const token = await getAuthToken();
  const response = await fetch('/api/v1/career-goals/active', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('API Response:', response.status);
};
```

## Expected Resolution

After implementing fixes:
- ✅ Frontend generates valid JWT tokens
- ✅ Backend successfully validates tokens
- ✅ API endpoints return data instead of 403 errors
- ✅ Dashboard components load user data correctly

## Next Steps

1. **Immediate**: Test JWT template configuration
2. **Short-term**: Ensure all frontend services use new auth utilities  
3. **Long-term**: Add token caching and refresh logic for better performance

The authentication infrastructure is solid - this is primarily a token generation/configuration issue that should resolve quickly once the JWT template is properly configured.