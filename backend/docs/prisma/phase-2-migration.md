# Phase 2: Router Migration Strategy

**Duration**: 2-3 hours  
**Priority**: High (Core implementation)

## 🎯 Objective

Systematically migrate all 44+ FastAPI routers from SQLAlchemy to Prisma ORM using a prioritized, batch-based approach.

## 📊 Migration Priority Matrix

### Tier 1: Critical Authentication & User Management (30 min)
**High Impact, High Risk** - Core platform functionality
- `users.py` - User profile operations
- `auth_clerk.py` - Authentication endpoints  
- `profiles.py` - User profile management
- `onboarding.py` - User registration flow

### Tier 2: Core Features (45 min)
**High Impact, Medium Risk** - Primary platform features
- `chat.py` - Chat functionality
- `conversations.py` - Conversation management
- `career_goals.py` - Career planning
- `recommendations.py` - Recommendation engine

### Tier 3: Secondary Features (60 min)
**Medium Impact, Low Risk** - Supporting features
- `hexaco_test.py` - Personality assessments
- `holland_test.py` - Career assessments  
- `jobs.py` - Job listings
- `careers.py` - Career information
- `education.py` - Education data

### Tier 4: Utility & Analytics (45 min)
**Low Impact, Low Risk** - Support and monitoring
- `analytics.py` - Analytics endpoints
- `test.py` - Test endpoints
- `cache_monitoring.py` - Cache monitoring
- `database_monitoring.py` - Database monitoring

## 🔄 Per-Router Migration Process

### Step 1: Pre-Migration Analysis (5 min per router)

**Analyze current patterns:**
```bash
# Search for SQLAlchemy usage
grep -n "Session.*Depends\|db\.query\|db\.add\|db\.commit" router_file.py

# Identify models used
grep -n "from.*models.*import" router_file.py

# Find database operations
grep -n "filter\|join\|all()\|first()" router_file.py
```

### Step 2: Import Updates (2 min per router)

**Replace SQLAlchemy imports:**
```python
# BEFORE
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User as UserModel

# AFTER  
from prisma import Prisma
from ..utils.prisma_client import get_prisma
# Remove SQLAlchemy model imports (Prisma generates types)
```

### Step 3: Function Signature Updates (3 min per router)

**Update dependency injection:**
```python
# BEFORE
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

# AFTER
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma)
):
```

### Step 4: Query Pattern Conversion (10-15 min per router)

**Convert database operations:**
```python
# BEFORE (SQLAlchemy)
user = db.query(UserModel).filter(UserModel.id == user_id).first()
if not user:
    raise HTTPException(status_code=404)

# AFTER (Prisma)
user = await db.user.find_unique(where={"id": user_id})
if not user:
    raise HTTPException(status_code=404)
```

### Step 5: Testing & Validation (5 min per router)

**Test converted endpoints:**
```python
# Verify endpoint still works
# Check response format matches
# Validate error handling
# Test with authentication
```

## 📝 Standard Migration Template

### Template for Router Conversion

```python
"""
MIGRATION TEMPLATE: SQLAlchemy → Prisma Router Conversion
"""

# 1. UPDATE IMPORTS
from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from ..utils.prisma_client import get_prisma
from ..utils.clerk_auth import get_current_user_with_db_sync as get_current_user

# 2. ROUTER SETUP (unchanged)
router = APIRouter(prefix="/api/endpoint", tags=["Endpoint"])

# 3. CONVERT ENDPOINTS
@router.get("/example")
async def example_endpoint(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma)  # ← Changed from Session
):
    """Example converted endpoint"""
    
    # 4. CONVERT QUERIES
    # Old: result = db.query(Model).filter(...).all()
    # New: result = await db.model.find_many(where={...})
    
    try:
        result = await db.user.find_many(
            where={"is_active": True},
            include={"profile": True}  # Relationships
        )
        return {"data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🛡️ Migration Safety Protocols

### Backup Strategy
1. **Git branch**: Create feature branch for each tier
2. **Incremental commits**: Commit after each router conversion  
3. **Testing checkpoints**: Test thoroughly after each tier

### Rollback Procedures
```python
# Keep SQLAlchemy imports available during transition
try:
    from prisma import Prisma
    from ..utils.prisma_client import get_prisma
    USE_PRISMA = True
except ImportError:
    from sqlalchemy.orm import Session
    from ..database import get_db  
    USE_PRISMA = False

# Conditional dependency injection
if USE_PRISMA:
    db_dependency = Depends(get_prisma)
else:
    db_dependency = Depends(get_db)
```

### Error Handling Patterns
```python
async def safe_prisma_operation(db: Prisma, operation_func):
    """Wrapper for safe Prisma operations with fallback"""
    try:
        return await operation_func(db)
    except Exception as e:
        logger.error(f"Prisma operation failed: {e}")
        # Add alerting/monitoring here
        raise HTTPException(
            status_code=500, 
            detail="Database operation failed"
        )
```

## 📊 Progress Tracking

### Migration Checklist Template

```markdown
## Router: `{router_name}.py`

- [ ] **Analysis Complete** - Identified all SQLAlchemy patterns
- [ ] **Imports Updated** - Prisma imports added, SQLAlchemy removed  
- [ ] **Dependencies Updated** - `get_prisma` instead of `get_db`
- [ ] **Queries Converted** - All database operations use Prisma syntax
- [ ] **Testing Complete** - All endpoints tested and working
- [ ] **Error Handling** - Proper exception handling implemented
- [ ] **Documentation** - Comments updated to reflect Prisma usage

**Migration Time**: _____ minutes  
**Issues Encountered**: _____  
**Notes**: _____
```

## 🔍 Common Migration Patterns

### High-Frequency Conversions

1. **User Lookups**:
```python
# Before: db.query(User).filter(User.id == user_id).first()  
# After:  await db.user.find_unique(where={"id": user_id})
```

2. **List Operations**:
```python
# Before: db.query(Model).filter(Model.user_id == user_id).all()
# After:  await db.model.find_many(where={"user_id": user_id})
```

3. **Create Operations**:
```python
# Before: obj = Model(**data); db.add(obj); db.commit()
# After:  await db.model.create(data=data)
```

4. **Update Operations**:
```python
# Before: db.query(Model).filter(...).update(data); db.commit()  
# After:  await db.model.update(where={...}, data=data)
```

## 📈 Success Metrics

### Per-Router Success Criteria
- ✅ All endpoints respond correctly
- ✅ Authentication integration maintained
- ✅ Response formats unchanged  
- ✅ Error handling preserved
- ✅ Performance maintained or improved

### Tier Completion Criteria
- ✅ All routers in tier converted
- ✅ Integration tests passing
- ✅ No breaking changes to API contracts
- ✅ Logging and monitoring functional

## 🔄 Next Steps

After completing Phase 2:
1. Validate all converted routers work correctly
2. Run comprehensive integration tests
3. Monitor performance and error rates
4. Proceed to [Phase 3: Query Standardization](./phase-3-patterns.md)

---
**⚠️ Critical**: Test each tier thoroughly before proceeding to the next. Each tier builds upon the previous one's stability.