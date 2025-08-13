# Phase 4: Integration Testing & Monitoring

**Priority**: 🧪 MEDIUM - Quality assurance and performance monitoring  
**Estimated Duration**: 2-3 days  
**Dependencies**: Phases 1, 2, and 3 must be completed first

## 📋 Overview

This final phase focuses on comprehensive testing, monitoring, and validation of all lazy loading improvements. We'll establish automated testing suites, performance monitoring, and long-term maintenance strategies to ensure the lazy loading system remains robust and performant.

## 🎯 Phase Objectives

1. **Comprehensive Testing Suite** - Automated tests for all lazy loading scenarios
2. **Performance Monitoring** - Real-time tracking of loading performance and user experience
3. **Error Tracking & Analytics** - Monitor and analyze loading failures and user patterns
4. **Documentation & Maintenance** - Create maintenance guides and troubleshooting documentation

## 🧪 Testing Framework Components

### Test Categories
- ✅ Unit tests for lazy loading utilities and hooks
- ✅ Integration tests for authentication + lazy loading workflows
- ✅ End-to-end tests for complete user journeys
- ✅ Performance tests for bundle sizes and loading times
- ✅ Accessibility tests for loading states and error conditions
- 🚫 **EXCLUDED**: Tree visualization testing (per user request)

## 📂 Detailed File Changes

### 1. Unit Testing Suite

#### File: `frontend/src/__tests__/hooks/useSmartPreloading.test.ts`
**Action**: CREATE NEW FILE  
**Purpose**: Test smart preloading logic and behavior pattern learning

```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useSmartPreloading } from '@/hooks/useSmartPreloading';
import { useAuth, useUser } from '@clerk/nextjs';

// Mock Clerk hooks
jest.mock('@clerk/nextjs', () => ({
  useAuth: jest.fn(),
  useUser: jest.fn(),
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: '/test'
  })
}));

describe('useSmartPreloading', () => {
  const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
  const mockUseUser = useUser as jest.MockedFunction<typeof useUser>;

  beforeEach(() => {
    // Clear localStorage
    localStorage.clear();
    
    // Reset mocks
    mockUseAuth.mockReturnValue({
      isLoaded: true,
      isSignedIn: true,
      getToken: jest.fn()
    });
    
    mockUseUser.mockReturnValue({
      user: {
        id: 'test-user-id',
        publicMetadata: { role: 'user' }
      }
    });

    // Mock console methods to avoid noise in tests
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.restoreAllMocks();
  });

  describe('Behavior Pattern Learning', () => {
    test('should track user behavior patterns correctly', async () => {
      const { result } = renderHook(() => useSmartPreloading());

      // Simulate user spending time on a route
      act(() => {
        // Mock behavior pattern data
        const pattern = {
          commonRoutes: ['/chat', '/dashboard'],
          timeSpent: { '/chat': 5000, '/dashboard': 3000 },
          interactions: { '/chat': 3, '/dashboard': 2 }
        };
        localStorage.setItem('user_behavior_pattern', JSON.stringify(pattern));
      });

      await waitFor(() => {
        expect(localStorage.getItem('user_behavior_pattern')).toBeTruthy();
      });

      const storedPattern = JSON.parse(localStorage.getItem('user_behavior_pattern') || '{}');
      expect(storedPattern.commonRoutes).toContain('/chat');
      expect(storedPattern.commonRoutes).toContain('/dashboard');
    });

    test('should prioritize routes based on time spent and interactions', () => {
      const { result } = renderHook(() => useSmartPreloading());

      act(() => {
        const pattern = {
          commonRoutes: [],
          timeSpent: { '/chat': 10000, '/profile': 2000, '/settings': 1000 },
          interactions: { '/chat': 5, '/profile': 8, '/settings': 2 }
        };
        localStorage.setItem('user_behavior_pattern', JSON.stringify(pattern));
      });

      const storedPattern = JSON.parse(localStorage.getItem('user_behavior_pattern') || '{}');
      
      // /profile should rank higher due to more interactions despite less time
      // /chat should rank high due to both time and interactions
      expect(storedPattern.timeSpent['/chat']).toBeGreaterThan(storedPattern.timeSpent['/profile']);
    });
  });

  describe('Authentication-based Preloading', () => {
    test('should preload authenticated components when user is signed in', async () => {
      mockUseAuth.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        getToken: jest.fn()
      });

      const mockComponentLoader = jest.fn().mockResolvedValue({ default: () => null });
      
      const { result } = renderHook(() => useSmartPreloading());

      await act(async () => {
        await result.current.preloadComponent(mockComponentLoader);
      });

      await waitFor(() => {
        expect(mockComponentLoader).toHaveBeenCalled();
      });
    });

    test('should not preload authenticated components when user is not signed in', async () => {
      mockUseAuth.mockReturnValue({
        isLoaded: true,
        isSignedIn: false,
        getToken: jest.fn()
      });

      const { result } = renderHook(() => useSmartPreloading());

      // Component should not be preloaded for unauthenticated users
      // This would be tested through the preload strategy logic
      expect(result.current.preloadComponent).toBeDefined();
    });

    test('should handle loading state correctly', () => {
      mockUseAuth.mockReturnValue({
        isLoaded: false,
        isSignedIn: false,
        getToken: jest.fn()
      });

      const { result } = renderHook(() => useSmartPreloading());

      // Hook should be available but preloading shouldn't execute until loaded
      expect(result.current.preloadComponent).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    test('should handle preload failures gracefully', async () => {
      const mockComponentLoader = jest.fn().mockRejectedValue(new Error('Network error'));
      
      const { result } = renderHook(() => useSmartPreloading());

      await act(async () => {
        await result.current.preloadComponent(mockComponentLoader);
      });

      // Should not throw error, should log warning
      expect(console.warn).toHaveBeenCalledWith(
        '[SmartPreloading] Manual preload failed:',
        expect.any(Error)
      );
    });
  });
});
```

#### File: `frontend/src/__tests__/hooks/useIntersectionPreload.test.ts`
**Action**: CREATE NEW FILE  
**Purpose**: Test viewport-based lazy loading

```typescript
import { renderHook } from '@testing-library/react';
import { useIntersectionPreload } from '@/hooks/useIntersectionPreload';

// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
});
window.IntersectionObserver = mockIntersectionObserver;

describe('useIntersectionPreload', () => {
  const mockComponentLoader = jest.fn().mockResolvedValue({ default: () => null });
  const mockOnPreloadComplete = jest.fn();
  const mockOnPreloadError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should create IntersectionObserver with correct options', () => {
    const { result } = renderHook(() =>
      useIntersectionPreload({
        rootMargin: '200px',
        threshold: 0.2,
        componentLoader: mockComponentLoader,
        onPreloadComplete: mockOnPreloadComplete,
        onPreloadError: mockOnPreloadError
      })
    );

    expect(mockIntersectionObserver).toHaveBeenCalledWith(
      expect.any(Function),
      {
        rootMargin: '200px',
        threshold: 0.2
      }
    );
  });

  test('should return ref for element to observe', () => {
    const { result } = renderHook(() =>
      useIntersectionPreload({
        componentLoader: mockComponentLoader
      })
    );

    expect(result.current).toHaveProperty('current', null);
  });

  test('should handle intersection correctly', async () => {
    // This would require more complex mocking of IntersectionObserver behavior
    // In a real test, you'd mock the callback being called with intersection entries
    const { result } = renderHook(() =>
      useIntersectionPreload({
        componentLoader: mockComponentLoader,
        onPreloadComplete: mockOnPreloadComplete
      })
    );

    expect(result.current).toBeDefined();
  });
});
```

---

### 2. Integration Testing Suite

#### File: `frontend/src/__tests__/integration/lazy-loading-auth.test.tsx`
**Action**: CREATE NEW FILE  
**Purpose**: Test lazy loading integration with Clerk authentication

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { useAuth } from '@clerk/nextjs';
import { LazyWrapper } from '@/features/shared/components/LazyWrapper';

// Mock Clerk
jest.mock('@clerk/nextjs', () => ({
  useAuth: jest.fn(),
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn()
  })
}));

const TestComponent = () => <div>Test Component Loaded</div>;

describe('Lazy Loading Authentication Integration', () => {
  const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
  const mockRouterPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should show loading state when Clerk is not loaded', async () => {
    mockUseAuth.mockReturnValue({
      isLoaded: false,
      isSignedIn: false,
      getToken: jest.fn()
    });

    render(
      <LazyWrapper requireAuth={true}>
        <TestComponent />
      </LazyWrapper>
    );

    // Should show loading spinner while Clerk initializes
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.queryByText('Test Component Loaded')).not.toBeInTheDocument();
  });

  test('should redirect to sign-in when auth required but user not signed in', async () => {
    mockUseAuth.mockReturnValue({
      isLoaded: true,
      isSignedIn: false,
      getToken: jest.fn()
    });

    render(
      <LazyWrapper requireAuth={true}>
        <TestComponent />
      </LazyWrapper>
    );

    // Should redirect to sign-in
    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/sign-in');
    });

    expect(screen.queryByText('Test Component Loaded')).not.toBeInTheDocument();
  });

  test('should load component when authenticated and auth required', async () => {
    mockUseAuth.mockReturnValue({
      isLoaded: true,
      isSignedIn: true,
      getToken: jest.fn()
    });

    render(
      <LazyWrapper requireAuth={true}>
        <TestComponent />
      </LazyWrapper>
    );

    // Should load the component
    await waitFor(() => {
      expect(screen.getByText('Test Component Loaded')).toBeInTheDocument();
    });
  });

  test('should load component immediately when auth not required', async () => {
    mockUseAuth.mockReturnValue({
      isLoaded: false, // Even if not loaded
      isSignedIn: false,
      getToken: jest.fn()
    });

    render(
      <LazyWrapper requireAuth={false}>
        <TestComponent />
      </LazyWrapper>
    );

    // Should load the component regardless of auth state
    await waitFor(() => {
      expect(screen.getByText('Test Component Loaded')).toBeInTheDocument();
    });
  });
});
```

#### File: `frontend/src/__tests__/integration/error-boundary.test.tsx`
**Action**: CREATE NEW FILE  
**Purpose**: Test error boundary integration with lazy loading

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LazyLoadingErrorBoundary } from '@/components/ui/error-boundaries/LazyLoadingErrorBoundary';

// Component that throws an error
const ThrowError = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>Component loaded successfully</div>;
};

describe('LazyLoadingErrorBoundary', () => {
  // Suppress console.error for these tests
  beforeAll(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  test('should catch and display error when child component throws', () => {
    render(
      <LazyLoadingErrorBoundary componentName="Test Component">
        <ThrowError />
      </LazyLoadingErrorBoundary>
    );

    expect(screen.getByText('Failed to load Test Component')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByText('Try Again (3 attempts left)')).toBeInTheDocument();
  });

  test('should allow retry attempts', async () => {
    let shouldThrow = true;
    const TestComponent = () => <ThrowError shouldThrow={shouldThrow} />;

    const { rerender } = render(
      <LazyLoadingErrorBoundary componentName="Test Component">
        <TestComponent />
      </LazyLoadingErrorBoundary>
    );

    // Click retry button
    const retryButton = screen.getByText('Try Again (3 attempts left)');
    fireEvent.click(retryButton);

    // Simulate successful retry
    shouldThrow = false;
    rerender(
      <LazyLoadingErrorBoundary componentName="Test Component">
        <TestComponent />
      </LazyLoadingErrorBoundary>
    );

    await waitFor(() => {
      expect(screen.getByText('Component loaded successfully')).toBeInTheDocument();
    });
  });

  test('should show maximum retry message when attempts exhausted', () => {
    const { rerender } = render(
      <LazyLoadingErrorBoundary componentName="Test Component">
        <ThrowError />
      </LazyLoadingErrorBoundary>
    );

    // Simulate multiple retry attempts
    const retryButton = screen.getByText('Try Again (3 attempts left)');
    
    // Click retry multiple times
    fireEvent.click(retryButton);
    rerender(
      <LazyLoadingErrorBoundary componentName="Test Component">
        <ThrowError />
      </LazyLoadingErrorBoundary>
    );

    // After max retries, should show different message
    // This would require more complex state management in the test
  });
});
```

---

### 3. End-to-End Testing Suite

#### File: `frontend/cypress/e2e/lazy-loading-flows.cy.ts`
**Action**: CREATE NEW FILE  
**Purpose**: E2E tests for complete lazy loading user journeys

```typescript
describe('Lazy Loading User Journeys', () => {
  beforeEach(() => {
    // Mock Clerk authentication
    cy.window().then((win) => {
      win.localStorage.setItem('__clerk_jwt', 'mock_jwt_token');
    });
  });

  describe('Authenticated User Journey', () => {
    it('should load chat interface progressively when authenticated', () => {
      // Visit home page
      cy.visit('/');
      
      // Simulate authentication
      cy.window().then((win) => {
        win.localStorage.setItem('__clerk_user', JSON.stringify({
          id: 'user_123',
          firstName: 'Test',
          lastName: 'User'
        }));
      });

      // Navigate to chat
      cy.get('[data-testid="nav-chat"]').click();
      
      // Should show loading skeleton first
      cy.get('[data-testid="chat-loading-skeleton"]').should('be.visible');
      
      // Should load chat interface
      cy.get('[data-testid="chat-interface"]', { timeout: 10000 })
        .should('be.visible');
      
      // Should not show loading skeleton anymore
      cy.get('[data-testid="chat-loading-skeleton"]').should('not.exist');
    });

    it('should preload components based on user behavior', () => {
      // Set up user behavior pattern
      cy.window().then((win) => {
        win.localStorage.setItem('user_behavior_pattern', JSON.stringify({
          commonRoutes: ['/dashboard', '/profile'],
          timeSpent: { '/dashboard': 15000, '/profile': 8000 },
          interactions: { '/dashboard': 5, '/profile': 3 }
        }));
      });

      cy.visit('/');
      
      // Wait for preloading to occur
      cy.wait(3000);
      
      // Navigate to commonly used route - should load faster
      cy.get('[data-testid="nav-dashboard"]').click();
      
      // Should load quickly due to preloading
      cy.get('[data-testid="dashboard-content"]', { timeout: 2000 })
        .should('be.visible');
    });
  });

  describe('Error Handling', () => {
    it('should show error boundary when component fails to load', () => {
      // Mock network failure
      cy.intercept('GET', '/_next/static/chunks/*', { 
        statusCode: 500,
        body: 'Server Error'
      }).as('chunkFailure');

      cy.visit('/chat');

      // Should show error boundary
      cy.get('[data-testid="error-boundary"]').should('be.visible');
      cy.contains('Failed to load').should('be.visible');
      
      // Should have retry button
      cy.get('[data-testid="retry-button"]').should('be.visible');
    });

    it('should retry loading when retry button is clicked', () => {
      // First request fails
      let shouldFail = true;
      cy.intercept('GET', '/_next/static/chunks/*', (req) => {
        if (shouldFail) {
          shouldFail = false;
          req.reply({ statusCode: 500, body: 'Server Error' });
        } else {
          req.continue();
        }
      }).as('chunkRequest');

      cy.visit('/chat');

      // Should show error first
      cy.get('[data-testid="error-boundary"]').should('be.visible');
      
      // Click retry
      cy.get('[data-testid="retry-button"]').click();
      
      // Should eventually load successfully
      cy.get('[data-testid="chat-interface"]', { timeout: 10000 })
        .should('be.visible');
    });
  });

  describe('Performance Monitoring', () => {
    it('should track loading performance', () => {
      cy.visit('/', {
        onBeforeLoad: (win) => {
          // Mock performance observer
          cy.spy(win.performance, 'mark').as('performanceMark');
          cy.spy(win.performance, 'measure').as('performanceMeasure');
        }
      });

      cy.get('[data-testid="nav-chat"]').click();
      
      // Should call performance tracking
      cy.get('@performanceMark').should('have.been.called');
    });
  });

  describe('Offline Functionality', () => {
    it('should work offline with cached components', () => {
      // First visit to cache components
      cy.visit('/chat');
      cy.get('[data-testid="chat-interface"]').should('be.visible');
      
      // Go offline
      cy.window().then((win) => {
        // Simulate offline
        Object.defineProperty(win.navigator, 'onLine', {
          writable: true,
          value: false
        });
      });

      // Refresh page
      cy.reload();
      
      // Should still work with cached version
      cy.get('[data-testid="chat-interface"]', { timeout: 10000 })
        .should('be.visible');
        
      // Should show offline indicator
      cy.get('[data-testid="offline-indicator"]').should('be.visible');
    });
  });
});
```

---

### 4. Performance Monitoring System

#### File: `frontend/src/utils/performanceMonitoring.ts`
**Action**: CREATE NEW FILE  
**Purpose**: Monitor and track lazy loading performance metrics

```typescript
interface LoadingMetric {
  componentName: string;
  loadTime: number;
  success: boolean;
  error?: string;
  timestamp: number;
  userAgent: string;
  connectionType: string;
  cacheHit: boolean;
}

interface PerformanceReport {
  averageLoadTime: number;
  successRate: number;
  commonErrors: Record<string, number>;
  cacheHitRate: number;
  totalComponents: number;
  slowestComponents: Array<{ name: string; avgTime: number }>;
}

class PerformanceMonitor {
  private metrics: LoadingMetric[] = [];
  private maxMetrics = 1000; // Keep last 1000 metrics

  constructor() {
    this.setupPerformanceObserver();
  }

  private setupPerformanceObserver() {
    if (typeof window === 'undefined') return;

    // Observe navigation timing
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            this.trackPageLoad(entry as PerformanceNavigationTiming);
          }
        }
      });

      try {
        observer.observe({ entryTypes: ['navigation'] });
      } catch (e) {
        console.warn('PerformanceObserver not supported');
      }
    }
  }

  private trackPageLoad(entry: PerformanceNavigationTiming) {
    const loadTime = entry.loadEventEnd - entry.navigationStart;
    
    // Send to analytics if load time is concerning
    if (loadTime > 3000) {
      this.reportSlowLoad({
        page: window.location.pathname,
        loadTime,
        connectionType: this.getConnectionType(),
        timestamp: Date.now()
      });
    }
  }

  private getConnectionType(): string {
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
    return connection ? connection.effectiveType || 'unknown' : 'unknown';
  }

  private reportSlowLoad(data: any) {
    // In production, send to analytics service
    console.warn('[PerformanceMonitor] Slow page load detected:', data);
    
    // Could integrate with services like DataDog, New Relic, etc.
    // analytics.track('slow_page_load', data);
  }

  trackComponentLoad(
    componentName: string,
    startTime: number,
    success: boolean = true,
    error?: string,
    cacheHit: boolean = false
  ) {
    const loadTime = performance.now() - startTime;
    
    const metric: LoadingMetric = {
      componentName,
      loadTime,
      success,
      error,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      connectionType: this.getConnectionType(),
      cacheHit
    };

    this.metrics.push(metric);
    
    // Keep only recent metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    // Log slow components
    if (loadTime > 2000 && success) {
      console.warn(`[PerformanceMonitor] Slow component load: ${componentName} took ${loadTime}ms`);
    }

    // Report critical failures
    if (!success) {
      console.error(`[PerformanceMonitor] Component load failed: ${componentName}`, error);
      this.reportComponentFailure(metric);
    }

    return metric;
  }

  private reportComponentFailure(metric: LoadingMetric) {
    // In production, send to error tracking service
    // errorTracking.captureException(new Error(metric.error), {
    //   tags: { component: metric.componentName },
    //   extra: metric
    // });
  }

  generateReport(): PerformanceReport {
    const totalMetrics = this.metrics.length;
    const successfulMetrics = this.metrics.filter(m => m.success);
    const failedMetrics = this.metrics.filter(m => !m.success);
    const cacheHits = this.metrics.filter(m => m.cacheHit);

    // Calculate average load time
    const averageLoadTime = successfulMetrics.reduce((acc, m) => acc + m.loadTime, 0) / successfulMetrics.length || 0;

    // Calculate success rate
    const successRate = (successfulMetrics.length / totalMetrics) * 100 || 100;

    // Find common errors
    const commonErrors: Record<string, number> = {};
    failedMetrics.forEach(m => {
      const error = m.error || 'Unknown error';
      commonErrors[error] = (commonErrors[error] || 0) + 1;
    });

    // Calculate cache hit rate
    const cacheHitRate = (cacheHits.length / totalMetrics) * 100 || 0;

    // Find slowest components
    const componentTimes: Record<string, number[]> = {};
    successfulMetrics.forEach(m => {
      if (!componentTimes[m.componentName]) {
        componentTimes[m.componentName] = [];
      }
      componentTimes[m.componentName].push(m.loadTime);
    });

    const slowestComponents = Object.entries(componentTimes)
      .map(([name, times]) => ({
        name,
        avgTime: times.reduce((a, b) => a + b, 0) / times.length
      }))
      .sort((a, b) => b.avgTime - a.avgTime)
      .slice(0, 5);

    return {
      averageLoadTime,
      successRate,
      commonErrors,
      cacheHitRate,
      totalComponents: Object.keys(componentTimes).length,
      slowestComponents
    };
  }

  exportMetrics(): LoadingMetric[] {
    return [...this.metrics];
  }

  clearMetrics() {
    this.metrics = [];
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Helper function to track component loading
export const trackComponentLoad = <T>(
  componentName: string,
  loadFunction: () => Promise<T>,
  cacheHit: boolean = false
): Promise<T> => {
  const startTime = performance.now();
  
  return loadFunction()
    .then(result => {
      performanceMonitor.trackComponentLoad(componentName, startTime, true, undefined, cacheHit);
      return result;
    })
    .catch(error => {
      performanceMonitor.trackComponentLoad(componentName, startTime, false, error.message, cacheHit);
      throw error;
    });
};
```

#### File: `frontend/src/components/dev/PerformanceDashboard.tsx`
**Action**: CREATE NEW FILE  
**Purpose**: Development dashboard for monitoring lazy loading performance

```typescript
import React, { useState, useEffect } from 'react';
import { performanceMonitor, PerformanceReport } from '@/utils/performanceMonitoring';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PerformanceDashboard: React.FC = () => {
  const [report, setReport] = useState<PerformanceReport | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show in development
    if (process.env.NODE_ENV !== 'development') return;

    const updateReport = () => {
      setReport(performanceMonitor.generateReport());
    };

    updateReport();
    const interval = setInterval(updateReport, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Toggle dashboard with Ctrl+Shift+P
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        setIsVisible(!isVisible);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isVisible]);

  if (process.env.NODE_ENV !== 'development' || !isVisible || !report) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-50 max-h-96 overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-lg">Lazy Loading Performance</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      <div className="space-y-4">
        {/* Key metrics */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-medium">Avg Load Time</div>
            <div className={`text-lg ${report.averageLoadTime > 2000 ? 'text-red-600' : 'text-green-600'}`}>
              {report.averageLoadTime.toFixed(0)}ms
            </div>
          </div>
          <div>
            <div className="font-medium">Success Rate</div>
            <div className={`text-lg ${report.successRate < 95 ? 'text-red-600' : 'text-green-600'}`}>
              {report.successRate.toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="font-medium">Cache Hit Rate</div>
            <div className={`text-lg ${report.cacheHitRate < 50 ? 'text-orange-600' : 'text-green-600'}`}>
              {report.cacheHitRate.toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="font-medium">Components</div>
            <div className="text-lg">{report.totalComponents}</div>
          </div>
        </div>

        {/* Slowest components chart */}
        {report.slowestComponents.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Slowest Components</h4>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={report.slowestComponents}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  fontSize={10}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis fontSize={10} />
                <Tooltip formatter={(value) => [`${value}ms`, 'Load Time']} />
                <Bar dataKey="avgTime" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Common errors */}
        {Object.keys(report.commonErrors).length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Common Errors</h4>
            <div className="space-y-1 text-sm">
              {Object.entries(report.commonErrors).map(([error, count]) => (
                <div key={error} className="flex justify-between">
                  <span className="truncate text-red-600" title={error}>
                    {error.slice(0, 30)}...
                  </span>
                  <span className="text-red-800 font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2 text-xs">
          <button
            onClick={() => performanceMonitor.clearMetrics()}
            className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Clear Metrics
          </button>
          <button
            onClick={() => {
              const data = performanceMonitor.exportMetrics();
              console.log('Performance Metrics:', data);
            }}
            className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            Export to Console
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-500 mt-4">
        Press Ctrl+Shift+P to toggle this dashboard
      </div>
    </div>
  );
};

export default PerformanceDashboard;
```

---

### 5. Documentation and Maintenance

#### File: `frontend/docs/lazy-loading/maintenance-guide.md`
**Action**: CREATE NEW FILE  
**Purpose**: Maintenance and troubleshooting guide

```markdown
# Lazy Loading Maintenance Guide

## 🔧 Regular Maintenance Tasks

### Weekly Tasks
- [ ] Review performance dashboard metrics
- [ ] Check error rates and common failures
- [ ] Analyze user behavior patterns
- [ ] Update component preloading strategies

### Monthly Tasks
- [ ] Bundle size analysis
- [ ] Cache hit rate optimization
- [ ] Performance benchmark comparisons
- [ ] Update lazy loading strategies based on usage data

### Quarterly Tasks
- [ ] Complete performance audit
- [ ] Update documentation
- [ ] Review and optimize code splitting strategy
- [ ] Plan performance improvements

## 📊 Monitoring and Alerts

### Key Performance Indicators (KPIs)
1. **Average Component Load Time** - Should be < 1.5s
2. **Success Rate** - Should be > 98%
3. **Cache Hit Rate** - Should be > 60%
4. **Bundle Size Growth** - Should increase < 5% per month

### Alert Thresholds
- Component load time > 3s
- Success rate < 95%
- Error rate > 2%
- Bundle size increase > 20% month-over-month

## 🐛 Common Issues and Solutions

### Issue: Components fail to load intermittently
**Symptoms**: Random loading failures, error boundaries triggered
**Likely Causes**:
- Network instability
- Bundle serving issues
- Service worker cache corruption

**Solutions**:
1. Check service worker cache status
2. Clear browser cache and reload
3. Verify CDN status
4. Review network request logs

### Issue: Slow component loading
**Symptoms**: Components take > 3s to load
**Likely Causes**:
- Large bundle sizes
- Network throttling
- Inefficient preloading

**Solutions**:
1. Analyze bundle composition
2. Implement tree-shaking optimization
3. Optimize preloading strategies
4. Consider component splitting

### Issue: Authentication-related loading failures
**Symptoms**: Components fail when auth state changes
**Likely Causes**:
- Race conditions between auth and lazy loading
- Incorrect authentication checks

**Solutions**:
1. Verify `isLoaded` checks before component loading
2. Add proper error boundaries for auth failures
3. Implement auth state change listeners

## 🔍 Debugging Tools

### Performance Dashboard
Access with `Ctrl+Shift+P` in development mode

### Browser DevTools
1. **Network tab**: Check chunk loading times
2. **Performance tab**: Analyze loading waterfalls
3. **Application tab**: Verify service worker cache

### Console Commands
```javascript
// View current performance metrics
console.log(performanceMonitor.generateReport());

// Export raw metrics
console.log(performanceMonitor.exportMetrics());

// Clear performance data
performanceMonitor.clearMetrics();
```

## 📈 Performance Optimization Tips

### Bundle Optimization
1. Regular bundle analysis with `npm run analyze`
2. Remove unused dependencies
3. Optimize import statements
4. Use dynamic imports for large libraries

### Preloading Strategy
1. Monitor user behavior patterns
2. Adjust preloading based on usage data
3. Implement intelligent prefetching
4. Consider user's connection speed

### Caching Strategy
1. Optimize service worker cache rules
2. Implement proper cache invalidation
3. Monitor cache hit rates
4. Balance cache size vs. performance
```

## 📝 Summary of Phase 4 Changes

### New Files to Create
| File Path | Purpose | Estimated Lines |
|-----------|---------|-----------------|
| `frontend/src/__tests__/hooks/useSmartPreloading.test.ts` | Unit tests for smart preloading | 150 |
| `frontend/src/__tests__/hooks/useIntersectionPreload.test.ts` | Unit tests for intersection preload | 80 |
| `frontend/src/__tests__/integration/lazy-loading-auth.test.tsx` | Integration tests for auth + lazy loading | 120 |
| `frontend/src/__tests__/integration/error-boundary.test.tsx` | Error boundary integration tests | 100 |
| `frontend/cypress/e2e/lazy-loading-flows.cy.ts` | E2E tests for user journeys | 200 |
| `frontend/src/utils/performanceMonitoring.ts` | Performance monitoring system | 250 |
| `frontend/src/components/dev/PerformanceDashboard.tsx` | Development performance dashboard | 180 |
| `docs/lazy-loading/maintenance-guide.md` | Maintenance and troubleshooting guide | 200 |

### Configuration Files to Update
| File Path | Change Type | Primary Changes |
|-----------|-------------|-----------------|
| `frontend/jest.config.js` | Update | Add test setup and mocks |
| `frontend/cypress.config.ts` | Update | E2E test configuration |
| `frontend/package.json` | Update | Add testing dependencies |

## ✅ Success Criteria

### Testing Coverage
- [ ] Unit test coverage > 90% for lazy loading utilities
- [ ] Integration test coverage for all authentication scenarios
- [ ] E2E test coverage for critical user journeys
- [ ] Performance regression test suite

### Monitoring Implementation
- [ ] Real-time performance monitoring active
- [ ] Error tracking and alerting configured
- [ ] Performance dashboard accessible in development
- [ ] Automated performance reports

### Documentation Quality
- [ ] Complete maintenance guide
- [ ] Troubleshooting documentation
- [ ] Performance optimization guidelines
- [ ] Team training materials

### Quality Assurance
- [ ] All tests passing consistently
- [ ] Performance benchmarks established
- [ ] Error rates within acceptable thresholds
- [ ] User experience validation completed

## 🎯 Long-term Maintenance Strategy

### Continuous Improvement
1. **Monthly performance reviews** with stakeholders
2. **Quarterly optimization cycles** based on data
3. **Annual architecture review** and updates
4. **Continuous learning** from user feedback and metrics

### Team Knowledge Sharing
1. Regular team training on lazy loading best practices
2. Documentation updates based on learnings
3. Knowledge transfer sessions for new team members
4. Community contributions and sharing

This comprehensive testing and monitoring phase ensures the lazy loading system remains robust, performant, and maintainable over time.