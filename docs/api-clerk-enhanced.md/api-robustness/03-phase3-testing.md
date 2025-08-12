# Phase 3: Basic Testing

## Objective
Add essential tests to ensure API reliability and catch regressions.

## Current State
- No API contract tests
- No error handling tests
- No performance monitoring

## Tasks

### 1. Add API Contract Tests
**File**: `frontend/src/__tests__/api/clerkApiService.test.ts`

```typescript
import { clerkApiService } from '../../services/api';

describe('ClerkApiService', () => {
  const mockToken = 'test-token';

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  test('getCareerGoals returns typed response', async () => {
    const mockResponse = {
      data: [{ id: 1, title: 'Test Goal', progress_percentage: 50 }]
    };
    
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const result = await clerkApiService.getCareerGoals(mockToken);
    expect(result.data[0]).toHaveProperty('id');
    expect(result.data[0]).toHaveProperty('title');
  });

  test('handles 401 errors correctly', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 401
    });

    await expect(
      clerkApiService.getCareerGoals(mockToken)
    ).rejects.toThrow('Authentication required');
  });
});
```

### 2. Add Error Handling Tests
**File**: `frontend/src/__tests__/api/errorHandling.test.ts`

```typescript
import { clerkApiService } from '../../services/api';

describe('API Error Handling', () => {
  test('redirects to /sign-in on 401', async () => {
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true
    });

    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 401
    });

    try {
      await clerkApiService.request('/test', { token: 'invalid' });
    } catch (error) {
      expect(window.location.href).toBe('/sign-in');
    }
  });

  test('handles network errors gracefully', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

    await expect(
      clerkApiService.request('/test', { token: 'valid' })
    ).rejects.toThrow('Network error');
  });
});
```

### 3. Add Performance Monitoring
**File**: `frontend/src/utils/performance.ts`

```typescript
export class ApiPerformanceMonitor {
  private static metrics: Map<string, number[]> = new Map();

  static recordApiCall(endpoint: string, duration: number) {
    if (!this.metrics.has(endpoint)) {
      this.metrics.set(endpoint, []);
    }
    this.metrics.get(endpoint)!.push(duration);
  }

  static getAverageTime(endpoint: string): number {
    const times = this.metrics.get(endpoint) || [];
    return times.reduce((a, b) => a + b, 0) / times.length;
  }

  static logSlowCalls(threshold: number = 2000) {
    this.metrics.forEach((times, endpoint) => {
      const avg = this.getAverageTime(endpoint);
      if (avg > threshold) {
        console.warn(`Slow API call: ${endpoint} (${avg}ms average)`);
      }
    });
  }
}

// Integration in ClerkApiService
export class ClerkApiService {
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const startTime = performance.now();
    
    try {
      const result = await this.makeRequest<T>(endpoint, options);
      const duration = performance.now() - startTime;
      ApiPerformanceMonitor.recordApiCall(endpoint, duration);
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      ApiPerformanceMonitor.recordApiCall(endpoint, duration);
      throw error;
    }
  }
}
```

### 4. Add Test Configuration
**File**: `frontend/jest.config.js`

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],
  testMatch: ['**/__tests__/**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  }
};
```

**File**: `frontend/src/__tests__/setup.ts`

```typescript
// Mock Clerk hooks
jest.mock('@clerk/nextjs', () => ({
  useAuth: () => ({
    getToken: jest.fn().mockResolvedValue('mock-token'),
    isSignedIn: true,
    isLoaded: true
  })
}));

// Mock window.location
Object.defineProperty(window, 'location', {
  value: { href: '' },
  writable: true
});
```

## Implementation Prompt for Agent

```
Task: Add basic testing for API client

Instructions:
1. Create test files:
   - frontend/src/__tests__/api/clerkApiService.test.ts
   - frontend/src/__tests__/api/errorHandling.test.ts
   - frontend/src/__tests__/setup.ts

2. Add performance monitoring:
   - frontend/src/utils/performance.ts
   - Integrate with ClerkApiService

3. Configure Jest:
   - frontend/jest.config.js
   - Add test scripts to package.json

4. Write tests for:
   - API contract validation
   - Error handling (401 -> /sign-in redirect)
   - Network error handling
   - Performance monitoring

Requirements:
- Mock Clerk hooks properly
- Test authentication error redirects to '/sign-in'
- Verify API response types
- Monitor slow API calls (>2s)

Test: Run npm test and verify all tests pass.
```

## Success Criteria
- [ ] Contract tests verify API response structure
- [ ] Error handling tests confirm 401 redirects to '/sign-in'
- [ ] Performance monitoring tracks API call times
- [ ] Jest configuration works with TypeScript
- [ ] All tests pass without errors
- [ ] Slow API calls are logged (>2s)
- [ ] Network errors are handled gracefully