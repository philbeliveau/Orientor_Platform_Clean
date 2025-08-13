# Migration Examples: SQLAlchemy → Prisma

This document provides concrete before/after examples for common patterns found in the Orientor Platform codebase.

## 📋 Basic CRUD Operations

### Example 1: User Retrieval

#### BEFORE (SQLAlchemy)
```python
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User as UserModel

@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

#### AFTER (Prisma)
```python
from prisma import Prisma
from ..utils.prisma_client import get_prisma

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Prisma = Depends(get_prisma)
):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Example 2: User Creation

#### BEFORE (SQLAlchemy)
```python
@router.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Create new user
    db_user = UserModel(
        email=user_data.email,
        name=user_data.name,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

#### AFTER (Prisma)
```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: Prisma = Depends(get_prisma)
):
    # Check if user exists
    existing = await db.user.find_unique(where={"email": user_data.email})
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Create new user
    user = await db.user.create(data={
        "email": user_data.email,
        "name": user_data.name,
        "is_active": True
    })
    return user
```

### Example 3: User Update

#### BEFORE (SQLAlchemy)
```python
@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user
```

#### AFTER (Prisma)
```python
@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Prisma = Depends(get_prisma)
):
    # Verify user exists
    existing = await db.user.find_unique(where={"id": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    updated_user = await db.user.update(
        where={"id": user_id},
        data=user_data.dict(exclude_unset=True)
    )
    return updated_user
```

## 🔗 Relationship Examples

### Example 4: User with Profile

#### BEFORE (SQLAlchemy)
```python
from sqlalchemy.orm import joinedload

@router.get("/users/{user_id}/profile")
def get_user_with_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).options(
        joinedload(UserModel.profile)
    ).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": user,
        "profile": user.profile
    }
```

#### AFTER (Prisma)
```python
@router.get("/users/{user_id}/profile")
async def get_user_with_profile(
    user_id: int,
    db: Prisma = Depends(get_prisma)
):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={"profile": True}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user  # Profile is included in the response
```

### Example 5: User Conversations with Messages

#### BEFORE (SQLAlchemy)
```python
@router.get("/users/{user_id}/conversations")
def get_user_conversations(
    user_id: int,
    db: Session = Depends(get_db)
):
    conversations = db.query(ConversationModel).options(
        joinedload(ConversationModel.messages)
    ).filter(ConversationModel.user_id == user_id).all()
    
    return conversations
```

#### AFTER (Prisma)
```python
@router.get("/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: int,
    db: Prisma = Depends(get_prisma)
):
    conversations = await db.conversation.find_many(
        where={"user_id": user_id},
        include={"messages": True},
        order_by={"created_at": "desc"}
    )
    
    return conversations
```

## 🔍 Complex Query Examples

### Example 6: Search Users

#### BEFORE (SQLAlchemy)
```python
@router.get("/users/search")
def search_users(
    q: str = None,
    major: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(UserModel).join(UserModel.profile)
    
    if q:
        query = query.filter(
            or_(
                UserModel.name.ilike(f"%{q}%"),
                UserModel.email.ilike(f"%{q}%")
            )
        )
    
    if major:
        query = query.filter(ProfileModel.major == major)
    
    users = query.offset(skip).limit(limit).all()
    return users
```

#### AFTER (Prisma)
```python
@router.get("/users/search")
async def search_users(
    q: str = None,
    major: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Prisma = Depends(get_prisma)
):
    where_conditions = {}
    
    if q:
        where_conditions["OR"] = [
            {"name": {"contains": q, "mode": "insensitive"}},
            {"email": {"contains": q, "mode": "insensitive"}}
        ]
    
    if major:
        where_conditions["profile"] = {"major": major}
    
    users = await db.user.find_many(
        where=where_conditions,
        include={"profile": True},
        skip=skip,
        take=limit
    )
    
    return users
```

### Example 7: Aggregation Queries

#### BEFORE (SQLAlchemy)
```python
from sqlalchemy import func

@router.get("/users/stats")
def get_user_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(UserModel.id)).scalar()
    active_users = db.query(func.count(UserModel.id)).filter(
        UserModel.is_active == True
    ).scalar()
    
    # Users by major
    major_stats = db.query(
        ProfileModel.major,
        func.count(ProfileModel.user_id)
    ).join(UserModel).group_by(ProfileModel.major).all()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "major_distribution": [
            {"major": major, "count": count} 
            for major, count in major_stats
        ]
    }
```

#### AFTER (Prisma)
```python
@router.get("/users/stats")
async def get_user_stats(db: Prisma = Depends(get_prisma)):
    # Basic counts
    total_users = await db.user.count()
    active_users = await db.user.count(where={"is_active": True})
    
    # Complex aggregation via raw SQL (when needed)
    major_stats = await db.execute_raw("""
        SELECT p.major, COUNT(*) as count
        FROM UserProfile p
        JOIN User u ON p.user_id = u.id
        WHERE u.is_active = true
        GROUP BY p.major
        ORDER BY count DESC
    """)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "major_distribution": major_stats
    }
```

## 💬 Chat System Examples

### Example 8: Chat Message Creation (Complex Business Logic)

#### BEFORE (SQLAlchemy)
```python
@router.post("/chat/send")
def send_message(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get or create conversation
    if message.conversation_id:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == message.conversation_id,
            ConversationModel.user_id == current_user.id
        ).first()
    else:
        conversation = ConversationModel(
            user_id=current_user.id,
            title=message.text[:50]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Add user message
    user_message = ChatMessageModel(
        conversation_id=conversation.id,
        role="user",
        content=message.text
    )
    db.add(user_message)
    
    # ... AI processing logic ...
    
    # Add AI response
    ai_message = ChatMessageModel(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response,
        tokens_used=tokens_used
    )
    db.add(ai_message)
    
    db.commit()
    db.refresh(ai_message)
    
    return {
        "message": ai_response,
        "conversation_id": conversation.id
    }
```

#### AFTER (Prisma)
```python
@router.post("/chat/send")
async def send_message(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma)
):
    # Use transaction for complex operations
    async with db.tx() as transaction:
        # Get or create conversation
        if message.conversation_id:
            conversation = await transaction.conversation.find_unique(
                where={
                    "id": message.conversation_id,
                    "user_id": current_user.id
                }
            )
        else:
            conversation = await transaction.conversation.create(data={
                "user_id": current_user.id,
                "title": message.text[:50]
            })
        
        # Add user message
        user_message = await transaction.chatmessage.create(data={
            "conversation_id": conversation.id,
            "role": "user",
            "content": message.text
        })
        
        # ... AI processing logic ...
        
        # Add AI response
        ai_message = await transaction.chatmessage.create(data={
            "conversation_id": conversation.id,
            "role": "assistant",
            "content": ai_response,
            "tokens_used": tokens_used
        })
        
        return {
            "message": ai_response,
            "conversation_id": conversation.id
        }
```

## 📊 Pagination Examples

### Example 9: Paginated Results

#### BEFORE (SQLAlchemy)
```python
@router.get("/conversations")
def get_conversations(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page
    
    conversations = db.query(ConversationModel).filter(
        ConversationModel.user_id == current_user.id
    ).offset(offset).limit(per_page).all()
    
    total = db.query(func.count(ConversationModel.id)).filter(
        ConversationModel.user_id == current_user.id
    ).scalar()
    
    return {
        "conversations": conversations,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page)
    }
```

#### AFTER (Prisma)
```python
@router.get("/conversations")
async def get_conversations(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma)
):
    skip = (page - 1) * per_page
    
    # Get conversations and total count in parallel
    conversations_task = db.conversation.find_many(
        where={"user_id": current_user.id},
        skip=skip,
        take=per_page,
        order_by={"created_at": "desc"}
    )
    
    total_task = db.conversation.count(
        where={"user_id": current_user.id}
    )
    
    conversations, total = await asyncio.gather(
        conversations_task,
        total_task
    )
    
    return {
        "conversations": conversations,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page)
    }
```

## 🎯 Authentication Integration Examples

### Example 10: Protected Endpoint with User Context

#### BEFORE (SQLAlchemy)
```python
@router.get("/profile")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(ProfileModel).filter(
        ProfileModel.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile
```

#### AFTER (Prisma)
```python
@router.get("/profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma)
):
    profile = await db.userprofile.find_unique(
        where={"user_id": current_user.id}
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile
```

## 🛠️ Migration Checklist Per Example

For each router you convert, use this checklist:

### Import Changes
- [ ] Remove `from sqlalchemy.orm import Session`
- [ ] Remove `from ..database import get_db`
- [ ] Remove SQLAlchemy model imports
- [ ] Add `from prisma import Prisma`
- [ ] Add `from ..utils.prisma_client import get_prisma`

### Function Signature Changes
- [ ] Change `db: Session = Depends(get_db)` to `db: Prisma = Depends(get_prisma)`
- [ ] Add `async` to function definitions
- [ ] Update type hints if needed

### Query Pattern Changes
- [ ] `db.query(Model).filter(...).first()` → `await db.model.find_unique(where={...})`
- [ ] `db.query(Model).filter(...).all()` → `await db.model.find_many(where={...})`
- [ ] `db.add(obj); db.commit()` → `await db.model.create(data={...})`
- [ ] `db.query(Model).filter(...).update(...)` → `await db.model.update(where={...}, data={...})`
- [ ] `joinedload(...)` → `include={...}`

### Testing
- [ ] Test endpoint functionality
- [ ] Verify response format unchanged
- [ ] Check error handling works
- [ ] Validate authentication still works
- [ ] Test with real data

---
**💡 Pro Tip**: Start with the simplest endpoints first to get comfortable with the patterns, then tackle more complex ones.