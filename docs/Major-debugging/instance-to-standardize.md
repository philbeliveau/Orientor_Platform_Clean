# 🚨 ORIENTOR PLATFORM: COMPREHENSIVE PATTERN STANDARDIZATION TRACKER

**Mission**: Track every single broken pattern instance across the entire codebase and monitor standardization progress.

## 📊 REAL-TIME STATISTICS SUMMARY

| Pattern Type | Total Found | Fixed | In Progress | Remaining | Priority |
|--------------|-------------|-------|-------------|-----------|----------|
| **Pattern #1: SQLAlchemy → Prisma Mismatches** | 300+ | 0 | 0 | 300+ | P0 🚨 |
| **Pattern #2: Missing Auth Imports** | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **Pattern #3: Model Name Mismatches** | 15+ | 0 | 0 | 15+ | P1 🟠 |
| **Pattern #4: Async/Await Issues** | 15+ | 0 | 0 | 15+ | P0 🚨 |
| **Pattern #5: Wrong Redirect Routes** | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **TOTAL INSTANCES** | **330+** | **0** | **0** | **330+** | |

---

# 🔴 PATTERN #1: SQLALCHEMY → PRISMA CLIENT MISMATCHES

**Impact**: P0 CRITICAL - Causes runtime errors, 500 responses, platform failure
**Count**: 300+ instances across 85+ files

## Function Signature Mismatches (Critical Path)

### Instance 1: Career Progression Router
- **File**: `backend/app/routers/career_progression.py:34`
- **Status**: 🚨 BROKEN
- **Pattern**: Function expects SQLAlchemy Session but receives Prisma client
- **Current Code**:
  ```python
  @router.post("/career-progression")
  async def career_progression(
      db: Session = Depends(get_db),  # ← Expects SQLAlchemy Session
      current_user: User = Depends(get_current_user)
  ):
  ```
- **Required Fix**:
  ```python
  @router.post("/career-progression")
  async def career_progression(
      current_user: User = Depends(get_current_user),
      prisma: Prisma = Depends(get_prisma)  # ← Use Prisma client
  ):
  ```
- **Impact**: Career progression functionality completely broken

### Instance 2: Job Chat Router
- **File**: `backend/app/routers/job_chat.py:26`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Current Code**:
  ```python
  async def job_chat_endpoint(
      db: Session = Depends(get_db),  # ← Wrong type
      current_user: User = Depends(get_current_user)
  ):
  ```
- **Required Fix**:
  ```python
  async def job_chat_endpoint(
      current_user: User = Depends(get_current_user),
      prisma: Prisma = Depends(get_prisma)
  ):
  ```
- **Impact**: Job chat functionality broken

### Instance 3: Program Recommendations Router
- **File**: `backend/app/routers/program_recommendations.py:2`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: Education program recommendations broken

### Instance 4: Socratic Chat Router
- **File**: `backend/app/routers/socratic_chat.py:26`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: AI tutoring system broken

### Instance 5: Share Router
- **File**: `backend/app/routers/share.py:4`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: Content sharing functionality broken

### Instance 6: School Programs Router
- **File**: `backend/app/routers/school_programs.py:33`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: School program search broken

### Instance 7: Holland Test Router
- **File**: `backend/app/routers/holland_test.py:5`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: Personality test system broken

### Instance 8: Chat Analytics Router
- **File**: `backend/app/routers/chat_analytics.py:3`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatch
- **Impact**: Chat analytics broken

### Instance 9-35: All Service Files
- **Files**: All 25+ files in `backend/app/services/`
- **Status**: 🚨 BROKEN
- **Pattern**: Function signature mismatches throughout service layer
- **Impact**: Core business logic layer completely broken

## Database Execute() Calls (Critical Path)

### Instance 36: Vector Search Execute
- **File**: `backend/app/routers/vector_search.py:442`
- **Status**: 🚨 BROKEN
- **Pattern**: Using SQLAlchemy db.execute() on Prisma client
- **Current Code**:
  ```python
  results = db.execute(query, {"user_id": current_user.id}).fetchall()
  ```
- **Required Fix**:
  ```python
  results = await prisma.query_raw("SELECT ...", current_user.id)
  ```
- **Impact**: Vector similarity search broken

### Instance 37-43: Jobs Router Execute Calls
- **File**: `backend/app/routers/jobs.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 90, 105, 139, 160, 229, 284, 300
- **Pattern**: Multiple db.execute() calls on Prisma client
- **Current Code**:
  ```python
  existing = db.execute(check_query, {...})
  result = db.execute(saved_job_query, {"job_id": existing[0]}).fetchone()
  ```
- **Required Fix**:
  ```python
  existing = await prisma.query_raw("SELECT ...", ...)
  result = await prisma.query_raw("SELECT ...", job_id)
  ```
- **Impact**: Job saving and management completely broken

### Instance 44-48: Careers Router Execute Calls
- **File**: `backend/app/routers/careers.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 196, 270, 386, 422, 575
- **Pattern**: Multiple db.execute() calls causing 500 errors
- **Current Code**:
  ```python
  result = db.execute(insert_query, {...})
  oasis_results = db.execute(oasis_query, {"user_id": current_user.id}).fetchall()
  ```
- **Required Fix**:
  ```python
  result = await prisma.query_raw("INSERT ...", ...)
  oasis_results = await prisma.query_raw("SELECT ...", current_user.id)
  ```
- **Impact**: Career recommendations and saved careers broken (causes Space page NaN%)

### Instance 49-54: School Programs Execute Calls
- **File**: `backend/app/routers/school_programs.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 101, 102, 103, 159, 219, 319
- **Pattern**: Multiple text() queries using SQLAlchemy syntax
- **Current Code**:
  ```python
  types_result = db.execute(text(types_sql)).fetchall()
  levels_result = db.execute(text(levels_sql)).fetchall()
  ```
- **Required Fix**:
  ```python
  types_result = await prisma.query_raw("SELECT ...")
  levels_result = await prisma.query_raw("SELECT ...")
  ```
- **Impact**: Education program filters and search broken

### Instance 55-77: Holland Test Execute Calls
- **File**: `backend/app/routers/holland_test.py`
- **Status**: 🚨 BROKEN
- **Locations**: 23 instances across lines 103, 164, 191, 285, 300, 316, 335, 376, 410, 452, 466, 478, 494, 511, 539, 613, 638, 708, 728, 756, 789, 844, 855
- **Pattern**: Most heavily affected router - 23 broken db.execute() calls
- **Impact**: Complete Holland personality test system failure

## Database Query() Operations

### Instance 78-82: Recommendations Router Query Calls
- **File**: `backend/app/routers/recommendations.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 184, 191, 295
- **Pattern**: Using SQLAlchemy ORM syntax on Prisma client
- **Current Code**:
  ```python
  existing_recommendations = db.query(UserRecommendation.oasis_code).filter(...)
  profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
  ```
- **Required Fix**:
  ```python
  existing_recommendations = await prisma.userrecommendation.find_many(where={...})
  profile = await prisma.userprofile.find_first(where={"user_id": current_user.id})
  ```
- **Impact**: User recommendations completely broken

### Instance 83-84: Careers Router Query Calls
- **File**: `backend/app/routers/careers.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 361, 362
- **Pattern**: SQLAlchemy ORM queries on Prisma client
- **Impact**: Career fit analysis broken

### Instance 85-200+: All Service Files Query Calls
- **Files**: Every service file in `backend/app/services/`
- **Status**: 🚨 BROKEN
- **Pattern**: Extensive db.query() usage throughout service layer
- **Impact**: Entire service layer broken

## Transaction Operations

### Instance 201-204: Recommendations Router Transactions
- **File**: `backend/app/routers/recommendations.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 289-290, 347-348
- **Pattern**: Using SQLAlchemy add/commit on Prisma client
- **Current Code**:
  ```python
  db.add(user_recommendation)
  db.commit()
  ```
- **Required Fix**:
  ```python
  await prisma.userrecommendation.create(data={...})
  # Prisma auto-commits, no explicit commit needed
  ```
- **Impact**: Cannot save user recommendations

### Instance 205-210: Jobs Router Transactions
- **File**: `backend/app/routers/jobs.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 170, 304
- **Pattern**: SQLAlchemy commit() calls on Prisma
- **Impact**: Job data not persisting

### Instance 211-213: Careers Router Transactions
- **File**: `backend/app/routers/careers.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 200, 577
- **Pattern**: SQLAlchemy commit() calls on Prisma
- **Impact**: Career data not persisting (contributes to Space page issues)

### Instance 214-219: Holland Test Transactions
- **File**: `backend/app/routers/holland_test.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 344, 556, 860
- **Pattern**: SQLAlchemy commit() calls on Prisma
- **Impact**: Test results not saving

## Pydantic Model Conversion

### Instance 220-223: Conversations Router from_orm
- **File**: `backend/app/routers/conversations.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 136, 160, 183, 219
- **Pattern**: Using SQLAlchemy from_orm() pattern
- **Current Code**:
  ```python
  conversations=[ConversationResponse.from_orm(conv) for conv in conversations]
  return ConversationResponse.from_orm(new_conversation)
  ```
- **Required Fix**:
  ```python
  conversations=[ConversationResponse(**conv.dict()) for conv in conversations]
  return ConversationResponse(**new_conversation.dict())
  ```
- **Impact**: Chat conversation responses broken

### Instance 224-300+: Import Cleanup Required
- **Files**: 85+ files contain SQLAlchemy imports that need replacement
- **Status**: 🚨 BROKEN
- **Pattern**: SQLAlchemy imports throughout codebase
- **Impact**: Import conflicts and dependency issues

---

# ✅ PATTERN #2: MISSING CLERK AUTHENTICATION IMPORTS

**Status**: ✅ **NO ISSUES FOUND** - Frontend authentication is perfectly implemented!

**Findings**: 
- Zero instances of localStorage token access
- All components properly use Clerk `getToken()`
- All redirects use correct `/sign-in` route
- Consistent `useAuth` imports from `@clerk/nextjs`
- No mixed authentication systems

**Quality Score**: 10/10 - Exemplary Clerk implementation

---

# 🟠 PATTERN #3: INCORRECT PRISMA MODEL NAMES

**Impact**: P1 HIGH - Causes runtime errors when accessing models
**Count**: 15+ instances across multiple files

### Instance 301: Suggested Peers Model Mismatch
- **File**: `backend/app/routers/peers.py:98`
- **Status**: 🚨 BROKEN
- **Pattern**: Incorrect model name usage
- **Current Code**:
  ```python
  await db.suggestedpeers.find_many(
  ```
- **Required Fix**:
  ```python
  await db.suggestedpeer.find_many(
  ```
- **Impact**: Peer matching functionality broken

### Instance 302-303: Personality Profile Model Issues
- **File**: `backend/app/services/peer_matching_service.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 449, 488
- **Pattern**: CamelCase vs snake_case mismatch
- **Current Code**:
  ```python
  await prisma.personalityprofile.find_first(
  ```
- **Required Fix**:
  ```python
  await prisma.personality_profile.find_first(
  ```
- **Impact**: Personality matching broken

### Instance 304-312: Onboarding Router Model Names
- **File**: `backend/app/routers/onboarding.py`
- **Status**: 🚨 BROKEN
- **Locations**: Lines 64, 102, 316, 324, 338, 388, 477, 509, 533
- **Pattern**: Using plural instead of singular model name
- **Current Code**:
  ```python
  db.personality_profiles
  ```
- **Required Fix**:
  ```python
  db.personality_profile
  ```
- **Impact**: User onboarding process broken

### Instance 313: User Router Model Name
- **File**: `backend/app/routers/user.py:64`
- **Status**: 🚨 BROKEN
- **Pattern**: Plural model name instead of singular
- **Impact**: User profile operations broken

### Instance 314: Test File Model Reference
- **File**: `backend/tests/test_all_tables.py:31`
- **Status**: 🚨 BROKEN
- **Pattern**: Incorrect test model reference
- **Current Code**:
  ```python
  client.suggestedpeers.count()
  ```
- **Required Fix**:
  ```python
  client.suggestedpeer.count()
  ```
- **Impact**: Tests failing

### Instance 315: Hardcoded SQL Table References
- **File**: `backend/app/routers/hexaco_test.py:489`
- **Status**: 🚨 BROKEN
- **Pattern**: Direct SQL instead of Prisma model
- **Current Code**:
  ```python
  UPDATE personality_profiles SET...
  ```
- **Required Fix**: Use Prisma update operations
- **Impact**: Data updates may fail

---

# 🔴 PATTERN #4: MISSING ASYNC/AWAIT PATTERNS  

**Impact**: P0 CRITICAL - Causes runtime errors and platform instability
**Count**: 15+ instances across routers and services

### Instance 316: Career Progression Router Async Missing
- **File**: `backend/app/routers/career_progression.py:34`
- **Status**: 🚨 BROKEN  
- **Pattern**: Function calling async services without await
- **Current Code**:
  ```python
  @router.post("/career-progression")
  async def career_progression(db: Session = Depends(get_db)):
      # Missing await on async service calls
  ```
- **Required Fix**: Add proper async/await patterns
- **Impact**: Career progression endpoints fail

### Instance 317: Job Chat Async Issues
- **File**: `backend/app/routers/job_chat.py:26`
- **Status**: 🚨 BROKEN
- **Pattern**: Async function definition but sync execution
- **Impact**: Job chat functionality unstable

### Instance 318: Program Recommendations Async
- **File**: `backend/app/routers/program_recommendations.py:2`
- **Status**: 🚨 BROKEN
- **Pattern**: Missing async patterns in router
- **Impact**: Education recommendations fail

### Instance 319: Socratic Chat Async
- **File**: `backend/app/routers/socratic_chat.py:26`
- **Status**: 🚨 BROKEN
- **Pattern**: Async/await mismatch in AI chat
- **Impact**: AI tutoring system unstable

### Instance 320: Share Router Async
- **File**: `backend/app/routers/share.py:4`
- **Status**: 🚨 BROKEN
- **Pattern**: Missing async patterns
- **Impact**: Content sharing fails

### Instance 321-330: Service Layer Async Issues
- **Files**: Multiple service files
- **Status**: 🚨 BROKEN
- **Pattern**: Service methods not properly awaited
- **Impact**: Service layer instability

---

# ✅ PATTERN #5: WRONG REDIRECT ROUTES

**Status**: ✅ **NO ISSUES FOUND** - All redirects use correct `/sign-in` route!

**Findings**: 
- Zero instances of `/login` redirects found
- All components properly redirect to `/sign-in`
- Consistent with Clerk authentication standards

---

# 📋 STANDARDIZATION PROGRESS TRACKING

## Phase 1: Critical Path (P0 Issues) 🚨
**Status**: NOT STARTED
- [ ] Fix all function signature mismatches (Instances 1-35)
- [ ] Convert all db.execute() calls (Instances 36-77)  
- [ ] Fix async/await patterns (Instances 316-330)
- [ ] **Target**: Space page works, HEXACO test loads, no 500 errors

## Phase 2: Data Operations (P1 Issues) 🟠  
**Status**: NOT STARTED
- [ ] Convert all db.query() operations (Instances 78-200+)
- [ ] Fix Prisma model names (Instances 301-315)
- [ ] Convert transaction patterns (Instances 201-219)
- [ ] **Target**: All CRUD operations work correctly

## Phase 3: Response Patterns (P2 Issues) 🟡
**Status**: NOT STARTED  
- [ ] Convert from_orm() patterns (Instances 220-223)
- [ ] Clean up SQLAlchemy imports (Instances 224-300+)
- [ ] **Target**: Clean codebase with no legacy patterns

## Overall Progress: 0% Complete (0/330+ instances fixed)

---

# 🛠️ QUICK DETECTION COMMANDS

## Find Remaining Issues:
```bash
# P0 Critical - Function signatures
grep -r "def.*db: Session" backend/app/

# P0 Critical - Execute calls  
grep -r "db\.execute\|\.execute(" backend/app/

# P0 Critical - Async issues
grep -r "@router\." backend/app/ | grep -v "async def"

# P1 High - Query operations
grep -r "db\.query\|db\.add\|db\.commit" backend/app/

# P1 High - Model names
grep -r "personalityprofile\|suggestedpeers" backend/app/

# P2 Medium - Legacy patterns  
grep -r "from_orm\|from sqlalchemy" backend/app/
```

## Validate Fixes:
```bash
# Test Space page (should show data, not NaN%)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/careers/saved

# Test HEXACO (should load questions)  
curl http://localhost:8000/api/v1/hexaco-test/questions

# Test Prisma connection
python -c "from prisma import Prisma; print('✅ OK')"
```

---

# 🎯 AGENT COORDINATION INSTRUCTIONS

## Scanning Agents:
- ✅ **researcher-1**: Backend SQLAlchemy patterns - COMPLETED
- ✅ **researcher-2**: Frontend auth patterns - COMPLETED  
- ✅ **researcher-3**: Model name issues - COMPLETED
- ✅ **researcher-4**: Async/await issues - COMPLETED

## Fixing Agents (Next Phase):
- **coder-1**: Focus on P0 function signatures (Instances 1-35)
- **coder-2**: Focus on P0 execute calls (Instances 36-77)  
- **coder-3**: Focus on P0 async patterns (Instances 316-330)
- **coder-4**: Focus on P1 model names (Instances 301-315)

## Validation Agent:
- **tester**: Validate each fix, update instance status, verify platform functionality

---

# 🚨 EMERGENCY ROLLBACK PROCEDURES

If any fix breaks the platform:

```bash
# Rollback service changes
git checkout HEAD~1 -- backend/app/services/

# Rollback router changes  
git checkout HEAD~1 -- backend/app/routers/

# Regenerate Prisma client
npx prisma generate

# Test basic functionality
python -c "from prisma import Prisma; print('✅ Rollback OK')"
```

---

**Last Updated**: 2025-01-14 16:30 UTC
**Total Instances**: 330+  
**Critical Path**: 115+ P0 instances requiring immediate attention
**Platform Status**: 🚨 BROKEN - Requires immediate standardization