/**
 * API utility functions for consistent API URL handling
 */

// Get the API URL from environment variables with production fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Clean API URL (remove trailing spaces)
export const apiUrl = API_URL.trim();

// Helper to build full endpoint URLs
export const endpoint = (path: string): string => {
  // Ensure all paths include the /api/v1 prefix for backend compatibility
  let cleanPath = path;
  
  // Add /api/v1 prefix if not present
  if (!cleanPath.startsWith('/api/v1/')) {
    cleanPath = cleanPath.startsWith('/') ? `/api/v1${cleanPath}` : `/api/v1/${cleanPath}`;
  }
  
  return `${apiUrl}${cleanPath}`;
};

// Authentication helper for Clerk integration
export const getAuthHeader = async (getToken: () => Promise<string | null>): Promise<Record<string, string>> => {
  // Always require getToken function from Clerk
  if (!getToken) {
    console.error('getToken function is required for authentication');
    throw new Error('getToken function is required for authentication');
  }
  
  try {
    const token = await getToken();
    if (!token) {
      console.error('No authentication token available');
      throw new Error('No authentication token available');
    }
    return { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}` 
    };
  } catch (error) {
    console.error('Failed to get Clerk token:', error);
    throw error;
  }
};

// Debug/logging helper
export const logApiDetails = () => {
  console.log('API URL:', apiUrl);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Is production:', process.env.NODE_ENV === 'production');
  console.log('API URL from env:', process.env.NEXT_PUBLIC_API_URL);
  console.log('Example auth endpoint:', endpoint('/users/auth'));
}; 