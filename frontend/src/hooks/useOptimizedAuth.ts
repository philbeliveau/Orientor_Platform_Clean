import { useAuth, useUser } from '@clerk/nextjs'
import { useEffect, useCallback, useMemo } from 'react'
import { getCachedToken, clearTokenCache, getCacheStats } from '../utils/tokenCache'

/**
 * Enhanced type definitions for better TypeScript safety
 */
interface GetTokenOptions {
  template?: string;
  leewayInSeconds?: number;
  skipCache?: boolean;
  throwOnError?: boolean;
}

type OptimizedAuthReturn = ReturnType<typeof useAuth> & {
  getToken: (options?: GetTokenOptions) => Promise<string | null>;
  getCacheStats: () => ReturnType<typeof getCacheStats>;
  clearUserCache: () => void;
  forceTokenRefresh: () => Promise<string | null>;
}

/**
 * Performance-optimized and security-hardened drop-in replacement for useAuth
 * 
 * Features:
 * - Intelligent token caching with race condition prevention
 * - User-scoped cache isolation for security
 * - Automatic cache invalidation on session changes
 * - Enhanced TypeScript types for better developer experience
 * - Cache monitoring and statistics
 * - Force refresh capability for time-sensitive operations
 */
export function useOptimizedAuth(): OptimizedAuthReturn {
  const auth = useAuth()
  const { user } = useUser()
  
  // Get user ID for cache scoping
  const userId = useMemo(() => user?.id || auth.userId || undefined, [user?.id, auth.userId])
  
  // Clear cache when user signs out or changes
  useEffect(() => {
    if (!auth.isSignedIn || !auth.isLoaded) {
      // Clear all caches on sign out or during loading
      clearTokenCache()
    }
  }, [auth.isSignedIn, auth.isLoaded])
  
  // Clear user-specific cache when user changes
  useEffect(() => {
    // This effect runs when the user ID changes (different user logs in)
    // We don't clear the cache here as it will be handled by the userId parameter
    // in getCachedToken, but we could add user switching logic if needed
  }, [userId])
  
  // Enhanced getToken with intelligent caching
  const getToken = useCallback(async (options?: GetTokenOptions): Promise<string | null> => {
    // Always bypass cache if skipCache is explicitly requested
    if (options?.skipCache) {
      return auth.getToken(options)
    }
    
    // If user is not signed in, don't attempt caching
    if (!auth.isSignedIn || !auth.isLoaded) {
      return null
    }
    
    try {
      // Use cached token with user-scoped storage
      return await getCachedToken(() => auth.getToken(options), userId)
    } catch (error) {
      // If caching fails, fall back to direct token fetch
      console.warn('Token cache failed, falling back to direct fetch')
      return auth.getToken(options)
    }
  }, [auth, userId])
  
  // Force refresh capability for time-sensitive operations
  const forceTokenRefresh = useCallback(async (): Promise<string | null> => {
    // Clear user-specific cache first
    if (userId) {
      clearTokenCache(userId)
    }
    
    // Fetch fresh token
    return auth.getToken({ skipCache: true })
  }, [auth, userId])
  
  // Clear user-specific cache manually
  const clearUserCache = useCallback((): void => {
    clearTokenCache(userId)
  }, [userId])
  
  // Get cache statistics for monitoring
  const getCacheStatsWrapper = useCallback(() => {
    return getCacheStats()
  }, [])
  
  // Return enhanced auth object with same API plus optimizations
  return {
    // All the normal useAuth properties and methods
    ...auth,
    
    // Enhanced getToken with caching
    getToken,
    
    // Additional utility methods
    getCacheStats: getCacheStatsWrapper,
    clearUserCache,
    forceTokenRefresh,
  }
}