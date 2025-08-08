# 🔍 Migration Review Checklist - Preventing Systemic Database Issues

This checklist was created after discovering a critical systemic autoincrement issue affecting 29 out of 31 database tables. Use this checklist for ALL new migrations and model changes to prevent similar architectural disasters.

## 📋 Pre-Migration Checklist

### ✅ Model Definition Review

**For NEW Models:**
- [ ] Model inherits from `AutoIncrementBase` or `SimpleAutoIncrementBase` (recommended)
- [ ] If using raw `Base`, primary key includes `autoincrement=True`
- [ ] Primary key pattern: `Column(Integer, primary_key=True, index=True, autoincrement=True)`
- [ ] NO manual `id = Column(Integer, primary_key=True, index=True)` without autoincrement
- [ ] Check imports include proper base classes

**For EXISTING Models:**
- [ ] All modified models maintain `autoincrement=True`
- [ ] No regression to non-autoincrement primary keys
- [ ] Timestamp fields use proper timezone handling

### ✅ Migration File Review

**SQL DDL Statements:**
- [ ] All `CREATE TABLE` statements include proper autoincrement
- [ ] Pattern: `id INTEGER NOT NULL` with `SERIAL` or sequence default
- [ ] NO `sa.Column('id', sa.Integer(), nullable=False)` without autoincrement
- [ ] Sequence creation for existing tables includes ownership and proper starting values

**PostgreSQL Compatibility:**
- [ ] Uses PostgreSQL-compatible syntax
- [ ] Sequence names follow pattern: `{table_name}_id_seq`
- [ ] Proper sequence ownership: `ALTER SEQUENCE ... OWNED BY table.id`
- [ ] Starting values preserve existing data: `SELECT setval('seq', COALESCE(MAX(id), 0) + 1, false)`

### ✅ Database Impact Assessment

**Data Safety:**
- [ ] Migration tested on copy of production data
- [ ] Existing data preserved (no data loss)
- [ ] ID conflicts resolved (no duplicate or null IDs)
- [ ] Sequence values set correctly to prevent conflicts

**Performance Impact:**
- [ ] Migration runs in reasonable time (<5 minutes for production)
- [ ] No blocking operations during peak hours
- [ ] Rollback plan tested and documented

## 🔧 Migration Template Validation

### Required Pattern for Integer Primary Keys:

```python
# ✅ CORRECT - New table creation
op.create_table(
    'my_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),  # ✅ Has autoincrement
    sa.Column('name', sa.String(100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.Index('ix_my_table_id', 'id')
)

# ❌ WRONG - Missing autoincrement
op.create_table(
    'my_table', 
    sa.Column('id', sa.Integer(), nullable=False),  # ❌ Missing autoincrement
    # ... rest of table
)
```

### Required Pattern for Existing Tables:

```python
# ✅ CORRECT - Adding autoincrement to existing table
def upgrade() -> None:
    op.execute("""
        -- Create sequence if it doesn't exist
        CREATE SEQUENCE IF NOT EXISTS my_table_id_seq;
        
        -- Set sequence ownership
        ALTER SEQUENCE my_table_id_seq OWNED BY my_table.id;
        
        -- Set current value to max existing id + 1
        SELECT setval('my_table_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM my_table;
        
        -- Set default to use sequence
        ALTER TABLE my_table ALTER COLUMN id SET DEFAULT nextval('my_table_id_seq');
    """)
```

## 🧪 Testing Requirements

### Pre-Deployment Testing:
- [ ] Migration applies successfully on development database
- [ ] Migration applies successfully on staging database with production-like data
- [ ] Rollback migration tested and works
- [ ] INSERT operations work correctly after migration
- [ ] No sequence conflicts or ID collisions

### Post-Migration Validation:
- [ ] Test INSERT operations on all affected tables
- [ ] Verify ID generation works properly
- [ ] Check sequence current values are correct
- [ ] Run application integration tests
- [ ] Monitor for any ID-related errors in logs

## 🚨 Red Flags - STOP and Review

**Immediate Red Flags:**
- [ ] ❌ Any `Column(Integer, primary_key=True)` without `autoincrement=True`
- [ ] ❌ Migration creates tables without considering PostgreSQL sequences
- [ ] ❌ Copy-paste from old migration without reviewing autoincrement
- [ ] ❌ Model inherits directly from `Base` instead of `AutoIncrementBase`

**Warning Signs:**
- [ ] ⚠️ Complex multi-table migration without autoincrement audit
- [ ] ⚠️ Migration modifies existing primary keys without sequence handling
- [ ] ⚠️ New table creation doesn't follow established patterns

## 📋 Review Roles and Responsibilities

### Migration Author:
- [ ] Complete this entire checklist before creating PR
- [ ] Test migration locally with real data
- [ ] Document any special considerations or risks
- [ ] Include rollback plan in PR description

### Code Reviewer:
- [ ] Verify all checklist items are addressed
- [ ] Review SQL DDL statements for PostgreSQL compatibility  
- [ ] Check model definitions for proper base class usage
- [ ] Ensure no regression to previous autoincrement issues

### DevOps/DBA:
- [ ] Review production impact and timing
- [ ] Validate backup and rollback procedures
- [ ] Schedule migration during appropriate maintenance window
- [ ] Monitor migration execution and post-migration health

## 🔄 Continuous Improvement

### After Each Migration:
- [ ] Add new patterns discovered to this checklist
- [ ] Update migration templates if needed
- [ ] Share lessons learned with team
- [ ] Update automated testing if gaps discovered

### Monthly Review:
- [ ] Review recent migrations for adherence to checklist
- [ ] Audit new models for proper base class usage
- [ ] Update team training materials if needed
- [ ] Assess if additional automation can prevent issues

---

## 📚 Quick Reference

**Always Use:**
- `AutoIncrementBase` for new models
- `autoincrement=True` for Integer primary keys
- Proper sequence handling in migrations
- Production-like testing before deployment

**Never Do:**
- Copy-paste old migration patterns without review
- Create Integer primary keys without autoincrement
- Skip testing INSERT operations after migration
- Apply migrations without rollback plan

**Remember:** The autoincrement issue cost significant development time and could have caused major production outages. This checklist exists to prevent similar systemic issues from occurring again.

---

**Checklist Version**: 1.0  
**Created**: 2025-08-08  
**Last Updated**: 2025-08-08  
**Next Review**: 2025-09-08