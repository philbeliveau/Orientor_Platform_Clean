# Agent Prompt: Module B - Simple Auth Hook (SIMPLIFIED)

## 🎯 MISSION: MAKE TOKEN CACHING EASY FOR DEVELOPERS
**Problem**: Components need an easy way to use cached tokens
**Solution**: Simple hook that wraps useAuth with caching
**Complexity**: MINIMAL - Just 20 lines

## 🚨 WHAT WE'RE NOT DOING (Over-Engineering)
❌ Complex context providers
❌ HOCs and wrapper components
❌ Custom state management
❌ Performance monitoring
❌ Error boundaries
❌ Metrics collection

## ✅ WHAT WE'RE DOING (Simple & Useful)
✅ Single hook that provides cached getToken
✅ Drop-in replacement for useAuth
✅ Same familiar API, just faster

## 📋 SIMPLE IMPLEMENTATION

### Create Simple Hook
**File**: `frontend/src/hooks/useOptimizedAuth.ts`

```typescript
import { useAuth } from '@clerk/nextjs'
import { useSimpleTokenCache } from './useSimpleTokenCache'

/**
 * Drop-in replacement for useAuth with token caching
 * Same API, just faster token retrieval
 */
export function useOptimizedAuth() {
  const auth = useAuth()
  const { getCachedToken } = useSimpleTokenCache()
  
  return {
    // All the normal useAuth properties
    ...auth,
    
    // Enhanced getToken with caching
    getToken: getCachedToken
  }
}
```

That's it! The entire module is 20 lines.

## 🔧 USAGE EXAMPLES

### Before (Slow)
```typescript
import { useAuth } from '@clerk/nextjs'

const MyComponent = () => {
  const { getToken } = useAuth()
  
  const handleAction = async () => {
    const token = await getToken() // Slow network call every time
    // Use token
  }
}
```

### After (Fast)
```typescript
import { useOptimizedAuth } from '../hooks/useOptimizedAuth'

const MyComponent = () => {
  const { getToken } = useOptimizedAuth() // Same API!
  
  const handleAction = async () => {
    const token = await getToken() // Fast cached retrieval
    // Use token
  }
}
```

### Migration Strategy
**Step 1**: Create the hook (5 minutes)
**Step 2**: Update imports in components:
```typescript
// Find and replace across codebase:
// FROM: import { useAuth } from '@clerk/nextjs'
// TO:   import { useOptimizedAuth as useAuth } from '../hooks/useOptimizedAuth'

// Components don't need to change - same API!
```

## 📊 COMPONENTS TO UPDATE (Optional)

These components can benefit from the optimized hook:
```typescript
// High-priority (frequently used):
- ChatInterface.tsx
- Navigation components
- Protected route components

// Low-priority (update when convenient):
- Profile components
- Settings components
- Other authenticated components
```

## ✅ ALTERNATIVE APPROACH (Even Simpler)

If you want even less code, just create a utility:

**File**: `frontend/src/utils/auth.ts`
```typescript
import { useAuth } from '@clerk/nextjs'
import { getCachedToken } from './simpleTokenCache'

/**
 * Get optimized auth functions
 */
export function getOptimizedAuth() {
  const auth = useAuth()
  
  return {
    ...auth,
    getToken: getCachedToken // Use the cached version
  }
}
```

## 🔧 INTEGRATION WITH MODULE A

```typescript
// This module depends on Module A's simple token cache
import { getCachedToken } from '../utils/simpleTokenCache'
// OR
import { useSimpleTokenCache } from '../hooks/useSimpleTokenCache'

// The hook just provides a nice developer experience
// for using the cached token functionality
```

## 📊 SUCCESS CRITERIA (SIMPLE)

### Must Achieve:
- [ ] **Hook works** with same API as useAuth
- [ ] **Code is <20 lines** total
- [ ] **Zero breaking changes** for existing components
- [ ] **Drop-in replacement** ready
- [ ] **Integration with Module A** working

### Developer Experience:
- **Familiar API** - same as useAuth
- **Easy migration** - just change import
- **Immediate benefit** - faster token retrieval

## ✅ VALIDATION

### Simple Test
```typescript
describe('useOptimizedAuth', () => {
  it('provides same API as useAuth', () => {
    const { result } = renderHook(() => useOptimizedAuth())
    
    // Should have all useAuth properties
    expect(result.current).toHaveProperty('isSignedIn')
    expect(result.current).toHaveProperty('user')
    expect(result.current).toHaveProperty('getToken')
    expect(typeof result.current.getToken).toBe('function')
  })
  
  it('uses cached token', async () => {
    const { result } = renderHook(() => useOptimizedAuth())
    
    // getToken should use the cached version
    const token = await result.current.getToken()
    expect(token).toBeDefined()
  })
})
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Complete:
- [ ] Hook provides same API as useAuth
- [ ] Uses cached token from Module A
- [ ] Code is simple and readable  
- [ ] Ready for component integration
- [ ] Takes <1 hour to implement

### Implementation Time: **1 HOUR MAX**
- 15 minutes: Write the hook
- 15 minutes: Write simple test
- 30 minutes: Test integration with Module A

## 🔄 DEPENDENCIES
**Module A** - Simple Token Cache must be completed first

## 📝 REPORTING FORMAT
```
📊 MODULE B - SIMPLE AUTH HOOK
⏱️ STATUS: [Complete/In Progress]
🎯 LINES OF CODE: X/20 max
✅ WORKS: [Yes/No]
🔗 MODULE A INTEGRATION: [Yes/No]
🔄 READY FOR COMPONENTS: [Yes/No]
⏰ TIME SPENT: X hours (max 1)
```

**WAIT FOR MODULE A** then start immediately!

---

**REMEMBER**: 
- Keep it simple - just wrap useAuth!
- Same API, just faster
- No complex state management
- 🔐 CLERK AUTHENTICATION ONLY!