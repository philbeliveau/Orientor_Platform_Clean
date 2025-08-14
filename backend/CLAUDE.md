# 🚨 BACKEND BUG RESOLUTION AGENT GUIDE

## CRITICAL: AGENTS MUST USE CONTEXT7 FOR UP-TO-DATE DOCUMENTATION

**BEFORE ANY FIXES, ALWAYS FETCH LATEST DOCS:**
```bash
# Use Context7 MCP for current patterns and best practices
mcp__context7__get-library-docs /prisma/docs "migration patterns"
mcp__context7__get-library-docs /context7/fastapi_tiangolo "authentication" 
mcp__context7__get-library-docs /clerk/clerk-sdk-python "backend integration"
```

## 🗃️ CRITICAL PRISMA MIGRATION ISSUES

### ✅ REQUIRED DATABASE MODEL FIXES
Based on testing, these Prisma models are MISSING or MISCONFIGURED:

#### 1. **HEXACO Test Model Missing**
**Error**: `'Prisma' object has no attribute 'hexacoquestion'`
**Fix Pattern**:
```bash
# Check schema.prisma for missing model
grep -r "hexacoquestion\|HexacoQuestion" backend/prisma/

# Expected model structure
model HexacoQuestion {
  id        Int     @id @default(autoincrement())
  question  String
  dimension String
  // ... other fields
}
```

#### 2. **Saved Careers Model Missing**
**Error**: `'Prisma' object has no attribute 'savedcareers'`
**Fix Pattern**:
```bash
# Check schema.prisma for missing model
grep -r "savedcareers\|SavedCareer" backend/prisma/

# Expected model structure  
model SavedCareer {
  id        Int     @id @default(autoincrement())
  userId    Int
  careerId  Int
  // ... other fields
}
```

### 🔍 PRISMA SCHEMA VALIDATION COMMANDS
```bash
# 1. Validate current schema
npx prisma validate

# 2. Generate fresh client
npx prisma generate

# 3. Check database sync
npx prisma db pull

# 4. Test Prisma connection
PYTHONPATH=. python -c "from prisma import Prisma; print('✅ Prisma import OK')"
```

## 🐛 CRITICAL BACKEND SERVICE FAILURES

### 1. **CHAT SERVICE ANTHROPIC CLIENT ERROR** (P0 CRITICAL)
**Error**: `AsyncClient.__init__() got an unexpected keyword argument 'proxies'`
**Root Cause**: Anthropic client configuration issue
**Fix Pattern**:
```python
# ❌ BROKEN PATTERN
from anthropic import AsyncClient
client = AsyncClient(
    api_key=settings.ANTHROPIC_API_KEY,
    proxies=proxies_config  # THIS PARAMETER DOESN'T EXIST
)

# ✅ CORRECT PATTERN
from anthropic import AsyncClient
client = AsyncClient(
    api_key=settings.ANTHROPIC_API_KEY
    # Remove proxies parameter
)
```

### 2. **MISSING DEPENDENCIES** (P0 CRITICAL)
**Error**: `ModuleNotFoundError: No module named 'langchain'`
**Fix Commands**:
```bash
# Install missing dependencies
pip install langchain langchain-openai

# Verify installation
python -c "import langchain; print('✅ Langchain installed')"
python -c "import langchain_openai; print('✅ Langchain-OpenAI installed')"
```

### 3. **MISSING API ENDPOINTS** (P1 HIGH)
**Issues Found**: Notes creation (404), Education program save (404)
**Fix Pattern**:
```python
# Create missing endpoints in FastAPI
@router.post("/notes")
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    note = await prisma.note.create(data={
        "content": note_data.content,
        "userId": current_user.id
    })
    return note

@router.post("/education/save")
async def save_program(
    program_data: ProgramSave,
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    saved_program = await prisma.savedprogram.create(data={
        "programId": program_data.program_id,
        "userId": current_user.id
    })
    return saved_program
```

### 4. **AUTHENTICATION INTEGRATION ISSUES** (P1 HIGH)
**Error**: `Could not validate credentials` (401 errors)
**Fix Pattern**:
```python
# ✅ CORRECT CLERK BACKEND INTEGRATION
from app.utils.clerk_auth import get_current_user_with_db_sync

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user_with_db_sync),
    prisma: Prisma = Depends(get_prisma)
):
    # User is automatically validated by dependency
    return {"user_id": current_user.id}
```

## 🔐 CLERK AUTHENTICATION BACKEND PATTERNS

### ✅ REQUIRED IMPORTS (Verify with Context7)
```python
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from prisma import Prisma
```

### ✅ CORRECT DEPENDENCY INJECTION
```python
# ✅ ALWAYS USE THIS PATTERN
@router.post("/api/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    # Authentication and database handled automatically
    result = await prisma.model.find_first(where={"user_id": current_user.id})
    return result
```

### ❌ FORBIDDEN PATTERNS - NEVER USE THESE
```python
# ❌ FORBIDDEN - SQLAlchemy patterns
from sqlalchemy.orm import Session
db: Session = Depends(get_db)
result = db.query(Model).first()
db.add(instance)
db.commit()

# ❌ FORBIDDEN - from_orm usage
return Model.from_orm(result)

# ❌ FORBIDDEN - Manual JWT validation
token = request.headers.get("Authorization")
decoded = jwt.decode(token, secret)
```

## 🛠️ DATABASE SCHEMA MIGRATION GUIDE

### 1. **Check Missing Models**
```bash
# Search for model usage in code vs schema definition
grep -r "prisma\..*\." app/ | grep -v "create\|find\|update\|delete"

# Common missing models from testing:
# - hexacoquestion / HexacoQuestion
# - savedcareers / SavedCareer  
# - notes / Note
# - savedprograms / SavedProgram
```

### 2. **Add Missing Models to Schema**
```prisma
// schema.prisma additions needed

model HexacoQuestion {
  id        Int     @id @default(autoincrement())
  question  String
  dimension String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model SavedCareer {
  id        Int     @id @default(autoincrement())
  userId    Int
  careerId  Int
  createdAt DateTime @default(now())
  
  user      User    @relation(fields: [userId], references: [id])
}

model Note {
  id        Int     @id @default(autoincrement())
  content   String
  userId    Int
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  user      User    @relation(fields: [userId], references: [id])
}

model SavedProgram {
  id        Int     @id @default(autoincrement())
  programId Int
  userId    Int
  createdAt DateTime @default(now())
  
  user      User    @relation(fields: [userId], references: [id])
}
```

### 3. **Apply Schema Changes**
```bash
# Generate migration
npx prisma migrate dev --name "add-missing-models"

# Regenerate client
npx prisma generate

# Push to database
npx prisma db push
```

## 🔍 DEBUGGING COMMANDS FOR AGENTS

### 1. **Find Prisma Model Issues**
```bash
# Find missing model references
grep -r "prisma\." app/ | grep -E "(hexacoquestion|savedcareers|note|savedprogram)"

# Check schema.prisma for model definitions
cat backend/prisma/schema.prisma | grep -E "model.*\{|^\s*model"

# Validate Prisma setup
npx prisma validate
```

### 2. **Find SQLAlchemy Remnants**
```bash
# Find SQLAlchemy patterns that need conversion
grep -r "from_orm(" app/
grep -r "db\.query\|db\.add\|db\.commit" app/
grep -r "Session\|sessionmaker" app/

# Find missing Prisma imports
grep -r "from prisma import" app/
```

### 3. **Find Missing Dependencies**
```bash
# Check for import errors
python -c "import langchain; import langchain_openai; print('✅ All imports OK')"

# Find dependency usage without imports
grep -r "langchain\|anthropic" app/ | grep -v "import"
```

### 4. **Test API Endpoints**
```bash
# Test authentication endpoints
curl -H "Authorization: Bearer test" http://localhost:8000/api/v1/users/me

# Test missing endpoints
curl -X POST http://localhost:8000/api/v1/notes -d '{"content":"test"}'
curl -X POST http://localhost:8000/api/v1/education/save -d '{"program_id":1}'
```

## ✅ AGENT VALIDATION CHECKLIST

Before marking any backend bug as "FIXED", agents MUST verify:

### Prisma Migration Fixes
- [ ] All referenced models exist in schema.prisma
- [ ] `npx prisma validate` passes without errors
- [ ] `npx prisma generate` completes successfully
- [ ] Test imports: `from prisma import Prisma` works
- [ ] No SQLAlchemy patterns remain (`from_orm`, `db.query`)

### Service Configuration Fixes
- [ ] All dependencies are installed (`langchain`, `langchain-openai`)
- [ ] Anthropic client initializes without `proxies` parameter
- [ ] All imports resolve correctly
- [ ] No missing module errors in logs

### API Endpoint Fixes
- [ ] All missing endpoints return 200/201 (not 404)
- [ ] Proper request/response models defined
- [ ] Authentication dependencies added
- [ ] Database operations use Prisma (not SQLAlchemy)

### Authentication Integration
- [ ] All endpoints use `get_current_user` dependency
- [ ] No manual JWT token parsing
- [ ] All protected routes validate Clerk tokens
- [ ] Database user synchronization working

### Database Operations
- [ ] All queries use `await prisma.model.method()`
- [ ] No `db.session` or SQLAlchemy Session usage
- [ ] Proper error handling for database operations
- [ ] Foreign key relationships working correctly

## 🚨 CONTEXT7 VERIFICATION COMMANDS

**Before implementing any fix, check latest patterns:**

### Prisma Patterns
```bash
# Verify current Prisma patterns
mcp__context7__get-library-docs /prisma/docs "schema migration"
mcp__context7__get-library-docs /prisma/docs "client generation"
```

### FastAPI Authentication
```bash
# Check modern FastAPI auth patterns
mcp__context7__get-library-docs /context7/fastapi_tiangolo "dependency injection"
mcp__context7__get-library-docs /context7/fastapi_tiangolo "authentication"
```

### Clerk Backend Integration
```bash
# Verify Clerk backend patterns
mcp__context7__get-library-docs /clerk/clerk-sdk-python "authentication"
mcp__context7__get-library-docs /clerk/clerk-sdk-python "JWT validation"
```

## 📋 BACKEND BUG PRIORITY MATRIX

### P0 CRITICAL (Fix immediately)
1. **Prisma model errors** - Add missing models to schema
2. **Service initialization failures** - Fix Anthropic client, dependencies
3. **Authentication validation** - Fix Clerk integration

### P1 HIGH (Fix same session)
1. **Missing API endpoints** - Implement notes, education save endpoints
2. **Data serialization** - Remove `from_orm()` usage
3. **Database operations** - Convert remaining SQLAlchemy to Prisma

### P2 MEDIUM (Fix in follow-up)
1. **Error handling** - Improve API error responses
2. **Performance optimization** - Database query optimization
3. **Code cleanup** - Remove unused imports and dependencies

## 🎯 AGENT SUCCESS CRITERIA

A backend bug fix is COMPLETE when:
1. **Context7 documentation consulted** for current best practices
2. **All Prisma models exist** in schema.prisma and generate correctly
3. **All service dependencies installed** and import successfully
4. **All API endpoints return expected responses** (not 404/500)
5. **Authentication integration working** with Clerk
6. **Database operations use Prisma exclusively** (no SQLAlchemy)
7. **Manual testing confirms API functionality**

## 🔧 SERVICE CONFIGURATION FIXES

### Anthropic Client Configuration
```python
# ✅ CORRECT CONFIGURATION
from anthropic import AsyncClient

async def get_anthropic_client():
    return AsyncClient(
        api_key=settings.ANTHROPIC_API_KEY,
        # Remove any proxies or unsupported parameters
    )
```

### Dependency Installation Check
```python
# ✅ VALIDATE IMPORTS AT STARTUP
try:
    import langchain
    import langchain_openai
    from anthropic import AsyncClient
    print("✅ All required dependencies available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    raise
```

## 📞 WHEN TO ESCALATE

Escalate to senior developer if:
- Context7 documentation conflicts with existing patterns
- Database schema changes affect other services
- Authentication system architecture needs modification
- Service configuration requires infrastructure changes

**Remember: Many frontend bugs have backend root causes. Fix backend services first to resolve cascading frontend issues.**

## 🚨 CRITICAL REMINDER

**The Orientor Platform backend must use:**
1. **Prisma ORM exclusively** - No SQLAlchemy
2. **Clerk authentication only** - No custom JWT
3. **FastAPI dependency injection** - Proper async patterns
4. **Complete API endpoint coverage** - No missing endpoints

**Any deviation from these patterns will cause frontend failures and must be corrected immediately.**