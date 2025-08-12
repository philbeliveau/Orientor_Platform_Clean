# Agent Implementation Prompts - Setup Instructions

## Overview
These prompts are designed for immediate agent execution to implement the Clerk authentication optimization plan. Each prompt is self-contained with complete context and implementation requirements.

## Agent Assignment Strategy

### Parallel Track 1: Core Infrastructure (Day 1)
- **Agent 1**: Module A - Core Token Cache Service
- **Agent 2**: Module E - Backend Authentication Enhancement  
- **Agent 3**: Module P - Performance Metrics Setup

### Parallel Track 2: Context & Middleware (Day 2)
- **Agent 1**: Module B - Enhanced Authentication Context (after Module A)
- **Agent 2**: Module D - Frontend Middleware Optimization
- **Agent 3**: Infrastructure validation and setup

### Parallel Track 3: Component Optimization (Day 6)
- **Agent 1**: Module G - Chat Interface Optimization
- **Agent 2**: Module H - Navigation Component Updates
- **Agent 3**: Module I - Form Component Optimization

## Critical Instructions for All Agents

### 🔐 AUTHENTICATION REQUIREMENTS
```
MANDATORY RULES - NO EXCEPTIONS:
✅ Always use: const { getToken } = useAuth(); const token = await getToken();
❌ Never use: localStorage.getItem('access_token')
✅ Always redirect to: /sign-in
❌ Never redirect to: /login
🚨 IF YOU SEE NON-CLERK AUTH CODE, STOP AND FIX IT IMMEDIATELY
```

### 📁 File Organization Rules
```
CRITICAL: NEVER save working files to root folder
✅ Use appropriate subdirectories:
   - /frontend/src/services/auth/ - Authentication services
   - /frontend/src/contexts/ - React contexts
   - /frontend/src/hooks/ - Custom hooks
   - /frontend/src/components/auth/ - Auth components
   - /backend/app/utils/ - Backend utilities
   - /backend/app/middleware/ - Backend middleware
```

### 🎯 Success Criteria for All Modules
```
Performance Targets:
├── Token cache hit rate: >95%
├── Authentication latency: <50ms
├── API response time: <200ms
├── Page load time: <500ms
├── Error rate: <0.1%
└── Memory usage: <10MB for auth systems

Testing Requirements:
├── Unit tests with >90% coverage
├── Performance benchmarks
├── Error scenario testing
├── Integration testing
└── Security validation
```

## Implementation Context

### Current Platform Issues
- **Chat interface**: 8 getToken() calls per interaction (Lines 194, 309, 359, 406, 709, 739, 761, 811)
- **Backend inconsistency**: 15% of routers using non-standard auth patterns
- **No token caching**: Every request fetches new tokens
- **Loading delays**: 2-5 seconds on every user interaction

### Target Architecture
- **Frontend**: TokenCacheService → EnhancedAuthContext → Optimized Components
- **Backend**: EnhancedClerkAuth → Unified Routers → Performance Monitoring
- **Performance**: 85-90% reduction in auth latency, 75% fewer API calls

### Project Structure Context
```
Frontend: Next.js with App Router
├── /frontend/src/components/chat/ChatInterface.tsx (CRITICAL - 8 token calls)
├── /frontend/src/services/api.ts (needs optimization)
├── /frontend/src/contexts/ (needs enhancement)
└── /frontend/middleware.ts (basic Clerk middleware)

Backend: FastAPI with SQLAlchemy
├── /backend/app/routers/ (40+ files, 15% inconsistent)
├── /backend/app/utils/clerk_auth.py (needs enhancement)
├── /backend/app/models/user.py (User model)
└── /backend/app/main.py (FastAPI app)
```

## Agent Communication Protocol

### Status Reporting Format
```
Agent Report Template:
📊 MODULE: [Module Name]
⏱️ STATUS: [In Progress/Completed/Blocked]
🎯 PROGRESS: [X/Y tasks completed]
📈 METRICS: [Performance improvements observed]
🚨 ISSUES: [Any blockers or concerns]
🔄 NEXT: [Next steps or dependencies]
```

### Integration Points
```
Critical Handoffs:
├── Module A → Module B (TokenCacheService integration)
├── Module A,B → Module G (Chat optimization)
├── Module E → Module J (Backend standardization)
├── All Modules → Module Q (Final validation)
```

### Quality Gates
```
Before Module Completion:
├── All unit tests passing
├── Performance benchmarks met
├── Integration tests successful
├── Code review completed
├── Documentation updated
```

## Emergency Procedures

### If Implementation Fails
```
Rollback Strategy:
├── Feature flags: Disable new functionality
├── Graceful degradation: Fall back to current system
├── Error monitoring: Track and alert on issues
├── Hot fixes: Immediate patches for critical issues
```

### Performance Issues
```
Monitoring Protocol:
├── Real-time metrics dashboard
├── Alert thresholds for key metrics
├── Automatic scaling triggers
├── Manual intervention procedures
```

---

**IMPORTANT**: Each agent should read their specific module documentation in `/docs/api-clerk-enhanced.md/plan/` before starting implementation. The prompts below reference this detailed documentation for complete technical specifications.