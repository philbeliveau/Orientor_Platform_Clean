/**
 * Custom hook for making authenticated API requests with Clerk
 */
import { useCallback } from 'react';
import { useClerkToken } from '../utils/clerkAuth';
import { makeAuthenticatedRequest } from '../utils/clerkAuth';

export const useAuthenticatedFetch = () => {
  const { getAuthToken, isSignedIn, isLoaded } = useClerkToken();

  const authenticatedFetch = useCallback(
    async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
      if (!isLoaded) {
        throw new Error('Authentication not loaded');
      }

      if (!isSignedIn) {
        throw new Error('User not signed in');
      }

      const token = await getAuthToken();
      return makeAuthenticatedRequest(endpoint, options, token);
    },
    [getAuthToken, isSignedIn, isLoaded]
  );

  const authenticatedRequest = useCallback(
    async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
      const response = await authenticatedFetch(endpoint, options);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      return response.json();
    },
    [authenticatedFetch]
  );

  return {
    authenticatedFetch,
    authenticatedRequest,
    isSignedIn,
    isLoaded,
  };
};