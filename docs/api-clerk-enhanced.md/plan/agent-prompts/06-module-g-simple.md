# Agent Prompt: Module G - Chat Interface Token Reuse (SIMPLIFIED)

## 🎯 MISSION: SOLVE THE CORE PROBLEM
**Problem**: ChatInterface makes 8 `getToken()` calls per interaction → 2-5 second delays
**Solution**: Get token once, reuse for all 8 operations
**Complexity**: MINIMAL - Change 8 lines to reuse 1 cached token

## 🚨 WHAT WE'RE NOT DOING (Over-Engineering)
❌ Complex optimistic UI systems
❌ Elaborate error boundaries  
❌ Performance monitoring dashboards
❌ Complex state management
❌ Custom loading systems
❌ Extensive retry logic

## ✅ WHAT WE'RE DOING (Simple & Effective)
✅ Find the 8 getToken() calls in ChatInterface
✅ Replace with cached token from Module A
✅ Immediate 87.5% reduction in auth calls

## 📋 FIND THE CURRENT PROBLEM

### Step 1: Locate ChatInterface
```bash
find frontend/src -name "*ChatInterface*" -type f
grep -n "getToken()" frontend/src/components/chat/ChatInterface.tsx
```

### Step 2: Find the 8 Token Calls
Look for these patterns in ChatInterface.tsx:
```typescript
// CURRENT PROBLEMS (find these exact patterns):
const token = await getToken(); // Message sending (~line 194)
const token = await getToken(); // File upload (~line 309)  
const token = await getToken(); // Fallback token (~line 359)
const token = await getToken(); // Stream init (~line 406)
const token = await getToken(); // Save conversation (~line 709)
const token = await getToken(); // Delete conversation (~line 739)
const token = await getToken(); // Share conversation (~line 761)
const token = await getToken(); // Export conversation (~line 811)
```

## 🔧 SIMPLE SOLUTION

### Step 1: Update Imports
```typescript
// BEFORE:
import { useAuth } from '@clerk/nextjs'

// AFTER: 
import { useOptimizedAuth } from '../../hooks/useOptimizedAuth' // From Module B
// OR if Module B not ready:
import { getCachedToken } from '../../utils/simpleTokenCache' // From Module A
```

### Step 2: Cache Token at Component Level
```typescript
const ChatInterface = () => {
  // SIMPLE APPROACH - cache token in component state
  const [cachedToken, setCachedToken] = useState<string | null>(null)
  const { getToken } = useAuth() // Keep existing auth
  
  // Get token once when component mounts or user authenticates
  useEffect(() => {
    const initToken = async () => {
      if (isSignedIn && !cachedToken) {
        const token = await getToken()
        setCachedToken(token)
      }
    }
    initToken()
  }, [isSignedIn, cachedToken])
  
  // Helper function to get token
  const getTokenForOperation = async () => {
    if (cachedToken) return cachedToken
    const token = await getToken()
    setCachedToken(token)
    return token
  }
  
  // Rest of component...
}
```

### Step 3: Replace All 8 Token Calls
```typescript
// BEFORE (8 separate calls):
const handleSendMessage = async () => {
  const token = await getToken(); // SLOW
  // send message logic
}

const handleFileUpload = async () => {
  const token = await getToken(); // SLOW  
  // upload logic
}

// ... 6 more similar patterns

// AFTER (1 cached token):
const handleSendMessage = async () => {
  const token = await getTokenForOperation(); // FAST
  // send message logic
}

const handleFileUpload = async () => {
  const token = await getTokenForOperation(); // FAST
  // upload logic  
}

// ... same pattern for all 8 operations
```

## 📋 EVEN SIMPLER APPROACH

If you want the absolute minimum change:

```typescript
const ChatInterface = () => {
  // Just cache at the top level
  const tokenRef = useRef<string | null>(null)
  const { getToken } = useAuth()
  
  const getOrCacheToken = async () => {
    if (tokenRef.current) return tokenRef.current
    
    const token = await getToken()
    tokenRef.current = token
    
    // Clear cache after 5 minutes
    setTimeout(() => {
      tokenRef.current = null
    }, 5 * 60 * 1000)
    
    return token
  }
  
  // Then replace ALL 8 calls:
  // FROM: const token = await getToken()
  // TO:   const token = await getOrCacheToken()
}
```

## 🔧 SPECIFIC CHANGES NEEDED

### Find and Replace These Exact Patterns:

```typescript
// 1. Message sending (find ~line 194):
// CHANGE FROM:
const token = await getToken();
const response = await fetch('/api/v1/chat/messages', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// CHANGE TO:
const token = await getOrCacheToken(); // Same cached token!
const response = await fetch('/api/v1/chat/messages', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

Apply the same pattern to all 8 locations:
- File upload handler
- Fallback token retrieval  
- Stream initialization
- Save conversation
- Delete conversation
- Share conversation
- Export conversation

## ✅ VALIDATION

### Simple Test
```typescript
describe('ChatInterface Token Optimization', () => {
  it('reuses token for multiple operations', async () => {
    const mockGetToken = jest.fn().mockResolvedValue('mock-token')
    
    render(<ChatInterface />)
    
    // Perform multiple operations
    await userEvent.click(screen.getByText('Send Message'))
    await userEvent.click(screen.getByText('Upload File'))
    await userEvent.click(screen.getByText('Save Chat'))
    
    // Should only call getToken once!
    expect(mockGetToken).toHaveBeenCalledTimes(1)
  })
})
```

### Performance Measurement
```typescript
// Add simple timing to see the improvement
const ChatInterface = () => {
  const handleSendMessage = async () => {
    const startTime = performance.now()
    
    const token = await getOrCacheToken()
    // ... send message
    
    const duration = performance.now() - startTime
    console.log(`Message send time: ${duration}ms`) // Should be <200ms
  }
}
```

## 🚨 CRITICAL SUCCESS CRITERIA

### Must Achieve:
- [ ] **Find all 8 getToken() calls** in ChatInterface
- [ ] **Replace with cached version** that reuses token
- [ ] **Token is cached** for 5 minutes  
- [ ] **All chat functions still work** correctly
- [ ] **Performance improvement** is noticeable

### Expected Results:
- **8 getToken() calls → 1 cached token** = 87.5% reduction
- **Message send time: <200ms** (from 500-1500ms)
- **File upload start: <100ms** (from 300-800ms)
- **No more "platform feels slow"** complaints

### Implementation Time: **2 HOURS MAX**
- 30 minutes: Find the 8 token call locations
- 60 minutes: Implement caching solution
- 30 minutes: Test all functionality works

## 🔄 DEPENDENCIES
**Module A** - Simple Token Cache (recommended but not required)
**Module B** - Simple Auth Hook (optional, makes it easier)

## 💡 PRIORITY

**THIS IS THE HIGHEST PRIORITY MODULE**

This single change will solve the user's core complaint:
- "Platform feels so slow"
- "Loading every time I click something"

Everything else is secondary to fixing this.

## 📝 REPORTING FORMAT
```
📊 MODULE G - CHAT TOKEN OPTIMIZATION  
⏱️ STATUS: [Complete/In Progress]
🎯 TOKEN CALLS FOUND: X/8 locations
✅ CACHING IMPLEMENTED: [Yes/No]
📈 PERFORMANCE IMPROVEMENT: Xms reduction
🔄 ALL FUNCTIONS WORK: [Yes/No]
⏰ TIME SPENT: X hours (max 2)
```

**START AS SOON AS MODULE A IS READY** - This is the most important fix!

---

**REMEMBER**: 
- **This is THE core problem** - solve it simply
- **8 calls → 1 call = 87.5% reduction**
- **Focus on results, not complexity**
- 🔐 **CLERK AUTHENTICATION ONLY**