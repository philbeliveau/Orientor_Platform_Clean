# Quick Reference Emergency Guide

## 🚨 Emergency Response Checklists (< 5 minutes)

### System Down Procedures
```bash
# 1. Quick health check (30 seconds)
curl -f http://localhost:8000/health && echo "✅ Backend UP" || echo "❌ Backend DOWN"
curl -f http://localhost:3000/api/health && echo "✅ Frontend UP" || echo "❌ Frontend DOWN"

# 2. Restart services (2 minutes)
docker-compose down && docker-compose up -d
# OR
pm2 restart all

# 3. Check logs immediately
tail -f logs/error.log | grep -E "(ERROR|FATAL|CRITICAL)"
```

### Database Corruption Detection & Response
```bash
# 1. Quick integrity check (15 seconds)
psql -d orientor -c "SELECT count(*) FROM users;" 2>/dev/null && echo "✅ DB OK" || echo "❌ DB CORRUPTED"

# 2. Emergency backup restore (90 seconds)
pg_dump orientor > backup_$(date +%Y%m%d_%H%M%S).sql
psql -d orientor -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -d orientor < backups/latest_backup.sql

# 3. Verify critical data
psql -d orientor -c "SELECT count(*) FROM users, conversations, profiles;"
```

### Authentication Failure Emergency Fixes
```bash
# 1. Reset Clerk connection (30 seconds)
export CLERK_PUBLISHABLE_KEY="your-key"
export CLERK_SECRET_KEY="your-secret"
pm2 restart backend

# 2. Clear auth cache (15 seconds)
redis-cli FLUSHDB 1
# OR
rm -rf node_modules/.cache/clerk*

# 3. Verify auth endpoint
curl -H "Authorization: Bearer test-token" http://localhost:8000/api/auth/verify
```

### Performance Degradation Immediate Actions
```bash
# 1. Resource check (10 seconds)
top -n 1 | head -20
df -h
free -m

# 2. Kill resource hogs (30 seconds)
ps aux --sort=-%cpu | head -10
kill -9 $(ps aux --sort=-%cpu | grep -v "root\|system" | head -5 | awk '{print $2}')

# 3. Restart critical services (60 seconds)
pm2 restart backend frontend
systemctl restart redis postgresql
```

## ⚡ One-Line Diagnostic Commands

### System Health Check
```bash
curl -s http://localhost:8000/health | jq '.status' && curl -s http://localhost:3000/api/health | jq '.status' && echo "✅ SYSTEM HEALTHY" || echo "❌ SYSTEM ISSUES"
```

### Database Connectivity Test
```bash
psql -d orientor -c "SELECT 'DB_OK' as status, now() as timestamp;" 2>/dev/null && echo "✅ DB CONNECTED" || echo "❌ DB DISCONNECTED"
```

### API Endpoint Validation
```bash
curl -f -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/users/me | grep -q "200\|401" && echo "✅ API RESPONSIVE" || echo "❌ API DOWN"
```

### Frontend/Backend Integration Check
```bash
curl -s http://localhost:3000/api/test-backend-connection | grep -q "success" && echo "✅ INTEGRATION OK" || echo "❌ INTEGRATION BROKEN"
```

## 🔧 Common Error Quick Fixes

### "Invalid data format" - Immediate Fix
```bash
# Fix datetime serialization
sed -i 's/datetime.datetime/datetime.datetime.isoformat()/g' backend/app/services/*.py
pm2 restart backend
```

### Date Serialization Errors - Quick Patch
```bash
# Apply date fix patch
cat > /tmp/date_fix.py << 'EOF'
import json
from datetime import datetime
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
EOF
cp /tmp/date_fix.py backend/app/utils/
pm2 restart backend
```

### Authentication Redirect Loops - Emergency Reset
```bash
# Clear all auth sessions
redis-cli KEYS "clerk:*" | xargs redis-cli DEL
rm -rf frontend/.next/cache
npm run dev &
```

### Database Connection Failures - Rapid Recovery
```bash
# Reset database connections
systemctl restart postgresql
export DATABASE_URL="postgresql://user:pass@localhost:5432/orientor"
pm2 restart backend
```

## 📞 Emergency Contacts and Escalation

### On-Call Rotation
- **Primary**: Lead Developer (+1-XXX-XXX-XXXX)
- **Secondary**: DevOps Engineer (+1-XXX-XXX-XXXX)  
- **Escalation**: Technical Director (+1-XXX-XXX-XXXX)

### Expertise Areas
- **Authentication Issues**: @auth-specialist
- **Database Problems**: @db-admin
- **Frontend Crashes**: @frontend-lead
- **Infrastructure**: @devops-team

### Escalation Procedures
1. **P0 (System Down)**: Immediate call + Slack #emergency
2. **P1 (Critical Feature)**: 15min Slack response required
3. **P2 (Performance)**: 1hr response time
4. **P3 (Minor Issues)**: Next business day

### Incident Communication Template
```
🚨 INCIDENT ALERT 🚨
Severity: P0/P1/P2/P3
System: Frontend/Backend/Database
Impact: X users affected
Status: Investigating/Identified/Resolved
ETA: X minutes
Lead: @username
```

## 🔄 Rollback Procedures

### One-Command System Rollback
```bash
# Full system rollback (< 2 minutes)
git checkout HEAD~1
docker-compose down
docker-compose up -d
pm2 restart all
```

### Selective Feature Rollback
```bash
# Rollback specific feature
git revert <commit-hash> --no-edit
npm run build:prod
pm2 restart backend frontend
```

### Database Rollback
```bash
# Database rollback (90 seconds)
pg_dump orientor > emergency_backup_$(date +%Y%m%d_%H%M%S).sql
psql -d orientor < backups/stable_backup.sql
```

### Frontend Deployment Rollback
```bash
# Frontend rollback (60 seconds)
cd frontend
git checkout HEAD~1
npm run build
pm2 restart frontend
```

## 📊 Status Page Templates

### User Communication for Known Issues

#### System Maintenance
```
🔧 SCHEDULED MAINTENANCE
We're performing system updates to improve performance.
Expected downtime: 15 minutes
Start: [TIME]
End: [TIME] (estimated)
Updates: https://status.orientor.com
```

#### Authentication Issues
```
🔐 AUTHENTICATION SERVICE ISSUE
We're experiencing login difficulties.
Workaround: Clear browser cache and retry
Status: Investigating
ETA: 30 minutes
```

#### Performance Degradation
```
⚡ PERFORMANCE ISSUE DETECTED
Response times may be slower than normal.
Impact: Non-critical features affected
Status: Identified, applying fixes
ETA: 15 minutes
```

### Resolution Communication Template
```
✅ ISSUE RESOLVED
Problem: [Brief description]
Duration: [X minutes]  
Root Cause: [Technical summary]
Resolution: [What was fixed]
Prevention: [Steps taken to prevent recurrence]
Thank you for your patience.
```

### Post-Incident Communication
```
📋 INCIDENT POST-MORTEM
Date: [DATE]
Duration: [X minutes]
Impact: [X users, Y transactions]
Timeline: Available at [LINK]
Actions Taken: [Summary]
Improvements: [What we're doing better]
Questions: support@orientor.com
```

## 🎯 Emergency Action Priority

1. **0-30 seconds**: System health check
2. **30-60 seconds**: Identify affected services
3. **1-2 minutes**: Apply immediate fix or rollback
4. **2-5 minutes**: Verify resolution and communicate status
5. **5+ minutes**: Root cause analysis and prevention

## 🔗 Quick Links

- **Status Dashboard**: http://localhost:3000/admin/status
- **Log Viewer**: http://localhost:3000/admin/logs  
- **Database Admin**: http://localhost:5432/admin
- **Incident Tracker**: [Internal tracking system]
- **Runbook Repository**: /docs/runbooks/

---

**Remember**: When in doubt, rollback first, investigate later. User experience is priority #1.