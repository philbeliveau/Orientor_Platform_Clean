# Agent Prompt: Module B - Enhanced Authentication Context

## 🎯 MISSION CRITICAL TASK
You are implementing the **Enhanced Authentication Context** that will centralize auth state management and eliminate redundant authentication checks across 150+ components in the Orientor Platform.

## 🚨 CRITICAL PROBLEM TO SOLVE
Currently, **every component** implements its own authentication logic:
```typescript
// CURRENT PROBLEM (repeated in 150+ components):
import { useAuth, useUser } from '@clerk/nextjs';

function MyComponent() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!isLoaded) return; // Synchronous blocking
    if (!isSignedIn) {
      router.push('/sign-in'); // Repeated redirect logic
      return;
    }
  }, [isLoaded, isSignedIn, router]);

  const handleAction = async () => {
    const token = await getToken(); // No caching, every time
    // ... action logic
  };
}
```
**Impact**: Redundant auth checks, inconsistent error handling, poor performance

## 🎯 YOUR SOLUTION TARGET
Create a centralized authentication context that:
```typescript
// YOUR TARGET SOLUTION:
function MyComponent() {
  const { getOptimizedToken, authMetrics } = useEnhancedAuth();

  const handleAction = async () => {
    const token = await getOptimizedToken(); // Cached, <10ms
    // ... action logic
  };

  return <div>Component content</div>; // No auth boilerplate needed
}

// Apply protection at component level:
export default withAuth(MyComponent);
```

## 📋 IMPLEMENTATION REQUIREMENTS

### 1. Create Enhanced Authentication Context
**File**: `frontend/src/contexts/EnhancedAuthContext.tsx`

**Required Interface**:
```typescript
interface EnhancedAuthState {
  // Core authentication state
  isAuthenticated: boolean;
  isLoading: boolean;
  user: ClerkUser | null;
  
  // Performance state
  authMetrics: AuthMetrics;
  cacheStatus: CacheStatus;
  
  // Enhanced functionality
  getOptimizedToken: (template?: string) => Promise<string | null>;
  refreshAuth: () => Promise<void>;
  prefetchAuth: () => Promise<void>;
  
  // Error handling
  authError: AuthError | null;
  retryAuth: () => Promise<void>;
}

interface AuthMetrics {
  totalAuthCalls: number;
  cacheHitRate: number;
  averageAuthTime: number;
  errorRate: number;
  lastAuthTime: Date | null;
}
```

### 2. Required Features
```typescript
✅ MUST IMPLEMENT:
├── Integration with Module A (TokenCacheService)
├── Centralized auth state management
├── Automatic redirect handling
├── Performance metrics collection
├── Error boundary integration
├── Loading state optimization
├── Token prefetching capabilities
└── HOC for component protection

⚡ PERFORMANCE TARGETS:
├── Context render time: <5ms
├── Token retrieval: <10ms (via TokenCacheService)
├── Auth state consistency: 100%
├── Memory usage: <2MB
└── Re-render frequency: <10/minute per component
```

### 3. Integration with Module A
```typescript
// CRITICAL: Must integrate with TokenCacheService
import { tokenCacheService } from '../services/auth/TokenCacheService';

const getOptimizedToken = useCallback(async (template?: string) => {
  // Use the TokenCacheService from Module A
  return await tokenCacheService.getToken(template);
}, []);
```

### 4. Required Components to Create

#### EnhancedAuthProvider
**File**: `frontend/src/contexts/EnhancedAuthContext.tsx`
```typescript
interface EnhancedAuthProviderProps {
  children: React.ReactNode;
  config?: EnhancedAuthConfig;
}

interface EnhancedAuthConfig {
  autoRedirect: boolean;           // Auto-redirect to sign-in
  prefetchEnabled: boolean;        // Prefetch tokens
  metricsEnabled: boolean;         // Collect performance metrics
  retryAttempts: number;           // Max retry attempts
  loadingTimeout: number;          // Max loading state duration
}
```

#### withAuth Higher-Order Component
**File**: `frontend/src/components/auth/withAuth.tsx`
```typescript
interface WithAuthOptions {
  redirectTo?: string;
  loadingComponent?: React.ComponentType;
  errorComponent?: React.ComponentType<{ error: AuthError; retry: () => void }>;
  requireAuth?: boolean;
}

export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: WithAuthOptions = {}
) {
  // Implementation that replaces component-specific auth logic
}
```

#### AuthErrorBoundary Component
**File**: `frontend/src/components/auth/AuthErrorBoundary.tsx`
```typescript
interface AuthErrorBoundaryProps {
  error: AuthError;
  retry: () => void;
}

export function AuthErrorBoundary({ error, retry }: AuthErrorBoundaryProps) {
  // User-friendly error display with retry capability
}
```

#### Performance Monitor Component
**File**: `frontend/src/components/auth/AuthPerformanceMonitor.tsx`
```typescript
// Development-only component for monitoring auth performance
export function AuthPerformanceMonitor({ enabled }: { enabled?: boolean }) {
  // Real-time auth metrics display
}
```

## 🔧 DETAILED IMPLEMENTATION STEPS

### Step 1: Core Context Implementation
```typescript
// Start with this structure:
export function EnhancedAuthProvider({ children, config }: EnhancedAuthProviderProps) {
  const { isLoaded, isSignedIn, getToken: clerkGetToken } = useAuth();
  const { user } = useUser();
  const router = useRouter();
  
  // Local state for metrics and errors
  const [authMetrics, setAuthMetrics] = useState<AuthMetrics>(initializeMetrics());
  const [authError, setAuthError] = useState<AuthError | null>(null);

  // CRITICAL: Integrate with TokenCacheService from Module A
  const getOptimizedToken = useCallback(async (template?: string) => {
    const startTime = performance.now();
    
    try {
      const token = await tokenCacheService.getToken(template);
      
      // Update metrics
      const duration = performance.now() - startTime;
      updateMetrics(prev => ({
        ...prev,
        totalAuthCalls: prev.totalAuthCalls + 1,
        averageAuthTime: (prev.averageAuthTime + duration) / 2,
        lastAuthTime: new Date()
      }));
      
      return token;
    } catch (error) {
      // Handle errors and update metrics
      setAuthError({
        code: 'TOKEN_FETCH_ERROR',
        message: error.message,
        timestamp: new Date(),
        retryable: true
      });
      throw error;
    }
  }, []);

  // ... rest of implementation
}
```

### Step 2: Auto-Redirect Logic
```typescript
// Handle automatic redirects (replace component-specific logic)
useEffect(() => {
  if (!isLoaded) return;

  if (config.autoRedirect && !isSignedIn) {
    const currentPath = window.location.pathname;
    if (!currentPath.startsWith('/sign-in') && !currentPath.startsWith('/sign-up')) {
      router.push('/sign-in'); // ALWAYS use /sign-in, never /login
    }
  }

  // Prefetch token if authenticated
  if (config.prefetchEnabled && isSignedIn) {
    prefetchAuth();
  }
}, [isLoaded, isSignedIn, router, config]);
```

### Step 3: Performance Optimization
```typescript
// Implement smart loading states
const [isInitialized, setIsInitialized] = useState(false);
const loadingStartTime = useRef<number | null>(null);

useEffect(() => {
  if (!isLoaded) {
    loadingStartTime.current = performance.now();
    return;
  }

  if (loadingStartTime.current) {
    const loadTime = performance.now() - loadingStartTime.current;
    updateMetrics(prev => ({
      ...prev,
      averageAuthTime: (prev.averageAuthTime + loadTime) / 2,
      lastAuthTime: new Date()
    }));
  }

  setIsInitialized(true);
}, [isLoaded]);
```

### Step 4: HOC Implementation
```typescript
// Create withAuth HOC to replace component-specific auth logic
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: WithAuthOptions = {}
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading, authError, retryAuth } = useEnhancedAuth();

    if (isLoading) {
      return options.loadingComponent ? 
        <options.loadingComponent /> : 
        <LoadingSpinner />;
    }

    if (authError) {
      return options.errorComponent ? 
        <options.errorComponent error={authError} retry={retryAuth} /> : 
        <AuthErrorBoundary error={authError} retry={retryAuth} />;
    }

    if (options.requireAuth && !isAuthenticated) {
      // Redirect will be handled by context provider
      return <LoadingSpinner />;
    }

    return <Component {...props} />;
  };
}
```

### Step 5: App-Level Integration
**File**: `frontend/src/app/layout.tsx`
```typescript
// Integrate into the app root
import { ClerkProvider } from '@clerk/nextjs';
import { EnhancedAuthProvider } from '../contexts/EnhancedAuthContext';
import { AuthPerformanceMonitor } from '../components/auth/AuthPerformanceMonitor';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <ClerkProvider>
          <EnhancedAuthProvider
            config={{
              autoRedirect: true,
              prefetchEnabled: true,
              metricsEnabled: process.env.NODE_ENV === 'development',
              retryAttempts: 3,
              loadingTimeout: 10000
            }}
          >
            {children}
            <AuthPerformanceMonitor enabled={process.env.NODE_ENV === 'development'} />
          </EnhancedAuthProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
```

## 📊 SUCCESS VALIDATION

### Performance Benchmarks
```typescript
// Your implementation MUST achieve:
const performanceTests = {
  contextRenderTime: '<5ms',       // Context provider render
  tokenRetrieval: '<10ms',         // Via TokenCacheService
  stateConsistency: '100%',        // Auth state across components
  memoryUsage: '<2MB',            // Context state memory
  reRenderFreq: '<10/min',        // Component re-renders
};
```

### Component Migration Test
```typescript
// Test component migration from old to new pattern:
describe('Component Auth Migration', () => {
  it('should eliminate component-specific auth boilerplate', () => {
    // Before: Component has 20+ lines of auth logic
    // After: Component uses withAuth HOC, zero auth boilerplate
    
    const OriginalComponent = () => {
      const { getOptimizedToken } = useEnhancedAuth();
      
      const handleAction = async () => {
        const token = await getOptimizedToken();
        // Action logic only
      };
      
      return <div>Component content</div>;
    };
    
    const ProtectedComponent = withAuth(OriginalComponent);
    
    // Should render without any auth-related code in component
    render(<ProtectedComponent />);
    expect(screen.getByText('Component content')).toBeInTheDocument();
  });
});
```

### Integration Test with Module A
```typescript
// Critical: Test integration with TokenCacheService
describe('TokenCacheService Integration', () => {
  it('should use TokenCacheService for token retrieval', async () => {
    const { getOptimizedToken } = renderHook(() => useEnhancedAuth()).result.current;
    
    // Spy on TokenCacheService
    const spy = jest.spyOn(tokenCacheService, 'getToken');
    
    await getOptimizedToken();
    
    expect(spy).toHaveBeenCalledWith(undefined);
    expect(spy).toHaveReturnedWith(expect.any(String));
  });
});
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve Before Completion:
- [ ] **Successful integration** with Module A (TokenCacheService)
- [ ] **<5ms context render time** consistently
- [ ] **100% elimination** of component-specific auth boilerplate
- [ ] **Centralized error handling** for all auth scenarios
- [ ] **Performance metrics** collection and reporting
- [ ] **HOC pattern** working for component protection
- [ ] **Auto-redirect functionality** replacing manual redirects

### Component Integration Readiness:
- [ ] Ready for Module G (Chat interface) to use enhanced context
- [ ] Compatible with existing Clerk authentication flow
- [ ] Performance monitoring enabled for development
- [ ] Error boundaries working for all error scenarios

## 🔄 DEPENDENCIES
**CRITICAL**: This module DEPENDS on Module A (TokenCacheService) completion.
- Wait for Module A agent to complete TokenCacheService
- Import and integrate tokenCacheService singleton
- Test integration thoroughly before proceeding

## 📖 REFERENCE DOCUMENTATION
Complete technical specifications available in:
`/docs/api-clerk-enhanced.md/plan/phase-1-token-caching/module-b-auth-context.md`

## 🔄 REPORTING FORMAT
```
📊 MODULE B PROGRESS REPORT
⏱️ STATUS: [Waiting for Module A/In Progress/Completed/Blocked]
🎯 IMPLEMENTATION: [X/6 core components completed]
📈 PERFORMANCE: 
  ├── Context render time: Xms
  ├── Token retrieval time: Xms
  ├── Memory usage: XMB
  └── Re-render frequency: X/min
🧪 TESTING: [X/Y test suites passing]
🔗 INTEGRATION: Module A TokenCacheService - [Ready/Testing/Complete]
🚨 BLOCKERS: [Any issues or dependencies]
🔄 NEXT: [Ready for Module G integration / Additional work needed]
```

**WAIT FOR MODULE A COMPLETION** before starting - TokenCacheService integration is critical!

---

**REMINDER**: 🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
Always redirect to /sign-in, never /login!