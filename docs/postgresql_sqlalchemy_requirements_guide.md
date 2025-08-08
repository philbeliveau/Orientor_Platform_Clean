# PostgreSQL + SQLAlchemy Requirements Guide

**Critical guide created after discovering systemic autoincrement issues affecting 94% of database tables**

## 🚨 The Problem That Was Discovered

A critical architectural flaw was found where **29 out of 31 database tables** were missing proper autoincrement configuration, causing INSERT operations to fail with:

```
(psycopg2.errors.NotNullViolation) null value in column "id" of relation "table_name" violates not-null constraint
```

## 🔧 PostgreSQL-Specific Requirements

### 1. **Primary Key Autoincrement - MANDATORY**

**❌ WRONG (what was causing failures):**
```python
id = Column(Integer, primary_key=True, index=True)  # Missing autoincrement
```

**✅ CORRECT:**
```python
id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Has autoincrement
```

### 2. **Why PostgreSQL is Different**

Unlike MySQL which auto-increments by default, **PostgreSQL requires explicit configuration**:

- **MySQL**: `AUTO_INCREMENT` is implicit for primary keys
- **PostgreSQL**: Requires `SERIAL` type or explicit sequence
- **SQLAlchemy**: Must specify `autoincrement=True` for PostgreSQL compatibility

### 3. **Database Migration Requirements**

**For NEW tables:**
```python
op.create_table(
    'my_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),  # ✅ REQUIRED
    sa.PrimaryKeyConstraint('id')
)
```

**For EXISTING tables without autoincrement:**
```python
def upgrade() -> None:
    op.execute("""
        -- Create sequence
        CREATE SEQUENCE IF NOT EXISTS my_table_id_seq;
        
        -- Set ownership
        ALTER SEQUENCE my_table_id_seq OWNED BY my_table.id;
        
        -- Set current value to avoid conflicts
        SELECT setval('my_table_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM my_table;
        
        -- Set default to use sequence
        ALTER TABLE my_table ALTER COLUMN id SET DEFAULT nextval('my_table_id_seq');
    """)
```

## 📋 Mandatory Patterns

### Model Definition Standard

**Use Base Classes (Recommended):**
```python
from .base_model import AutoIncrementBase

class MyModel(AutoIncrementBase):  # ✅ Inherits proper autoincrement
    __tablename__ = "my_table"
    # id, created_at, updated_at inherited
    name = Column(String(100), nullable=False)
```

**Manual Definition (If needed):**
```python
from ..utils.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ✅ REQUIRED
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Migration Review Pattern

**Before creating any migration, verify:**
1. All Integer primary keys have `autoincrement=True`
2. All `CREATE TABLE` statements include autoincrement
3. Existing table modifications handle sequence creation
4. Test on development database first

## 🚫 Never Do This

**Forbidden Patterns:**
```python
# ❌ FORBIDDEN - Will cause INSERT failures
id = Column(Integer, primary_key=True)
id = Column(Integer, primary_key=True, index=True)  # Missing autoincrement

# ❌ FORBIDDEN - Migration without autoincrement
sa.Column('id', sa.Integer(), nullable=False)  # Missing autoincrement

# ❌ FORBIDDEN - Copy-paste old patterns
# Always review migration templates for autoincrement
```

## ✅ Always Do This

**Required Patterns:**
```python
# ✅ REQUIRED - Model with proper autoincrement
id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# ✅ REQUIRED - Migration with autoincrement
sa.Column('id', sa.Integer(), autoincrement=True, nullable=False)

# ✅ REQUIRED - Use base classes for consistency
class MyModel(AutoIncrementBase):  # Prevents errors automatically
```

## 🔄 UUID Alternative

**For models requiring UUIDs:**
```python
from .base_model import UUIDBase

class MyUUIDModel(UUIDBase):  # ✅ UUID autoincrement
    __tablename__ = "my_uuid_table"
    # id is UUID with auto-generation
```

**Manual UUID definition:**
```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ UUID auto-gen
```

## 🧪 Testing Requirements

### Mandatory Tests for New Models

```python
def test_model_autoincrement(db_session):
    """Test that model auto-generates IDs."""
    instance = MyModel(name="test")
    
    assert instance.id is None  # Before commit
    
    db_session.add(instance)
    db_session.commit()
    
    assert instance.id is not None  # After commit
    assert isinstance(instance.id, int)
    assert instance.id > 0
```

### Integration Test Pattern

1. **Before deployment**: Test INSERT on all new/modified models
2. **After migration**: Verify all tables can INSERT successfully  
3. **Regression testing**: Ensure no NULL ID constraint violations

## 📊 Migration Validation Checklist

Before applying ANY migration:

- [ ] All Integer primary keys have `autoincrement=True`
- [ ] Migration tested on development environment  
- [ ] INSERT operations tested on all affected tables
- [ ] Sequence conflicts checked and resolved
- [ ] Rollback plan tested and documented

## 🎯 Team Standards

### Code Review Requirements

**Reviewers must verify:**
1. No Integer primary keys without `autoincrement=True`
2. All migrations follow PostgreSQL sequence patterns
3. Models use recommended base classes
4. Tests verify INSERT operations work

### New Developer Onboarding

**Must understand:**
1. PostgreSQL requires explicit autoincrement
2. SQLAlchemy `autoincrement=True` is mandatory  
3. Base classes prevent common errors
4. Migration patterns for sequence handling

## 🚨 Emergency Response

**If autoincrement issues are discovered:**

1. **Immediate hotfix** for user-blocking tables
2. **Comprehensive audit** of all affected tables  
3. **Systematic remediation** using established patterns
4. **Testing verification** before production deployment

## 📈 Monitoring

**Ongoing vigilance:**
- Monitor for NULL ID constraint violations
- Review new model definitions in PRs
- Audit migration patterns regularly
- Maintain autoincrement test coverage

---

## Summary

**The Golden Rule**: Every Integer primary key in PostgreSQL must have `autoincrement=True` in SQLAlchemy. No exceptions.

**The Cost of Ignoring This**: 29 broken tables, multiple broken user flows, emergency remediation, and potential production outages.

**The Solution**: Use established patterns, review checklists, comprehensive testing, and team education.

---

**Document Version**: 1.0  
**Created**: 2025-08-08  
**Team**: Orientor Platform Development  
**Severity**: Critical - Production Impact