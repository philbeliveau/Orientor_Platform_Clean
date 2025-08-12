# Agent Prompt: Module C - Token Lifecycle Management

## 🎯 MISSION CRITICAL TASK
You are implementing the **Token Lifecycle Management** system that will intelligently manage token expiry, proactive refresh, and background maintenance to eliminate authentication interruptions in the Orientor Platform.

## 🚨 CRITICAL PROBLEM TO SOLVE
Currently, users experience sudden authentication failures when tokens expire:
```typescript
// CURRENT PROBLEM: Reactive token handling
User performing action → Token expired → API call fails → User sees error → Manual re-auth required
```
**Impact**: Session interruptions, poor user experience, lost work

## 🎯 YOUR SOLUTION TARGET
Create a proactive lifecycle management system:
```typescript
// YOUR TARGET SOLUTION: Proactive token management
Background service → Token 80% expired → Auto-refresh → Seamless user experience
```

## 📋 IMPLEMENTATION REQUIREMENTS

### 1. Create TokenLifecycleManager Service
**File**: `frontend/src/services/auth/TokenLifecycleManager.ts`

**Required Interface**:
```typescript
interface TokenLifecycleManager {
  // Core lifecycle management
  startLifecycleMonitoring(): void
  stopLifecycleMonitoring(): void
  
  // Proactive refresh
  scheduleProactiveRefresh(token: string, expiryTime: number): void
  cancelRefresh(tokenId: string): void
  
  // Manual controls
  forceRefresh(): Promise<void>
  pauseAutoRefresh(): void
  resumeAutoRefresh(): void
  
  // Status and metrics
  getLifecycleStatus(): LifecycleStatus
  getRefreshMetrics(): RefreshMetrics
}

interface LifecycleStatus {
  isMonitoring: boolean
  activeTokens: number
  nextRefreshTime: Date | null
  refreshInProgress: boolean
  lastRefreshTime: Date | null
}

interface RefreshMetrics {
  proactiveRefreshCount: number
  emergencyRefreshCount: number
  refreshSuccessRate: number
  averageRefreshTime: number
  sessionInterruptions: number
}
```

### 2. Required Features
```typescript
✅ MUST IMPLEMENT:
├── Automatic token expiry detection
├── Proactive refresh at 80% lifetime
├── Background token maintenance
├── Emergency refresh fallback
├── User activity tracking
├── Idle time optimization
├── Refresh queue management
└── Lifecycle metrics collection

⚡ PERFORMANCE TARGETS:
├── Proactive refresh rate: >80%
├── Emergency refresh rate: <5%
├── Session interruptions: 0%
├── Refresh latency: <500ms
└── Background operation invisibility: 100%
```

### 3. Integration with Module A & B
```typescript
// CRITICAL: Must integrate with both previous modules
import { tokenCacheService } from './TokenCacheService'
import { useEnhancedAuth } from '../../contexts/EnhancedAuthContext'

const lifecycleManager = new TokenLifecycleManager({
  cacheService: tokenCacheService,        // From Module A
  authContext: enhancedAuthContext        // From Module B
})
```

## 🔧 DETAILED IMPLEMENTATION STEPS

### Step 1: Core Lifecycle Manager
```typescript
// Start with this structure:
export class TokenLifecycleManager {
  private refreshTimers: Map<string, NodeJS.Timeout> = new Map()
  private refreshQueue: Map<string, RefreshJob> = new Map()
  private config: LifecycleConfig
  private metrics: RefreshMetrics
  private isMonitoring: boolean = false

  constructor(
    config: Partial<LifecycleConfig> = {},
    dependencies: {
      cacheService: TokenCacheService
      authContext: EnhancedAuthContext
    }
  ) {
    // Initialize with smart defaults
    this.config = {
      proactiveRefreshThreshold: 0.8,      // 80% of token lifetime
      emergencyRefreshThreshold: 0.95,     // 95% of token lifetime
      maxConcurrentRefresh: 3,             // Limit concurrent operations
      refreshRetryAttempts: 3,             // Retry failed refreshes
      backgroundRefreshEnabled: true,       // Background operations
      idleOptimizationEnabled: true,       // Optimize during idle time
      ...config
    }
  }

  startLifecycleMonitoring(): void {
    if (this.isMonitoring) return
    
    this.isMonitoring = true
    
    // Start token monitoring loop
    this.monitorActiveTokens()
    
    // Start user activity tracking
    this.startActivityTracking()
    
    // Initialize background maintenance
    this.scheduleBackgroundMaintenance()
  }

  private async monitorActiveTokens(): Promise<void> {
    // Monitor all cached tokens for expiry
    // Schedule proactive refreshes
    // Handle emergency scenarios
  }
}
```

### Step 2: Proactive Refresh Logic
```typescript
// Implement intelligent refresh scheduling
private scheduleProactiveRefresh(
  tokenKey: string, 
  expiryTime: number
): void {
  const now = Date.now()
  const lifetime = expiryTime - now
  const refreshTime = now + (lifetime * this.config.proactiveRefreshThreshold)
  
  // Cancel existing timer if present
  this.cancelRefresh(tokenKey)
  
  // Schedule proactive refresh
  const timer = setTimeout(async () => {
    await this.performProactiveRefresh(tokenKey)
  }, refreshTime - now)
  
  this.refreshTimers.set(tokenKey, timer)
}

private async performProactiveRefresh(tokenKey: string): Promise<void> {
  const startTime = performance.now()
  
  try {
    // Add to refresh queue
    const refreshJob: RefreshJob = {
      tokenKey,
      startTime,
      type: 'proactive',
      status: 'in_progress'
    }
    this.refreshQueue.set(tokenKey, refreshJob)
    
    // Perform refresh through TokenCacheService
    await this.dependencies.cacheService.refreshToken(tokenKey)
    
    // Update metrics
    this.metrics.proactiveRefreshCount++
    this.updateRefreshMetrics(performance.now() - startTime, true)
    
    // Reschedule for new token
    const newToken = await this.dependencies.cacheService.getToken()
    if (newToken) {
      const claims = this.parseTokenClaims(newToken)
      this.scheduleProactiveRefresh(tokenKey, claims.exp * 1000)
    }
    
  } catch (error) {
    // Handle refresh failure
    await this.handleRefreshFailure(tokenKey, error)
  } finally {
    this.refreshQueue.delete(tokenKey)
  }
}
```

### Step 3: User Activity Integration
```typescript
// Smart activity tracking for optimization
private startActivityTracking(): void {
  // Track user interactions
  this.trackUserActivity()
  
  // Optimize refresh timing based on activity
  this.optimizeRefreshTiming()
}

private trackUserActivity(): void {
  const activityEvents = ['click', 'keydown', 'scroll', 'mousemove']
  
  activityEvents.forEach(event => {
    document.addEventListener(event, () => {
      this.updateLastActivity()
    }, { passive: true })
  })
  
  // Track page visibility changes
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      this.handlePageHidden()
    } else {
      this.handlePageVisible()
    }
  })
}

private optimizeRefreshTiming(): void {
  // Prefer refreshing during user activity
  // Delay non-critical refreshes during idle time
  // Batch multiple refreshes when possible
}

private handlePageHidden(): void {
  // Pause non-essential background operations
  // Reduce refresh frequency
  this.pauseBackgroundMaintenance()
}

private handlePageVisible(): void {
  // Resume normal operations
  // Check for missed refreshes
  this.resumeBackgroundMaintenance()
  this.catchUpMissedRefreshes()
}
```

### Step 4: Background Maintenance
```typescript
// Implement background token maintenance
private scheduleBackgroundMaintenance(): void {
  setInterval(() => {
    this.performBackgroundMaintenance()
  }, 60000) // Every minute
}

private async performBackgroundMaintenance(): Promise<void> {
  if (!this.config.backgroundRefreshEnabled) return
  
  // Clean up expired refresh timers
  this.cleanupExpiredTimers()
  
  // Validate token cache consistency
  await this.validateCacheConsistency()
  
  // Optimize refresh scheduling
  this.optimizeRefreshSchedule()
  
  // Update lifecycle metrics
  this.updateLifecycleMetrics()
}

private cleanupExpiredTimers(): void {
  for (const [tokenKey, timer] of this.refreshTimers.entries()) {
    // Check if token is still valid/needed
    if (!this.isTokenStillNeeded(tokenKey)) {
      clearTimeout(timer)
      this.refreshTimers.delete(tokenKey)
    }
  }
}

private async validateCacheConsistency(): Promise<void> {
  // Ensure cached tokens match scheduled refreshes
  // Fix any inconsistencies found
  const cachedTokens = await this.dependencies.cacheService.getCacheStatus()
  
  for (const tokenKey of cachedTokens.activeTokens) {
    if (!this.refreshTimers.has(tokenKey)) {
      // Schedule missing refresh
      const token = await this.dependencies.cacheService.getToken(tokenKey)
      if (token) {
        const claims = this.parseTokenClaims(token)
        this.scheduleProactiveRefresh(tokenKey, claims.exp * 1000)
      }
    }
  }
}
```

### Step 5: Emergency Handling
```typescript
// Emergency refresh when proactive refresh fails
private async handleRefreshFailure(
  tokenKey: string, 
  error: Error
): Promise<void> {
  this.metrics.emergencyRefreshCount++
  
  // Attempt emergency refresh
  try {
    await this.performEmergencyRefresh(tokenKey)
  } catch (emergencyError) {
    // Last resort: force user re-authentication
    await this.handleCriticalAuthFailure(tokenKey, emergencyError)
  }
}

private async performEmergencyRefresh(tokenKey: string): Promise<void> {
  // Immediate refresh attempt
  await this.dependencies.cacheService.invalidateToken(tokenKey)
  
  // Force new token fetch
  const newToken = await this.dependencies.authContext.getOptimizedToken()
  
  if (!newToken) {
    throw new Error('Emergency refresh failed: No token available')
  }
  
  // Reschedule with new token
  const claims = this.parseTokenClaims(newToken)
  this.scheduleProactiveRefresh(tokenKey, claims.exp * 1000)
}

private async handleCriticalAuthFailure(
  tokenKey: string, 
  error: Error
): Promise<void> {
  // Record session interruption
  this.metrics.sessionInterruptions++
  
  // Notify enhanced auth context
  this.dependencies.authContext.handleAuthenticationFailure(error)
  
  // Clear all scheduled refreshes
  this.stopLifecycleMonitoring()
  
  // Force user to re-authenticate
  window.location.href = '/sign-in'
}
```

### Step 6: React Hook Integration
**File**: `frontend/src/hooks/useTokenLifecycle.ts`
```typescript
export function useTokenLifecycle() {
  const { authMetrics } = useEnhancedAuth()
  const [lifecycleStatus, setLifecycleStatus] = useState<LifecycleStatus>()
  const [refreshMetrics, setRefreshMetrics] = useState<RefreshMetrics>()

  useEffect(() => {
    // Start lifecycle monitoring when component mounts
    lifecycleManager.startLifecycleMonitoring()
    
    // Set up status updates
    const updateStatus = () => {
      setLifecycleStatus(lifecycleManager.getLifecycleStatus())
      setRefreshMetrics(lifecycleManager.getRefreshMetrics())
    }
    
    const interval = setInterval(updateStatus, 5000) // Update every 5s
    updateStatus() // Initial update
    
    return () => {
      clearInterval(interval)
      // Note: Don't stop monitoring on unmount - it's global
    }
  }, [])

  return {
    lifecycleStatus,
    refreshMetrics,
    forceRefresh: lifecycleManager.forceRefresh.bind(lifecycleManager),
    pauseAutoRefresh: lifecycleManager.pauseAutoRefresh.bind(lifecycleManager),
    resumeAutoRefresh: lifecycleManager.resumeAutoRefresh.bind(lifecycleManager)
  }
}
```

## 📊 SUCCESS VALIDATION

### Performance Benchmarks
```typescript
// Your implementation MUST achieve:
const lifecycleTests = {
  proactiveRefreshRate: '>80%',          // Successful proactive refreshes
  emergencyRefreshRate: '<5%',           // Emergency refresh occurrences
  sessionInterruptions: '0',             // User session interruptions
  refreshLatency: '<500ms',              // Time to complete refresh
  backgroundInvisibility: '100%',        // User-invisible operations
}
```

### Integration Test with Modules A & B
```typescript
describe('Lifecycle Integration', () => {
  it('should integrate with TokenCacheService and EnhancedAuthContext', async () => {
    const cacheService = new TokenCacheService()
    const authContext = new EnhancedAuthContext()
    
    const lifecycle = new TokenLifecycleManager({}, {
      cacheService,
      authContext
    })
    
    // Start monitoring
    lifecycle.startLifecycleMonitoring()
    
    // Simulate token approaching expiry
    const mockToken = 'mock.jwt.token'
    const expiryTime = Date.now() + 60000 // 1 minute from now
    
    lifecycle.scheduleProactiveRefresh('default', expiryTime)
    
    // Verify refresh is scheduled
    const status = lifecycle.getLifecycleStatus()
    expect(status.isMonitoring).toBe(true)
    expect(status.nextRefreshTime).toBeDefined()
  })
})
```

### User Experience Test
```typescript
describe('Seamless User Experience', () => {
  it('should refresh tokens without user interruption', async () => {
    // Simulate user performing actions during token refresh
    const userActions = [
      () => chatService.sendMessage('test'),
      () => fileService.uploadFile(file),
      () => profileService.updateProfile(data)
    ]
    
    // Trigger proactive refresh
    await lifecycle.performProactiveRefresh('default')
    
    // All user actions should succeed without interruption
    const results = await Promise.all(userActions.map(action => action()))
    
    expect(results.every(result => result.success)).toBe(true)
    expect(lifecycle.getRefreshMetrics().sessionInterruptions).toBe(0)
  })
})
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve Before Completion:
- [ ] **>80% proactive refresh rate** in testing environment
- [ ] **<5% emergency refresh rate** under normal conditions
- [ ] **Zero session interruptions** during token transitions
- [ ] **<500ms refresh latency** for all refresh operations
- [ ] **Seamless integration** with Modules A & B
- [ ] **100% background operation invisibility** to users
- [ ] **Comprehensive error recovery** for all failure scenarios

### Integration Readiness:
- [ ] Ready for Module D (Frontend Middleware) integration
- [ ] Compatible with existing token caching flow
- [ ] Performance monitoring enabled
- [ ] User activity optimization working

## 🔄 DEPENDENCIES
**CRITICAL**: This module DEPENDS on both Module A AND Module B completion.
- Module A: TokenCacheService for refresh operations
- Module B: EnhancedAuthContext for authentication state
- Test integration with both modules thoroughly

## 📖 REFERENCE DOCUMENTATION
Complete technical specifications available in:
`/docs/api-clerk-enhanced.md/plan/phase-1-token-caching/module-c-lifecycle.md`

## 🔄 REPORTING FORMAT
```
📊 MODULE C PROGRESS REPORT
⏱️ STATUS: [Waiting for A&B/In Progress/Completed/Blocked]
🎯 IMPLEMENTATION: [X/7 core features completed]
📈 PERFORMANCE: 
  ├── Proactive refresh rate: X%
  ├── Emergency refresh rate: X%
  ├── Session interruptions: X
  └── Refresh latency: Xms
🧪 TESTING: [X/Y test suites passing]
🔗 INTEGRATION: Modules A&B - [Ready/Testing/Complete]
🚨 BLOCKERS: [Any issues or dependencies]
🔄 NEXT: [Ready for Module D integration / Additional work needed]
```

**WAIT FOR MODULES A & B COMPLETION** before starting - both integrations are critical!

---

**REMINDER**: 🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
Seamless user experience is the ultimate goal!