# Module B: Enhanced Authentication Context Provider

## Overview
Enhances the existing Clerk authentication context with intelligent caching, performance monitoring, and centralized auth state management to eliminate redundant authentication checks across components.

## Current Problem Analysis

### Existing Authentication Usage
```typescript
// CURRENT PATTERN (scattered across 150+ components)
import { useAuth, useUser } from '@clerk/nextjs';

function MyComponent() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const { user } = useUser();
  
  useEffect(() => {
    if (!isLoaded) return; // Synchronous blocking
    
    if (!isSignedIn) {
      router.push('/sign-in'); // Repeated redirect logic
      return;
    }
    
    // Component-specific auth logic
  }, [isLoaded, isSignedIn, router]);
  
  const handleAction = async () => {
    const token = await getToken(); // No caching, every time
    // ... action logic
  };
}
```

### Problems Identified
- **150+ components** with individual auth state management
- **Repeated auth checks** on every component render
- **No centralized loading state** coordination
- **Inconsistent error handling** across components
- **No performance monitoring** of auth operations

## Solution: Enhanced Authentication Context

### Architecture
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

interface CacheStatus {
  tokenCached: boolean;
  tokenExpiry: Date | null;
  userDataCached: boolean;
  cacheSize: number;
}

interface AuthError {
  code: string;
  message: string;
  timestamp: Date;
  retryable: boolean;
}
```

### Implementation

#### 1. Enhanced Authentication Context
```typescript
// File: frontend/src/contexts/EnhancedAuthContext.tsx

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { tokenCacheService } from '../services/auth/TokenCacheService';

const EnhancedAuthContext = createContext<EnhancedAuthState | null>(null);

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

const DEFAULT_CONFIG: EnhancedAuthConfig = {
  autoRedirect: true,
  prefetchEnabled: true,
  metricsEnabled: true,
  retryAttempts: 3,
  loadingTimeout: 10000 // 10 seconds
};

export function EnhancedAuthProvider({ children, config = DEFAULT_CONFIG }: EnhancedAuthProviderProps) {
  const router = useRouter();
  const { isLoaded, isSignedIn, getToken: clerkGetToken } = useAuth();
  const { user } = useUser();
  
  // Local state
  const [authMetrics, setAuthMetrics] = useState<AuthMetrics>(initializeMetrics());
  const [authError, setAuthError] = useState<AuthError | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Refs for performance tracking
  const metricsRef = useRef<AuthMetrics>(authMetrics);
  const loadingStartTime = useRef<number | null>(null);

  // Initialize auth state
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
      loadingStartTime.current = null;
    }

    setIsInitialized(true);

    // Auto-redirect logic
    if (config.autoRedirect && !isSignedIn) {
      const currentPath = window.location.pathname;
      if (!currentPath.startsWith('/sign-in') && !currentPath.startsWith('/sign-up')) {
        router.push('/sign-in');
      }
    }

    // Prefetch token if authenticated
    if (config.prefetchEnabled && isSignedIn) {
      prefetchAuth();
    }
  }, [isLoaded, isSignedIn, router, config]);

  // Loading timeout protection
  useEffect(() => {
    if (!isLoaded) {
      const timeout = setTimeout(() => {
        setAuthError({
          code: 'LOADING_TIMEOUT',
          message: 'Authentication loading timeout',
          timestamp: new Date(),
          retryable: true
        });
      }, config.loadingTimeout);

      return () => clearTimeout(timeout);
    }
  }, [isLoaded, config.loadingTimeout]);

  /**
   * Optimized token retrieval with caching and metrics
   */
  const getOptimizedToken = useCallback(async (template?: string): Promise<string | null> => {
    const startTime = performance.now();
    
    try {
      updateMetrics(prev => ({ ...prev, totalAuthCalls: prev.totalAuthCalls + 1 }));
      
      const token = await tokenCacheService.getToken(template);
      
      const duration = performance.now() - startTime;
      updateMetrics(prev => ({
        ...prev,
        averageAuthTime: (prev.averageAuthTime + duration) / 2,
        cacheHitRate: tokenCacheService.getMetrics().hitRate,
        lastAuthTime: new Date()
      }));
      
      // Clear any existing errors on success
      if (authError) {
        setAuthError(null);
      }
      
      return token;
    } catch (error) {
      const duration = performance.now() - startTime;
      updateMetrics(prev => ({
        ...prev,
        errorRate: Math.min(prev.errorRate + 0.01, 1),
        averageAuthTime: (prev.averageAuthTime + duration) / 2
      }));
      
      setAuthError({
        code: 'TOKEN_FETCH_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
        retryable: true
      });
      
      throw error;
    }
  }, [authError]);

  /**
   * Refresh authentication state and clear caches
   */
  const refreshAuth = useCallback(async (): Promise<void> => {
    try {
      tokenCacheService.invalidateToken();
      await tokenCacheService.getToken();
      setAuthError(null);
      updateMetrics(prev => ({
        ...prev,
        lastAuthTime: new Date()
      }));
    } catch (error) {
      setAuthError({
        code: 'REFRESH_ERROR',
        message: error instanceof Error ? error.message : 'Refresh failed',
        timestamp: new Date(),
        retryable: true
      });
    }
  }, []);

  /**
   * Prefetch authentication data for performance
   */
  const prefetchAuth = useCallback(async (): Promise<void> => {
    if (!isSignedIn) return;
    
    try {
      // Prefetch default token
      await tokenCacheService.getToken();
      
      // Prefetch common templates if needed
      const commonTemplates = ['default', 'api'];
      await Promise.all(
        commonTemplates.map(template => 
          tokenCacheService.getToken(template).catch(() => {
            // Ignore prefetch errors
          })
        )
      );
    } catch (error) {
      // Prefetch errors are non-critical
      console.warn('Auth prefetch failed:', error);
    }
  }, [isSignedIn]);

  /**
   * Retry authentication after error
   */
  const retryAuth = useCallback(async (): Promise<void> => {
    if (!authError?.retryable) return;
    
    setAuthError(null);
    try {
      await refreshAuth();
    } catch (error) {
      // Error will be set by refreshAuth
    }
  }, [authError, refreshAuth]);

  /**
   * Update metrics state
   */
  const updateMetrics = useCallback((updater: (prev: AuthMetrics) => AuthMetrics) => {
    if (!config.metricsEnabled) return;
    
    setAuthMetrics(prev => {
      const updated = updater(prev);
      metricsRef.current = updated;
      return updated;
    });
  }, [config.metricsEnabled]);

  /**
   * Get current cache status
   */
  const getCacheStatus = useCallback((): CacheStatus => {
    const cacheStatus = tokenCacheService.getCacheStatus();
    const defaultCache = cacheStatus['default'];
    
    return {
      tokenCached: !!defaultCache,
      tokenExpiry: defaultCache?.expiresAt || null,
      userDataCached: !!user,
      cacheSize: Object.keys(cacheStatus).length
    };
  }, [user]);

  // Context value
  const contextValue: EnhancedAuthState = {
    // Core authentication state
    isAuthenticated: isLoaded && isSignedIn,
    isLoading: !isLoaded && !authError,
    user,
    
    // Performance state
    authMetrics,
    cacheStatus: getCacheStatus(),
    
    // Enhanced functionality
    getOptimizedToken,
    refreshAuth,
    prefetchAuth,
    
    // Error handling
    authError,
    retryAuth
  };

  return (
    <EnhancedAuthContext.Provider value={contextValue}>
      {children}
    </EnhancedAuthContext.Provider>
  );
}

/**
 * Hook to use enhanced authentication context
 */
export function useEnhancedAuth(): EnhancedAuthState {
  const context = useContext(EnhancedAuthContext);
  if (!context) {
    throw new Error('useEnhancedAuth must be used within an EnhancedAuthProvider');
  }
  return context;
}

/**
 * Initialize metrics object
 */
function initializeMetrics(): AuthMetrics {
  return {
    totalAuthCalls: 0,
    cacheHitRate: 0,
    averageAuthTime: 0,
    errorRate: 0,
    lastAuthTime: null
  };
}
```

#### 2. Higher-Order Component for Auth Protection
```typescript
// File: frontend/src/components/auth/withAuth.tsx

import React from 'react';
import { useEnhancedAuth } from '../../contexts/EnhancedAuthContext';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { AuthErrorBoundary } from './AuthErrorBoundary';

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
  const {
    redirectTo = '/sign-in',
    loadingComponent: LoadingComponent = LoadingSpinner,
    errorComponent: ErrorComponent = AuthErrorBoundary,
    requireAuth = true
  } = options;

  return function AuthenticatedComponent(props: P) {
    const { 
      isAuthenticated, 
      isLoading, 
      authError, 
      retryAuth 
    } = useEnhancedAuth();

    // Show loading state
    if (isLoading) {
      return <LoadingComponent />;
    }

    // Show error state
    if (authError) {
      return <ErrorComponent error={authError} retry={retryAuth} />;
    }

    // Redirect if authentication required but not authenticated
    if (requireAuth && !isAuthenticated) {
      // Redirect will be handled by context provider
      return <LoadingComponent />;
    }

    // Render protected component
    return <Component {...props} />;
  };
}
```

#### 3. Authentication Error Boundary
```typescript
// File: frontend/src/components/auth/AuthErrorBoundary.tsx

import React from 'react';
import { AuthError } from '../../contexts/EnhancedAuthContext';

interface AuthErrorBoundaryProps {
  error: AuthError;
  retry: () => void;
}

export function AuthErrorBoundary({ error, retry }: AuthErrorBoundaryProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-gray-900">
              Authentication Error
            </h3>
          </div>
        </div>
        
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            {error.message}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Error Code: {error.code}
          </p>
          <p className="text-xs text-gray-400">
            Time: {error.timestamp.toLocaleString()}
          </p>
        </div>
        
        {error.retryable && (
          <div className="flex space-x-3">
            <button
              onClick={retry}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Retry
            </button>
            <button
              onClick={() => window.location.href = '/sign-in'}
              className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Sign In Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

#### 4. Performance Monitoring Component
```typescript
// File: frontend/src/components/auth/AuthPerformanceMonitor.tsx

import React, { useState, useEffect } from 'react';
import { useEnhancedAuth } from '../../contexts/EnhancedAuthContext';

interface AuthPerformanceMonitorProps {
  enabled?: boolean;
  updateInterval?: number;
}

export function AuthPerformanceMonitor({ 
  enabled = true, 
  updateInterval = 5000 
}: AuthPerformanceMonitorProps) {
  const { authMetrics, cacheStatus } = useEnhancedAuth();
  const [showDetails, setShowDetails] = useState(false);

  if (!enabled || process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-3 rounded-lg shadow-lg text-xs">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center space-x-2 hover:bg-gray-800 px-2 py-1 rounded"
      >
        <span>Auth Performance</span>
        <span className={`w-2 h-2 rounded-full ${
          authMetrics.errorRate < 0.05 ? 'bg-green-400' : 'bg-red-400'
        }`}></span>
      </button>
      
      {showDetails && (
        <div className="mt-2 space-y-1 min-w-[200px]">
          <div>Cache Hit Rate: {(authMetrics.cacheHitRate * 100).toFixed(1)}%</div>
          <div>Avg Auth Time: {authMetrics.averageAuthTime.toFixed(1)}ms</div>
          <div>Total Calls: {authMetrics.totalAuthCalls}</div>
          <div>Error Rate: {(authMetrics.errorRate * 100).toFixed(2)}%</div>
          <div>Token Cached: {cacheStatus.tokenCached ? '✓' : '✗'}</div>
          {cacheStatus.tokenExpiry && (
            <div>Expires: {new Date(cacheStatus.tokenExpiry).toLocaleTimeString()}</div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Usage Examples

#### Before (Component-specific auth)
```typescript
// CURRENT PATTERN (repeated in 150+ components)
import { useAuth, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

function MyComponent() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.push('/sign-in');
      return;
    }
  }, [isLoaded, isSignedIn, router]);

  const handleAction = async () => {
    const token = await getToken(); // No caching
    // ... action logic
  };

  if (!isLoaded) return <div>Loading...</div>;
  if (!isSignedIn) return null;

  return <div>Component content</div>;
}
```

#### After (Enhanced context usage)
```typescript
// OPTIMIZED PATTERN (centralized auth)
import { useEnhancedAuth } from '../contexts/EnhancedAuthContext';
import { withAuth } from '../components/auth/withAuth';

function MyComponent() {
  const { getOptimizedToken } = useEnhancedAuth();

  const handleAction = async () => {
    const token = await getOptimizedToken(); // Cached
    // ... action logic
  };

  return <div>Component content</div>;
}

// Apply authentication protection
export default withAuth(MyComponent);
```

### App-Level Integration
```typescript
// File: frontend/src/app/layout.tsx (or _app.tsx for Pages Router)

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

## Testing Strategy

### Context Testing
```typescript
// File: frontend/src/contexts/__tests__/EnhancedAuthContext.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { EnhancedAuthProvider, useEnhancedAuth } from '../EnhancedAuthContext';

const TestComponent = () => {
  const { isAuthenticated, getOptimizedToken, authMetrics } = useEnhancedAuth();
  
  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'not authenticated'}</div>
      <div data-testid="cache-hit-rate">{authMetrics.cacheHitRate}</div>
      <button 
        onClick={() => getOptimizedToken()}
        data-testid="get-token"
      >
        Get Token
      </button>
    </div>
  );
};

describe('EnhancedAuthContext', () => {
  it('should provide authentication state', async () => {
    render(
      <EnhancedAuthProvider>
        <TestComponent />
      </EnhancedAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toBeInTheDocument();
    });
  });

  it('should track performance metrics', async () => {
    render(
      <EnhancedAuthProvider config={{ metricsEnabled: true }}>
        <TestComponent />
      </EnhancedAuthProvider>
    );

    const getTokenButton = screen.getByTestId('get-token');
    fireEvent.click(getTokenButton);

    await waitFor(() => {
      const hitRateElement = screen.getByTestId('cache-hit-rate');
      expect(hitRateElement).toHaveTextContent(/\d+/);
    });
  });
});
```

## Performance Targets

### Context Performance
- **Context render time**: <5ms
- **Token retrieval**: <10ms (cached), <100ms (network)
- **Memory usage**: <2MB for auth state
- **Re-render frequency**: <10 per minute per component

### User Experience
- **Loading state duration**: <500ms
- **Error recovery time**: <2 seconds
- **Cache hit rate**: >95%
- **Auth state consistency**: 100%

## Integration Dependencies

### Requires (Module A)
- TokenCacheService implementation
- Core caching infrastructure

### Provides to Other Modules
- Centralized auth state management
- Performance metrics collection
- Error handling infrastructure
- Token caching integration

## Deployment Checklist

- [ ] Implement EnhancedAuthContext
- [ ] Create withAuth HOC
- [ ] Add AuthErrorBoundary component
- [ ] Integrate with app layout
- [ ] Update existing components to use enhanced context
- [ ] Add performance monitoring in development
- [ ] Test error scenarios and recovery
- [ ] Validate cache hit rates

## Success Metrics

### Technical Metrics
- **95%+ cache hit rate** for token requests
- **<5ms context render time**
- **100% elimination** of redundant auth checks

### User Experience Metrics
- **Instant auth state** availability
- **Consistent error handling** across all components
- **Performance visibility** in development mode

---

**Dependencies**: Module A (TokenCacheService)
**Estimated Implementation Time**: 1-2 days
**Risk Level**: Medium (affects all components)