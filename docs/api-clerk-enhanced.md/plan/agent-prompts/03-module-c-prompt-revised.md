# Agent Prompt: Module C - Clerk-Native Token Lifecycle Management

## 🎯 MISSION CRITICAL TASK
You are implementing the **Clerk-Native Token Lifecycle Management** system that intelligently enhances Clerk's built-in token refresh mechanisms with user activity optimization, comprehensive monitoring, and seamless fallback handling to eliminate authentication interruptions in the Orientor Platform.

## 🚨 CRITICAL PROBLEM TO SOLVE
Currently, users experience authentication failures despite Clerk's built-in refresh:
```typescript
// CURRENT PROBLEM: Unoptimized token usage
User performing action → Token near expiry → Clerk refreshes in background → Timing conflicts → API call fails
```
**Impact**: Session interruptions, poor UX, timing conflicts with Clerk's native refresh

## 🎯 YOUR SOLUTION TARGET
Create an intelligent enhancement layer for Clerk's native token management:
```typescript
// YOUR TARGET SOLUTION: Clerk-enhanced lifecycle management
Activity monitor → Smart token optimization → Clerk native refresh → Seamless user experience
```

## 📋 IMPLEMENTATION REQUIREMENTS

### 1. Create ClerkTokenLifecycleManager Service
**File**: `frontend/src/services/auth/ClerkTokenLifecycleManager.ts`

**Required Interface**:
```typescript
interface ClerkTokenLifecycleManager {
  // Clerk-native operations
  getOptimizedToken(options?: ClerkTokenOptions): Promise<string | null>
  forceTokenRefresh(): Promise<string | null>
  
  // Activity-based optimization
  startActivityMonitoring(): void
  stopActivityMonitoring(): void
  optimizeTokenTiming(): void
  
  // Metrics and monitoring
  getTokenMetrics(): TokenMetrics
  getActivityStatus(): ActivityStatus
  
  // Emergency handling
  handleTokenFailure(error: Error): Promise<void>
  validateTokenHealth(): Promise<boolean>
}

interface ClerkTokenOptions {
  skipCache?: boolean
  template?: string
  activityOptimized?: boolean
  emergencyMode?: boolean
}

interface TokenMetrics {
  clerkRefreshCount: number
  optimizedRefreshCount: number
  conflictPreventionCount: number
  emergencyHandlingCount: number
  averageTokenLifetime: number
  activityCorrelation: number
}

interface ActivityStatus {
  isUserActive: boolean
  lastActivityTime: Date
  activityLevel: 'high' | 'medium' | 'low' | 'idle'
  nextOptimizedRefresh: Date | null
  clerkRefreshEstimate: Date | null
}
```

### 2. Required Features
```typescript
✅ MUST IMPLEMENT:
├── Clerk native getToken() optimization
├── Activity-based refresh timing
├── Conflict prevention with Clerk's refresh
├── Emergency fallback to Clerk defaults
├── Token health monitoring
├── Performance metrics collection
├── Seamless Module A & B integration
└── Zero interference with Clerk mechanisms

⚡ PERFORMANCE TARGETS:
├── Clerk compatibility: 100%
├── Conflict prevention: 100%
├── Token availability: >99.9%
├── Emergency handling: <1%
├── Activity optimization: >90%
└── User interruptions: 0%
```

### 3. Integration with Clerk & Previous Modules
```typescript
// CRITICAL: Must work WITH Clerk, not against it
import { useAuth, useUser } from '@clerk/nextjs'
import { tokenCacheService } from './TokenCacheService'     // Module A
import { useEnhancedAuth } from '../../contexts/EnhancedAuthContext' // Module B

const lifecycleManager = new ClerkTokenLifecycleManager({
  clerkAuth: useAuth(),              // Primary Clerk integration
  clerkUser: useUser(),              // User state management
  cacheService: tokenCacheService,   // Module A integration
  authContext: enhancedAuthContext   // Module B integration
})
```

## 🔧 DETAILED IMPLEMENTATION STEPS

### Step 1: Clerk-Native Core Manager
```typescript
// Start with Clerk-first approach:
export class ClerkTokenLifecycleManager {
  private clerkAuth: ReturnType<typeof useAuth>
  private clerkUser: ReturnType<typeof useUser>
  private activityMonitor: ActivityMonitor
  private metrics: TokenMetrics
  private config: LifecycleConfig

  constructor(dependencies: {
    clerkAuth: ReturnType<typeof useAuth>
    clerkUser: ReturnType<typeof useUser>
    cacheService: TokenCacheService
    authContext: EnhancedAuthContext
  }) {
    this.clerkAuth = dependencies.clerkAuth
    this.clerkUser = dependencies.clerkUser
    
    // Initialize with Clerk-optimized defaults
    this.config = {
      activityOptimization: true,
      conflictPrevention: true,
      emergencyFallback: true,
      metricsCollection: true,
      clerkNativeFirst: true,        // Always prefer Clerk methods
      backgroundOptimization: true,
      activityThresholds: {
        high: 30000,    // 30 seconds
        medium: 120000, // 2 minutes
        low: 300000,    // 5 minutes
        idle: 900000    // 15 minutes
      }
    }
  }

  // PRIMARY METHOD: Clerk-optimized token retrieval
  async getOptimizedToken(options: ClerkTokenOptions = {}): Promise<string | null> {
    const startTime = performance.now()
    
    try {
      // Check if user is signed in
      if (!this.clerkAuth.isSignedIn) {
        await this.handleAuthenticationRequired()
        return null
      }

      // Determine optimal token retrieval strategy
      const strategy = this.determineTokenStrategy(options)
      
      // Use Clerk's native getToken with optimization
      const token = await this.clerkAuth.getToken({
        skipCache: strategy.skipCache,
        template: options.template,
        // Clerk handles expiration automatically
      })

      if (!token) {
        return await this.handleTokenFailure(new Error('No token available'))
      }

      // Update metrics
      this.updateTokenMetrics(performance.now() - startTime, strategy.type)
      
      // Cache optimization (integrate with Module A)
      if (this.dependencies.cacheService && strategy.shouldCache) {
        await this.dependencies.cacheService.optimizeToken(token)
      }

      return token

    } catch (error) {
      return await this.handleTokenFailure(error as Error)
    }
  }

  private determineTokenStrategy(options: ClerkTokenOptions): TokenStrategy {
    const activity = this.getActivityStatus()
    const clerkRefreshEstimate = this.estimateClerkRefreshTiming()
    
    return {
      skipCache: options.skipCache || 
                this.shouldSkipCacheBasedOnActivity(activity) ||
                options.emergencyMode,
      shouldCache: !options.emergencyMode && activity.activityLevel !== 'idle',
      type: options.emergencyMode ? 'emergency' : 
            options.skipCache ? 'forced' : 
            activity.activityLevel === 'high' ? 'optimized' : 'normal'
    }
  }
}
```

### Step 2: Activity-Based Optimization
```typescript
// Intelligent activity monitoring
class ActivityMonitor {
  private lastActivity: Date = new Date()
  private activityLevel: ActivityLevel = 'medium'
  private isMonitoring: boolean = false

  startMonitoring(): void {
    if (this.isMonitoring) return
    
    this.isMonitoring = true
    
    // Track user interactions
    this.trackUserActivity()
    
    // Monitor page visibility
    this.trackPageVisibility()
    
    // Start activity analysis loop
    this.startActivityAnalysis()
  }

  private trackUserActivity(): void {
    const activityEvents = [
      'click', 'keydown', 'scroll', 'mousemove', 
      'touchstart', 'focus', 'input'
    ]
    
    const updateActivity = () => {
      this.lastActivity = new Date()
      this.updateActivityLevel()
    }

    activityEvents.forEach(event => {
      document.addEventListener(event, updateActivity, { 
        passive: true,
        capture: true 
      })
    })
  }

  private trackPageVisibility(): void {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.handlePageHidden()
      } else {
        this.handlePageVisible()
      }
    })
  }

  private updateActivityLevel(): void {
    const timeSinceActivity = Date.now() - this.lastActivity.getTime()
    
    if (timeSinceActivity < 30000) {
      this.activityLevel = 'high'
    } else if (timeSinceActivity < 120000) {
      this.activityLevel = 'medium'
    } else if (timeSinceActivity < 300000) {
      this.activityLevel = 'low'
    } else {
      this.activityLevel = 'idle'
    }
  }

  shouldOptimizeForActivity(): boolean {
    // High activity: prefer fresh tokens
    // Low activity: prefer cached tokens
    // Idle: minimal token operations
    return this.activityLevel === 'high' || this.activityLevel === 'medium'
  }
}
```

### Step 3: Clerk Refresh Coordination
```typescript
// Coordinate with Clerk's native 50-second refresh cycle
private estimateClerkRefreshTiming(): Date | null {
  // Clerk refreshes every 50 seconds automatically
  // We need to coordinate our optimization around this
  
  const lastTokenTime = this.getLastTokenTimestamp()
  if (!lastTokenTime) return null
  
  // Estimate next Clerk refresh (50-second intervals)
  const clerkRefreshInterval = 50000 // 50 seconds
  const timeSinceLastToken = Date.now() - lastTokenTime
  const timeToNextRefresh = clerkRefreshInterval - (timeSinceLastToken % clerkRefreshInterval)
  
  return new Date(Date.now() + timeToNextRefresh)
}

private shouldSkipCacheBasedOnActivity(activity: ActivityStatus): boolean {
  const clerkRefreshEstimate = this.estimateClerkRefreshTiming()
  
  if (!clerkRefreshEstimate) return false
  
  const timeToClerkRefresh = clerkRefreshEstimate.getTime() - Date.now()
  
  // If Clerk refresh is imminent and user is active, skip cache to get fresh token
  if (timeToClerkRefresh < 5000 && activity.activityLevel === 'high') {
    return true
  }
  
  // If user just became active and token might be stale, refresh
  if (activity.activityLevel === 'high' && timeToClerkRefresh > 40000) {
    return true
  }
  
  return false
}

// Prevent conflicts with Clerk's native refresh
private async preventClerkConflicts(): Promise<void> {
  const clerkRefreshEstimate = this.estimateClerkRefreshTiming()
  
  if (!clerkRefreshEstimate) return
  
  const timeToClerkRefresh = clerkRefreshEstimate.getTime() - Date.now()
  
  // Avoid operations during Clerk's refresh window
  if (timeToClerkRefresh < 2000) {
    await this.waitForClerkRefresh()
  }
}

private async waitForClerkRefresh(): Promise<void> {
  // Wait for Clerk's refresh to complete
  await new Promise(resolve => setTimeout(resolve, 3000))
}
```

### Step 4: Emergency Handling with Clerk Fallbacks
```typescript
// Robust emergency handling using Clerk's built-in mechanisms
async handleTokenFailure(error: Error): Promise<string | null> {
  this.metrics.emergencyHandlingCount++
  
  try {
    // Step 1: Try user.reload() - refreshes both user and session
    if (this.clerkUser.user) {
      await this.clerkUser.user.reload()
      const reloadedToken = await this.clerkAuth.getToken({ skipCache: true })
      if (reloadedToken) {
        this.metrics.emergencySuccessCount++
        return reloadedToken
      }
    }

    // Step 2: Force token refresh with skipCache
    const forcedToken = await this.clerkAuth.getToken({ skipCache: true })
    if (forcedToken) {
      this.metrics.emergencySuccessCount++
      return forcedToken
    }

    // Step 3: Check authentication status
    if (!this.clerkAuth.isSignedIn) {
      await this.handleAuthenticationRequired()
      return null
    }

    // Step 4: Last resort - clear any cached state and retry
    await this.clearCacheAndRetry()
    
  } catch (emergencyError) {
    // Critical failure - redirect to sign-in
    await this.handleCriticalAuthFailure(emergencyError)
  }
  
  return null
}

private async handleAuthenticationRequired(): Promise<void> {
  // Always redirect to Clerk's sign-in page
  if (typeof window !== 'undefined') {
    window.location.href = '/sign-in'
  }
}

private async clearCacheAndRetry(): Promise<string | null> {
  // Clear Module A cache if available
  if (this.dependencies.cacheService) {
    await this.dependencies.cacheService.clearCache()
  }
  
  // One final attempt with Clerk
  return await this.clerkAuth.getToken({ skipCache: true })
}

private async handleCriticalAuthFailure(error: Error): Promise<void> {
  // Log the critical failure
  console.error('Critical authentication failure:', error)
  
  // Update metrics
  this.metrics.criticalFailures++
  
  // Notify enhanced auth context (Module B)
  if (this.dependencies.authContext) {
    this.dependencies.authContext.handleCriticalFailure(error)
  }
  
  // Force redirect to sign-in
  await this.handleAuthenticationRequired()
}
```

### Step 5: React Hook Integration
**File**: `frontend/src/hooks/useClerkTokenLifecycle.ts`
```typescript
export function useClerkTokenLifecycle() {
  const clerkAuth = useAuth()
  const clerkUser = useUser()
  const { authMetrics } = useEnhancedAuth()
  
  const [lifecycleStatus, setLifecycleStatus] = useState<ActivityStatus>()
  const [tokenMetrics, setTokenMetrics] = useState<TokenMetrics>()

  // Initialize lifecycle manager
  const lifecycleManager = useMemo(() => {
    if (!clerkAuth.isLoaded) return null
    
    return new ClerkTokenLifecycleManager({
      clerkAuth,
      clerkUser,
      cacheService: tokenCacheService,
      authContext: enhancedAuthContext
    })
  }, [clerkAuth.isLoaded, clerkAuth, clerkUser])

  useEffect(() => {
    if (!lifecycleManager) return

    // Start activity monitoring
    lifecycleManager.startActivityMonitoring()
    
    // Set up status updates
    const updateStatus = () => {
      setLifecycleStatus(lifecycleManager.getActivityStatus())
      setTokenMetrics(lifecycleManager.getTokenMetrics())
    }
    
    const interval = setInterval(updateStatus, 5000)
    updateStatus()
    
    return () => {
      clearInterval(interval)
      lifecycleManager.stopActivityMonitoring()
    }
  }, [lifecycleManager])

  // Primary token access method
  const getOptimizedToken = useCallback(async (options?: ClerkTokenOptions) => {
    if (!lifecycleManager) return null
    return await lifecycleManager.getOptimizedToken(options)
  }, [lifecycleManager])

  return {
    // Token operations
    getOptimizedToken,
    forceTokenRefresh: lifecycleManager?.forceTokenRefresh.bind(lifecycleManager),
    
    // Status monitoring
    lifecycleStatus,
    tokenMetrics,
    
    // Clerk native access (for compatibility)
    clerkAuth,
    clerkUser,
    
    // Health checks
    validateTokenHealth: lifecycleManager?.validateTokenHealth.bind(lifecycleManager)
  }
}
```

## 📊 SUCCESS VALIDATION

### Performance Benchmarks
```typescript
// Your implementation MUST achieve:
const clerkEnhancedTests = {
  clerkCompatibility: '100%',           // No interference with Clerk
  conflictPrevention: '100%',           // Zero timing conflicts
  tokenAvailability: '>99.9%',          // Always available when needed
  emergencyHandling: '<1%',             // Rare emergency scenarios
  activityOptimization: '>90%',         // Smart timing based on activity
  userInterruptions: '0',               // Zero session interruptions
}
```

### Integration Test with Clerk + Modules A & B
```typescript
describe('Clerk-Enhanced Lifecycle Integration', () => {
  it('should work seamlessly with Clerk native refresh', async () => {
    const { getOptimizedToken } = useClerkTokenLifecycle()
    
    // Simulate user activity
    fireEvent.click(screen.getByText('Test Action'))
    
    // Get token during high activity
    const token1 = await getOptimizedToken({ activityOptimized: true })
    expect(token1).toBeTruthy()
    
    // Simulate idle period
    await act(() => advance(900000)) // 15 minutes
    
    // Token should still be available but optimized for idle
    const token2 = await getOptimizedToken()
    expect(token2).toBeTruthy()
    
    // Verify no conflicts with Clerk's refresh
    expect(mockClerkRefresh).toHaveBeenCalledTimes(18) // Normal Clerk intervals
  })
})
```

### Clerk Integration Compliance Test
```typescript
describe('Clerk Compliance', () => {
  it('should only use Clerk authentication methods', async () => {
    const manager = new ClerkTokenLifecycleManager(deps)
    
    // Verify no localStorage usage
    const localStorageSpy = jest.spyOn(Storage.prototype, 'getItem')
    await manager.getOptimizedToken()
    expect(localStorageSpy).not.toHaveBeenCalledWith('access_token')
    
    // Verify only /sign-in redirects
    const windowSpy = jest.spyOn(window.location, 'href', 'set')
    await manager.handleAuthenticationRequired()
    expect(windowSpy).toHaveBeenCalledWith('/sign-in')
    expect(windowSpy).not.toHaveBeenCalledWith('/login')
  })
})
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve Before Completion:
- [ ] **100% Clerk compatibility** - Zero interference with native mechanisms
- [ ] **100% conflict prevention** - No timing conflicts with Clerk refresh
- [ ] **>99.9% token availability** - Always ready when user needs it
- [ ] **<1% emergency handling** - Rare fallback scenarios only
- [ ] **>90% activity optimization** - Smart timing based on user behavior
- [ ] **Zero session interruptions** - Seamless user experience
- [ ] **Complete Module A & B integration** - Works with existing cache and context

### Clerk Authentication Compliance:
- [ ] Uses only `useAuth()` and `useUser()` hooks
- [ ] All token access via `await getToken()`
- [ ] All redirects to `/sign-in` (never `/login`)
- [ ] No localStorage token usage
- [ ] Emergency fallbacks use Clerk methods

## 🔄 DEPENDENCIES
**CRITICAL**: This module ENHANCES Clerk's native capabilities and integrates with:
- **Clerk Native**: useAuth(), useUser(), getToken() methods
- **Module A**: TokenCacheService for optimization
- **Module B**: EnhancedAuthContext for state management
- Test integration with all components thoroughly

## 📖 REFERENCE DOCUMENTATION
Enhanced technical specifications available in:
`/docs/api-clerk-enhanced.md/plan/phase-1-token-caching/module-c-clerk-native.md`

## 🔄 REPORTING FORMAT
```
📊 MODULE C PROGRESS REPORT
⏱️ STATUS: [Waiting for A&B/In Progress/Completed/Blocked]
🎯 IMPLEMENTATION: [X/7 core features completed]
📈 PERFORMANCE: 
  ├── Clerk compatibility: X%
  ├── Conflict prevention: X%
  ├── Token availability: X%
  └── Activity optimization: X%
🧪 TESTING: [X/Y test suites passing]
🔗 INTEGRATION: Clerk + Modules A&B - [Ready/Testing/Complete]
🚨 BLOCKERS: [Any issues or dependencies]
🔄 NEXT: [Ready for Module D integration / Additional work needed]
```

**WAIT FOR MODULES A & B COMPLETION** before starting - integration is critical!

---

**REMINDER**: 🔐 CLERK AUTHENTICATION ONLY - NO EXCEPTIONS
Work WITH Clerk's native mechanisms, not against them!