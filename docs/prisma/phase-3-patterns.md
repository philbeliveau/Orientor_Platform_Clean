# Phase 3: Query Pattern Standardization

**Duration**: 1-2 hours  
**Priority**: Medium (Quality & Consistency)

## 🎯 Objective

Establish standardized query patterns and best practices for Prisma operations across all converted FastAPI endpoints, ensuring consistent, performant, and maintainable code.

## 📋 Standard Query Patterns

### Pattern 1: Basic CRUD Operations

#### Create Operations
```python
# ✅ STANDARD PATTERN
async def create_user(user_data: UserCreate, db: Prisma = Depends(get_prisma)):
    """Create a new user with error handling"""
    try:
        user = await db.user.create(
            data={
                "email": user_data.email,
                "name": user_data.name,
                "is_active": True
            }
        )
        return user
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="User already exists")
        raise HTTPException(status_code=500, detail="Failed to create user")
```

#### Read Operations
```python
# ✅ SINGLE RECORD
async def get_user(user_id: int, db: Prisma = Depends(get_prisma)):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={"profile": True}  # Include related data
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ✅ MULTIPLE RECORDS WITH FILTERING
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True,
    db: Prisma = Depends(get_prisma)
):
    where_clause = {"is_active": True} if active_only else {}
    
    users = await db.user.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={"profile": True},
        order_by={"created_at": "desc"}
    )
    return users
```

#### Update Operations
```python
# ✅ STANDARD UPDATE PATTERN
async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Prisma = Depends(get_prisma)
):
    # Verify user exists
    existing_user = await db.user.find_unique(where={"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update with only provided fields
    update_data = user_data.dict(exclude_unset=True)
    
    updated_user = await db.user.update(
        where={"id": user_id},
        data=update_data
    )
    return updated_user
```

#### Delete Operations
```python
# ✅ SOFT DELETE (PREFERRED)
async def deactivate_user(user_id: int, db: Prisma = Depends(get_prisma)):
    user = await db.user.update(
        where={"id": user_id},
        data={"is_active": False, "deactivated_at": datetime.utcnow()}
    )
    return {"message": "User deactivated successfully"}

# ✅ HARD DELETE (USE SPARINGLY)
async def delete_user(user_id: int, db: Prisma = Depends(get_prisma)):
    await db.user.delete(where={"id": user_id})
    return {"message": "User deleted successfully"}
```

### Pattern 2: Relationship Handling

#### One-to-One Relationships
```python
# ✅ USER WITH PROFILE
async def get_user_with_profile(user_id: int, db: Prisma = Depends(get_prisma)):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={"profile": True}
    )
    return user
```

#### One-to-Many Relationships
```python
# ✅ USER WITH CONVERSATIONS
async def get_user_conversations(user_id: int, db: Prisma = Depends(get_prisma)):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={
            "conversations": {
                "include": {"messages": True},
                "order_by": {"created_at": "desc"},
                "take": 10  # Limit conversations
            }
        }
    )
    return user.conversations if user else []
```

#### Many-to-Many Relationships
```python
# ✅ USER SKILLS
async def get_user_skills(user_id: int, db: Prisma = Depends(get_prisma)):
    user_skills = await db.userskill.find_many(
        where={"user_id": user_id},
        include={"skill": True}  # Include skill details
    )
    return [{"skill": us.skill, "level": us.level} for us in user_skills]
```

### Pattern 3: Complex Queries

#### Filtering & Searching
```python
# ✅ ADVANCED FILTERING
async def search_users(
    search_term: str = None,
    major: str = None,
    min_age: int = None,
    max_age: int = None,
    db: Prisma = Depends(get_prisma)
):
    where_conditions = {"is_active": True}
    
    if search_term:
        where_conditions["OR"] = [
            {"name": {"contains": search_term, "mode": "insensitive"}},
            {"email": {"contains": search_term, "mode": "insensitive"}}
        ]
    
    if major:
        where_conditions["profile"] = {"major": major}
    
    if min_age or max_age:
        age_filter = {}
        if min_age:
            age_filter["gte"] = min_age
        if max_age:
            age_filter["lte"] = max_age
        where_conditions["profile"]["age"] = age_filter
    
    users = await db.user.find_many(
        where=where_conditions,
        include={"profile": True}
    )
    return users
```

#### Aggregations
```python
# ✅ COUNT OPERATIONS
async def get_user_stats(db: Prisma = Depends(get_prisma)):
    total_users = await db.user.count()
    active_users = await db.user.count(where={"is_active": True})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }

# ✅ GROUP BY OPERATIONS (via raw SQL when needed)
async def get_users_by_major(db: Prisma = Depends(get_prisma)):
    result = await db.execute_raw("""
        SELECT p.major, COUNT(*) as user_count
        FROM UserProfile p
        JOIN User u ON p.user_id = u.id
        WHERE u.is_active = true
        GROUP BY p.major
        ORDER BY user_count DESC
    """)
    return result
```

### Pattern 4: Transaction Management

#### Simple Transactions
```python
# ✅ TRANSACTION FOR MULTIPLE OPERATIONS
async def create_user_with_profile(
    user_data: UserCreate,
    profile_data: ProfileCreate,
    db: Prisma = Depends(get_prisma)
):
    async with db.tx() as transaction:
        # Create user
        user = await transaction.user.create(data={
            "email": user_data.email,
            "name": user_data.name
        })
        
        # Create profile
        profile = await transaction.userprofile.create(data={
            "user_id": user.id,
            "age": profile_data.age,
            "major": profile_data.major
        })
        
        return {"user": user, "profile": profile}
```

#### Complex Business Logic Transactions
```python
# ✅ COMPLEX TRANSACTION WITH BUSINESS LOGIC
async def complete_user_onboarding(
    user_id: int,
    onboarding_data: OnboardingComplete,
    db: Prisma = Depends(get_prisma)
):
    async with db.tx() as transaction:
        # Update user profile
        await transaction.userprofile.update(
            where={"user_id": user_id},
            data={
                "onboarding_completed": True,
                "onboarding_completed_at": datetime.utcnow()
            }
        )
        
        # Create initial career goals
        for goal in onboarding_data.career_goals:
            await transaction.careergoal.create(data={
                "user_id": user_id,
                "title": goal.title,
                "description": goal.description
            })
        
        # Add initial skills
        for skill_data in onboarding_data.skills:
            await transaction.userskill.create(data={
                "user_id": user_id,
                "skill_id": skill_data.skill_id,
                "level": skill_data.level
            })
        
        return {"message": "Onboarding completed successfully"}
```

## 🎨 Coding Standards

### Error Handling Standards
```python
# ✅ COMPREHENSIVE ERROR HANDLING
async def standard_endpoint(id: int, db: Prisma = Depends(get_prisma)):
    try:
        # Prisma operations
        result = await db.model.find_unique(where={"id": id})
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource with ID {id} not found"
            )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### Logging Standards
```python
# ✅ STRUCTURED LOGGING
import logging

logger = logging.getLogger(__name__)

async def logged_endpoint(db: Prisma = Depends(get_prisma)):
    logger.info("Starting database operation", extra={
        "operation": "find_many",
        "model": "user"
    })
    
    start_time = time.time()
    
    try:
        result = await db.user.find_many()
        
        duration = (time.time() - start_time) * 1000
        logger.info("Database operation completed", extra={
            "duration_ms": duration,
            "records_returned": len(result)
        })
        
        return result
        
    except Exception as e:
        logger.error("Database operation failed", extra={
            "error": str(e),
            "operation": "find_many",
            "model": "user"
        })
        raise
```

### Performance Standards
```python
# ✅ EFFICIENT QUERIES
async def efficient_user_data(user_id: int, db: Prisma = Depends(get_prisma)):
    # Good: Select only needed fields
    user = await db.user.find_unique(
        where={"id": user_id},
        select={
            "id": True,
            "name": True,
            "email": True,
            "profile": {
                "select": {
                    "age": True,
                    "major": True
                }
            }
        }
    )
    return user

# ❌ AVOID: Selecting all fields when not needed
async def inefficient_user_data(user_id: int, db: Prisma = Depends(get_prisma)):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={"profile": True}  # Gets ALL profile fields
    )
    return user
```

## 📊 Pattern Guidelines

### Naming Conventions
```python
# ✅ FUNCTION NAMING
async def get_user_by_id()          # Single record retrieval
async def get_users_by_criteria()  # Multiple records with filtering
async def create_user()            # Create operations
async def update_user()            # Update operations
async def delete_user()            # Delete operations
async def search_users()           # Search operations
```

### Response Patterns
```python
# ✅ CONSISTENT RESPONSE FORMATS
# Single record
return user

# Multiple records
return {
    "data": users,
    "total": total_count,
    "page": page,
    "per_page": per_page
}

# Success operations
return {"message": "Operation completed successfully", "id": created_id}

# Error responses (via HTTPException)
raise HTTPException(status_code=404, detail="Resource not found")
```

### Validation Patterns
```python
# ✅ INPUT VALIDATION
async def create_resource(data: ResourceCreate, db: Prisma = Depends(get_prisma)):
    # Validate business rules
    if data.age < 0:
        raise HTTPException(status_code=400, detail="Age cannot be negative")
    
    # Check for conflicts
    existing = await db.resource.find_first(where={"email": data.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    # Create resource
    return await db.resource.create(data=data.dict())
```

## 🔄 Next Steps

After completing Phase 3:
1. Review all converted routers for pattern consistency
2. Update any non-conforming code to match standards
3. Document any custom patterns specific to your domain
4. Proceed to [Phase 4: Testing & Validation](./phase-4-testing.md)

---
**📝 Note**: These patterns should be consistently applied across all routers to ensure maintainable and predictable code.