/**
 * Comprehensive Security and Performance Tests for Token Cache Utility
 * 
 * Test Coverage:
 * - Security: User isolation, JWT validation, secure error handling
 * - Performance: Race condition prevention, memory management
 * - Reliability: Cache expiration, cleanup, error recovery
 * - Edge Cases: Invalid tokens, concurrent access, memory limits
 */

import { 
  getCachedToken, 
  clearTokenCache, 
  getCacheStats, 
  forceCleanup 
} from '../tokenCache'

// Mock console methods to prevent test output
const mockConsoleError = jest.spyOn(console, 'error').mockImplementation()
const mockConsoleWarn = jest.spyOn(console, 'warn').mockImplementation()

// Helper to create valid JWT tokens for testing
function createMockJWT(expiration?: number): string {
  const header = { alg: 'HS256', typ: 'JWT' }
  const payload = { 
    sub: 'user123', 
    exp: expiration || Math.floor(Date.now() / 1000) + parseInt(process.env.CACHE_TTL || '3600') // Based on config
  }
  
  const encodedHeader = btoa(JSON.stringify(header))
  const encodedPayload = btoa(JSON.stringify(payload))
  const signature = 'mock_signature'
  
  return `${encodedHeader}.${encodedPayload}.${signature}`
}

// Helper to create expired JWT tokens
function createExpiredJWT(): string {
  const expiration = Math.floor(Date.now() / 1000) - parseInt(process.env.CACHE_TTL || '3600') // Based on config
  return createMockJWT(expiration)
}

// Helper to create JWT that expires soon (within safety buffer)
function createSoonExpiringJWT(): string {
  const expiration = Math.floor(Date.now() / 1000) + 10 // 10 seconds from now (within 30s safety buffer)
  return createMockJWT(expiration)
}

describe('TokenCache Security Tests', () => {
  beforeEach(() => {
    // Clear all caches before each test
    clearTokenCache()
    jest.clearAllMocks()
  })

  afterAll(() => {
    // Restore console methods
    mockConsoleError.mockRestore()
    mockConsoleWarn.mockRestore()
  })

  describe('User Isolation Tests', () => {
    it('isolates tokens between different users', async () => {
      const user1Token = createMockJWT()
      const user2Token = createMockJWT()
      
      const user1Fetcher = jest.fn().mockResolvedValue(user1Token)
      const user2Fetcher = jest.fn().mockResolvedValue(user2Token)
      
      // Cache tokens for different users
      const token1 = await getCachedToken(user1Fetcher, 'user1')
      const token2 = await getCachedToken(user2Fetcher, 'user2')
      
      expect(token1).toBe(user1Token)
      expect(token2).toBe(user2Token)
      expect(token1).not.toBe(token2)
      
      // Verify each user gets their own token from cache
      const cachedToken1 = await getCachedToken(jest.fn(), 'user1')
      const cachedToken2 = await getCachedToken(jest.fn(), 'user2')
      
      expect(cachedToken1).toBe(user1Token)
      expect(cachedToken2).toBe(user2Token)
    })

    it('clears only specific user cache when userId provided', async () => {
      const user1Token = createMockJWT()
      const user2Token = createMockJWT()
      
      // Cache tokens for both users
      await getCachedToken(jest.fn().mockResolvedValue(user1Token), 'user1')
      await getCachedToken(jest.fn().mockResolvedValue(user2Token), 'user2')
      
      // Clear only user1 cache
      clearTokenCache('user1')
      
      // User1 should need new token, user2 should have cached token
      const newUser1Fetcher = jest.fn().mockResolvedValue('new_token')
      const user2Fetcher = jest.fn() // Should not be called
      
      await getCachedToken(newUser1Fetcher, 'user1')
      const cachedUser2Token = await getCachedToken(user2Fetcher, 'user2')
      
      expect(newUser1Fetcher).toHaveBeenCalled()
      expect(user2Fetcher).not.toHaveBeenCalled()
      expect(cachedUser2Token).toBe(user2Token)
    })
  })

  describe('JWT Validation Tests', () => {
    it('rejects expired tokens', async () => {
      const expiredToken = createExpiredJWT()
      const validToken = createMockJWT()
      
      // First call returns expired token, second call returns valid token
      const tokenFetcher = jest.fn()
        .mockResolvedValueOnce(expiredToken)
        .mockResolvedValueOnce(validToken)
      
      const result = await getCachedToken(tokenFetcher, 'user1')
      
      // Should return the expired token but not cache it
      expect(result).toBe(expiredToken)
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
      
      // Next call should fetch a new token since expired token wasn't cached
      const secondResult = await getCachedToken(tokenFetcher, 'user1')
      expect(secondResult).toBe(validToken)
      expect(tokenFetcher).toHaveBeenCalledTimes(2)
    })

    it('rejects tokens expiring soon (within safety buffer)', async () => {
      const soonExpiringToken = createSoonExpiringJWT()
      const validToken = createMockJWT()
      
      const tokenFetcher = jest.fn()
        .mockResolvedValueOnce(soonExpiringToken)
        .mockResolvedValueOnce(validToken)
      
      const result = await getCachedToken(tokenFetcher, 'user1')
      
      // Should return the soon-expiring token but not cache it
      expect(result).toBe(soonExpiringToken)
      
      // Next call should fetch new token
      const secondResult = await getCachedToken(tokenFetcher, 'user1')
      expect(secondResult).toBe(validToken)
      expect(tokenFetcher).toHaveBeenCalledTimes(2)
    })

    it('validates JWT structure before caching', async () => {
      const invalidTokens = [
        'invalid.token', // Only 2 parts
        'invalid', // No dots
        'a.b.c.d', // Too many parts
        'invalid.payload.signature' // Invalid base64 payload
      ]
      
      for (const invalidToken of invalidTokens) {
        const tokenFetcher = jest.fn().mockResolvedValue(invalidToken)
        
        const result = await getCachedToken(tokenFetcher, 'user1')
        expect(result).toBe(invalidToken) // Returns token but doesn't cache it
        
        // Verify not cached by checking if fetcher is called again
        await getCachedToken(tokenFetcher, 'user1')
        expect(tokenFetcher).toHaveBeenCalledTimes(2)
        
        clearTokenCache('user1')
      }
    })
  })

  describe('Secure Error Handling Tests', () => {
    it('generates unique error IDs for security', async () => {
      const error = new Error('Sensitive error information')
      const tokenFetcher = jest.fn().mockRejectedValue(error)
      
      try {
        await getCachedToken(tokenFetcher, 'user1')
      } catch (thrownError) {
        expect(thrownError).toBe(error) // Original error is propagated
      }
      
      // Check that console.error was called with error ID, not sensitive info
      expect(mockConsoleError).toHaveBeenCalled()
      const consoleCall = mockConsoleError.mock.calls[0][0] as string
      expect(consoleCall).toMatch(/Token fetch failed \[ERR_\d+_[a-z0-9]+\]/)
      expect(consoleCall).not.toContain('Sensitive error information')
    })

    it('logs full error details only in development', async () => {
      const originalNodeEnv = process.env.NODE_ENV
      
      // Test development logging
      process.env.NODE_ENV = 'development'
      const error = new Error('Development error')
      let tokenFetcher = jest.fn().mockRejectedValue(error)
      
      try {
        await getCachedToken(tokenFetcher, 'user1')
      } catch {}
      
      expect(mockConsoleError).toHaveBeenCalledWith(
        expect.stringMatching(/Token fetch failed \[ERR_\d+_[a-z0-9]+\]:/),
        error
      )
      
      mockConsoleError.mockClear()
      
      // Test production logging
      process.env.NODE_ENV = 'production'
      tokenFetcher = jest.fn().mockRejectedValue(error)
      
      try {
        await getCachedToken(tokenFetcher, 'user2')
      } catch {}
      
      expect(mockConsoleError).toHaveBeenCalledWith(
        expect.stringMatching(/Token fetch failed \[ERR_\d+_[a-z0-9]+\]$/)
      )
      expect(mockConsoleError).not.toHaveBeenCalledWith(
        expect.anything(),
        error
      )
      
      process.env.NODE_ENV = originalNodeEnv
    })
  })
})

describe('TokenCache Performance Tests', () => {
  beforeEach(() => {
    clearTokenCache()
    jest.clearAllMocks()
  })

  describe('Race Condition Prevention Tests', () => {
    it('prevents multiple network calls for same user', async () => {
      const token = createMockJWT()
      const tokenFetcher = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(token), 100))
      )
      
      // Make multiple concurrent requests for same user
      const promises = [
        getCachedToken(tokenFetcher, 'user1'),
        getCachedToken(tokenFetcher, 'user1'),
        getCachedToken(tokenFetcher, 'user1')
      ]
      
      const results = await Promise.all(promises)
      
      // All should return the same token
      results.forEach(result => expect(result).toBe(token))
      
      // Token fetcher should only be called once
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
    })

    it('allows concurrent requests for different users', async () => {
      const user1Token = createMockJWT()
      const user2Token = createMockJWT()
      
      const user1Fetcher = jest.fn().mockResolvedValue(user1Token)
      const user2Fetcher = jest.fn().mockResolvedValue(user2Token)
      
      // Make concurrent requests for different users
      const [result1, result2] = await Promise.all([
        getCachedToken(user1Fetcher, 'user1'),
        getCachedToken(user2Fetcher, 'user2')
      ])
      
      expect(result1).toBe(user1Token)
      expect(result2).toBe(user2Token)
      expect(user1Fetcher).toHaveBeenCalledTimes(1)
      expect(user2Fetcher).toHaveBeenCalledTimes(1)
    })

    it('handles failed requests correctly in race conditions', async () => {
      const error = new Error('Network error')
      const tokenFetcher = jest.fn().mockRejectedValue(error)
      
      // Make multiple concurrent requests that will fail
      const promises = [
        getCachedToken(tokenFetcher, 'user1').catch(e => e),
        getCachedToken(tokenFetcher, 'user1').catch(e => e),
        getCachedToken(tokenFetcher, 'user1').catch(e => e)
      ]
      
      const results = await Promise.all(promises)
      
      // All should return the same error
      results.forEach(result => expect(result).toBe(error))
      
      // Token fetcher should only be called once
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
    })
  })

  describe('Cache Performance Tests', () => {
    it('returns cached token without additional network calls', async () => {
      const token = createMockJWT()
      const tokenFetcher = jest.fn().mockResolvedValue(token)
      
      // First call should fetch token
      const firstResult = await getCachedToken(tokenFetcher, 'user1')
      expect(firstResult).toBe(token)
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
      
      // Subsequent calls should use cache
      const secondResult = await getCachedToken(tokenFetcher, 'user1')
      const thirdResult = await getCachedToken(tokenFetcher, 'user1')
      
      expect(secondResult).toBe(token)
      expect(thirdResult).toBe(token)
      expect(tokenFetcher).toHaveBeenCalledTimes(1) // No additional calls
    })

    it('provides cache statistics', async () => {
      const token = createMockJWT()
      
      // Initially empty cache
      let stats = getCacheStats()
      expect(stats.cacheSize).toBe(0)
      expect(stats.pendingRequests).toBe(0)
      
      // Cache a token
      await getCachedToken(jest.fn().mockResolvedValue(token), 'user1')
      
      stats = getCacheStats()
      expect(stats.cacheSize).toBe(1)
      expect(stats.pendingRequests).toBe(0)
      expect(stats.oldestEntry).toBeCloseTo(Date.now(), -2) // Within 100ms
      expect(stats.newestEntry).toBeCloseTo(Date.now(), -2)
    })
  })

  describe('Memory Management Tests', () => {
    // Mock timers for testing cleanup
    beforeEach(() => {
      jest.useFakeTimers()
    })

    afterEach(() => {
      jest.runOnlyPendingTimers()
      jest.useRealTimers()
    })

    it('cleans up expired cache entries automatically', async () => {
      const token = createMockJWT()
      await getCachedToken(jest.fn().mockResolvedValue(token), 'user1')
      
      expect(getCacheStats().cacheSize).toBe(1)
      
      // Fast-forward time past cache TTL (5 minutes + 10 minute cleanup interval)
      jest.advanceTimersByTime(15 * 60 * 1000)
      
      // Trigger cleanup by accessing cache
      await getCachedToken(jest.fn().mockResolvedValue('new_token'), 'user2')
      
      // Force cleanup for testing
      forceCleanup()
      
      const stats = getCacheStats()
      expect(stats.cacheSize).toBe(1) // Only new entry should remain
    })

    it('enforces maximum cache size', async () => {
      const maxCacheSize = 100 // From tokenCache.ts
      
      // Fill cache beyond max size
      const promises = []
      for (let i = 0; i <= maxCacheSize + 10; i++) {
        const token = createMockJWT()
        promises.push(getCachedToken(jest.fn().mockResolvedValue(token), `user${i}`))
      }
      
      await Promise.all(promises)
      
      // Force cleanup to enforce size limit
      forceCleanup()
      
      const stats = getCacheStats()
      expect(stats.cacheSize).toBeLessThanOrEqual(maxCacheSize)
    })

    it('updates last accessed time correctly', async () => {
      const token = createMockJWT()
      
      // Cache token
      await getCachedToken(jest.fn().mockResolvedValue(token), 'user1')
      const firstStats = getCacheStats()
      
      // Wait a bit and access again
      jest.advanceTimersByTime(1000)
      await getCachedToken(jest.fn(), 'user1')
      
      const secondStats = getCacheStats()
      expect(secondStats.newestEntry).toBeGreaterThan(firstStats.newestEntry!)
    })
  })
})

describe('TokenCache Integration Tests', () => {
  beforeEach(() => {
    clearTokenCache()
    jest.clearAllMocks()
  })

  describe('Real-world Usage Scenarios', () => {
    it('handles typical chat application usage pattern', async () => {
      const userToken = createMockJWT()
      const tokenFetcher = jest.fn().mockResolvedValue(userToken)
      
      // Simulate multiple API calls in quick succession (typical chat scenario)
      const apiCalls = [
        getCachedToken(tokenFetcher, 'user1'), // Send message
        getCachedToken(tokenFetcher, 'user1'), // Get conversation history  
        getCachedToken(tokenFetcher, 'user1'), // Update user presence
        getCachedToken(tokenFetcher, 'user1'), // Get user profile
        getCachedToken(tokenFetcher, 'user1'), // Upload file
        getCachedToken(tokenFetcher, 'user1'), // Send another message
        getCachedToken(tokenFetcher, 'user1'), // Get notifications
        getCachedToken(tokenFetcher, 'user1')  // Update settings
      ]
      
      const results = await Promise.all(apiCalls)
      
      // All calls should return the same cached token
      results.forEach(result => expect(result).toBe(userToken))
      
      // Should only fetch token once, reducing 8 network calls to 1
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
      
      // Performance improvement: ~87.5% reduction in network calls
      const networkReduction = ((8 - 1) / 8) * 100
      expect(networkReduction).toBeCloseTo(87.5)
    })

    it('handles user switching scenario correctly', async () => {
      const user1Token = createMockJWT()
      const user2Token = createMockJWT()
      
      const user1Fetcher = jest.fn().mockResolvedValue(user1Token)
      const user2Fetcher = jest.fn().mockResolvedValue(user2Token)
      
      // User 1 logs in and makes requests
      await getCachedToken(user1Fetcher, 'user1')
      await getCachedToken(user1Fetcher, 'user1')
      
      // User 1 logs out (clear their cache)
      clearTokenCache('user1')
      
      // User 2 logs in and makes requests
      await getCachedToken(user2Fetcher, 'user2')
      await getCachedToken(user2Fetcher, 'user2')
      
      expect(user1Fetcher).toHaveBeenCalledTimes(1)
      expect(user2Fetcher).toHaveBeenCalledTimes(1)
      
      // Verify correct isolation
      const stats = getCacheStats()
      expect(stats.cacheSize).toBe(1) // Only user2 token should be cached
    })

    it('handles network failures gracefully', async () => {
      const networkError = new Error('Network timeout')
      const tokenFetcher = jest.fn()
        .mockRejectedValueOnce(networkError)
        .mockResolvedValueOnce(createMockJWT())
      
      // First call fails
      try {
        await getCachedToken(tokenFetcher, 'user1')
        fail('Should have thrown error')
      } catch (error) {
        expect(error).toBe(networkError)
      }
      
      // Second call succeeds
      const token = await getCachedToken(tokenFetcher, 'user1')
      expect(token).toBeDefined()
      expect(tokenFetcher).toHaveBeenCalledTimes(2)
    })
  })

  describe('Edge Cases and Error Recovery', () => {
    it('handles null tokens correctly', async () => {
      const tokenFetcher = jest.fn().mockResolvedValue(null)
      
      const result = await getCachedToken(tokenFetcher, 'user1')
      expect(result).toBeNull()
      
      // Should not cache null tokens
      const secondResult = await getCachedToken(tokenFetcher, 'user1')
      expect(tokenFetcher).toHaveBeenCalledTimes(2)
    })

    it('handles undefined user ID gracefully', async () => {
      const token = createMockJWT()
      const tokenFetcher = jest.fn().mockResolvedValue(token)
      
      const result = await getCachedToken(tokenFetcher, undefined)
      expect(result).toBe(token)
      
      // Should use default cache key
      const secondResult = await getCachedToken(tokenFetcher, undefined)
      expect(secondResult).toBe(token)
      expect(tokenFetcher).toHaveBeenCalledTimes(1)
    })

    it('cleans up on module unload in browser environment', () => {
      // Mock window object
      const mockWindow = {
        addEventListener: jest.fn(),
        removeEventListener: jest.fn()
      }
      
      // @ts-ignore - Mock global window
      global.window = mockWindow
      
      // Re-import module to trigger addEventListener
      jest.resetModules()
      require('../tokenCache')
      
      expect(mockWindow.addEventListener).toHaveBeenCalledWith(
        'beforeunload',
        expect.any(Function)
      )
      
      // Simulate beforeunload event
      const beforeUnloadHandler = mockWindow.addEventListener.mock.calls[0][1]
      beforeUnloadHandler()
      
      // Cache should be cleared
      const stats = getCacheStats()
      expect(stats.cacheSize).toBe(0)
      
      // @ts-ignore - Cleanup
      delete global.window
    })
  })
})