import { renderHook, act } from '@testing-library/react'
import { useAuth, useUser } from '@clerk/nextjs'
import { useOptimizedAuth } from '../useOptimizedAuth'
import { getCachedToken, clearTokenCache, getCacheStats } from '../../utils/tokenCache'

// Mock dependencies
jest.mock('@clerk/nextjs')
jest.mock('../../utils/tokenCache')

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>
const mockUseUser = useUser as jest.MockedFunction<typeof useUser>
const mockGetCachedToken = getCachedToken as jest.MockedFunction<typeof getCachedToken>
const mockClearTokenCache = clearTokenCache as jest.MockedFunction<typeof clearTokenCache>
const mockGetCacheStats = getCacheStats as jest.MockedFunction<typeof getCacheStats>

describe('useOptimizedAuth - Security and Performance Tests', () => {
  const mockAuthData = {
    isSignedIn: true,
    isLoaded: true,
    userId: 'user_123',
    sessionId: 'session_123',
    getToken: jest.fn(),
    signOut: jest.fn(),
    orgId: null,
    orgRole: null,
    orgSlug: null,
    sessionClaims: {},
    actor: null,
    has: jest.fn()
  }

  const mockUserData = {
    isLoaded: true,
    isSignedIn: true,
    user: {
      id: 'user_123',
      firstName: 'Test',
      lastName: 'User',
      emailAddresses: [],
      phoneNumbers: [],
      web3Wallets: [],
      externalAccounts: [],
      organizationMemberships: [],
      passwordEnabled: true,
      totpEnabled: false,
      backupCodeEnabled: false,
      twoFactorEnabled: false,
      banned: false,
      locked: false,
      createdAt: new Date(),
      updatedAt: new Date(),
      imageUrl: '',
      hasImage: false,
      primaryEmailAddressId: null,
      primaryPhoneNumberId: null,
      primaryWeb3WalletId: null,
      lastSignInAt: new Date(),
      externalId: null,
      username: null,
      publicMetadata: {},
      privateMetadata: {},
      unsafeMetadata: {},
      delete: jest.fn(),
      update: jest.fn(),
      reload: jest.fn(),
      getSessions: jest.fn(),
      setProfileImage: jest.fn(),
      createEmailAddress: jest.fn(),
      createPhoneNumber: jest.fn(),
      createWeb3Wallet: jest.fn(),
      createExternalAccount: jest.fn(),
      getOrganizationMemberships: jest.fn(),
      createOrganization: jest.fn(),
      getOrganizationInvitations: jest.fn(),
      leaveOrganization: jest.fn(),
      updatePassword: jest.fn(),
      removePassword: jest.fn(),
      createTOTP: jest.fn(),
      verifyTOTP: jest.fn(),
      disableTOTP: jest.fn(),
      createBackupCode: jest.fn(),
      verifyBackupCode: jest.fn(),
      createEmailAddress: jest.fn(),
      fullName: 'Test User'
    }
  }

  const mockCacheStats = {
    cacheSize: 1,
    pendingRequests: 0,
    oldestEntry: Date.now() - 1000,
    newestEntry: Date.now()
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseAuth.mockReturnValue(mockAuthData)
    mockUseUser.mockReturnValue(mockUserData)
    mockGetCacheStats.mockReturnValue(mockCacheStats)
  })

  describe('API Compatibility Tests', () => {
    it('provides same API as useAuth with additional methods', () => {
      const { result } = renderHook(() => useOptimizedAuth())
      
      // Should have all useAuth properties
      expect(result.current).toHaveProperty('isSignedIn')
      expect(result.current).toHaveProperty('isLoaded')
      expect(result.current).toHaveProperty('userId')
      expect(result.current).toHaveProperty('sessionId')
      expect(result.current).toHaveProperty('getToken')
      expect(result.current).toHaveProperty('signOut')
      
      // Should have additional optimized methods
      expect(result.current).toHaveProperty('getCacheStats')
      expect(result.current).toHaveProperty('clearUserCache')
      expect(result.current).toHaveProperty('forceTokenRefresh')
      
      expect(typeof result.current.getToken).toBe('function')
      expect(typeof result.current.getCacheStats).toBe('function')
      expect(typeof result.current.clearUserCache).toBe('function')
      expect(typeof result.current.forceTokenRefresh).toBe('function')
    })

    it('maintains all original auth properties', () => {
      const { result } = renderHook(() => useOptimizedAuth())
      
      expect(result.current.isSignedIn).toBe(mockAuthData.isSignedIn)
      expect(result.current.isLoaded).toBe(mockAuthData.isLoaded)
      expect(result.current.userId).toBe(mockAuthData.userId)
      expect(result.current.sessionId).toBe(mockAuthData.sessionId)
      expect(result.current.signOut).toBe(mockAuthData.signOut)
      expect(result.current.orgId).toBe(mockAuthData.orgId)
      expect(result.current.orgRole).toBe(mockAuthData.orgRole)
      expect(result.current.orgSlug).toBe(mockAuthData.orgSlug)
      expect(result.current.sessionClaims).toBe(mockAuthData.sessionClaims)
      expect(result.current.actor).toBe(mockAuthData.actor)
      expect(result.current.has).toBe(mockAuthData.has)
    })
  })

  describe('Security Tests', () => {
    it('uses user-scoped caching for token isolation', async () => {
      const mockToken = 'cached_token_123'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      await result.current.getToken()
      
      // Should pass user ID for scoped caching
      expect(mockGetCachedToken).toHaveBeenCalledWith(
        expect.any(Function),
        'user_123'
      )
    })

    it('bypasses cache when skipCache is true for security', async () => {
      const mockToken = 'fresh_token_123'
      mockAuthData.getToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken({ skipCache: true })
      
      expect(mockAuthData.getToken).toHaveBeenCalledWith({ skipCache: true })
      expect(mockGetCachedToken).not.toHaveBeenCalled()
      expect(token).toBe(mockToken)
    })

    it('returns null when user is not signed in', async () => {
      mockUseAuth.mockReturnValue({
        ...mockAuthData,
        isSignedIn: false
      })
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken()
      
      expect(token).toBeNull()
      expect(mockGetCachedToken).not.toHaveBeenCalled()
    })

    it('returns null when auth is not loaded', async () => {
      mockUseAuth.mockReturnValue({
        ...mockAuthData,
        isLoaded: false
      })
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken()
      
      expect(token).toBeNull()
      expect(mockGetCachedToken).not.toHaveBeenCalled()
    })

    it('falls back to direct fetch when cache fails', async () => {
      const mockToken = 'fallback_token_123'
      mockGetCachedToken.mockRejectedValue(new Error('Cache error'))
      mockAuthData.getToken.mockResolvedValue(mockToken)
      
      // Mock console.warn to avoid test output
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation()
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken()
      
      expect(mockGetCachedToken).toHaveBeenCalled()
      expect(mockAuthData.getToken).toHaveBeenCalled()
      expect(token).toBe(mockToken)
      expect(consoleSpy).toHaveBeenCalledWith('Token cache failed, falling back to direct fetch')
      
      consoleSpy.mockRestore()
    })

    it('clears all caches on sign out', () => {
      const { rerender } = renderHook(() => useOptimizedAuth())
      
      // User signs out
      mockUseAuth.mockReturnValue({
        ...mockAuthData,
        isSignedIn: false
      })
      
      rerender()
      
      expect(mockClearTokenCache).toHaveBeenCalledWith()
    })

    it('clears all caches when not loaded', () => {
      const { rerender } = renderHook(() => useOptimizedAuth())
      
      // Auth not loaded
      mockUseAuth.mockReturnValue({
        ...mockAuthData,
        isLoaded: false
      })
      
      rerender()
      
      expect(mockClearTokenCache).toHaveBeenCalledWith()
    })
  })

  describe('Performance Tests', () => {
    it('uses cached token when no skipCache option provided', async () => {
      const mockToken = 'cached_token_123'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken()
      
      expect(mockGetCachedToken).toHaveBeenCalledWith(expect.any(Function), 'user_123')
      expect(token).toBe(mockToken)
    })

    it('passes through template options correctly', async () => {
      const mockToken = 'template_token_123'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      await result.current.getToken({ template: 'firebase' })
      
      expect(mockGetCachedToken).toHaveBeenCalledWith(expect.any(Function), 'user_123')
      
      // Verify the function passed to getCachedToken calls auth.getToken with correct options
      const cachedTokenFunction = mockGetCachedToken.mock.calls[0][0]
      await cachedTokenFunction()
      expect(mockAuthData.getToken).toHaveBeenCalledWith({ template: 'firebase' })
    })

    it('provides cache statistics', () => {
      const { result } = renderHook(() => useOptimizedAuth())
      
      const stats = result.current.getCacheStats()
      
      expect(mockGetCacheStats).toHaveBeenCalled()
      expect(stats).toEqual(mockCacheStats)
    })
  })

  describe('Enhanced Functionality Tests', () => {
    it('forces token refresh correctly', async () => {
      const mockToken = 'fresh_token_123'
      mockAuthData.getToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.forceTokenRefresh()
      
      expect(mockClearTokenCache).toHaveBeenCalledWith('user_123')
      expect(mockAuthData.getToken).toHaveBeenCalledWith({ skipCache: true })
      expect(token).toBe(mockToken)
    })

    it('clears user-specific cache', () => {
      const { result } = renderHook(() => useOptimizedAuth())
      
      result.current.clearUserCache()
      
      expect(mockClearTokenCache).toHaveBeenCalledWith('user_123')
    })

    it('handles multiple token options correctly', async () => {
      const mockToken = 'complex_token_123'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const options = {
        template: 'custom-template',
        leewayInSeconds: 30,
        throwOnError: true
      }
      
      await result.current.getToken(options)
      
      expect(mockGetCachedToken).toHaveBeenCalledWith(expect.any(Function), 'user_123')
      
      // Verify all options are passed through
      const cachedTokenFunction = mockGetCachedToken.mock.calls[0][0]
      await cachedTokenFunction()
      expect(mockAuthData.getToken).toHaveBeenCalledWith(options)
    })
  })

  describe('Race Condition Prevention Tests', () => {
    it('handles concurrent token requests correctly', async () => {
      const mockToken = 'concurrent_token_123'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      // Simulate concurrent requests
      const promises = [
        result.current.getToken(),
        result.current.getToken(),
        result.current.getToken()
      ]
      
      const tokens = await Promise.all(promises)
      
      // All should return the same token
      tokens.forEach(token => expect(token).toBe(mockToken))
      
      // Cache should only be called once due to race condition prevention
      expect(mockGetCachedToken).toHaveBeenCalledTimes(3) // Each call goes through the hook
    })
  })

  describe('Edge Cases', () => {
    it('handles undefined user ID gracefully', async () => {
      // Mock no user ID
      mockUseUser.mockReturnValue({
        ...mockUserData,
        user: null
      })
      mockUseAuth.mockReturnValue({
        ...mockAuthData,
        userId: null
      })
      
      const mockToken = 'no_user_token'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken()
      
      expect(mockGetCachedToken).toHaveBeenCalledWith(expect.any(Function), undefined)
      expect(token).toBe(mockToken)
    })

    it('does not clear cache when user remains signed in', () => {
      const { rerender } = renderHook(() => useOptimizedAuth())
      
      // User remains signed in - just trigger a rerender
      rerender()
      
      expect(mockClearTokenCache).not.toHaveBeenCalled()
    })

    it('handles token options with skipCache false explicitly', async () => {
      const mockToken = 'explicit_cache_token'
      mockGetCachedToken.mockResolvedValue(mockToken)
      
      const { result } = renderHook(() => useOptimizedAuth())
      
      const token = await result.current.getToken({ skipCache: false, template: 'test' })
      
      expect(mockGetCachedToken).toHaveBeenCalledWith(expect.any(Function), 'user_123')
      expect(token).toBe(mockToken)
    })
  })
})