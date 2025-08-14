## ALWAYS WORK IN THE ORIENTOR_PLATFORM_CLEAN REPO.

# authentication-critical-reminders
🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
✅ Always use: const { getToken } = useAuth(); const token = await getToken();
❌ Never use: localStorage.getItem('access_token')
✅ Always redirect to: /sign-in  
❌ Never redirect to: /login
🚨 IF YOU SEE NON-CLERK AUTH CODE, STOP AND FIX IT IMMEDIATELY

# Claude Code Configuration - SPARC Development Environment

## 🚨 CRITICAL: CONCURRENT EXECUTION & FILE MANAGEMENT

**ABSOLUTE RULES**:
1. ALL operations MUST be concurrent/parallel in a single message
2. **NEVER save working files, text/mds and tests to the root folder**
3. ALWAYS organize files in appropriate subdirectories

### ⚡ GOLDEN RULE: "1 MESSAGE = ALL RELATED OPERATIONS"

**MANDATORY PATTERNS:**
- **TodoWrite**: ALWAYS batch ALL todos in ONE call (5-10+ todos minimum)
- **Task tool**: ALWAYS spawn ALL agents in ONE message with full instructions
- **File operations**: ALWAYS batch ALL reads/writes/edits in ONE message
- **Bash commands**: ALWAYS batch ALL terminal operations in ONE message
- **Memory operations**: ALWAYS batch ALL memory store/retrieve in ONE message

### 📁 File Organization Rules

**NEVER save to root folder. Use these directories:**
- `/src` - Source code files
- `/tests` - Test files
- `/docs` - Documentation and markdown files
- `/config` - Configuration files
- `/scripts` - Utility scripts
- `/examples` - Example code

## Project Overview

This project uses SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) methodology with Claude-Flow orchestration for systematic Test-Driven Development.

## SPARC Commands

### Core Commands
- `npx claude-flow sparc modes` - List available modes
- `npx claude-flow sparc run <mode> "<task>"` - Execute specific mode
- `npx claude-flow sparc tdd "<feature>"` - Run complete TDD workflow
- `npx claude-flow sparc info <mode>` - Get mode details

### Batchtools Commands
- `npx claude-flow sparc batch <modes> "<task>"` - Parallel execution
- `npx claude-flow sparc pipeline "<task>"` - Full pipeline processing
- `npx claude-flow sparc concurrent <mode> "<tasks-file>"` - Multi-task processing

### Build Commands
- `npm run build` - Build project
- `npm run test` - Run tests
- `npm run lint` - Linting
- `npm run typecheck` - Type checking

## SPARC Workflow Phases

1. **Specification** - Requirements analysis (`sparc run spec-pseudocode`)
2. **Pseudocode** - Algorithm design (`sparc run spec-pseudocode`)
3. **Architecture** - System design (`sparc run architect`)
4. **Refinement** - TDD implementation (`sparc tdd`)
5. **Completion** - Integration (`sparc run integration`)

## 🔐 CRITICAL: AUTHENTICATION STANDARDIZATION

### ⚠️ MANDATORY CLERK AUTHENTICATION ONLY

**ABSOLUTE RULES - NO EXCEPTIONS:**

1. **NEVER use custom JWT tokens or localStorage.getItem('access_token')**
2. **ALWAYS use Clerk authentication hooks and methods**
3. **STANDARDIZE all authentication across frontend and backend**
4. **NO mixing of authentication systems**

### 🚨 Frontend Authentication Rules

**REQUIRED IMPORTS:**
```typescript
import { useAuth, useUser } from '@clerk/nextjs';
```

**CORRECT TOKEN RETRIEVAL:**
```typescript
// ✅ CORRECT - Use Clerk hooks
const { getToken } = useAuth();
const token = await getToken();

// ❌ WRONG - Never use localStorage
const token = localStorage.getItem('access_token');
```

**MANDATORY PATTERNS:**

#### 1. Page-Level Authentication
```typescript
export default function MyPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!isLoaded) return; // Wait for auth to load
    
    if (!isSignedIn) {
      router.push('/sign-in'); // Always use /sign-in, not /login
      return;
    }
  }, [isLoaded, isSignedIn, router]);

  // Component logic...
}
```

#### 2. API Call Authentication
```typescript
const handleAPICall = async () => {
  const { getToken } = useAuth();
  const token = await getToken();
  
  if (!token) {
    router.push('/sign-in');
    return;
  }

  const response = await axios.post('/api/endpoint', data, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
};
```

#### 3. Error Handling
```typescript
// ✅ CORRECT - Proper error handling
if (error.response?.status === 401) {
  router.push('/sign-in'); // Use Clerk route
  return;
}

// ❌ WRONG - Old routes
router.push('/login'); // Never use this
```

### 🚨 Backend Authentication Rules

**REQUIRED IMPORT:**
```python
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
```

**MANDATORY PATTERN:**
```python
@router.post("/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use current_user.id for all operations
    return {"user_id": current_user.id}
```

### 🔍 Authentication Audit Checklist

Before any authentication work, ALWAYS audit:

1. **Frontend Components**: Search for `localStorage.getItem('access_token')`
2. **API Calls**: Ensure all use `await getToken()`  
3. **Error Handling**: Check all redirect to `/sign-in`
4. **Route Protection**: Verify `useAuth()` hooks used correctly
5. **Backend Endpoints**: Confirm `get_current_user` dependency used

### 🚫 FORBIDDEN PATTERNS

**NEVER DO THESE:**
```typescript
// ❌ FORBIDDEN - Custom JWT storage
localStorage.setItem('access_token', token);
localStorage.getItem('access_token');

// ❌ FORBIDDEN - Mixed auth systems
const customToken = getCustomToken();
const clerkToken = await getToken();

// ❌ FORBIDDEN - Old route redirects
router.push('/login');
window.location.href = '/login';

// ❌ FORBIDDEN - Manual token parsing
const decoded = jwt.decode(token);
```

### ✅ REQUIRED STANDARDIZATION

**When working on ANY component with authentication:**

1. **AUDIT FIRST**: Search component for authentication patterns
2. **STANDARDIZE IMPORTS**: Use only Clerk hooks
3. **REPLACE TOKENS**: Convert all localStorage calls to `getToken()`
4. **UPDATE ROUTES**: Change `/login` to `/sign-in`
5. **TEST FLOW**: Verify authentication works end-to-end
6. **DOCUMENT CHANGES**: Update any authentication-related documentation

### 🔧 Authentication Migration Template

```typescript
// BEFORE (❌ Wrong)
const handleAction = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    router.push('/login');
    return;
  }
  // API call...
};

// AFTER (✅ Correct)
const handleAction = async () => {
  const token = await getToken();
  if (!token) {
    router.push('/sign-in');
    return;
  }
  // API call...
};
```

### 🎯 Key Reminder

**The Orientor Platform uses CLERK AUTHENTICATION exclusively. Any component, service, or API endpoint that doesn't follow these patterns is BROKEN and must be immediately updated to use Clerk authentication.**

### 🐛 COMMON AUTHENTICATION ISSUES TO PREVENT

#### Issue #1: Chat Redirect Bug
**Problem**: Chat interface redirects to dashboard instead of sending messages
**Root Cause**: Using `localStorage.getItem('access_token')` instead of Clerk's `getToken()`
**Solution**: Always use `const token = await getToken()` in all components

#### Issue #2: Mixed Authentication Systems  
**Problem**: Some components use Clerk, others use custom JWT
**Root Cause**: Inconsistent authentication implementation
**Solution**: Standardize ALL components to use Clerk authentication only

#### Issue #3: Wrong Redirect Routes
**Problem**: Components redirect to `/login` instead of `/sign-in`
**Root Cause**: Using old authentication route conventions
**Solution**: Always redirect to `/sign-in` for Clerk compatibility

#### Issue #4: Missing Authentication Dependencies
**Problem**: Components break when authentication state changes
**Root Cause**: Not importing required Clerk hooks
**Solution**: Always import `useAuth` and `useUser` from `@clerk/nextjs`

### 🔧 AUTHENTICATION DEBUGGING COMMANDS

When debugging authentication issues:

```bash
# 1. Search for problematic patterns
grep -r "localStorage.getItem('access_token')" frontend/src/
grep -r "router.push('/login')" frontend/src/
grep -r "window.location.*login" frontend/src/

# 2. Find components missing Clerk imports  
grep -r "getToken\|useAuth\|useUser" frontend/src/ | grep -v "@clerk/nextjs"

# 3. Validate backend authentication
grep -r "get_current_user" backend/app/routers/
```

### 📋 AUTHENTICATION TESTING CHECKLIST

Before deploying any authentication-related changes:

- [ ] All API calls use `await getToken()` 
- [ ] All redirects go to `/sign-in`
- [ ] No `localStorage.getItem('access_token')` calls
- [ ] All components import `useAuth` from `@clerk/nextjs`
- [ ] Backend endpoints use `get_current_user` dependency
- [ ] Error handling redirects to correct Clerk routes
- [ ] Chat functionality works without redirects
- [ ] All protected pages check `isSignedIn` properly

### 🎯 FINAL AUTHENTICATION RULE

**IF YOU SEE ANY AUTHENTICATION CODE THAT DOESN'T USE CLERK, STOP IMMEDIATELY AND FIX IT. NO EXCEPTIONS. NO MIXED SYSTEMS. CLERK ONLY.**

## Code Style & Best Practices

- **Modular Design**: Files under 500 lines
- **Environment Safety**: Never hardcode secrets
- **Test-First**: Write tests before implementation
- **Clean Architecture**: Separate concerns
- **Documentation**: Keep updated
- **Clerk Authentication**: MANDATORY - no exceptions
