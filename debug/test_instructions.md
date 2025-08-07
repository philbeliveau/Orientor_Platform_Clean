# Testing Authentication Fixes

## Steps to Test

1. **Start Backend Server**
   ```bash
   cd backend && uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend Server** 
   ```bash
   cd frontend && npm run dev
   ```

3. **Open Browser**
   - Go to http://localhost:3000
   - Open Developer Tools (F12)
   - Go to Console tab

4. **Check Authentication Flow**
   - Look for `[DEBUG]` messages in console
   - Should see messages like:
     - `[DEBUG] Skipping ... fetch - user not ready`  (initially)
     - `[DEBUG] Fetching ... with token: eyJhbGci...`  (after auth)

5. **Check Network Tab**
   - Look for requests to `http://localhost:8000/api/v1/...`
   - Should have `Authorization: Bearer <token>` headers
   - Should get 200 responses (not 401)

## Expected Behavior

### Before User Loads
- Console: Multiple "[DEBUG] Skipping ... - user not ready" messages
- Network: No API requests to backend
- No infinite loop of 401 errors

### After User Authenticates  
- Console: "[DEBUG] Fetching ... with token" messages
- Network: API requests with Bearer tokens
- Successful 200 responses from backend

## Troubleshooting

### Still Getting 401s?
1. Check if token is being sent: Network tab → Headers → Authorization
2. Verify token format: Should be a long JWT string (3 parts separated by dots)
3. Copy token and check at https://jwt.io to verify it's valid

### Still Seeing Infinite Loops?
1. Check console for "[DEBUG] Skipping" messages - should prevent loops
2. If API calls are still happening before auth, check useEffect dependencies
3. Make sure Clerk is properly configured in your app

### Backend Issues?
1. Make sure backend is running on port 8000
2. Check backend logs for JWT validation errors
3. Run the debug/auth_debugger.py script again

## Frontend Token Debug Script

Copy this into browser console to check tokens:
```javascript
// Check what tokens are available
console.log('Clerk session:', window.Clerk?.session?.id);
console.log('Clerk user:', window.Clerk?.user?.id);

// Get and examine token
if (window.Clerk?.session) {
  window.Clerk.session.getToken().then(token => {
    console.log('Token available:', !!token);
    if (token) {
      console.log('Token preview:', token.substring(0, 50) + '...');
      // Decode JWT header
      try {
        const parts = token.split('.');
        const header = JSON.parse(atob(parts[0]));
        console.log('JWT header:', header);
      } catch (e) {
        console.log('Could not decode JWT:', e);
      }
    }
  });
}
```