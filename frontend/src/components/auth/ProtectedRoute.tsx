'use client';

import React from 'react';
import { useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/nextjs';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({ 
  children, 
  fallback,
  redirectTo = '/sign-in'
}: ProtectedRouteProps) {
  return (
    <>
      <SignedIn>
        {children}
      </SignedIn>
      <SignedOut>
        {fallback || <RedirectToSignIn />}
      </SignedOut>
    </>
  );
}

// Hook for components that need auth state
export function useAuthGuard() {
  const { isLoaded, userId, isSignedIn } = useAuth();
  const router = useRouter();

  const requireAuth = (redirectPath: string = '/sign-in') => {
    if (isLoaded && !userId) {
      router.push(redirectPath);
      return false;
    }
    return true;
  };

  const redirectIfAuthenticated = (redirectPath: string = '/dashboard') => {
    if (isLoaded && userId) {
      router.push(redirectPath);
      return true;
    }
    return false;
  };

  return {
    isLoaded,
    isAuthenticated: isSignedIn,
    userId,
    requireAuth,
    redirectIfAuthenticated,
  };
}

export default ProtectedRoute;