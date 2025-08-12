# Agent Prompt: Module A - Core Token Cache Service

## 🎯 MISSION CRITICAL TASK
You are implementing the **Core Token Cache Service** - the foundation that will eliminate the authentication bottleneck causing 2-5 second delays on every user interaction in the Orientor Platform.

## 🚨 CRITICAL PROBLEM TO SOLVE
The chat interface currently makes **8 separate `getToken()` calls** per user interaction:
```typescript
// CURRENT PROBLEM (ChatInterface.tsx):
const token = await getToken(); // Line 194 - Message sending
const token = await getToken(); // Line 309 - File upload  
const token = await getToken(); // Line 359 - Fallback token
const token = await getToken(); // Line 406 - Stream init
const token = await getToken(); // Line 709 - Save conversation
const token = await getToken(); // Line 739 - Delete conversation  
const token = await getToken(); // Line 761 - Share conversation
const token = await getToken(); // Line 811 - Export conversation
```
**Impact**: 410-1400ms delay per user action, poor user experience

## 🎯 YOUR SOLUTION TARGET
Create a TokenCacheService that reduces this to **1 cached token** per session:
```typescript
// YOUR TARGET SOLUTION:
const token = await tokenCacheService.getToken(); // <10ms cached retrieval
// Same token reused for all 8 operations = 87.5% reduction in auth calls
```

## 📋 IMPLEMENTATION REQUIREMENTS

### 1. Create Core TokenCacheService
**File**: `frontend/src/services/auth/TokenCacheService.ts`

**Required Interface**:
```typescript
interface TokenCacheService {
  // Core functionality
  getToken(template?: string): Promise<string | null>
  invalidateToken(template?: string): void
  refreshToken(template?: string): Promise<string | null>
  
  // Performance features
  getCacheStatus(): Record<string, any>
  getMetrics(): TokenCacheMetrics
  
  // Lifecycle
  destroy(): void
}

interface TokenCacheMetrics {
  hitRate: number;
  missRate: number;
  averageFetchTime: number;
  averageCacheTime: number;
  errorRate: number;
  refreshCount: number;
}
```

### 2. Required Features
```typescript
✅ MUST IMPLEMENT:
├── Token caching with expiry (5-minute default)
├── Automatic refresh at 80% token lifetime
├── Request batching (prevent duplicate simultaneous requests)
├── Retry logic with exponential backoff (3 attempts)
├── Performance metrics collection
├── Error handling and recovery
├── Memory-efficient cache management
└── Integration with @clerk/nextjs useAuth hook

⚡ PERFORMANCE TARGETS:
├── Cache hit rate: >95%
├── Cache retrieval: <10ms
├── Network fetch: <100ms (when cache miss)
├── Memory usage: <5MB
└── Error rate: <0.1%
```

### 3. Implementation Strategy
```typescript
// Use this exact pattern for Clerk integration:
import { useAuth } from '@clerk/nextjs';

// In your service:
const { getToken } = useAuth();
const token = await getToken(options);

// NEVER use localStorage.getItem('access_token')
// ALWAYS use Clerk's getToken() method
```

### 4. Required Testing
Create comprehensive tests in `frontend/src/services/auth/__tests__/`:
```typescript
✅ REQUIRED TESTS:
├── Token caching and retrieval
├── Cache expiry and refresh
├── Request batching functionality
├── Error handling and retry logic
├── Performance benchmarks (<10ms cache hits)
├── Memory leak prevention
├── Concurrent request handling
└── Cache invalidation scenarios
```

## 🔧 DETAILED IMPLEMENTATION STEPS

### Step 1: Basic Cache Implementation
```typescript
// Start with this structure:
export class TokenCacheService {
  private cache: Map<string, CachedToken> = new Map();
  private pendingRequests: Map<string, Promise<string | null>> = new Map();
  private config: TokenCacheConfig;
  private metrics: TokenCacheMetrics;

  constructor(config: Partial<TokenCacheConfig> = {}) {
    // Initialize with performance-focused defaults
  }

  async getToken(templateName: string = 'default'): Promise<string | null> {
    // 1. Check cache first (target <10ms)
    // 2. Handle pending requests (batch duplicates)
    // 3. Fetch from Clerk if needed
    // 4. Update metrics
  }
}
```

### Step 2: Add Clerk Integration
```typescript
// Critical: Use ONLY Clerk authentication
private async fetchTokenFromClerk(templateName: string): Promise<string | null> {
  const { getToken } = useAuth();
  const options = templateName !== 'default' ? { template: templateName } : undefined;
  return await getToken(options);
}

// NEVER DO THIS:
// const token = localStorage.getItem('access_token'); // ❌ FORBIDDEN
```

### Step 3: Implement Performance Features
```typescript
// Add these performance optimizations:
├── Request deduplication for simultaneous calls
├── Proactive refresh before expiry
├── Background token maintenance
├── Metrics collection and reporting
└── Memory-efficient cache cleanup
```

### Step 4: Create React Hook Integration
**File**: `frontend/src/hooks/useOptimizedAuth.ts`
```typescript
export function useOptimizedAuth() {
  const { isLoaded, isSignedIn, user } = useAuth();
  
  const getOptimizedToken = useCallback(async (template?: string) => {
    return await tokenCacheService.getToken(template);
  }, []);

  return {
    isAuthenticated: isLoaded && isSignedIn,
    isLoading: !isLoaded,
    user,
    getOptimizedToken, // This replaces direct getToken() calls
    // ... other optimized methods
  };
}
```

## 📊 SUCCESS VALIDATION

### Performance Benchmarks
```typescript
// Your implementation MUST achieve:
const performanceTests = {
  cacheHitTime: '<10ms',           // Cached token retrieval
  networkFetchTime: '<100ms',     // Fresh token fetch
  cacheHitRate: '>95%',          // After warm-up period
  memoryUsage: '<5MB',           // Total cache memory
  errorRate: '<0.1%',            // Failed token requests
  concurrentRequests: '100+',     // Simultaneous request handling
};
```

### Integration Test
```typescript
// Test this exact scenario (ChatInterface.tsx simulation):
describe('ChatInterface Token Usage', () => {
  it('should reduce 8 token calls to 1 cached token', async () => {
    const service = new TokenCacheService();
    
    // Simulate 8 rapid token requests (like ChatInterface)
    const tokenPromises = [
      service.getToken(), // Message sending
      service.getToken(), // File upload
      service.getToken(), // Fallback
      service.getToken(), // Stream init
      service.getToken(), // Save conversation
      service.getToken(), // Delete conversation
      service.getToken(), // Share conversation
      service.getToken(), // Export conversation
    ];
    
    const tokens = await Promise.all(tokenPromises);
    
    // All should be the same cached token
    expect(new Set(tokens).size).toBe(1);
    
    // Cache hit rate should be 87.5% (7 of 8 calls were cache hits)
    expect(service.getMetrics().hitRate).toBeGreaterThan(0.85);
  });
});
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve Before Completion:
- [ ] **>95% cache hit rate** in testing environment
- [ ] **<10ms average** cache retrieval time
- [ ] **87.5% reduction** in actual token API calls
- [ ] **Zero memory leaks** over 1000+ operations
- [ ] **100% test coverage** for core functionality
- [ ] **Successful integration** with @clerk/nextjs
- [ ] **Performance benchmarks** documented and met

### Integration Readiness:
- [ ] Ready for Module B (EnhancedAuthContext) integration
- [ ] Compatible with existing Clerk authentication flow
- [ ] Backward compatible (graceful fallback to direct getToken)
- [ ] Production-ready error handling and monitoring

## 📖 REFERENCE DOCUMENTATION
Complete technical specifications available in:
`/docs/api-clerk-enhanced.md/plan/phase-1-token-caching/module-a-core-cache.md`

## 🔄 REPORTING FORMAT
```
📊 MODULE A PROGRESS REPORT
⏱️ STATUS: [In Progress/Completed/Blocked]
🎯 IMPLEMENTATION: [X/8 core features completed]
📈 PERFORMANCE: 
  ├── Cache hit rate: X%
  ├── Cache retrieval time: Xms
  ├── Memory usage: XMB
  └── Error rate: X%
🧪 TESTING: [X/Y test suites passing]
🚨 BLOCKERS: [Any issues or dependencies]
🔄 NEXT: [Ready for Module B integration / Additional work needed]
```

**START IMMEDIATELY** - This is the foundation for the entire optimization plan. Module B depends on your completion!

---

**REMINDER**: 🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
Never use localStorage for tokens, always use Clerk's getToken() method!