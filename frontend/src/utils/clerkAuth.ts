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
    if (!isLoaded) {
      throw new Error('Clerk not loaded');
    }
    
    if (!isSignedIn) {
      throw new Error('User not signed in');
    }

    // Get JWT token with the orientor-jwt template, fallback to default
    const token = await getToken({ template: 'orientor-jwt' }).catch(async () => {
      console.warn('[Auth] orientor-jwt template not found, using default token');
      return await getToken();
    });
    
    if (!token) {
      throw new Error('No authentication token available');
    }
    
    // Validate token format - ensure it's a JWT
    if (!token.startsWith('eyJ')) {
      console.error('[Auth] ❌ Invalid JWT format:', token.substring(0, 20));
      throw new Error('Invalid JWT token format');
    }
    
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
  if (!token) {
    throw new Error('Authentication token required');
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  return response;
};

/**
 * Server-side utility for API calls with token
 * Can be used in API routes or server components
 */
export const createAuthenticatedFetch = (token: string) => {
  return async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
    return makeAuthenticatedRequest(endpoint, options, token);
  };
};