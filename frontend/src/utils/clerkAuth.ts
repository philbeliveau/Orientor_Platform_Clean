/**
 * Clerk Authentication Utilities
 * Provides helper functions for making authenticated API calls with Clerk JWT tokens
 */

import { useAuth } from '@clerk/nextjs';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Utility to get Clerk JWT token for API calls
 * Must be used within a React component with Clerk auth context
 */
export const useClerkToken = () => {
  const { getToken, isSignedIn, isLoaded } = useAuth();

  const getAuthToken = async (): Promise<string> => {
    console.log('[Auth] 🔍 Getting authentication token...');
    console.log('[Auth] 📊 State:', { isLoaded, isSignedIn });
    
    if (!isLoaded) {
      console.error('[Auth] ❌ Clerk not loaded');
      throw new Error('Clerk not loaded');
    }
    
    if (!isSignedIn) {
      console.error('[Auth] ❌ User not signed in');
      throw new Error('User not signed in');
    }

    console.log('[Auth] 🎫 Attempting to get JWT token...');
    
    // Get JWT token - try orientor-jwt template first, fallback to default
    let token;
    try {
      token = await getToken({ template: 'orientor-jwt' });
      console.log('[Auth] ✅ Token obtained with orientor-jwt template');
    } catch (templateError) {
      console.warn('[Auth] ⚠️ orientor-jwt template not available, using default token');
      try {
        token = await getToken();
        console.log('[Auth] ✅ Token obtained with default template');
      } catch (defaultError) {
        const errorMessage = defaultError instanceof Error ? defaultError.message : 'Unknown error';
        console.error('[Auth] ❌ Failed to get token with both template and default:', errorMessage);
        throw new Error('Failed to obtain authentication token');
      }
    }
    
    if (!token) {
      console.error('[Auth] ❌ No authentication token available');
      throw new Error('No authentication token available');
    }
    
    // Validate token format - ensure it's a JWT
    if (!token.startsWith('eyJ')) {
      console.error('[Auth] ❌ Invalid JWT format:', token.substring(0, 20));
      throw new Error('Invalid JWT token format');
    }
    
    console.log('[Auth] ✅ Valid JWT token obtained, length:', token.length);
    return token;
  };

  return { getAuthToken, isSignedIn, isLoaded };
};

/**
 * Make an authenticated API request using Clerk JWT token
 * For use outside of React components
 */
export const makeAuthenticatedRequest = async (
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<Response> => {
  console.log('[API] 🌐 Making authenticated request to:', endpoint);
  
  if (!token) {
    console.error('[API] ❌ Authentication token required');
    throw new Error('Authentication token required');
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  console.log('[API] 🎯 Full URL:', url);
  
  const requestOptions = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  };
  
  console.log('[API] 📦 Request options:', {
    method: requestOptions.method || 'GET',
    headers: {
      ...requestOptions.headers,
      'Authorization': `Bearer ${token.substring(0, 20)}...`
    }
  });

  try {
    const response = await fetch(url, requestOptions);
    console.log('[API] 📡 Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unable to read error response');
      console.error('[API] ❌ Request failed:', { status: response.status, statusText: response.statusText, error: errorText });
    } else {
      console.log('[API] ✅ Request successful');
    }
    
    return response;
  } catch (error) {
    console.error('[API] ❌ Network error:', error);
    throw error;
  }
};

/**
 * Server-side utility for API calls with token
 * Can be used in API routes or server components
 */
export const createAuthenticatedFetch = (token: string) => {
  console.log('[Auth] 🔧 Creating authenticated fetch function');
  return async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
    return makeAuthenticatedRequest(endpoint, options, token);
  };
};