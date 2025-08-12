# API Reliability Enhancement - Product Requirements Document

## Problem Statement

The Orientor Platform has inconsistent API client patterns causing maintenance issues:
- Multiple API utilities (`utils/api.ts`, `services/api.ts`, 20+ service files)
- Mixed `fetch`/`axios` usage across services
- Inconsistent error handling
- Duplicate authentication logic

## Solution Overview

**Goal**: Standardize API client to reduce bugs and improve maintainability.

**Approach**: Enhance existing `ClerkApiService` instead of creating new systems.

## Success Metrics

- Zero breaking changes during migration
- 50% reduction in API-related bugs
- Consistent error handling across all services
- 100% Clerk authentication compliance

## Implementation Phases

### Phase 1: Standardize API Client (Week 1)
- Enhance existing `ClerkApiService` class
- Add ESLint rules to prevent direct fetch/axios
- Migrate 3 core services (Avatar, Career Goals, Skills Tree)

### Phase 2: Add TypeScript Validation (Week 2)
- Generate types from backend OpenAPI spec
- Add request/response validation
- Implement proper error types

### Phase 3: Basic Testing (Week 3)
- Add contract tests for migrated services
- Implement error handling tests
- Basic performance monitoring

## Authentication Requirements

**MANDATORY CLERK PATTERNS:**
```typescript
// ✅ CORRECT
const { getToken } = useAuth();
const token = await getToken();

// ❌ FORBIDDEN
const token = localStorage.getItem('access_token');
```

**ROUTING:**
- ✅ Always redirect to: `/sign-in`
- ❌ Never redirect to: `/login`

## Risk Mitigation

- Keep existing services during migration
- Feature flags for gradual rollout
- Quick rollback to old patterns if needed
- Monitor error rates during migration

## Definition of Done

- All services use enhanced `ClerkApiService`
- ESLint prevents direct HTTP library usage
- TypeScript validates all API calls
- Basic tests verify functionality
- Zero regressions in production