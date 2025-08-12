# Module C: Token Lifecycle Management

## Overview
Implements intelligent token lifecycle management including automatic refresh, proactive renewal, expiry handling, and background token maintenance to ensure seamless user experience without authentication interruptions.

## Current Problem Analysis

### Token Expiry Issues
```typescript
// CURRENT PATTERN (no lifecycle management)
const { getToken } = useAuth();

const apiCall = async () => {
  const token = await getToken(); // May be expired
  
  const response = await fetch('/api/data', {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (response.status === 401) {
    // Token expired mid-session
    // User experiences error, manual re-authentication required
    router.push('/sign-in');
  }
};
```

### Problems Identified
- **No proactive token refresh** before expiration
- **Sudden authentication failures** during user sessions
- **Manual re-authentication** required on token expiry
- **No background token maintenance**
- **Poor user experience** with unexpected logouts

## Solution: Token Lifecycle Manager

### Architecture
```typescript
interface TokenLifecycleConfig {
  // Refresh thresholds
  refreshThreshold: number;        // Refresh when 80% lifetime passed
  earlyRefreshBuffer: number;      // Refresh 5 min before expiry
  maxTokenAge: number;             // Maximum token age (1 hour)
  
  // Background operations
  backgroundRefreshEnabled: boolean;
  refreshCheckInterval: number;    // Check every 30 seconds
  prefetchOnIdle: boolean;         // Prefetch during idle time
  
  // Error handling
  maxRetryAttempts: number;        // 3 retry attempts
  retryBackoffBase: number;        // 1000ms base backoff
  gracePeriod: number;             // 2 min grace period
}

interface TokenInfo {
  token: string;
  issuedAt: Date;
  expiresAt: Date;
  refreshedAt?: Date;
  source: 'fresh' | 'cached' | 'refreshed';
  isValid: boolean;
  timeUntilExpiry: number;
}

interface LifecycleMetrics {
  totalRefreshes: number;
  proactiveRefreshes: number;
  emergencyRefreshes: number;
  refreshSuccessRate: number;
  averageTokenLifetime: number;
  backgroundOperations: number;
}
```

### Implementation

#### 1. Core Token Lifecycle Manager
```typescript
// File: frontend/src/services/auth/TokenLifecycleManager.ts

import { tokenCacheService } from './TokenCacheService';

export class TokenLifecycleManager {
  private config: TokenLifecycleConfig;
  private metrics: LifecycleMetrics;
  private refreshTimer?: NodeJS.Timeout;
  private idleTimer?: NodeJS.Timeout;
  private isRefreshing = false;
  private refreshPromises = new Map<string, Promise<string | null>>();
  
  constructor(config: Partial<TokenLifecycleConfig> = {}) {
    this.config = {
      refreshThreshold: 0.8,              // Refresh at 80% lifetime
      earlyRefreshBuffer: 5 * 60 * 1000,  // 5 minutes before expiry
      maxTokenAge: 60 * 60 * 1000,        // 1 hour max age
      backgroundRefreshEnabled: true,
      refreshCheckInterval: 30 * 1000,    // 30 seconds
      prefetchOnIdle: true,
      maxRetryAttempts: 3,
      retryBackoffBase: 1000,             // 1 second
      gracePeriod: 2 * 60 * 1000,         // 2 minutes
      ...config
    };
    
    this.metrics = this.initializeMetrics();
    this.startBackgroundOperations();
    this.setupIdleDetection();
  }

  /**
   * Get token with lifecycle management
   */
  async getTokenWithLifecycle(template: string = 'default'): Promise<string | null> {
    try {
      // Check if token needs refresh
      const shouldRefresh = await this.shouldRefreshToken(template);
      
      if (shouldRefresh) {
        return await this.refreshTokenProactively(template);
      }
      
      // Get cached token
      const token = await tokenCacheService.getToken(template);
      
      if (!token) {
        // Emergency refresh if no token available
        return await this.emergencyRefresh(template);
      }
      
      return token;
    } catch (error) {
      console.error('Token lifecycle error:', error);
      throw error;
    }
  }

  /**
   * Check if token should be refreshed proactively
   */
  private async shouldRefreshToken(template: string): Promise<boolean> {
    const cacheStatus = tokenCacheService.getCacheStatus();
    const tokenInfo = cacheStatus[template];
    
    if (!tokenInfo) {
      return true; // No token, need refresh
    }
    
    const now = Date.now();
    const expiresAt = new Date(tokenInfo.expiresAt).getTime();
    const issuedAt = new Date(tokenInfo.issuedAt || 0).getTime();
    
    // Calculate token lifetime and remaining time
    const totalLifetime = expiresAt - issuedAt;
    const timeRemaining = expiresAt - now;
    const lifetimeUsed = (totalLifetime - timeRemaining) / totalLifetime;
    
    // Refresh conditions
    const shouldRefreshByThreshold = lifetimeUsed >= this.config.refreshThreshold;
    const shouldRefreshByBuffer = timeRemaining <= this.config.earlyRefreshBuffer;
    const shouldRefreshByAge = (now - issuedAt) >= this.config.maxTokenAge;
    
    return shouldRefreshByThreshold || shouldRefreshByBuffer || shouldRefreshByAge;
  }

  /**
   * Proactively refresh token before expiration
   */
  private async refreshTokenProactively(template: string): Promise<string | null> {
    // Prevent concurrent refreshes for same template
    if (this.refreshPromises.has(template)) {
      return await this.refreshPromises.get(template)!;
    }
    
    const refreshPromise = this.performTokenRefresh(template, 'proactive');
    this.refreshPromises.set(template, refreshPromise);
    
    try {
      const token = await refreshPromise;
      this.metrics.proactiveRefreshes++;
      return token;
    } finally {
      this.refreshPromises.delete(template);
    }
  }

  /**
   * Emergency refresh when no valid token available
   */
  private async emergencyRefresh(template: string): Promise<string | null> {
    const token = await this.performTokenRefresh(template, 'emergency');
    this.metrics.emergencyRefreshes++;
    return token;
  }

  /**
   * Perform actual token refresh with retry logic
   */
  private async performTokenRefresh(
    template: string, 
    type: 'proactive' | 'emergency'
  ): Promise<string | null> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= this.config.maxRetryAttempts; attempt++) {
      try {
        // Invalidate current token
        tokenCacheService.invalidateToken(template);
        
        // Fetch fresh token
        const token = await tokenCacheService.getToken(template);
        
        if (token) {
          this.metrics.totalRefreshes++;
          this.updateRefreshSuccessRate(true);
          return token;
        }
        
        throw new Error('No token returned from refresh');
      } catch (error) {
        lastError = error as Error;
        this.updateRefreshSuccessRate(false);
        
        if (attempt < this.config.maxRetryAttempts) {
          const backoffDelay = this.config.retryBackoffBase * Math.pow(2, attempt - 1);
          await this.delay(backoffDelay);
        }
      }
    }
    
    throw lastError;
  }

  /**
   * Background token maintenance
   */
  private startBackgroundOperations(): void {
    if (!this.config.backgroundRefreshEnabled) return;
    
    this.refreshTimer = setInterval(async () => {
      await this.performBackgroundMaintenance();
    }, this.config.refreshCheckInterval);
  }

  /**
   * Perform background token maintenance
   */
  private async performBackgroundMaintenance(): Promise<void> {
    if (this.isRefreshing) return;
    
    this.isRefreshing = true;
    this.metrics.backgroundOperations++;
    
    try {
      const cacheStatus = tokenCacheService.getCacheStatus();
      
      // Check each cached token
      for (const [template, tokenInfo] of Object.entries(cacheStatus)) {
        if (await this.shouldRefreshToken(template)) {
          try {
            await this.refreshTokenProactively(template);
          } catch (error) {
            console.warn(`Background refresh failed for template ${template}:`, error);
          }
        }
      }
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Setup idle detection for prefetching
   */
  private setupIdleDetection(): void {
    if (!this.config.prefetchOnIdle) return;
    
    let idleTimer: NodeJS.Timeout;
    
    const resetIdleTimer = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        this.performIdlePrefetch();
      }, 60000); // 1 minute idle threshold
    };
    
    // Listen for user activity
    if (typeof window !== 'undefined') {
      ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetIdleTimer, true);
      });
    }
    
    resetIdleTimer();
  }

  /**
   * Prefetch tokens during idle time
   */
  private async performIdlePrefetch(): Promise<void> {
    try {
      // Prefetch common templates
      const commonTemplates = ['default', 'api'];
      
      await Promise.all(
        commonTemplates.map(async template => {
          try {
            if (await this.shouldRefreshToken(template)) {
              await this.refreshTokenProactively(template);
            }
          } catch (error) {
            // Ignore prefetch errors
          }
        })
      );
    } catch (error) {
      console.warn('Idle prefetch failed:', error);
    }
  }

  /**
   * Get token information for debugging
   */
  getTokenInfo(template: string = 'default'): TokenInfo | null {
    const cacheStatus = tokenCacheService.getCacheStatus();
    const tokenInfo = cacheStatus[template];
    
    if (!tokenInfo) return null;
    
    const now = Date.now();
    const expiresAt = new Date(tokenInfo.expiresAt).getTime();
    
    return {
      token: '***', // Don't expose actual token
      issuedAt: new Date(tokenInfo.issuedAt || 0),
      expiresAt: new Date(tokenInfo.expiresAt),
      source: tokenInfo.source as 'fresh' | 'cached' | 'refreshed',
      isValid: tokenInfo.isValid,
      timeUntilExpiry: Math.max(0, expiresAt - now)
    };
  }

  /**
   * Get lifecycle metrics
   */
  getMetrics(): LifecycleMetrics {
    return { ...this.metrics };
  }

  /**
   * Force refresh all tokens
   */
  async refreshAllTokens(): Promise<void> {
    const cacheStatus = tokenCacheService.getCacheStatus();
    
    await Promise.all(
      Object.keys(cacheStatus).map(template =>
        this.refreshTokenProactively(template).catch(error => {
          console.warn(`Failed to refresh template ${template}:`, error);
        })
      )
    );
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
    if (this.idleTimer) {
      clearTimeout(this.idleTimer);
    }
    this.refreshPromises.clear();
  }

  // Helper methods
  private updateRefreshSuccessRate(success: boolean): void {
    const total = this.metrics.totalRefreshes;
    const currentSuccesses = this.metrics.refreshSuccessRate * total;
    
    this.metrics.refreshSuccessRate = success
      ? (currentSuccesses + 1) / (total + 1)
      : currentSuccesses / (total + 1);
  }

  private initializeMetrics(): LifecycleMetrics {
    return {
      totalRefreshes: 0,
      proactiveRefreshes: 0,
      emergencyRefreshes: 0,
      refreshSuccessRate: 1,
      averageTokenLifetime: this.config.maxTokenAge,
      backgroundOperations: 0
    };
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Singleton instance
export const tokenLifecycleManager = new TokenLifecycleManager();
```

#### 2. Enhanced Auth Hook with Lifecycle
```typescript
// File: frontend/src/hooks/useLifecycleAuth.ts

import { useCallback, useEffect, useState } from 'react';
import { useEnhancedAuth } from '../contexts/EnhancedAuthContext';
import { tokenLifecycleManager } from '../services/auth/TokenLifecycleManager';

interface LifecycleAuthState {
  getTokenWithLifecycle: (template?: string) => Promise<string | null>;
  tokenInfo: TokenInfo | null;
  lifecycleMetrics: LifecycleMetrics;
  refreshAllTokens: () => Promise<void>;
  isTokenValid: (template?: string) => boolean;
}

export function useLifecycleAuth(): LifecycleAuthState {
  const { isAuthenticated } = useEnhancedAuth();
  const [tokenInfo, setTokenInfo] = useState<TokenInfo | null>(null);
  const [lifecycleMetrics, setLifecycleMetrics] = useState(
    tokenLifecycleManager.getMetrics()
  );

  // Update token info and metrics periodically
  useEffect(() => {
    if (!isAuthenticated) return;

    const updateInfo = () => {
      setTokenInfo(tokenLifecycleManager.getTokenInfo());
      setLifecycleMetrics(tokenLifecycleManager.getMetrics());
    };

    updateInfo();
    const interval = setInterval(updateInfo, 5000);

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const getTokenWithLifecycle = useCallback(async (template?: string) => {
    return await tokenLifecycleManager.getTokenWithLifecycle(template);
  }, []);

  const refreshAllTokens = useCallback(async () => {
    await tokenLifecycleManager.refreshAllTokens();
  }, []);

  const isTokenValid = useCallback((template: string = 'default') => {
    const info = tokenLifecycleManager.getTokenInfo(template);
    return info?.isValid ?? false;
  }, []);

  return {
    getTokenWithLifecycle,
    tokenInfo,
    lifecycleMetrics,
    refreshAllTokens,
    isTokenValid
  };
}
```

#### 3. Token Status Dashboard Component
```typescript
// File: frontend/src/components/auth/TokenStatusDashboard.tsx

import React, { useState, useEffect } from 'react';
import { useLifecycleAuth } from '../../hooks/useLifecycleAuth';

interface TokenStatusDashboardProps {
  enabled?: boolean;
  detailed?: boolean;
}

export function TokenStatusDashboard({ 
  enabled = false, 
  detailed = false 
}: TokenStatusDashboardProps) {
  const { tokenInfo, lifecycleMetrics, refreshAllTokens } = useLifecycleAuth();
  const [showDetails, setShowDetails] = useState(detailed);

  if (!enabled || process.env.NODE_ENV === 'production') {
    return null;
  }

  const formatTime = (ms: number) => {
    if (ms < 60000) return `${Math.round(ms / 1000)}s`;
    if (ms < 3600000) return `${Math.round(ms / 60000)}m`;
    return `${Math.round(ms / 3600000)}h`;
  };

  const getStatusColor = () => {
    if (!tokenInfo) return 'bg-gray-400';
    if (tokenInfo.timeUntilExpiry < 5 * 60 * 1000) return 'bg-red-400'; // <5 min
    if (tokenInfo.timeUntilExpiry < 15 * 60 * 1000) return 'bg-yellow-400'; // <15 min
    return 'bg-green-400';
  };

  return (
    <div className="fixed top-4 right-4 bg-gray-900 text-white p-3 rounded-lg shadow-lg text-xs max-w-sm">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center space-x-2 hover:bg-gray-800 px-2 py-1 rounded w-full"
      >
        <span>Token Status</span>
        <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
      </button>
      
      {showDetails && (
        <div className="mt-3 space-y-2">
          {tokenInfo && (
            <div className="border-b border-gray-700 pb-2">
              <div className="font-semibold mb-1">Current Token</div>
              <div>Valid: {tokenInfo.isValid ? '✓' : '✗'}</div>
              <div>Expires in: {formatTime(tokenInfo.timeUntilExpiry)}</div>
              <div>Source: {tokenInfo.source}</div>
              <div>Issued: {tokenInfo.issuedAt.toLocaleTimeString()}</div>
            </div>
          )}
          
          <div className="border-b border-gray-700 pb-2">
            <div className="font-semibold mb-1">Lifecycle Metrics</div>
            <div>Total Refreshes: {lifecycleMetrics.totalRefreshes}</div>
            <div>Proactive: {lifecycleMetrics.proactiveRefreshes}</div>
            <div>Emergency: {lifecycleMetrics.emergencyRefreshes}</div>
            <div>Success Rate: {(lifecycleMetrics.refreshSuccessRate * 100).toFixed(1)}%</div>
            <div>Background Ops: {lifecycleMetrics.backgroundOperations}</div>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={refreshAllTokens}
              className="flex-1 bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs"
            >
              Refresh Now
            </button>
            <button
              onClick={() => window.location.reload()}
              className="flex-1 bg-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-xs"
            >
              Reload
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 4. Automatic Token Refresh Middleware
```typescript
// File: frontend/src/middleware/tokenRefreshMiddleware.ts

import { NextRequest, NextResponse } from 'next/server';
import { tokenLifecycleManager } from '../services/auth/TokenLifecycleManager';

/**
 * Middleware to ensure tokens are refreshed before API calls
 */
export async function tokenRefreshMiddleware(request: NextRequest) {
  // Only process API routes
  if (!request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  try {
    // Check if this is an authenticated request
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.next();
    }

    // Ensure token is fresh before proceeding
    const freshToken = await tokenLifecycleManager.getTokenWithLifecycle();
    
    if (freshToken && authHeader !== `Bearer ${freshToken}`) {
      // Update authorization header with fresh token
      const requestHeaders = new Headers(request.headers);
      requestHeaders.set('authorization', `Bearer ${freshToken}`);
      
      return NextResponse.next({
        request: {
          headers: requestHeaders,
        },
      });
    }

    return NextResponse.next();
  } catch (error) {
    console.error('Token refresh middleware error:', error);
    return NextResponse.next();
  }
}
```

### Integration Examples

#### Enhanced API Service
```typescript
// File: frontend/src/services/api.ts (UPDATED)

import { tokenLifecycleManager } from './auth/TokenLifecycleManager';

export async function getAuthHeader(): Promise<Record<string, string>> {
  // Use lifecycle-managed token instead of direct getToken()
  const token = await tokenLifecycleManager.getTokenWithLifecycle();
  
  if (!token) {
    throw new Error('No authentication token available');
  }
  
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

// Enhanced API client with automatic token refresh
class EnhancedApiClient {
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    let response = await this.makeRequest(endpoint, options);
    
    // If 401, try refreshing token once
    if (response.status === 401) {
      try {
        await tokenLifecycleManager.refreshAllTokens();
        response = await this.makeRequest(endpoint, options);
      } catch (error) {
        // Redirect to sign-in if refresh fails
        if (typeof window !== 'undefined') {
          window.location.href = '/sign-in';
        }
        throw error;
      }
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  private async makeRequest(endpoint: string, options: RequestInit): Promise<Response> {
    const headers = await getAuthHeader();
    
    return fetch(endpoint, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    });
  }
}

export const apiClient = new EnhancedApiClient();
```

### Testing Strategy

#### Lifecycle Testing
```typescript
// File: frontend/src/services/auth/__tests__/TokenLifecycleManager.test.ts

describe('TokenLifecycleManager', () => {
  let manager: TokenLifecycleManager;

  beforeEach(() => {
    manager = new TokenLifecycleManager({
      refreshThreshold: 0.5, // 50% for testing
      backgroundRefreshEnabled: false
    });
  });

  it('should refresh token proactively', async () => {
    // Mock an aging token
    jest.spyOn(manager as any, 'shouldRefreshToken').mockResolvedValue(true);
    
    const token = await manager.getTokenWithLifecycle();
    expect(token).toBeTruthy();
    
    const metrics = manager.getMetrics();
    expect(metrics.proactiveRefreshes).toBeGreaterThan(0);
  });

  it('should handle emergency refresh', async () => {
    // Mock no cached token
    jest.spyOn(tokenCacheService, 'getToken').mockResolvedValueOnce(null);
    
    const token = await manager.getTokenWithLifecycle();
    expect(token).toBeTruthy();
    
    const metrics = manager.getMetrics();
    expect(metrics.emergencyRefreshes).toBeGreaterThan(0);
  });

  it('should perform background maintenance', async () => {
    const manager = new TokenLifecycleManager({
      backgroundRefreshEnabled: true,
      refreshCheckInterval: 100 // Fast for testing
    });
    
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const metrics = manager.getMetrics();
    expect(metrics.backgroundOperations).toBeGreaterThan(0);
    
    manager.destroy();
  });
});
```

## Performance Targets

### Lifecycle Performance
- **Proactive refresh rate**: >80% of all refreshes
- **Emergency refresh rate**: <20% of all refreshes
- **Background operation frequency**: Every 30 seconds
- **Refresh success rate**: >98%

### User Experience
- **Zero unexpected logouts** due to token expiry
- **Seamless session continuity** across long sessions
- **Invisible token maintenance** in background
- **Instant recovery** from token issues

## Integration Dependencies

### Requires
- Module A: TokenCacheService
- Module B: EnhancedAuthContext

### Provides
- Proactive token refresh
- Background token maintenance
- Emergency token recovery
- Lifecycle metrics

## Deployment Checklist

- [ ] Implement TokenLifecycleManager
- [ ] Create useLifecycleAuth hook
- [ ] Add TokenStatusDashboard component
- [ ] Update API services to use lifecycle tokens
- [ ] Configure background refresh intervals
- [ ] Add lifecycle monitoring
- [ ] Test proactive refresh scenarios
- [ ] Validate emergency recovery

## Success Metrics

### Technical Metrics
- **>80% proactive refresh rate**
- **<5% emergency refresh rate**
- **>98% refresh success rate**
- **Zero token expiry errors** in user sessions

### User Experience Metrics
- **100% session continuity** for active users
- **No authentication interruptions**
- **Invisible token management**

---

**Dependencies**: Module A (TokenCacheService), Module B (EnhancedAuthContext)
**Estimated Implementation Time**: 2-3 days
**Risk Level**: Medium (complex lifecycle logic)