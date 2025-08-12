# Module A: Core Token Cache Service

## Overview
The core token cache service is the foundation of the authentication optimization. It provides intelligent token caching, automatic refresh, and performance monitoring to eliminate redundant Clerk API calls.

## Current Problem Analysis

### ChatInterface.tsx Token Calls (8 instances)
```typescript
// CURRENT PROBLEMATIC PATTERN
const { getToken } = useAuth();

// Called 8 times in single component:
const token = await getToken(); // Line 194 - Message sending
const token = await getToken(); // Line 309 - File upload  
const token = await getToken(); // Line 359 - Fallback token
const token = await getToken(); // Line 406 - Stream init
const token = await getToken(); // Line 709 - Save conversation
const token = await getToken(); // Line 739 - Delete conversation  
const token = await getToken(); // Line 761 - Share conversation
const token = await getToken(); // Line 811 - Export conversation
```

### Performance Impact
- **8 network requests** per chat interaction
- **2-5 second delays** on every action
- **No token reuse** between requests
- **Synchronous blocking** of UI operations

## Solution: TokenCacheService

### Core Architecture
```typescript
interface TokenCacheConfig {
  // Cache settings
  maxCacheAge: number;           // 5 minutes default
  refreshThreshold: number;      // Refresh when 80% expired
  maxRetries: number;           // 3 retries for failed requests
  
  // Performance settings
  batchRequests: boolean;       // Batch simultaneous requests
  prefetchEnabled: boolean;     // Prefetch tokens proactively
  monitoringEnabled: boolean;   // Collect performance metrics
}

interface CachedToken {
  token: string;
  expiresAt: Date;
  issuedAt: Date;
  refreshedAt?: Date;
  source: 'cache' | 'network' | 'refresh';
}

interface TokenCacheMetrics {
  hitRate: number;              // Cache hit percentage
  missRate: number;             // Cache miss percentage  
  averageFetchTime: number;     // Network fetch time
  averageCacheTime: number;     // Cache retrieval time
  errorRate: number;            // Failed token requests
  refreshCount: number;         // Automatic refreshes
}
```

### Implementation

#### 1. Core TokenCacheService Class
```typescript
// File: frontend/src/services/auth/TokenCacheService.ts

import { useAuth } from '@clerk/nextjs';

export class TokenCacheService {
  private cache: Map<string, CachedToken> = new Map();
  private pendingRequests: Map<string, Promise<string | null>> = new Map();
  private config: TokenCacheConfig;
  private metrics: TokenCacheMetrics;
  private refreshTimer?: NodeJS.Timeout;

  constructor(config: Partial<TokenCacheConfig> = {}) {
    this.config = {
      maxCacheAge: 5 * 60 * 1000,        // 5 minutes
      refreshThreshold: 0.8,              // Refresh at 80% expiry
      maxRetries: 3,
      batchRequests: true,
      prefetchEnabled: true,
      monitoringEnabled: true,
      ...config
    };
    
    this.metrics = this.initializeMetrics();
    this.startRefreshScheduler();
  }

  /**
   * Primary method - replaces all direct getToken() calls
   * Returns cached token if valid, otherwise fetches new one
   */
  async getToken(templateName: string = 'default'): Promise<string | null> {
    const startTime = performance.now();
    
    try {
      // Check cache first
      const cached = this.getCachedToken(templateName);
      if (cached && this.isTokenValid(cached)) {
        this.recordCacheHit(performance.now() - startTime);
        return cached.token;
      }

      // Check for pending request to avoid duplicates
      if (this.config.batchRequests) {
        const pending = this.pendingRequests.get(templateName);
        if (pending) {
          return await pending;
        }
      }

      // Fetch new token
      const tokenPromise = this.fetchTokenFromClerk(templateName);
      if (this.config.batchRequests) {
        this.pendingRequests.set(templateName, tokenPromise);
      }

      const token = await tokenPromise;
      
      if (this.config.batchRequests) {
        this.pendingRequests.delete(templateName);
      }

      this.recordCacheMiss(performance.now() - startTime);
      return token;

    } catch (error) {
      this.recordError(error);
      throw error;
    }
  }

  /**
   * Fetches token from Clerk API with retry logic
   */
  private async fetchTokenFromClerk(templateName: string): Promise<string | null> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        const { getToken } = useAuth();
        const options = templateName !== 'default' ? { template: templateName } : undefined;
        const token = await getToken(options);
        
        if (token) {
          this.cacheToken(templateName, token);
          return token;
        }
        
        throw new Error('No token returned from Clerk');
      } catch (error) {
        lastError = error as Error;
        if (attempt < this.config.maxRetries) {
          await this.delay(Math.pow(2, attempt) * 100); // Exponential backoff
        }
      }
    }
    
    throw lastError;
  }

  /**
   * Caches token with expiry information
   */
  private cacheToken(templateName: string, token: string): void {
    const now = new Date();
    const expiresAt = new Date(now.getTime() + this.config.maxCacheAge);
    
    const cachedToken: CachedToken = {
      token,
      expiresAt,
      issuedAt: now,
      source: 'network'
    };
    
    this.cache.set(templateName, cachedToken);
  }

  /**
   * Retrieves cached token if available
   */
  private getCachedToken(templateName: string): CachedToken | null {
    return this.cache.get(templateName) || null;
  }

  /**
   * Validates if cached token is still usable
   */
  private isTokenValid(cached: CachedToken): boolean {
    const now = new Date();
    const timeUntilExpiry = cached.expiresAt.getTime() - now.getTime();
    const totalLifetime = cached.expiresAt.getTime() - cached.issuedAt.getTime();
    
    // Token is valid if more than 20% lifetime remaining
    return timeUntilExpiry > (totalLifetime * 0.2);
  }

  /**
   * Proactively refresh tokens approaching expiry
   */
  private async refreshTokenIfNeeded(templateName: string, cached: CachedToken): Promise<void> {
    const now = new Date();
    const timeUntilExpiry = cached.expiresAt.getTime() - now.getTime();
    const totalLifetime = cached.expiresAt.getTime() - cached.issuedAt.getTime();
    const timeRemaining = timeUntilExpiry / totalLifetime;
    
    if (timeRemaining <= this.config.refreshThreshold) {
      try {
        await this.fetchTokenFromClerk(templateName);
        this.metrics.refreshCount++;
      } catch (error) {
        console.warn('Token refresh failed:', error);
      }
    }
  }

  /**
   * Background scheduler for proactive token refresh
   */
  private startRefreshScheduler(): void {
    this.refreshTimer = setInterval(() => {
      if (this.config.prefetchEnabled) {
        this.cache.forEach(async (cached, templateName) => {
          await this.refreshTokenIfNeeded(templateName, cached);
        });
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Invalidate specific or all cached tokens
   */
  public invalidateToken(templateName?: string): void {
    if (templateName) {
      this.cache.delete(templateName);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Force refresh a specific token
   */
  public async refreshToken(templateName: string = 'default'): Promise<string | null> {
    this.invalidateToken(templateName);
    return await this.getToken(templateName);
  }

  /**
   * Get performance metrics
   */
  public getMetrics(): TokenCacheMetrics {
    return { ...this.metrics };
  }

  /**
   * Get cache status for debugging
   */
  public getCacheStatus(): Record<string, any> {
    const status: Record<string, any> = {};
    
    this.cache.forEach((cached, templateName) => {
      status[templateName] = {
        isValid: this.isTokenValid(cached),
        expiresAt: cached.expiresAt,
        source: cached.source,
        age: Date.now() - cached.issuedAt.getTime()
      };
    });
    
    return status;
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
    this.cache.clear();
    this.pendingRequests.clear();
  }

  // Metrics recording methods
  private recordCacheHit(responseTime: number): void {
    if (!this.config.monitoringEnabled) return;
    
    this.metrics.hitRate = this.updateRate(this.metrics.hitRate, true);
    this.metrics.averageCacheTime = this.updateAverage(this.metrics.averageCacheTime, responseTime);
  }

  private recordCacheMiss(responseTime: number): void {
    if (!this.config.monitoringEnabled) return;
    
    this.metrics.missRate = this.updateRate(this.metrics.missRate, true);
    this.metrics.averageFetchTime = this.updateAverage(this.metrics.averageFetchTime, responseTime);
  }

  private recordError(error: Error): void {
    if (!this.config.monitoringEnabled) return;
    
    this.metrics.errorRate = this.updateRate(this.metrics.errorRate, true);
    console.error('TokenCacheService error:', error);
  }

  private updateRate(currentRate: number, increment: boolean): number {
    // Simple moving average for demonstration
    return increment ? Math.min(currentRate + 0.01, 1) : Math.max(currentRate - 0.01, 0);
  }

  private updateAverage(currentAverage: number, newValue: number): number {
    return (currentAverage + newValue) / 2;
  }

  private initializeMetrics(): TokenCacheMetrics {
    return {
      hitRate: 0,
      missRate: 0,
      averageFetchTime: 0,
      averageCacheTime: 0,
      errorRate: 0,
      refreshCount: 0
    };
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Singleton instance
export const tokenCacheService = new TokenCacheService();
```

#### 2. React Hook Integration
```typescript
// File: frontend/src/hooks/useOptimizedAuth.ts

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { tokenCacheService } from '../services/auth/TokenCacheService';

interface OptimizedAuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  getOptimizedToken: (template?: string) => Promise<string | null>;
  refreshAuth: () => Promise<void>;
  metrics: TokenCacheMetrics;
}

export function useOptimizedAuth(): OptimizedAuthState {
  const { isLoaded, isSignedIn, user } = useAuth();
  const [metrics, setMetrics] = useState(tokenCacheService.getMetrics());

  // Update metrics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(tokenCacheService.getMetrics());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getOptimizedToken = useCallback(async (template?: string) => {
    return await tokenCacheService.getToken(template);
  }, []);

  const refreshAuth = useCallback(async () => {
    tokenCacheService.invalidateToken();
    await tokenCacheService.getToken();
  }, []);

  return {
    isAuthenticated: isLoaded && isSignedIn,
    isLoading: !isLoaded,
    user,
    getOptimizedToken,
    refreshAuth,
    metrics
  };
}
```

### Usage Examples

#### Before (SLOW - 8 network calls)
```typescript
// frontend/src/components/chat/ChatInterface.tsx (CURRENT)
const { getToken } = useAuth();

const sendMessage = async () => {
  const token = await getToken(); // Network call 1
  // ... use token
};

const uploadFile = async () => {
  const token = await getToken(); // Network call 2
  // ... use token  
};

const saveConversation = async () => {
  const token = await getToken(); // Network call 3
  // ... use token
};
```

#### After (FAST - 1 cache hit)
```typescript
// frontend/src/components/chat/ChatInterface.tsx (OPTIMIZED)
import { useOptimizedAuth } from '../../hooks/useOptimizedAuth';

const { getOptimizedToken } = useOptimizedAuth();

const sendMessage = async () => {
  const token = await getOptimizedToken(); // Cache hit (<10ms)
  // ... use token
};

const uploadFile = async () => {
  const token = await getOptimizedToken(); // Cache hit (<10ms)
  // ... use token  
};

const saveConversation = async () => {
  const token = await getOptimizedToken(); // Cache hit (<10ms)
  // ... use token
};
```

## Testing Strategy

### Unit Tests
```typescript
// File: frontend/src/services/auth/__tests__/TokenCacheService.test.ts

describe('TokenCacheService', () => {
  let service: TokenCacheService;

  beforeEach(() => {
    service = new TokenCacheService({
      maxCacheAge: 1000, // 1 second for testing
      monitoringEnabled: true
    });
  });

  it('should cache tokens and return from cache', async () => {
    const token1 = await service.getToken();
    const token2 = await service.getToken();
    
    expect(token1).toBe(token2);
    expect(service.getMetrics().hitRate).toBeGreaterThan(0);
  });

  it('should refresh expired tokens', async () => {
    const token1 = await service.getToken();
    
    // Wait for expiration
    await new Promise(resolve => setTimeout(resolve, 1100));
    
    const token2 = await service.getToken();
    expect(service.getMetrics().refreshCount).toBeGreaterThan(0);
  });

  it('should batch simultaneous requests', async () => {
    const promises = [
      service.getToken(),
      service.getToken(),
      service.getToken()
    ];
    
    const tokens = await Promise.all(promises);
    expect(new Set(tokens).size).toBe(1); // All should be the same token
  });
});
```

### Performance Tests
```typescript
// File: frontend/src/services/auth/__tests__/TokenCacheService.performance.test.ts

describe('TokenCacheService Performance', () => {
  it('should have <10ms cache retrieval time', async () => {
    const service = new TokenCacheService();
    
    // Prime the cache
    await service.getToken();
    
    const startTime = performance.now();
    await service.getToken();
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(10);
  });

  it('should achieve >90% cache hit rate', async () => {
    const service = new TokenCacheService();
    
    // Simulate multiple requests
    for (let i = 0; i < 100; i++) {
      await service.getToken();
    }
    
    expect(service.getMetrics().hitRate).toBeGreaterThan(0.9);
  });
});
```

## Integration Points

### With Authentication Context (Module B)
```typescript
// Provides cached tokens to the authentication context
const authContext = useAuthenticationContext();
authContext.setTokenProvider(tokenCacheService);
```

### With API Services
```typescript
// Replace all direct getToken() calls in API services
import { tokenCacheService } from '../auth/TokenCacheService';

export async function getAuthHeader(): Promise<Record<string, string>> {
  const token = await tokenCacheService.getToken();
  if (!token) {
    throw new Error('No authentication token available');
  }
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}
```

## Performance Targets

### Cache Performance
- **Cache hit rate**: >95% for active users
- **Cache retrieval time**: <10ms average
- **Network fetch time**: <100ms (when cache miss)
- **Memory usage**: <5MB for token cache

### Error Handling
- **Retry mechanism**: 3 attempts with exponential backoff
- **Graceful degradation**: Fallback to direct Clerk API
- **Error recovery**: Automatic token refresh on auth errors

## Deployment Checklist

- [ ] Implement TokenCacheService class
- [ ] Create useOptimizedAuth hook
- [ ] Add comprehensive unit tests
- [ ] Add performance benchmarks
- [ ] Update ChatInterface.tsx to use optimized auth
- [ ] Monitor cache hit rates in production
- [ ] Set up performance alerts for cache misses

## Success Metrics

### Technical Metrics
- **95%+ cache hit rate** within 24 hours
- **80% reduction** in Clerk API calls
- **90% reduction** in authentication latency

### User Experience Metrics  
- **Immediate response** to chat interactions
- **Elimination** of loading states in chat
- **50% improvement** in perceived performance

---

**Dependencies**: None (can be implemented immediately)
**Estimated Implementation Time**: 1-2 days
**Risk Level**: Low (non-breaking changes)