# Phase 1: Standardize API Client

## Objective
Enhance existing `ClerkApiService` and migrate core services to use it consistently.

## Current State Analysis
- `frontend/src/services/api.ts` has `ClerkApiService` class
- `frontend/src/utils/api.ts` has basic helpers
- Services use mixed patterns (fetch, axios, different auth)

## Tasks

### 1. Enhance ClerkApiService
**File**: `frontend/src/services/api.ts`

Add these methods to existing `ClerkApiService`:
```typescript
// Add comprehensive error handling
private handleError(error: any): never {
  if (error.status === 401) {
    window.location.href = '/sign-in'; // Clerk standard
    throw new Error('Authentication required');
  }
  throw new Error(`API Error: ${error.status} - ${error.message}`);
}

// Add request interceptor
private async makeRequest<T>(url: string, options: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, options);
    if (!response.ok) this.handleError(response);
    return response.json();
  } catch (error) {
    this.handleError(error);
  }
}
```

### 2. Add ESLint Rules
**File**: `frontend/.eslintrc.json`

Add rule to prevent direct HTTP library usage:
```json
{
  "rules": {
    "no-restricted-imports": ["error", {
      "patterns": ["axios", "node-fetch"],
      "message": "Use ClerkApiService instead of direct HTTP libraries"
    }]
  }
}
```

### 3. Migrate Core Services

#### Avatar Service
**File**: `frontend/src/services/avatarService.ts`

Replace direct fetch calls:
```typescript
// Before
const response = await fetch(endpoint('/avatar/me'), {
  headers: { 'Authorization': `Bearer ${token}` }
});

// After
const response = await clerkApiService.request('/api/v1/avatar/me', {
  method: 'GET',
  token
});
```

#### Career Goals Service  
**File**: `frontend/src/services/careerGoalsService.ts`

Replace authentication pattern:
```typescript
// Before
const token = await getToken();
const headers = { 'Authorization': `Bearer ${token}` };

// After
// Remove manual auth - ClerkApiService handles it
const response = await clerkApiService.request('/api/v1/career-goals', {
  method: 'POST',
  token,
  body: JSON.stringify(data)
});
```

#### Skills Tree Service
**File**: `frontend/src/services/skillsTreeService.ts`

Replace axios usage:
```typescript
// Before
import axios from 'axios';

// After
import { clerkApiService } from './api';
// Use clerkApiService.request() instead of axios
```

## Implementation Prompt for Agent

```
Task: Enhance ClerkApiService and migrate 3 core services

Instructions:
1. Edit frontend/src/services/api.ts:
   - Add comprehensive error handling method
   - Add request interceptor with Clerk auth
   - Ensure all redirects use '/sign-in' not '/login'

2. Edit frontend/.eslintrc.json:
   - Add no-restricted-imports rule for axios/fetch

3. Migrate these files to use ClerkApiService:
   - frontend/src/services/avatarService.ts
   - frontend/src/services/careerGoalsService.ts  
   - frontend/src/services/skillsTreeService.ts

Requirements:
- Keep existing API signatures working
- Use Clerk auth patterns: const { getToken } = useAuth(); const token = await getToken();
- Redirect to '/sign-in' for auth errors
- No breaking changes

Test: Verify avatar, career goals, and skills tree still work after migration.
```

## Success Criteria
- [ ] Enhanced ClerkApiService with error handling
- [ ] ESLint rule prevents direct HTTP library imports
- [ ] Avatar service migrated to ClerkApiService
- [ ] Career Goals service migrated to ClerkApiService  
- [ ] Skills Tree service migrated to ClerkApiService
- [ ] All services still function correctly
- [ ] No console errors related to authentication