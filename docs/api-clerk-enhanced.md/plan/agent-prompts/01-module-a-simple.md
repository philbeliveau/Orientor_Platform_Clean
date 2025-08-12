# Agent Prompt: Module A - Simple Token Cache (SIMPLIFIED)

## 🎯 MISSION: SOLVE THE CORE PROBLEM SIMPLY
**Problem**: ChatInterface makes 8 `getToken()` calls per interaction → 2-5 second delays
**Solution**: Cache the token for 5 minutes, reuse it
**Complexity**: MINIMAL - Just 30 lines of simple code

## 🚨 WHAT WE'RE NOT DOING (Over-Engineering)
❌ Complex classes and interfaces
❌ Metrics collection and monitoring  
❌ Retry logic and error handling systems
❌ Memory management and cleanup
❌ Performance benchmarking systems
❌ Background services

## ✅ WHAT WE'RE DOING (Simple & Effective)
✅ Simple function that caches getToken() result
✅ 5-minute expiry (same as Clerk default)
✅ Direct solution to 8→1 token call reduction

## 📋 SIMPLE IMPLEMENTATION

### Create Simple Token Cache
**File**: `frontend/src/utils/simpleTokenCache.ts`

```typescript
import { useAuth } from '@clerk/nextjs'

// Simple in-memory cache
let tokenCache: {
  token: string | null
  expiresAt: number
} = {
  token: null,
  expiresAt: 0
}

/**
 * Get cached token or fetch new one
 * Caches for 5 minutes to match Clerk's default
 */
export async function getCachedToken(): Promise<string | null> {
  const now = Date.now()
  
  // Return cached token if still valid
  if (tokenCache.token && now < tokenCache.expiresAt) {
    return tokenCache.token
  }
  
  // Get fresh token from Clerk
  const { getToken } = useAuth()
  const freshToken = await getToken()
  
  if (freshToken) {
    // Cache for 5 minutes
    tokenCache = {
      token: freshToken,
      expiresAt: now + (5 * 60 * 1000) // 5 minutes
    }
  }
  
  return freshToken
}

/**
 * Clear cache (for logout, etc.)
 */
export function clearTokenCache(): void {
  tokenCache = {
    token: null,
    expiresAt: 0
  }
}
```

### Alternative Hook Version
**File**: `frontend/src/hooks/useSimpleTokenCache.ts`

```typescript
import { useAuth } from '@clerk/nextjs'
import { useRef, useCallback } from 'react'

export function useSimpleTokenCache() {
  const { getToken, isSignedIn } = useAuth()
  
  // Cache ref persists across re-renders
  const cacheRef = useRef<{
    token: string | null
    expiresAt: number
  }>({
    token: null,
    expiresAt: 0
  })
  
  const getCachedToken = useCallback(async (): Promise<string | null> => {
    if (!isSignedIn) return null
    
    const now = Date.now()
    
    // Return cached if valid
    if (cacheRef.current.token && now < cacheRef.current.expiresAt) {
      return cacheRef.current.token
    }
    
    // Get fresh token
    const freshToken = await getToken()
    
    if (freshToken) {
      cacheRef.current = {
        token: freshToken,
        expiresAt: now + (5 * 60 * 1000) // 5 minutes
      }
    }
    
    return freshToken
  }, [getToken, isSignedIn])
  
  return { getCachedToken }
}
```

## 🔧 USAGE EXAMPLES

### In ChatInterface (Module G will use this)
```typescript
import { getCachedToken } from '../utils/simpleTokenCache'

const ChatInterface = () => {
  const handleSendMessage = async () => {
    // Instead of: const token = await getToken() 
    const token = await getCachedToken() // Uses cache!
    
    // Send message with token
  }
  
  const handleFileUpload = async () => {
    const token = await getCachedToken() // Same cached token!
    // Upload file
  }
  
  // All 8 operations use the same cached token
}
```

### Hook Usage
```typescript
import { useSimpleTokenCache } from '../hooks/useSimpleTokenCache'

const SomeComponent = () => {
  const { getCachedToken } = useSimpleTokenCache()
  
  const handleAction = async () => {
    const token = await getCachedToken()
    // Use token
  }
}
```

## 📊 SUCCESS CRITERIA (SIMPLE)

### Must Achieve:
- [ ] **Token caching works** (5-minute expiry)
- [ ] **Function is <30 lines** total
- [ ] **Zero external dependencies** (beyond Clerk)
- [ ] **Drop-in replacement** for getToken()
- [ ] **Ready for ChatInterface** integration

### Performance Target:
- **8 getToken() calls → 1 cached token** = 87.5% reduction
- **Cache hit time: <1ms** (just memory access)
- **No complex logic** - just cache and expiry check

## ✅ VALIDATION

### Simple Test
```typescript
// Test the cache works
describe('Simple Token Cache', () => {
  it('caches token for 5 minutes', async () => {
    // Mock getToken
    const mockGetToken = jest.fn().mockResolvedValue('mock-token')
    
    // First call - should fetch
    const token1 = await getCachedToken()
    expect(mockGetToken).toHaveBeenCalledTimes(1)
    
    // Second call within 5 minutes - should use cache
    const token2 = await getCachedToken()
    expect(mockGetToken).toHaveBeenCalledTimes(1) // Still 1!
    expect(token2).toBe(token1)
  })
})
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Complete:
- [ ] Function works and caches tokens
- [ ] Code is simple and readable
- [ ] No over-engineering
- [ ] Ready for ChatInterface integration
- [ ] Takes <2 hours to implement

### Implementation Time: **2 HOURS MAX**
- 30 minutes: Write the function
- 30 minutes: Write simple test
- 1 hour: Test integration

## 🔄 DEPENDENCIES
**NONE** - This is a simple utility function

## 📝 REPORTING FORMAT
```
📊 MODULE A - SIMPLE TOKEN CACHE
⏱️ STATUS: [Complete/In Progress]
🎯 LINES OF CODE: X/30 max
✅ WORKS: [Yes/No]
🔄 READY FOR MODULE G: [Yes/No]
⏰ TIME SPENT: X hours (max 2)
```

**START IMMEDIATELY** - This is simple and foundational!

---

**REMEMBER**: 
- Keep it simple - just cache the token!
- No classes, no complex logic
- Just solve the 8→1 token problem
- 🔐 CLERK AUTHENTICATION ONLY!