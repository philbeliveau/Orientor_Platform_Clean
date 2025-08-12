# Phase 2: Add TypeScript Validation

## Objective
Add proper TypeScript types and validation to API calls using backend OpenAPI spec.

## Current State
- Backend has 42+ endpoints with consistent structure
- Frontend lacks type validation for API requests/responses
- No runtime validation of API contracts

## Tasks

### 1. Generate TypeScript Types from Backend
**Script**: Generate types from FastAPI OpenAPI

```bash
# Add to package.json scripts:
"generate-api-types": "curl http://localhost:8000/openapi.json | npx swagger-typescript-api -p - -o src/types/api-generated.ts"
```

### 2. Add Type Definitions
**File**: `frontend/src/types/api.ts`

```typescript
// Common API types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: string;
}

// Career Goals types
export interface CareerGoal {
  id: number;
  title: string;
  description?: string;
  target_date: string;
  progress_percentage: number;
}

// Avatar types
export interface AvatarData {
  success: boolean;
  avatar_name?: string;
  avatar_description?: string;
  avatar_image_url?: string;
}
```

### 3. Enhance ClerkApiService with Types
**File**: `frontend/src/services/api.ts`

Add generic type support:
```typescript
class ClerkApiService {
  async request<T>(
    endpoint: string, 
    options?: RequestInit & { token?: string }
  ): Promise<ApiResponse<T>> {
    // existing implementation with type safety
  }

  // Type-safe methods
  async getCareerGoals(token: string): Promise<ApiResponse<CareerGoal[]>> {
    return this.request<CareerGoal[]>('/api/v1/career-goals', {
      method: 'GET',
      token
    });
  }

  async getAvatarData(token: string): Promise<ApiResponse<AvatarData>> {
    return this.request<AvatarData>('/api/v1/avatar/me', {
      method: 'GET', 
      token
    });
  }
}
```

### 4. Add Runtime Validation
**File**: `frontend/src/utils/validation.ts`

Simple validation helpers:
```typescript
export function validateApiResponse<T>(
  response: any,
  requiredFields: (keyof T)[]
): T {
  for (const field of requiredFields) {
    if (!(field in response)) {
      throw new Error(`Missing required field: ${String(field)}`);
    }
  }
  return response as T;
}

// Usage in ClerkApiService
const validated = validateApiResponse<CareerGoal>(response, [
  'id', 'title', 'target_date', 'progress_percentage'
]);
```

## Implementation Prompt for Agent

```
Task: Add TypeScript validation to API client

Instructions:
1. Create frontend/src/types/api.ts with common API types
2. Generate types from backend OpenAPI spec (add npm script)
3. Enhance ClerkApiService with generic types:
   - Add ApiResponse<T> return types
   - Add type-safe methods for career goals and avatar
   - Maintain existing functionality

4. Add basic runtime validation in frontend/src/utils/validation.ts
5. Update migrated services to use typed methods

Requirements:
- All API calls must be type-safe
- Keep existing method signatures working
- Add validation for critical fields
- Generate types from running backend at localhost:8000

Test: Verify TypeScript compilation and runtime validation works.
```

## Success Criteria
- [ ] TypeScript types generated from backend OpenAPI
- [ ] ClerkApiService has generic type support
- [ ] Type-safe methods for career goals and avatar APIs
- [ ] Basic runtime validation for API responses  
- [ ] No TypeScript compilation errors
- [ ] Services use typed API methods
- [ ] Validation catches malformed responses