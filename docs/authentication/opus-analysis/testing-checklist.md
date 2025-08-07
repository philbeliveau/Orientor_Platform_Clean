# ✅ Authentication Testing Checklist

## Pre-Test Setup
- [ ] Backend stopped and restarted with new environment loading
- [ ] Frontend stopped and restarted  
- [ ] Browser cache cleared
- [ ] Browser cookies cleared for localhost
- [ ] Developer console open with Network tab active
- [ ] Backend terminal visible for logs

---

## 🔍 Phase 1: Environment Validation

### Backend Environment Check
```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLERK_SECRET_KEY:', 'SET' if os.getenv('CLERK_SECRET_KEY') else 'MISSING')"
```
- [ ] Output shows "CLERK_SECRET_KEY: SET"

### Frontend Environment Check
```bash
cd frontend
grep CLERK .env.local
```
- [ ] Shows all three Clerk environment variables

### Clerk Dashboard Check
- [ ] Navigate to https://dashboard.clerk.com
- [ ] JWT Templates section shows "orientor-jwt" template
- [ ] Template status is "Active"

---

## 🔍 Phase 2: Token Generation Testing

### Test 1: Frontend Token Request
1. Open browser to http://localhost:3000
2. Open Console (F12)
3. Run in console:
```javascript
// Test getting JWT token
const test = async () => {
  const { getToken } = window.Clerk.session;
  const token = await getToken({ template: 'orientor-jwt' });
  console.log('Token type:', token ? token.substring(0, 10) : 'null');
  return token;
};
test();
```

**Expected Result**:
- [ ] Token starts with "eyJ" (JWT format)
- [ ] Token does NOT start with "sess_" (session format)
- [ ] No errors in console

### Test 2: Token Validation
Copy the token from Test 1 and decode at https://jwt.io

**Expected Payload Contains**:
- [ ] `sub` (user ID)
- [ ] `email` (user email)
- [ ] `aud` (audience - should match publishable key)
- [ ] `iss` (issuer - should be Clerk domain)
- [ ] `exp` (expiration time)

---

## 🔍 Phase 3: Backend Validation Testing

### Test 3: JWKS Endpoint
```bash
curl https://ruling-halibut-89.clerk.accounts.dev/.well-known/jwks.json
```
- [ ] Returns JSON with "keys" array
- [ ] At least 1 key present

### Test 4: Backend Health
```bash
curl http://localhost:8000/docs
```
- [ ] Returns HTML (FastAPI docs)
- [ ] Status code 200

### Test 5: Unauthenticated Request
```bash
curl -v http://localhost:8000/api/v1/tests/holland/user-results
```
- [ ] Returns 401 Unauthorized
- [ ] Error message about missing credentials

### Test 6: Invalid Token Request
```bash
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:8000/api/v1/tests/holland/user-results
```
- [ ] Returns 401 Unauthorized
- [ ] Backend logs show "Invalid token format"

---

## 🔍 Phase 4: End-to-End Authentication Flow

### Test 7: Complete Login Flow
1. Navigate to http://localhost:3000
2. Click Sign In
3. Enter credentials
4. Submit

**Console Checks**:
- [ ] See: `[Auth] Requesting JWT token with orientor-jwt template...`
- [ ] See: `[Auth] ✅ JWT token obtained: eyJ...`
- [ ] NO: `[Auth] ❌ Got session token instead of JWT`

**Network Tab Checks**:
- [ ] API calls include `Authorization: Bearer eyJ...` header
- [ ] Authorization header does NOT contain `sess_`

**Backend Log Checks**:
- [ ] See: `🔐 Auth Request: GET /api/v1/...`
- [ ] See: `Token Type: JWT`
- [ ] See: `✅ Token validated for user: user_xxx`
- [ ] NO: `❌ Received session token instead of JWT`

### Test 8: Protected Endpoints
After successful login, check these endpoints return data:

```bash
# Get the token from browser console first
token="eyJ..." # paste your token here

# Test each endpoint
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/tests/holland/user-results
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/space/notes
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/jobs/recommendations/me
```

- [ ] Holland results: Returns data or empty array (not 401)
- [ ] Space notes: Returns data or empty array (not 401)
- [ ] Job recommendations: Returns data or empty array (not 401)

---

## 🔍 Phase 5: Dashboard Functionality

### Test 9: Dashboard Load
1. Navigate to http://localhost:3000/dashboard
2. Wait for page to fully load

**Visual Checks**:
- [ ] User card shows correct name
- [ ] No error messages displayed
- [ ] Data sections loading or showing content

**Console Checks**:
- [ ] NO: Repeating 401 errors
- [ ] NO: "Could not validate credentials" loops
- [ ] NO: Session token warnings

**Network Tab Checks**:
- [ ] API calls returning 200 status
- [ ] Multiple successful API requests
- [ ] No infinite retry loops

### Test 10: Data Refresh
1. On dashboard, refresh the page (F5)
2. Watch network tab

- [ ] Authentication completes quickly
- [ ] No authentication loops
- [ ] Data loads successfully

---

## 🔍 Phase 6: Error Scenarios

### Test 11: Expired Token
1. Wait for token to expire (1 hour) OR
2. Manually modify token in browser storage
3. Try to access protected resource

- [ ] Receives 401 error
- [ ] Redirected to login
- [ ] Can re-authenticate successfully

### Test 12: Network Error
1. Stop backend server
2. Try to load dashboard

- [ ] Shows appropriate error message
- [ ] No infinite loops
- [ ] Frontend remains responsive

### Test 13: Wrong Token Type
1. In browser console, override getToken to return session token:
```javascript
window.Clerk.session.getToken = async () => 'sess_fake_token';
```
2. Try to make API request

- [ ] Frontend logs error about wrong token type
- [ ] Backend rejects with appropriate message
- [ ] User prompted to re-authenticate

---

## 🔍 Phase 7: Performance Testing

### Test 14: Authentication Speed
Time from login click to dashboard load:
- [ ] Less than 3 seconds
- [ ] No noticeable delays
- [ ] Smooth transition

### Test 15: Concurrent Requests
Dashboard makes multiple API calls simultaneously:
- [ ] All requests include proper auth
- [ ] No race conditions
- [ ] Consistent authentication

---

## 📊 Success Criteria Summary

### Critical Success Indicators
- [ ] ✅ JWT tokens being generated (not session tokens)
- [ ] ✅ Backend validates tokens successfully
- [ ] ✅ No 401 error loops
- [ ] ✅ Dashboard loads with data
- [ ] ✅ Protected endpoints accessible

### Performance Indicators
- [ ] Authentication < 3 seconds
- [ ] No retry loops
- [ ] Clean console (no errors)
- [ ] Clean backend logs

### User Experience
- [ ] Smooth login flow
- [ ] Clear error messages
- [ ] No unexpected logouts
- [ ] Data loads consistently

---

## 🐛 Common Issues & Solutions

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Still getting sess_ tokens | JWT template not configured | Check Clerk Dashboard |
| Token starts with eyJ but still 401 | Wrong audience/issuer | Verify Clerk domain in .env |
| CORS errors | Backend CORS not updated | Check main.py CORS config |
| "Could not validate credentials" | Environment vars not loaded | Check run.py loads .env first |
| Works then stops | Token expired | Implement token refresh |
| Random 401s | Race condition | Check token await in frontend |

---

## 📝 Test Report Template

```markdown
## Authentication System Test Report
Date: ___________
Tester: ___________

### Environment
- Frontend URL: http://localhost:3000
- Backend URL: http://localhost:8000
- Clerk Dashboard: Verified ✓

### Test Results
- Phase 1 (Environment): ___ / 3 passed
- Phase 2 (Token Generation): ___ / 2 passed  
- Phase 3 (Backend Validation): ___ / 4 passed
- Phase 4 (End-to-End): ___ / 2 passed
- Phase 5 (Dashboard): ___ / 2 passed
- Phase 6 (Error Scenarios): ___ / 3 passed
- Phase 7 (Performance): ___ / 2 passed

### Overall Status
[ ] PASS - All tests passed
[ ] FAIL - Issues found (list below)

### Issues Found
1. ___________
2. ___________

### Notes
___________
```

---

## 🎯 Quick Verification Script

Save as `backend/quick_auth_test.sh`:

```bash
#!/bin/bash

echo "🧪 Quick Authentication Test"
echo "============================"

# Check environment
echo -n "1. Environment variables: "
if grep -q "CLERK_SECRET_KEY" .env; then
    echo "✅"
else
    echo "❌"
fi

# Check backend
echo -n "2. Backend running: "
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅"
else
    echo "❌"
fi

# Check JWKS
echo -n "3. Clerk JWKS accessible: "
if curl -s https://ruling-halibut-89.clerk.accounts.dev/.well-known/jwks.json | grep -q "keys"; then
    echo "✅"
else
    echo "❌"
fi

# Check for 401 on protected endpoint
echo -n "4. Auth required: "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/tests/holland/user-results)
if [ "$response" = "401" ]; then
    echo "✅"
else
    echo "❌ (got $response)"
fi

echo "============================"
echo "Basic checks complete!"
```

Run with: `chmod +x quick_auth_test.sh && ./quick_auth_test.sh`

---

*Testing Duration: 30-45 minutes for full suite*
*Quick Test: 5 minutes*
*Automated Tests: 2 minutes*