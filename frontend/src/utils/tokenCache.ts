// Simple token cache - solves 8 getToken() calls problem
let cachedToken: string | null = null;
let tokenExpiry: number = 0;

export async function getCachedToken(getToken: () => Promise<string | null>): Promise<string | null> {
  const now = Date.now();
  
  // Return cached token if valid (5 minute cache)
  if (cachedToken && now < tokenExpiry) {
    return cachedToken;
  }
  
  // Fetch new token
  try {
    const token = await getToken();
    if (token) {
      cachedToken = token;
      tokenExpiry = now + (5 * 60 * 1000); // 5 minutes
    }
    return token;
  } catch (error) {
    console.error('Token fetch error:', error);
    return null;
  }
}

// Clear cache on logout
export function clearTokenCache() {
  cachedToken = null;
  tokenExpiry = 0;
}