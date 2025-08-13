# Query Patterns: Complete SQLAlchemy → Prisma Conversion Guide

This guide provides comprehensive patterns for converting every type of database operation from SQLAlchemy to Prisma.

## 📋 Table of Contents

1. [Basic Queries](#basic-queries)
2. [Filtering & Searching](#filtering--searching)  
3. [Relationships](#relationships)
4. [Aggregations](#aggregations)
5. [Complex Queries](#complex-queries)
6. [Transactions](#transactions)
7. [Raw SQL](#raw-sql)

## 🔍 Basic Queries

### Find Operations

| SQLAlchemy | Prisma |
|------------|--------|
| `db.query(User).first()` | `await db.user.find_first()` |
| `db.query(User).filter(User.id == 1).first()` | `await db.user.find_unique(where={"id": 1})` |
| `db.query(User).all()` | `await db.user.find_many()` |
| `db.query(User).limit(10).all()` | `await db.user.find_many(take=10)` |
| `db.query(User).offset(20).limit(10).all()` | `await db.user.find_many(skip=20, take=10)` |

### Create Operations

| SQLAlchemy | Prisma |
|------------|--------|
| `user = User(name="John"); db.add(user); db.commit()` | `await db.user.create(data={"name": "John"})` |
| `db.bulk_insert_mappings(User, data_list)` | `await db.user.create_many(data=data_list)` |

### Update Operations

| SQLAlchemy | Prisma |
|------------|--------|
| `user.name = "Jane"; db.commit()` | `await db.user.update(where={"id": user.id}, data={"name": "Jane"})` |
| `db.query(User).filter(User.id == 1).update({"name": "Jane"})` | `await db.user.update(where={"id": 1}, data={"name": "Jane"})` |
| `db.query(User).filter(User.is_active == True).update({"status": "updated"})` | `await db.user.update_many(where={"is_active": True}, data={"status": "updated"})` |

### Delete Operations

| SQLAlchemy | Prisma |
|------------|--------|
| `db.delete(user); db.commit()` | `await db.user.delete(where={"id": user.id})` |
| `db.query(User).filter(User.id == 1).delete()` | `await db.user.delete(where={"id": 1})` |
| `db.query(User).filter(User.is_active == False).delete()` | `await db.user.delete_many(where={"is_active": False})` |

## 🔍 Filtering & Searching

### Basic Filters

| SQLAlchemy | Prisma |
|------------|--------|
| `User.name == "John"` | `{"name": "John"}` |
| `User.age > 18` | `{"age": {"gt": 18}}` |
| `User.age >= 18` | `{"age": {"gte": 18}}` |
| `User.age < 65` | `{"age": {"lt": 65}}` |
| `User.age <= 65` | `{"age": {"lte": 65}}` |
| `User.age != 25` | `{"age": {"not": 25}}` |
| `User.name.in_(["John", "Jane"])` | `{"name": {"in": ["John", "Jane"]}}` |
| `User.name.notin_(["Admin", "System"])` | `{"name": {"notIn": ["Admin", "System"]}}` |

### String Filters

| SQLAlchemy | Prisma |
|------------|--------|
| `User.name.like("%john%")` | `{"name": {"contains": "john"}}` |
| `User.name.ilike("%john%")` | `{"name": {"contains": "john", "mode": "insensitive"}}` |
| `User.name.startswith("John")` | `{"name": {"startsWith": "John"}}` |
| `User.name.endswith("Doe")` | `{"name": {"endsWith": "Doe"}}` |
| `User.email.contains("@gmail")` | `{"email": {"contains": "@gmail"}}` |

### Date Filters

| SQLAlchemy | Prisma |
|------------|--------|
| `User.created_at > datetime.now()` | `{"created_at": {"gt": datetime.now()}}` |
| `User.created_at.between(start, end)` | `{"created_at": {"gte": start, "lte": end}}` |
| `func.date(User.created_at) == date.today()` | `{"created_at": {"gte": start_of_day, "lt": end_of_day}}` |

### Logical Operators

#### AND Conditions
```python
# SQLAlchemy
db.query(User).filter(
    User.is_active == True,
    User.age > 18
).all()

# Prisma
await db.user.find_many(where={
    "is_active": True,
    "age": {"gt": 18}
})
```

#### OR Conditions
```python
# SQLAlchemy
from sqlalchemy import or_
db.query(User).filter(
    or_(User.name == "John", User.email.like("%admin%"))
).all()

# Prisma
await db.user.find_many(where={
    "OR": [
        {"name": "John"},
        {"email": {"contains": "admin"}}
    ]
})
```

#### NOT Conditions
```python
# SQLAlchemy
from sqlalchemy import not_
db.query(User).filter(
    not_(User.is_active == False)
).all()

# Prisma
await db.user.find_many(where={
    "NOT": {"is_active": False}
})
```

## 🔗 Relationships

### One-to-One Relationships

```python
# SQLAlchemy
from sqlalchemy.orm import joinedload
user = db.query(User).options(
    joinedload(User.profile)
).filter(User.id == 1).first()

# Prisma
user = await db.user.find_unique(
    where={"id": 1},
    include={"profile": True}
)
```

### One-to-Many Relationships

```python
# SQLAlchemy
user = db.query(User).options(
    joinedload(User.conversations)
).filter(User.id == 1).first()

# Prisma
user = await db.user.find_unique(
    where={"id": 1},
    include={"conversations": True}
)
```

### Many-to-Many Relationships

```python
# SQLAlchemy
user = db.query(User).options(
    joinedload(User.skills)
).filter(User.id == 1).first()

# Prisma - Through explicit junction table
user_skills = await db.userskill.find_many(
    where={"user_id": 1},
    include={"skill": True}
)
```

### Nested Relationships

```python
# SQLAlchemy
user = db.query(User).options(
    joinedload(User.conversations).joinedload(Conversation.messages)
).filter(User.id == 1).first()

# Prisma
user = await db.user.find_unique(
    where={"id": 1},
    include={
        "conversations": {
            "include": {"messages": True}
        }
    }
)
```

### Filtering Relationships

```python
# SQLAlchemy
users = db.query(User).join(User.conversations).filter(
    Conversation.created_at > datetime.now() - timedelta(days=7)
).all()

# Prisma
users = await db.user.find_many(where={
    "conversations": {
        "some": {
            "created_at": {"gt": datetime.now() - timedelta(days=7)}
        }
    }
})
```

## 📊 Aggregations

### Count Operations

```python
# SQLAlchemy
from sqlalchemy import func
total = db.query(func.count(User.id)).scalar()
active_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

# Prisma
total = await db.user.count()
active_count = await db.user.count(where={"is_active": True})
```

### Group By Operations

```python
# SQLAlchemy
results = db.query(
    User.major,
    func.count(User.id).label('count')
).join(User.profile).group_by(User.major).all()

# Prisma - Use raw SQL for complex aggregations
results = await db.execute_raw("""
    SELECT p.major, COUNT(*) as count
    FROM UserProfile p
    JOIN User u ON p.user_id = u.id
    GROUP BY p.major
    ORDER BY count DESC
""")
```

### Sum, Average, Min, Max

```python
# SQLAlchemy
stats = db.query(
    func.sum(User.score),
    func.avg(User.score),
    func.min(User.score),
    func.max(User.score)
).first()

# Prisma - Use raw SQL for complex aggregations
stats = await db.execute_raw("""
    SELECT 
        SUM(score) as total_score,
        AVG(score) as avg_score,
        MIN(score) as min_score,
        MAX(score) as max_score
    FROM User
    WHERE is_active = true
""")
```

## 🏗️ Complex Queries

### Subqueries

```python
# SQLAlchemy
subquery = db.query(func.max(Conversation.created_at)).filter(
    Conversation.user_id == User.id
).correlate(User).as_scalar()

users = db.query(User).filter(
    User.last_activity > subquery
).all()

# Prisma - Break into multiple queries or use raw SQL
recent_conversations = await db.execute_raw("""
    SELECT user_id, MAX(created_at) as last_conversation
    FROM Conversation
    GROUP BY user_id
""")

# Then filter users based on results
user_ids = [conv["user_id"] for conv in recent_conversations]
users = await db.user.find_many(where={"id": {"in": user_ids}})
```

### Window Functions

```python
# SQLAlchemy
from sqlalchemy import func
results = db.query(
    User.name,
    func.row_number().over(
        partition_by=User.department,
        order_by=User.created_at.desc()
    ).label('rank')
).all()

# Prisma - Use raw SQL
results = await db.execute_raw("""
    SELECT 
        name,
        ROW_NUMBER() OVER (
            PARTITION BY department 
            ORDER BY created_at DESC
        ) as rank
    FROM User
""")
```

### Union Queries

```python
# SQLAlchemy
from sqlalchemy import union
query1 = db.query(User.email).filter(User.is_active == True)
query2 = db.query(User.email).filter(User.is_premium == True)
combined = union(query1, query2).all()

# Prisma - Use raw SQL
results = await db.execute_raw("""
    SELECT email FROM User WHERE is_active = true
    UNION
    SELECT email FROM User WHERE is_premium = true
""")
```

## 💾 Transactions

### Simple Transactions

```python
# SQLAlchemy
try:
    user = User(name="John")
    db.add(user)
    db.flush()  # Get the ID
    
    profile = UserProfile(user_id=user.id, age=25)
    db.add(profile)
    
    db.commit()
except Exception:
    db.rollback()
    raise

# Prisma
async with db.tx() as transaction:
    user = await transaction.user.create(data={"name": "John"})
    profile = await transaction.userprofile.create(data={
        "user_id": user.id,
        "age": 25
    })
    # Auto-commit on success, auto-rollback on exception
```

### Nested Transactions

```python
# SQLAlchemy
try:
    # Outer transaction
    user = User(name="John")
    db.add(user)
    
    savepoint = db.begin_nested()
    try:
        # Inner transaction
        profile = UserProfile(user_id=user.id, age=25)
        db.add(profile)
        savepoint.commit()
    except Exception:
        savepoint.rollback()
        # Continue with outer transaction
    
    db.commit()
except Exception:
    db.rollback()

# Prisma - Nested transactions not directly supported
# Use separate transaction blocks or handle at application level
```

## 🔧 Raw SQL

### Raw Queries

```python
# SQLAlchemy
result = db.execute(text("SELECT * FROM users WHERE age > :age"), {"age": 18})
users = result.fetchall()

# Prisma
users = await db.execute_raw("SELECT * FROM User WHERE age > $1", 18)
```

### Raw Queries with Parameters

```python
# SQLAlchemy
result = db.execute(
    text("SELECT * FROM users WHERE name = :name AND age > :age"),
    {"name": "John", "age": 18}
)

# Prisma
users = await db.execute_raw(
    "SELECT * FROM User WHERE name = $1 AND age > $2",
    "John", 18
)
```

## 🎯 Performance Optimization Patterns

### Select Specific Fields

```python
# SQLAlchemy
users = db.query(User.id, User.name, User.email).all()

# Prisma
users = await db.user.find_many(select={
    "id": True,
    "name": True,
    "email": True
})
```

### Batch Operations

```python
# SQLAlchemy
users_data = [{"name": f"User{i}", "email": f"user{i}@example.com"} for i in range(100)]
db.bulk_insert_mappings(User, users_data)
db.commit()

# Prisma
users_data = [{"name": f"User{i}", "email": f"user{i}@example.com"} for i in range(100)]
await db.user.create_many(data=users_data)
```

### Parallel Queries

```python
# SQLAlchemy - Sequential
users = db.query(User).all()
conversations = db.query(Conversation).all()
messages = db.query(ChatMessage).all()

# Prisma - Parallel
import asyncio

users_task = db.user.find_many()
conversations_task = db.conversation.find_many()
messages_task = db.chatmessage.find_many()

users, conversations, messages = await asyncio.gather(
    users_task, conversations_task, messages_task
)
```

## 📝 Common Pitfalls & Solutions

### Pitfall 1: Forgetting Async/Await

```python
# ❌ Wrong
users = db.user.find_many()

# ✅ Correct  
users = await db.user.find_many()
```

### Pitfall 2: Incorrect Where Clauses

```python
# ❌ Wrong - SQLAlchemy syntax in Prisma
await db.user.find_many(where={"name.contains": "john"})

# ✅ Correct - Prisma syntax
await db.user.find_many(where={"name": {"contains": "john"}})
```

### Pitfall 3: Missing Transaction Context

```python
# ❌ Wrong - Multiple operations without transaction
user = await db.user.create(data=user_data)
profile = await db.userprofile.create(data=profile_data)
# If profile creation fails, user is still created

# ✅ Correct - Use transaction
async with db.tx() as transaction:
    user = await transaction.user.create(data=user_data)
    profile = await transaction.userprofile.create(data=profile_data)
```

---
**🎯 Quick Reference**: Bookmark this guide and use it during your migration to quickly find the Prisma equivalent of any SQLAlchemy pattern.