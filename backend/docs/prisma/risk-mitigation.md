# Risk Mitigation & Rollback Procedures

This document outlines comprehensive safety measures, rollback procedures, and risk mitigation strategies for the Prisma migration.

## 🛡️ Risk Assessment Matrix

### High Risk Areas

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **Data Loss** | Critical | Low | Database backups + Transaction rollbacks |
| **Authentication Breaks** | High | Medium | Preserve Clerk integration + Staged testing |
| **API Contract Changes** | High | Medium | Response format validation + Gradual rollout |
| **Performance Degradation** | Medium | Medium | Performance monitoring + Query optimization |
| **Connection Pool Issues** | Medium | Low | Connection monitoring + Fallback mechanisms |

### Medium Risk Areas

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **Relationship Query Errors** | Medium | Medium | Comprehensive testing + Pattern documentation |
| **Type Mismatch Issues** | Medium | Low | Type validation + Runtime checks |
| **Complex Query Failures** | Medium | Medium | Raw SQL fallbacks + Testing |

## 🔄 Rollback Strategies

### Strategy 1: Feature Flag Rollback (Recommended)

**Implementation**:
```python
# Feature flag configuration
USE_PRISMA = os.getenv("USE_PRISMA", "false").lower() == "true"

# Conditional dependency injection
if USE_PRISMA:
    from ..utils.prisma_client import get_prisma
    db_dependency = Depends(get_prisma)
else:
    from ..database import get_db
    db_dependency = Depends(get_db)

@router.get("/users")
async def get_users(db=db_dependency):
    if USE_PRISMA:
        return await prisma_get_users(db)
    else:
        return sqlalchemy_get_users(db)
```

**Advantages**:
- ✅ Instant rollback via environment variable
- ✅ Zero downtime switching
- ✅ A/B testing capability
- ✅ Gradual rollout possible

### Strategy 2: Git Branch Rollback

**Implementation**:
```bash
# Emergency rollback procedure
git checkout main                    # Switch to stable branch
git reset --hard <stable-commit>     # Reset to known good state
docker-compose restart backend      # Restart services
```

**Advantages**:
- ✅ Complete system rollback
- ✅ All changes reverted instantly
- ✅ Known working state restored

**Disadvantages**:
- ❌ Requires service restart
- ❌ Loses all recent changes
- ❌ More disruptive

### Strategy 3: Database Migration Rollback

**Implementation**:
```bash
# If database schema changes were made
alembic downgrade -1                 # Rollback last migration
# or
alembic downgrade <revision_id>      # Rollback to specific revision

# Restart application
systemctl restart orientor-backend
```

## 🚨 Emergency Procedures

### Procedure 1: Immediate Rollback (< 5 minutes)

**When to Use**: Critical failures, data corruption, authentication breakdown

**Steps**:
1. **Set rollback flag**:
   ```bash
   export USE_PRISMA=false
   # or update environment file
   echo "USE_PRISMA=false" >> .env
   ```

2. **Restart services**:
   ```bash
   docker-compose restart backend
   # or
   systemctl restart orientor-backend
   ```

3. **Verify rollback**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/users/me
   ```

4. **Monitor logs**:
   ```bash
   docker-compose logs -f backend
   ```

### Procedure 2: Partial Rollback (Router-Specific)

**When to Use**: Single router/endpoint failures

**Steps**:
1. **Identify failing router**:
   ```bash
   grep "ERROR" logs/backend.log | grep -E "(router|endpoint)"
   ```

2. **Revert specific router**:
   ```bash
   git checkout HEAD~1 -- backend/app/routers/failing_router.py
   git commit -m "Rollback: Revert failing_router.py to SQLAlchemy"
   ```

3. **Test specific endpoints**:
   ```bash
   pytest tests/test_specific_router.py -v
   ```

### Procedure 3: Database Recovery

**When to Use**: Data corruption or loss detected

**Steps**:
1. **Stop all write operations**:
   ```bash
   # Set application to read-only mode
   export READ_ONLY_MODE=true
   ```

2. **Restore from backup**:
   ```bash
   # Railway database restore (if available)
   railway database:restore --backup-id <backup_id>
   
   # Or manual restore
   psql $DATABASE_URL < backup_$(date +%Y%m%d).sql
   ```

3. **Verify data integrity**:
   ```bash
   python scripts/verify_data_integrity.py
   ```

## 📊 Monitoring & Alerting

### Critical Metrics to Monitor

#### Application Metrics
```python
# Monitoring code to add to endpoints
import time
import logging
from prometheus_client import Counter, Histogram

# Metrics
prisma_operations = Counter('prisma_operations_total', ['operation', 'model', 'status'])
prisma_duration = Histogram('prisma_operation_duration_seconds', ['operation', 'model'])

async def monitored_prisma_operation(operation_func, operation_name, model_name):
    start_time = time.time()
    try:
        result = await operation_func()
        prisma_operations.labels(operation=operation_name, model=model_name, status='success').inc()
        return result
    except Exception as e:
        prisma_operations.labels(operation=operation_name, model=model_name, status='error').inc()
        logging.error(f"Prisma {operation_name} failed on {model_name}: {e}")
        raise
    finally:
        duration = time.time() - start_time
        prisma_duration.labels(operation=operation_name, model=model_name).observe(duration)
```

#### Database Connection Monitoring
```python
# Connection health check
async def monitor_db_health():
    """Monitor database connection health"""
    try:
        async with get_prisma() as db:
            start_time = time.time()
            await db.execute_raw("SELECT 1")
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 1000:  # 1 second threshold
                logging.warning(f"Slow database response: {response_time:.2f}ms")
            
            return {"status": "healthy", "response_time_ms": response_time}
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        # Trigger alert
        send_alert(f"Database connection failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
```

### Alert Conditions

#### Critical Alerts (Immediate Response Required)
- Database connection failures > 5 in 1 minute
- Authentication endpoint failures > 10% error rate
- Response times > 5 seconds for 3 consecutive requests
- Memory usage > 90% for 2 minutes

#### Warning Alerts (Monitor Closely)
- Response times > 2 seconds
- Error rate > 5% for any endpoint
- Database query count > normal baseline by 50%
- Connection pool utilization > 80%

## 🧪 Pre-Migration Safety Checks

### Automated Safety Validation

```python
# Pre-migration validation script
import asyncio
import logging
from typing import Dict, List

async def validate_migration_readiness() -> Dict[str, bool]:
    """Comprehensive pre-migration validation"""
    checks = {}
    
    # 1. Database connectivity
    try:
        async with get_prisma() as db:
            await db.execute_raw("SELECT 1")
        checks["database_connection"] = True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        checks["database_connection"] = False
    
    # 2. Schema compatibility
    try:
        async with get_prisma() as db:
            # Test key tables exist
            await db.user.find_first()
            await db.conversation.find_first()
            await db.chatmessage.find_first()
        checks["schema_compatibility"] = True
    except Exception as e:
        logging.error(f"Schema validation failed: {e}")
        checks["schema_compatibility"] = False
    
    # 3. Authentication integration
    try:
        # Test auth endpoints
        # This would be integration test
        checks["auth_integration"] = True
    except Exception as e:
        logging.error(f"Auth integration failed: {e}")
        checks["auth_integration"] = False
    
    # 4. Backup verification
    checks["backup_available"] = verify_backup_exists()
    
    # 5. Rollback mechanism
    checks["rollback_ready"] = verify_rollback_mechanism()
    
    return checks

def verify_backup_exists() -> bool:
    """Verify recent database backup exists"""
    # Check Railway backups or manual backup files
    return True  # Implement actual check

def verify_rollback_mechanism() -> bool:
    """Verify rollback mechanism is working"""
    # Test feature flag switching
    return True  # Implement actual check
```

### Manual Pre-Flight Checklist

```markdown
## Pre-Migration Checklist

### Infrastructure
- [ ] **Database backup** created and verified (< 24 hours old)
- [ ] **Application backup** (Git tag/branch) created
- [ ] **Environment variables** documented and backed up
- [ ] **Monitoring** systems operational
- [ ] **Alert channels** tested and verified

### Code Preparation
- [ ] **Feature flags** implemented and tested
- [ ] **Rollback procedures** documented and verified
- [ ] **Emergency contacts** notified and available
- [ ] **Test environment** migration completed successfully
- [ ] **Performance baselines** recorded

### Team Readiness
- [ ] **Migration team** identified and briefed
- [ ] **Support team** on standby during migration window
- [ ] **Communication channels** established
- [ ] **Escalation procedures** defined
- [ ] **Go/No-Go decision** criteria established
```

## 🔧 Recovery Procedures

### Data Recovery

#### Scenario 1: Partial Data Loss
```python
# Data recovery script
async def recover_missing_data(table_name: str, backup_file: str):
    """Recover missing data from backup"""
    async with get_prisma() as db:
        # Read backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Find missing records
        existing_ids = await db.execute_raw(f"SELECT id FROM {table_name}")
        existing_id_set = {row['id'] for row in existing_ids}
        
        missing_records = [
            record for record in backup_data 
            if record['id'] not in existing_id_set
        ]
        
        # Restore missing records
        if missing_records:
            await db.execute_raw(
                f"INSERT INTO {table_name} VALUES ...",
                missing_records
            )
            
        return len(missing_records)
```

#### Scenario 2: Complete Table Recovery
```bash
#!/bin/bash
# Complete table recovery script

TABLE_NAME=$1
BACKUP_FILE=$2

echo "🔄 Recovering table: $TABLE_NAME"

# Create recovery table
psql $DATABASE_URL -c "CREATE TABLE ${TABLE_NAME}_recovery AS SELECT * FROM $TABLE_NAME WHERE false;"

# Import backup data
pg_restore --table=${TABLE_NAME}_recovery $BACKUP_FILE

# Compare data
psql $DATABASE_URL -c "
    SELECT 
        'Original' as source, COUNT(*) as count FROM $TABLE_NAME
    UNION ALL
    SELECT 
        'Recovery' as source, COUNT(*) as count FROM ${TABLE_NAME}_recovery;
"

# Manual verification required before final restore
echo "⚠️  Manual verification required before proceeding with restore"
```

### Service Recovery

#### Application Service Recovery
```bash
#!/bin/bash
# Application recovery script

echo "🚨 Starting emergency recovery procedure"

# 1. Stop current service
docker-compose stop backend

# 2. Revert to known good state
git checkout production-stable
git reset --hard

# 3. Restore environment
cp .env.backup .env

# 4. Restart services
docker-compose up -d backend

# 5. Health check
sleep 30
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    exit 1
}

echo "✅ Recovery completed successfully"
```

#### Database Service Recovery
```bash
#!/bin/bash
# Database recovery script

echo "🔄 Starting database recovery"

# 1. Create recovery point
pg_dump $DATABASE_URL > recovery_point_$(date +%Y%m%d_%H%M%S).sql

# 2. Stop write operations
export READ_ONLY_MODE=true

# 3. Restore from backup
psql $DATABASE_URL < latest_backup.sql

# 4. Verify restoration
python scripts/verify_data_integrity.py

# 5. Resume operations
export READ_ONLY_MODE=false

echo "✅ Database recovery completed"
```

## 📞 Emergency Contacts & Escalation

### Contact Information
```markdown
## Emergency Response Team

### Primary Contacts
- **Lead Developer**: [Contact Info]
- **DevOps Engineer**: [Contact Info]  
- **Database Administrator**: [Contact Info]

### Secondary Contacts
- **Product Manager**: [Contact Info]
- **CTO/Technical Lead**: [Contact Info]

### External Contacts
- **Railway Support**: [Support Channel]
- **Clerk Support**: [Support Channel]
```

### Escalation Matrix

| Severity | Response Time | Who to Contact | Actions Required |
|----------|---------------|----------------|------------------|
| **Critical** | < 15 minutes | All primary contacts | Immediate rollback, all hands |
| **High** | < 30 minutes | Lead Developer + DevOps | Investigation, prepare rollback |
| **Medium** | < 1 hour | Lead Developer | Monitor, investigate, document |
| **Low** | < 4 hours | Lead Developer | Standard troubleshooting |

### Communication Templates

#### Critical Alert Template
```
🚨 CRITICAL: Prisma Migration Issue

Severity: CRITICAL
Affected: [Describe impact]
Started: [Timestamp]
Actions Taken: [List actions]
Status: [Current status]
ETA: [Estimated resolution]

Next Update: [Time]
```

#### Resolution Template
```
✅ RESOLVED: Prisma Migration Issue

Issue: [Brief description]
Root Cause: [Explanation]
Resolution: [What was done]
Prevention: [How to prevent recurrence]
Duration: [Total downtime]

Post-Mortem: [Link to detailed analysis]
```

---
**🛡️ Remember**: Better safe than sorry. When in doubt, rollback first and investigate later.