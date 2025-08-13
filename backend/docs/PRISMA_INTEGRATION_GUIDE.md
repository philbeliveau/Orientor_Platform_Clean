# Prisma + Railway Integration Guide

Complete guide for integrating Prisma ORM with your Railway PostgreSQL database in the Orientor Platform.

## 🚀 Quick Setup

### 1. Get Your Railway Database URL

1. Go to [railway.app](https://railway.app) dashboard
2. Select your Orientor project
3. Click on your **PostgreSQL** service
4. Go to **Variables** tab
5. Copy the `DATABASE_URL` value

### 2. Update Environment Variables

Edit `backend/.env`:

```env
# Replace with your actual Railway database URL
DATABASE_URL="postgresql://postgres:your_password@your_host:5432/railway"
DATABASE_PUBLIC_URL="postgresql://postgres:your_password@your_host:5432/railway"
```

### 3. Run Setup Script

```bash
cd backend
bash scripts/setup_prisma.sh
```

This script will:
- ✅ Test database connection
- 🔍 Introspect your existing database
- ⚙️ Generate TypeScript client
- 🐍 Generate Python client

## 📋 Manual Setup Steps

If you prefer to run steps manually:

### 1. Database Introspection

```bash
cd backend
npx prisma db pull
```

This generates Prisma models from your existing SQLAlchemy tables.

### 2. Generate Clients

```bash
# Generate TypeScript client
npx prisma generate

# Generate Python client  
python -m prisma generate
```

### 3. Test Connection

```bash
# Test with Prisma CLI
npx prisma studio
```

## 🔧 Integration with FastAPI

### Import Prisma Client

```python
from app.utils.prisma_client import get_prisma_client, get_prisma
from prisma import Prisma
from fastapi import Depends
```

### Use in Routes

```python
@router.get("/users")
async def get_users(db: Prisma = Depends(get_prisma_client)):
    users = await db.user.find_many(
        include={"user_profile": True},
        take=10
    )
    return users
```

### Async Context Manager

```python
async def some_service_function():
    async with get_prisma() as db:
        user = await db.user.find_unique(where={"id": user_id})
        return user
```

## 🎯 Key Benefits You'll Get

### 1. Type Safety

```python
# ✅ Type-safe queries
user = await db.user.find_unique(where={"id": 1})
# user is properly typed with all fields

# ❌ No more raw SQL strings
# db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### 2. Intelligent Auto-completion

Your IDE will provide full autocomplete for:
- Model fields
- Query methods
- Filter conditions
- Include/select options

### 3. Relation Loading

```python
# Load user with profile and conversations
user = await db.user.find_unique(
    where={"id": user_id},
    include={
        "user_profile": True,
        "conversations": {
            "take": 5,
            "order_by": {"created_at": "desc"}
        }
    }
)
```

### 4. Transactions

```python
async with db.tx() as transaction:
    user = await transaction.user.create(data=user_data)
    profile = await transaction.user_profile.create(
        data={"user_id": user.id, ...profile_data}
    )
```

## 📊 Comparing SQLAlchemy vs Prisma

| Feature | SQLAlchemy | Prisma |
|---------|------------|--------|
| Type Safety | Manual typing | Auto-generated types |
| Relations | Manual joins | Automatic include/select |
| Queries | Raw SQL or ORM | Type-safe query builder |
| Migrations | Alembic | Prisma Migrate |
| IDE Support | Basic | Full autocomplete |
| Performance | Good | Optimized by default |

## 🔄 Migration Strategy

### Option 1: Gradual Migration (Recommended)

1. **Keep existing SQLAlchemy code working**
2. **Use Prisma for new features**
3. **Gradually migrate existing routes**

Example:
```python
# Existing SQLAlchemy route (keep working)
@router.get("/users/legacy")
def get_users_legacy(db: Session = Depends(get_db)):
    return db.query(User).all()

# New Prisma route (better type safety)
@router.get("/users/prisma") 
async def get_users_prisma(db: Prisma = Depends(get_prisma_client)):
    return await db.user.find_many()
```

### Option 2: Full Migration

1. Replace all database operations with Prisma
2. Remove SQLAlchemy dependencies
3. Use Prisma Migrate instead of Alembic

## 🛠 Practical Examples

### User Management with Clerk Integration

```python
@router.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),  # Clerk auth
    db: Prisma = Depends(get_prisma_client)          # Prisma DB
):
    # Get user data with Prisma type safety
    prisma_user = await db.user.find_unique(
        where={"clerk_user_id": current_user.clerk_user_id},
        include={
            "user_profile": True,
            "conversations": {"take": 5},
            "saved_recommendations": {"take": 10}
        }
    )
    return prisma_user
```

### Advanced Querying

```python
# Complex search with filters
users = await db.user.find_many(
    where={
        "AND": [
            {"created_at": {"gte": datetime.now() - timedelta(days=30)}},
            {"OR": [
                {"first_name": {"contains": search_term}},
                {"last_name": {"contains": search_term}}
            ]}
        ]
    },
    include={"user_profile": True},
    order_by={"created_at": "desc"},
    take=20
)
```

### Aggregations and Analytics

```python
# Get user statistics
stats = await db.user.aggregate(
    _count={"id": True},
    _avg={"age": True},
    where={"created_at": {"gte": start_date}}
)

# Group by with counts
monthly_signups = await db.user.group_by(
    by=["created_at"],
    _count={"id": True},
    having={"id": {"_count": {"gt": 10}}}
)
```

## 🎨 Using Prisma Studio

Prisma Studio provides a visual database browser:

```bash
cd backend
npx prisma studio
```

This opens a web interface where you can:
- Browse all your data
- Edit records visually
- Run queries
- Understand relationships

## 🔒 Security Best Practices

### 1. Environment Variables
```env
# ✅ Good
DATABASE_URL="postgresql://user:pass@host:5432/db"

# ❌ Never commit real credentials
DATABASE_URL="postgresql://prod_user:real_password@prod.host:5432/prod_db"
```

### 2. Query Validation
```python
# ✅ Validate input data
@router.get("/users/{user_id}")
async def get_user(user_id: int):  # FastAPI validates int
    user = await db.user.find_unique(where={"id": user_id})
    
# ✅ Use Pydantic models for request validation
class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)
```

### 3. Authentication Integration
```python
# Always use your existing Clerk authentication
@router.post("/users/update")
async def update_user(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),  # Clerk auth
    db: Prisma = Depends(get_prisma_client)
):
    # Only update current user's data
    return await db.user.update(
        where={"id": current_user.id},
        data=data.dict(exclude_unset=True)
    )
```

## 📈 Performance Optimization

### 1. Select Only What You Need
```python
# ✅ Select specific fields
user = await db.user.find_unique(
    where={"id": user_id},
    select={"first_name": True, "email": True}
)

# ❌ Don't load unnecessary data
user = await db.user.find_unique(where={"id": user_id})  # Loads all fields
```

### 2. Efficient Relation Loading
```python
# ✅ Load related data efficiently
users = await db.user.find_many(
    include={
        "conversations": {
            "take": 5,  # Limit related records
            "select": {"title": True, "created_at": True}  # Select specific fields
        }
    }
)
```

### 3. Use Pagination
```python
# ✅ Implement pagination
users = await db.user.find_many(
    skip=(page - 1) * limit,
    take=limit,
    order_by={"created_at": "desc"}
)
```

## 🐛 Troubleshooting

### Common Issues

1. **"Prisma Client not found"**
   ```bash
   cd backend
   npx prisma generate
   python -m prisma generate
   ```

2. **"Environment variable not found"**
   - Check `backend/.env` file exists
   - Verify `DATABASE_URL` is set correctly

3. **"Connection refused"**
   - Verify Railway database URL is correct
   - Check database is running on Railway

4. **"Schema out of sync"**
   ```bash
   npx prisma db pull  # Re-introspect database
   npx prisma generate # Regenerate client
   ```

### Debug Commands

```bash
# Test connection
npx prisma db execute --stdin <<< "SELECT 1;"

# View current schema
npx prisma format

# Reset and regenerate
npx prisma generate --force-update
```

## 🎯 Next Steps

1. **✅ Complete setup** using the guide above
2. **🔍 Explore your generated schema** in `prisma/schema.prisma`
3. **🧪 Test example endpoints** in `/api/prisma/*`
4. **🔄 Start migrating routes** gradually to Prisma
5. **📊 Use Prisma Studio** for data visualization

## 📚 Additional Resources

- [Prisma Documentation](https://www.prisma.io/docs)
- [Railway + Prisma Guide](https://docs.railway.app/guides/prisma)
- [FastAPI + Prisma Examples](https://github.com/RobertCraigie/prisma-client-py)
- [Type Safety Best Practices](https://www.prisma.io/docs/concepts/components/prisma-client/type-safety)

---

**Ready to get started?** Run the setup script and start enjoying type-safe database operations! 🚀