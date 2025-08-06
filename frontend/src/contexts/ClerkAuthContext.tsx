'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { ClerkProvider, useAuth as useClerkAuthHook, useUser, useClerk } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

// Authentication Context Types
interface ClerkAuthContextType {
  // State
  user: any | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  signOut: () => Promise<void>;
  getAuthToken: () => Promise<string | null>;
  clearError: () => void;
  
  // Clerk specific
  clerk: any;
  userId: string | null;
  sessionId: string | null;
}

// Create Context
const ClerkAuthContext = createContext<ClerkAuthContextType | undefined>(undefined);

// Provider Props
interface ClerkAuthProviderProps {
  children: ReactNode;
}

// Main Provider Component
export function ClerkAuthProvider({ children }: ClerkAuthProviderProps) {
  const router = useRouter();
  
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}
      navigate={(to) => router.push(to)}
      appearance={{
        baseTheme: undefined, // Use system theme
        variables: {
          colorPrimary: '#3b82f6',
          colorBackground: '#ffffff',
          colorInputBackground: '#f8fafc',
        },
        elements: {
          formButtonPrimary: 'bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-4 py-2 font-medium transition-colors',
          card: 'shadow-lg border border-gray-200 rounded-lg',
          headerTitle: 'text-xl font-semibold text-gray-900',
          formFieldLabel: 'text-sm font-medium text-gray-700',
          formFieldInput: 'rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        }
      }}
    >
      <ClerkAuthContextProvider>
        {children}
      </ClerkAuthContextProvider>
    </ClerkProvider>
  );
}

// Internal Context Provider
function ClerkAuthContextProvider({ children }: { children: ReactNode }) {
  const { isLoaded, userId, sessionId, getToken, signOut: clerkSignOut } = useClerkAuthHook();
  const { user } = useUser();
  const clerk = useClerk();
  const router = useRouter();

  const [error, setError] = useState<string | null>(null);

  // Authentication state
  const isAuthenticated = isLoaded && !!userId;
  const isLoading = !isLoaded;

  // Handle sign out
  const signOut = async () => {
    try {
      setError(null);
      await clerkSignOut();
      router.push('/');
    } catch (err) {
      console.error('Sign out error:', err);
      setError('Failed to sign out');
    }
  };

  // Get authentication token
  const getAuthToken = async (): Promise<string | null> => {
    try {
      if (!isAuthenticated) return null;
      return await getToken();
    } catch (err) {
      console.error('Token fetch error:', err);
      setError('Failed to get authentication token');
      return null;
    }
  };

  // Clear error state
  const clearError = () => {
    setError(null);
  };

  // Transform Clerk user to our expected format
  const transformedUser = user ? {
    id: userId,
    clerk_user_id: userId,
    email: user.primaryEmailAddress?.emailAddress || '',
    firstName: user.firstName || '',
    lastName: user.lastName || '',
    imageUrl: user.imageUrl || '',
    createdAt: user.createdAt,
    updatedAt: user.updatedAt,
  } : null;

  const value: ClerkAuthContextType = {
    user: transformedUser,
    isAuthenticated,
    isLoading,
    error,
    signOut,
    getAuthToken,
    clearError,
    clerk,
    userId,
    sessionId,
  };

  return (
    <ClerkAuthContext.Provider value={value}>
      {children}
    </ClerkAuthContext.Provider>
  );
}

// Hook to use the context
export function useClerkAuth() {
  const context = useContext(ClerkAuthContext);
  if (context === undefined) {
    throw new Error('useClerkAuth must be used within a ClerkAuthProvider');
  }
  return context;
}

// Export for backwards compatibility with existing code
export const useAuth = useClerkAuth;

export default ClerkAuthProvider;