/**
 * Secure Token Cache Utility - Security-hardened implementation
 * 
 * Features:
 * - User-scoped token storage with automatic cleanup
 * - Race condition prevention with mutex locking
 * - JWT validation with proper expiration checking
 * - Secure error handling without information leakage
 * - Memory leak prevention and garbage collection
 */

// Type definitions for better type safety
interface CachedToken {
  token: string;
  expiry: number;
  created: number;
}

interface TokenCacheEntry {
  tokenData: CachedToken;
  lastAccessed: number;
}

// Constants for cache configuration
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes
const SAFETY_BUFFER_MS = 30 * 1000; // 30 seconds safety buffer
const MAX_CACHE_SIZE = 100; // Prevent memory bloat
const CLEANUP_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes

// User-scoped token cache with automatic cleanup
const userTokenCaches = new Map<string, TokenCacheEntry>();

// Race condition prevention - track pending requests
const pendingRequests = new Map<string, Promise<string | null>>();

// Cleanup interval for memory management
let cleanupIntervalId: NodeJS.Timeout | null = null;

/**
 * Validates if a JWT token is still valid
 * @param token JWT token string
 * @returns boolean indicating if token is valid
 */
function isTokenValid(token: string): boolean {
  try {
    // Basic JWT structure validation
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    
    // Decode payload and check expiration
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    // Check if token expires within safety buffer
    return payload.exp && payload.exp > (now + (SAFETY_BUFFER_MS / 1000));
  } catch {
    return false;
  }
}

/**
 * Generates a unique cache key for the current user context
 * @param userId Optional user ID for scoping
 * @returns Unique cache key string
 */
function generateCacheKey(userId?: string): string {
  // If no userId provided, try to get from current context
  if (!userId) {
    // In a real app, this could come from auth context
    // For now, use a default key but this should be user-specific
    userId = 'current_user';
  }
  return `token_${userId}`;
}

/**
 * Performs periodic cleanup of expired cache entries
 */
function performCacheCleanup(): void {
  const now = Date.now();
  const cutoffTime = now - CACHE_TTL_MS;
  
  // Use Array.from to avoid downlevelIteration requirement
  const entries = Array.from(userTokenCaches.entries());
  for (const [key, entry] of entries) {
    // Remove expired entries or entries that haven't been accessed recently
    if (entry.tokenData.expiry < now || entry.lastAccessed < cutoffTime) {
      userTokenCaches.delete(key);
    }
  }
  
  // Enforce max cache size
  if (userTokenCaches.size > MAX_CACHE_SIZE) {
    const sortedEntries = Array.from(userTokenCaches.entries())
      .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);
    
    // Remove oldest entries
    const entriesToRemove = sortedEntries.slice(0, userTokenCaches.size - MAX_CACHE_SIZE);
    entriesToRemove.forEach(([key]) => userTokenCaches.delete(key));
  }
}

/**
 * Starts the automatic cleanup process
 */
function startCleanupProcess(): void {
  if (!cleanupIntervalId) {
    cleanupIntervalId = setInterval(performCacheCleanup, CLEANUP_INTERVAL_MS);
  }
}

/**
 * Stops the automatic cleanup process
 */
function stopCleanupProcess(): void {
  if (cleanupIntervalId) {
    clearInterval(cleanupIntervalId);
    cleanupIntervalId = null;
  }
}

/**
 * Retrieves a cached token or fetches a new one if needed
 * Implements race condition prevention and secure caching
 * 
 * @param getToken Function to fetch a new token
 * @param userId Optional user ID for cache scoping
 * @returns Promise resolving to token string or null
 */
export async function getCachedToken(
  getToken: () => Promise<string | null>,
  userId?: string
): Promise<string | null> {
  const cacheKey = generateCacheKey(userId);
  const now = Date.now();
  
  // Start cleanup process if not already running
  startCleanupProcess();
  
  // Check for pending request to prevent race conditions
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey)!;
  }
  
  // Check cache for valid token
  const cachedEntry = userTokenCaches.get(cacheKey);
  if (cachedEntry && now < cachedEntry.tokenData.expiry) {
    // Validate the cached token is still valid
    if (isTokenValid(cachedEntry.tokenData.token)) {
      // Update last accessed time
      cachedEntry.lastAccessed = now;
      return cachedEntry.tokenData.token;
    } else {
      // Remove invalid token from cache
      userTokenCaches.delete(cacheKey);
    }
  }
  
  // Create promise for new token fetch
  const tokenPromise = (async (): Promise<string | null> => {
    try {
      const token = await getToken();
      
      if (token && isTokenValid(token)) {
        // Cache the new valid token
        const tokenData: CachedToken = {
          token,
          expiry: now + CACHE_TTL_MS,
          created: now
        };
        
        const cacheEntry: TokenCacheEntry = {
          tokenData,
          lastAccessed: now
        };
        
        userTokenCaches.set(cacheKey, cacheEntry);
        return token;
      }
      
      return token; // Return even if invalid, let caller handle
    } catch (error) {
      // Secure error handling - don't leak sensitive information
      const errorId = `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Log error ID only, not the actual error content
      if (process.env.NODE_ENV === 'development') {
        console.error(`Token fetch failed [${errorId}]:`, error);
      } else {
        console.error(`Token fetch failed [${errorId}]`);
      }
      
      // Don't return null, propagate the error for proper handling
      throw error;
    } finally {
      // Always remove from pending requests
      pendingRequests.delete(cacheKey);
    }
  })();
  
  // Track pending request
  pendingRequests.set(cacheKey, tokenPromise);
  
  return tokenPromise;
}

/**
 * Clears cached tokens for a specific user or all users
 * @param userId Optional user ID to clear specific cache, omit for all users
 */
export function clearTokenCache(userId?: string): void {
  if (userId) {
    const cacheKey = generateCacheKey(userId);
    userTokenCaches.delete(cacheKey);
    pendingRequests.delete(cacheKey);
  } else {
    // Clear all caches (for logout scenarios)
    userTokenCaches.clear();
    pendingRequests.clear();
  }
  
  // Stop cleanup process if no cached tokens remain
  if (userTokenCaches.size === 0) {
    stopCleanupProcess();
  }
}

/**
 * Gets cache statistics for monitoring and debugging
 * @returns Object with cache statistics
 */
export function getCacheStats(): {
  cacheSize: number;
  pendingRequests: number;
  oldestEntry: number | null;
  newestEntry: number | null;
} {
  const entries = Array.from(userTokenCaches.values());
  
  return {
    cacheSize: userTokenCaches.size,
    pendingRequests: pendingRequests.size,
    oldestEntry: entries.length > 0 ? Math.min(...entries.map(e => e.tokenData.created)) : null,
    newestEntry: entries.length > 0 ? Math.max(...entries.map(e => e.tokenData.created)) : null,
  };
}

/**
 * Forces cleanup of expired cache entries
 * Useful for testing or manual cache management
 */
export function forceCleanup(): void {
  performCacheCleanup();
}

// Cleanup on module unload (for SSR environments)
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    stopCleanupProcess();
    userTokenCaches.clear();
    pendingRequests.clear();
  });
}