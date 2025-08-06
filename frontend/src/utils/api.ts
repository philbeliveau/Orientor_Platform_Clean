/**
 * API utility functions for consistent API URL handling
 */

// Get the API URL from environment variables with production fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Clean API URL (remove trailing spaces)
export const apiUrl = API_URL.trim();

// Helper to build full endpoint URLs
export const endpoint = (path: string): string => {
  // Remove /api prefix if present since our backend doesn't use it
  const cleanPath = path.replace('/api/', '/');
  
  // Make sure path starts with a slash
  const formattedPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`;
  
  return `${apiUrl}${formattedPath}`;
};

// Authentication helper for Clerk integration
export const getAuthHeader = async (getToken?: () => Promise<string | null>): Promise<Record<string, string>> => {
  // If getToken function is provided (from Clerk), use it
  if (getToken) {
    try {
      const token = await getToken();
      return token ? { 'Authorization': `Bearer ${token}` } : {};
    } catch (error) {
      console.error('Failed to get Clerk token:', error);
      return {};
    }
  }
  
  // Legacy fallback - should be removed after full Clerk migration
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
  return {};
};

// Debug/logging helper
export const logApiDetails = () => {
  console.log('API URL:', apiUrl);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Is production:', process.env.NODE_ENV === 'production');
  console.log('API URL from env:', process.env.NEXT_PUBLIC_API_URL);
  console.log('Example login endpoint:', endpoint('/users/login'));
}; 