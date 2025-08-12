# Implementation Prompts for Agents

## Phase 1 Agent Prompt: Standardize API Client

```
You are implementing Phase 1 of the API reliability enhancement for the Orientor Platform.

TASK: Enhance existing ClerkApiService and migrate 3 core services

CURRENT STATE:
- frontend/src/services/api.ts has ClerkApiService class
- frontend/src/services/avatarService.ts uses direct fetch
- frontend/src/services/careerGoalsService.ts uses manual auth
- frontend/src/services/skillsTreeService.ts uses axios

REQUIREMENTS:
1. Enhance ClerkApiService in frontend/src/services/api.ts:
   - Add comprehensive error handling method
   - Add request interceptor with proper error types
   - Ensure 401 errors redirect to '/sign-in' (NOT '/login')

2. Add ESLint rule in frontend/.eslintrc.json:
   - Prevent direct axios/fetch imports
   - Message: "Use ClerkApiService instead of direct HTTP libraries"

3. Migrate services to use ClerkApiService:
   - avatarService.ts: Replace fetch calls with clerkApiService.request()
   - careerGoalsService.ts: Remove manual auth, use ClerkApiService
   - skillsTreeService.ts: Replace axios with ClerkApiService

AUTHENTICATION REQUIREMENTS (CRITICAL):
✅ CORRECT: const { getToken } = useAuth(); const token = await getToken();
❌ FORBIDDEN: localStorage.getItem('access_token')
✅ REDIRECT: '/sign-in'
❌ FORBIDDEN: '/login'

SUCCESS CRITERIA:
- ClerkApiService has proper error handling
- ESLint prevents direct HTTP library usage
- 3 services migrated successfully
- All services still work (no breaking changes)
- Authentication follows Clerk patterns exactly

DELIVERABLES:
1. Enhanced frontend/src/services/api.ts
2. Updated frontend/.eslintrc.json
3. Migrated frontend/src/services/avatarService.ts
4. Migrated frontend/src/services/careerGoalsService.ts
5. Migrated frontend/src/services/skillsTreeService.ts
```

## Phase 2 Agent Prompt: Add TypeScript Validation

```
You are implementing Phase 2 of the API reliability enhancement for the Orientor Platform.

TASK: Add TypeScript types and validation to API client

PREREQUISITES:
- Phase 1 completed (ClerkApiService enhanced)
- Backend running on localhost:8000 with OpenAPI spec

REQUIREMENTS:
1. Generate API types from backend:
   - Add npm script: "generate-api-types"
   - Fetch from http://localhost:8000/openapi.json
   - Generate TypeScript types

2. Create frontend/src/types/api.ts:
   - ApiResponse<T> interface
   - CareerGoal interface
   - AvatarData interface
   - ApiError interface

3. Enhance ClerkApiService with generics:
   - Add generic type support to request() method
   - Add typed methods: getCareerGoals(), getAvatarData()
   - Maintain existing functionality

4. Add basic runtime validation:
   - frontend/src/utils/validation.ts
   - validateApiResponse() function
   - Validate critical fields

AUTHENTICATION REQUIREMENTS (CRITICAL):
✅ CORRECT: const { getToken } = useAuth(); const token = await getToken();
❌ FORBIDDEN: localStorage.getItem('access_token')
✅ REDIRECT: '/sign-in'
❌ FORBIDDEN: '/login'

SUCCESS CRITERIA:
- TypeScript types generated from backend OpenAPI
- ClerkApiService has generic type support
- Type-safe methods for career goals and avatar
- Runtime validation catches malformed responses
- No TypeScript compilation errors
- Existing functionality preserved

DELIVERABLES:
1. Updated package.json with generate-api-types script
2. frontend/src/types/api.ts with API types
3. Enhanced frontend/src/services/api.ts with generics
4. frontend/src/utils/validation.ts with runtime validation
5. Updated services using typed methods
```

## Phase 3 Agent Prompt: Add Basic Testing

```
You are implementing Phase 3 of the API reliability enhancement for the Orientor Platform.

TASK: Add essential tests for API reliability

PREREQUISITES:
- Phase 1 completed (ClerkApiService standardized)
- Phase 2 completed (TypeScript validation added)

REQUIREMENTS:
1. Setup Jest configuration:
   - frontend/jest.config.js for TypeScript
   - frontend/src/__tests__/setup.ts with Clerk mocks
   - Test scripts in package.json

2. Create API contract tests:
   - frontend/src/__tests__/api/clerkApiService.test.ts
   - Test typed responses
   - Test request/response structure

3. Create error handling tests:
   - frontend/src/__tests__/api/errorHandling.test.ts
   - Test 401 redirects to '/sign-in'
   - Test network error handling

4. Add performance monitoring:
   - frontend/src/utils/performance.ts
   - ApiPerformanceMonitor class
   - Integration with ClerkApiService
   - Log slow calls (>2s)

AUTHENTICATION REQUIREMENTS (CRITICAL):
✅ CORRECT: Mock useAuth() hook properly
✅ TEST: 401 errors redirect to '/sign-in' (NOT '/login')
❌ FORBIDDEN: Any '/login' references in tests

SUCCESS CRITERIA:
- Jest runs TypeScript tests successfully
- Contract tests verify API response types
- Error tests confirm '/sign-in' redirect on 401
- Performance monitoring tracks API call times
- All tests pass without errors
- Slow API calls are logged

DELIVERABLES:
1. frontend/jest.config.js
2. frontend/src/__tests__/setup.ts
3. frontend/src/__tests__/api/clerkApiService.test.ts
4. frontend/src/__tests__/api/errorHandling.test.ts
5. frontend/src/utils/performance.ts
6. Updated package.json with test scripts
```

## Quality Checklist for All Phases

### Authentication Compliance ✅
- [ ] Uses `const { getToken } = useAuth(); const token = await getToken();`
- [ ] Never uses `localStorage.getItem('access_token')`
- [ ] Redirects to `/sign-in` on auth errors
- [ ] Never redirects to `/login`

### Code Quality ✅
- [ ] No breaking changes to existing APIs
- [ ] TypeScript compilation passes
- [ ] ESLint rules enforced
- [ ] All tests pass

### Functionality ✅
- [ ] Avatar service works correctly
- [ ] Career goals service works correctly
- [ ] Skills tree service works correctly
- [ ] Error handling works as expected
- [ ] Performance monitoring active

Use these prompts to implement each phase systematically with focus on Clerk authentication compliance.