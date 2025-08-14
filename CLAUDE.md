## ALWAYS WORK IN THE ORIENTOR_PLATFORM_CLEAN REPO.

# 🚨 POST-PRISMA MIGRATION BUG RESOLUTION

## CRITICAL TRIAGE SYSTEM
- **P0 CRITICAL**: Authentication failures, database connection errors  
- **P1 HIGH**: API endpoint failures, data model mismatches
- **P2 MEDIUM**: Performance degradation, import issues
- **P3 LOW**: Documentation, cleanup tasks

## SPARC BUG RESOLUTION WORKFLOW
- `npx claude-flow sparc run bug-triage "<issue>"` - Classify and prioritize
- `npx claude-flow sparc run prisma-debug "<error>"` - Prisma-specific debugging
- `npx claude-flow sparc batch bug-fix,test,validate "<issue>"` - Full resolution pipeline

## 🗃️ PRISMA MIGRATION STATUS TRACKER

### COMPLETED MIGRATIONS ✅
- Schema generation: Prisma Client Python + JS
- Model definitions: 65+ tables migrated
- Database connection: PostgreSQL configured
- Authentication system: 85% Clerk standardization complete

### PENDING CRITICAL FIXES 🚨 (UPDATED PRIORITIES)
- [ ] **P0 CRITICAL**: Fix function signature mismatches (Pattern #1) - ~27 service files
- [ ] **P0 CRITICAL**: Convert `db.execute()` to `prisma.query_raw()` - All affected services  
- [ ] **P1 HIGH**: Add missing `useAuth` imports to frontend components
- [ ] **P1 HIGH**: Fix redirect routes from `/login` to `/sign-in`
- [ ] **P2 MEDIUM**: `from_orm()` pattern elimination across codebase
- [ ] **P2 MEDIUM**: Transaction handling migration to `prisma.$transaction()`
- [ ] **P3 LOW**: Foreign key relationship optimizations

## 🛠️ BUG RESOLUTION TOOLKIT

### Prisma Debugging Commands
- `npx prisma db pull` - Sync schema with database
- `npx prisma generate` - Regenerate Prisma client
- `PYTHONPATH=. python -c "from prisma import Prisma; print('✅ Prisma import OK')"` - Test imports

### Issue Scanning Commands  
- `grep -r "from_orm(" backend/app/` - Find SQLAlchemy remnants
- `grep -r "db\.query\|db\.add\|db\.commit" backend/app/` - Find old session patterns
- `grep -r "Session\|sessionmaker" backend/app/` - Find SQLAlchemy sessions

### Migration Validation
- `npm run test:prisma` - Run Prisma-specific tests
- `npm run migrate:validate` - Validate all migrations

## 🔍 COMMON PRISMA MIGRATION ERRORS

### Error: "'Prisma' object has no attribute 'execute'"
**Cause**: SQLAlchemy `db.execute()` pattern used on Prisma client
**Root Pattern**: 
```python
# ❌ BROKEN PATTERN:
def get_saved_careers(db: Session, user_id: int):  # Expects SQLAlchemy
    result = db.execute(text(query), params)       # SQLAlchemy method
    
# Router injects Prisma client:
esco_careers = get_saved_careers(db, current_user.id)  # db = Prisma client
```
**Fix**: Convert to Prisma operations
```python
# ✅ CORRECT PATTERN:
async def get_saved_careers(prisma: Prisma, user_id: int):
    return await prisma.query_raw("SELECT * FROM saved_recommendations WHERE user_id = $1", user_id)
    # OR use Prisma client methods:
    return await prisma.savedrecommendation.find_many(where={"user_id": user_id})
```

### Error: "AttributeError: 'NoneType' object has no attribute 'from_orm'"
**Cause**: SQLAlchemy pattern still in use
**Fix**: Replace `Model.from_orm(data)` with `Model(**data.dict())`

### Error: "ImportError: cannot import name 'Session'"
**Cause**: SQLAlchemy Session import
**Fix**: Replace with `from prisma import Prisma` and dependency injection

### Error: "'Prisma' object has no attribute 'savedcareers'"
**Cause**: Incorrect Prisma model name (should be `savedrecommendation`)
**Fix**: Use correct model name from schema.prisma

### Error: "Field 'id' is required"  
**Cause**: Prisma model requires explicit ID handling
**Fix**: Use `prisma.model.create(data={...})` with proper field mapping

### Error: "Cannot resolve field on Prisma model"
**Cause**: Schema mismatch between Prisma and database
**Fix**: Run `npx prisma db push` to sync schema

### Error: "'async' object has no method 'commit'"
**Cause**: Trying to use SQLAlchemy transaction methods on Prisma
**Fix**: Use `await prisma.$transaction([...])` for Prisma transactions

## 🔧 CRITICAL BROKEN PATTERNS IDENTIFIED

### Pattern #1: Function Signature Mismatch (Most Common)
**Problem**: Routers inject Prisma clients, but services expect SQLAlchemy Sessions

**Where Found**: `backend/app/routers/careers.py:250` → `backend/app/services/Swipe_career_recommendation_service.py:1035`

**Broken Code**:
```python
# Router (careers.py:250):
@router.get("/saved")
def read_saved_careers(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)  # ← PRISMA CLIENT injected
):
    esco_careers = get_saved_careers(db, current_user.id)  # ← PASSES PRISMA CLIENT

# Service (service.py:1035):
def get_saved_careers(db: Session, user_id: int):  # ← EXPECTS SQLAlchemy Session
    result = db.execute(text(query), {"user_id": user_id})  # ← CALLS .execute() on PRISMA
```

**Standard Fix Pattern**:
```python
# ✅ CORRECT - Update service signature and method calls:
async def get_saved_careers(prisma: Prisma, user_id: int):  # ← Prisma client parameter
    result = await prisma.query_raw(  # ← Use Prisma's query_raw method
        "SELECT * FROM saved_recommendations WHERE user_id = $1", 
        user_id
    )
    return result

# ✅ CORRECT - Update router to async:
@router.get("/saved")
async def read_saved_careers(  # ← Add async
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma_client)  # ← Use consistent naming
):
    esco_careers = await get_saved_careers(prisma, current_user.id)  # ← Add await
```

### Pattern #2: Missing useAuth Imports (Frontend)
**Problem**: Components use `getToken()` without importing from `@clerk/nextjs`

**Broken Code**:
```typescript
// ❌ BROKEN:
const token = await getToken();  // ← getToken is not defined
if (error.status === 401) router.push('/login');  // ← Wrong route
```

**Standard Fix Pattern**:
```typescript
// ✅ CORRECT:
import { useAuth } from '@clerk/nextjs';  // ← Add import

const { getToken } = useAuth();  // ← Extract from hook
const token = await getToken();
if (error.status === 401) router.push('/sign-in');  // ← Correct route
```

### Pattern #3: Model Name Mismatches
**Problem**: Using incorrect Prisma model names that don't match schema.prisma

**Examples Found**:
- `prisma.savedcareers` (wrong) → `prisma.savedrecommendation` (correct)
- `prisma.hexaco_test` (wrong) → `prisma.hexacoquestion` (correct)

**Standard Fix**: Always check `schema.prisma` for exact model names

## 🛠️ STANDARDIZED DEBUGGING WORKFLOW

### Step 1: Identify the Broken Pattern
```bash
# Find Prisma execution errors:
grep -r "db\.execute\|\.execute(" backend/app/services/

# Find function signature mismatches:
grep -r "def.*db: Session" backend/app/services/
grep -r "Depends(get_prisma" backend/app/routers/

# Find frontend auth issues:
grep -r "getToken.*not.*function" frontend/src/
grep -r "localStorage.getItem.*access_token" frontend/src/
```

### Step 2: Apply Standard Fix Pattern
1. **Service Layer**: Change `Session` to `Prisma`, `db.execute()` to `prisma.query_raw()`
2. **Router Layer**: Add `async/await` for service calls
3. **Frontend**: Add `useAuth` imports, fix redirect routes

### Step 3: Validate the Fix
```bash
# Test Prisma connection:
python -c "from prisma import Prisma; print('✅ Prisma import OK')"

# Test specific service:
grep -n "async def get_saved_careers" backend/app/services/

# Test frontend auth:
grep -n "useAuth.*@clerk/nextjs" frontend/src/app/space/
```

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

### 🔄 PRISMA-SPECIFIC BATCHING
- **Schema updates**: Generate + migrate + test in single operation
- **Model fixes**: Update all related models simultaneously
- **Import cleanup**: Fix all imports across entire module together
- **Database operations**: Convert ALL queries in related files together

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

## 📋 SYSTEMATIC BUG RESOLUTION PHASES

### Phase 1: Critical Database Operations (Week 1)
- [ ] Convert all `db.query()` to `prisma.model.find()`
- [ ] Replace `db.add()` with `prisma.model.create()`
- [ ] Update all `db.commit()` to `await prisma.$transaction()`
- [ ] Fix foreign key relationships and constraints

### Phase 2: Authentication Integration (Week 1)
- [ ] Standardize all routers to use `get_current_user_with_db_sync`
- [ ] Update frontend token handling for Prisma compatibility
- [ ] Test all authentication flows end-to-end

### Phase 3: Data Model Synchronization (Week 2)
- [ ] Validate all Pydantic models match Prisma schema
- [ ] Update response serialization (remove `from_orm()`)
- [ ] Fix type mismatches and validation errors

### Phase 4: Performance & Testing (Week 2)
- [ ] Optimize Prisma queries for performance
- [ ] Create comprehensive test suite
- [ ] Load testing and validation

## 🔐 CRITICAL: AUTHENTICATION + PRISMA INTEGRATION

### ⚠️ MANDATORY CLERK AUTHENTICATION ONLY

**ABSOLUTE RULES - NO EXCEPTIONS:**

1. **NEVER use custom JWT tokens or localStorage.getItem('access_token')**
2. **ALWAYS use Clerk authentication hooks and methods**
3. **STANDARDIZE all authentication across frontend and backend**
4. **NO mixing of authentication systems**
5. **ALWAYS use Prisma for all database operations**

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

### 🚨 Backend Authentication + Prisma Rules

**REQUIRED IMPORTS:**
```python
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from prisma import Prisma
```

**MANDATORY PATTERN:**
```python
@router.post("/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    # ✅ CORRECT - Use Prisma client for all database operations
    result = await prisma.model.find_first(where={"user_id": current_user.id})
    return result

# ❌ WRONG - Never use SQLAlchemy sessions
# db: Session = Depends(get_db)
# result = db.query(Model).filter(Model.user_id == current_user.id).first()
```

### 🔍 Authentication Audit Checklist

Before any authentication work, ALWAYS audit:

1. **Frontend Components**: Search for `localStorage.getItem('access_token')`
2. **API Calls**: Ensure all use `await getToken()`  
3. **Error Handling**: Check all redirect to `/sign-in`
4. **Route Protection**: Verify `useAuth()` hooks used correctly
5. **Backend Endpoints**: Confirm `get_current_user` dependency used
6. **Database Operations**: Ensure all use Prisma client, not SQLAlchemy

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

```python
# ❌ FORBIDDEN - SQLAlchemy patterns
from sqlalchemy.orm import Session
db: Session = Depends(get_db)
result = db.query(Model).first()
db.add(instance)
db.commit()

# ❌ FORBIDDEN - from_orm usage
return Model.from_orm(result)
```

### ✅ REQUIRED STANDARDIZATION

**When working on ANY component with authentication:**

1. **AUDIT FIRST**: Search component for authentication patterns
2. **STANDARDIZE IMPORTS**: Use only Clerk hooks and Prisma client
3. **REPLACE TOKENS**: Convert all localStorage calls to `getToken()`
4. **UPDATE ROUTES**: Change `/login` to `/sign-in`
5. **MIGRATE DATABASE**: Convert all SQLAlchemy to Prisma operations
6. **TEST FLOW**: Verify authentication works end-to-end
7. **DOCUMENT CHANGES**: Update any authentication-related documentation

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

```python
# BEFORE (❌ Wrong)
@router.post("/endpoint")
async def my_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(Model).filter(Model.user_id == current_user.id).first()
    return Model.from_orm(result)

# AFTER (✅ Correct)
@router.post("/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    result = await prisma.model.find_first(where={"user_id": current_user.id})
    return result
```

### 🎯 Key Reminder

**The Orientor Platform uses CLERK AUTHENTICATION + PRISMA exclusively. Any component, service, or API endpoint that doesn't follow these patterns is BROKEN and must be immediately updated to use Clerk authentication and Prisma database operations.**

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

#### Issue #5: SQLAlchemy + Prisma Mix
**Problem**: Some endpoints still use SQLAlchemy sessions
**Root Cause**: Incomplete migration from SQLAlchemy to Prisma
**Solution**: Convert all database operations to use Prisma client

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

# 4. Find SQLAlchemy remnants
grep -r "Session\|sessionmaker\|from_orm" backend/app/
grep -r "db\.query\|db\.add\|db\.commit" backend/app/
```

### 📋 AUTHENTICATION TESTING CHECKLIST

Before deploying any authentication-related changes:

- [ ] All API calls use `await getToken()` 
- [ ] All redirects go to `/sign-in`
- [ ] No `localStorage.getItem('access_token')` calls
- [ ] All components import `useAuth` from `@clerk/nextjs`
- [ ] Backend endpoints use `get_current_user` dependency
- [ ] All database operations use Prisma client
- [ ] No SQLAlchemy Session dependencies remain
- [ ] Error handling redirects to correct Clerk routes
- [ ] Chat functionality works without redirects
- [ ] All protected pages check `isSignedIn` properly

### 🎯 FINAL AUTHENTICATION RULE

**IF YOU SEE ANY AUTHENTICATION CODE THAT DOESN'T USE CLERK, OR ANY DATABASE CODE THAT DOESN'T USE PRISMA, STOP IMMEDIATELY AND FIX IT. NO EXCEPTIONS. NO MIXED SYSTEMS. CLERK + PRISMA ONLY.**

## Code Style & Best Practices

- **Modular Design**: Files under 500 lines
- **Environment Safety**: Never hardcode secrets
- **Test-First**: Write tests before implementation
- **Clean Architecture**: Separate concerns
- **Documentation**: Keep updated
- **Clerk Authentication**: MANDATORY - no exceptions
- **Prisma Database**: MANDATORY - no SQLAlchemy

## 🚀 QUICK REFERENCE: ORIENTOR PLATFORM PATTERNS

### Critical Errors & Instant Fixes
```bash
# ERROR: 'Prisma' object has no attribute 'execute'
# LOCATION: Any service file using db.execute()
# FIX: Replace with await prisma.query_raw()

# ERROR: 'Prisma' object has no attribute 'savedcareers'  
# LOCATION: careers.py, space page
# FIX: Use correct model name: prisma.savedrecommendation

# ERROR: getToken is not a function
# LOCATION: Frontend auth components
# FIX: import { useAuth } from '@clerk/nextjs'
```

### 30-Second Pattern Check
```bash
# Is service broken? (Should return 0 matches)
grep -c "def.*db: Session" backend/app/services/

# Is frontend auth broken? (Should find imports)  
grep -c "useAuth.*@clerk/nextjs" frontend/src/app/space/page.tsx

# Are redirects correct? (Should return 0 matches for /login)
grep -c "router.push('/login')" frontend/src/
```

### Emergency Rollback Commands
```bash
# If service fixes break anything:
git checkout HEAD~1 -- backend/app/services/Swipe_career_recommendation_service.py
npx prisma generate

# If schema changes break anything:
git checkout HEAD~1 -- backend/prisma/schema.prisma
npx prisma migrate reset --force
```

### Success Validation (All Should Work)
```bash
# ✅ Space page shows data (not NaN%)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/careers/saved

# ✅ HEXACO loads questions  
curl http://localhost:8000/api/v1/hexaco-test/questions

# ✅ No auth console errors
# Visit http://localhost:3000/space and check browser console
```

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.