'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatOnboard from '../../components/onboarding/ChatOnboard';
import { useOnboardingService } from '../../services/onboardingService';
import { useUser } from '@clerk/nextjs';
import ErrorBoundary from '../../components/ui/ErrorBoundary';
import { AlertTriangle } from 'lucide-react';

const OnboardingPage: React.FC = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [needsOnboarding, setNeedsOnboarding] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  // Protect this route - redirect unauthenticated users to sign in
  const { isLoaded, isSignedIn, user } = useUser();

  // Initialize onboarding service - hooks must be called unconditionally
  const onboardingService = useOnboardingService();

  useEffect(() => {
    checkOnboardingStatus();
  }, [retryCount]);

  const checkOnboardingStatus = async () => {
    try {
      setError(null);
      
      const status = await onboardingService.getStatus();
      if (status.isComplete) {
        // User has already completed onboarding, redirect to dashboard
        console.log('Onboarding already complete, redirecting to dashboard');
        router.push('/dashboard');
        return;
      }
      setNeedsOnboarding(true);
    } catch (error: any) {
      console.error('Error checking onboarding status:', error);
      
      // Set user-friendly error message
      if (error.message?.includes('Authentication service not available')) {
        setError('Authentication system is initializing. Please wait...');
      } else if (error.message?.includes('not authenticated')) {
        setError('Please sign in to continue with onboarding.');
        setTimeout(() => router.push('/sign-in'), 2000);
        return;
      } else {
        setError('Unable to check onboarding status. Assuming you need onboarding.');
      }
      
      // If we can't check, assume they need onboarding
      setNeedsOnboarding(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setIsLoading(true);
    setRetryCount(prev => prev + 1);
  };

  const handleOnboardingComplete = async (responses: any[]) => {
    try {
      console.log('Onboarding completed with responses:', responses);
      
      // CRITICAL: Mark onboarding as complete in the database
      console.log('Calling backend to mark onboarding complete...');
      await onboardingService.markOnboardingComplete();
      console.log('✅ Onboarding marked complete in database');
      
      // Update state to show completion message
      setNeedsOnboarding(false);
      
      // Show a success message briefly, then redirect to dashboard
      setTimeout(() => {
        console.log('Redirecting to dashboard after onboarding completion');
        router.push('/dashboard');
      }, 2000);
    } catch (error: any) {
      console.error('Error handling onboarding completion:', error);
      
      // Provide better error feedback to user
      if (error?.message?.includes('401') || error?.message?.includes('403')) {
        console.error('Authentication error during onboarding completion');
        setError('Authentication error. Please sign in again.');
        setTimeout(() => router.push('/sign-in'), 2000);
        return;
      }
      
      // For other errors, still proceed but warn user
      console.log('Error occurred during completion, but proceeding to dashboard');
      setError('Onboarding completion had an issue, but you can still proceed.');
      
      // Still redirect to dashboard after showing error briefly
      setTimeout(() => {
        router.push('/dashboard');
      }, 3000);
    }
  };

  // Show loading while checking authentication or onboarding status
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading onboarding...</p>
          {error && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <p className="text-yellow-800 text-sm">{error}</p>
              </div>
              <button
                onClick={handleRetry}
                className="mt-2 text-sm bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded transition-colors"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Redirect to sign in if not authenticated
  if (!isSignedIn) {
    router.push('/sign-in');
    return null;
  }

  if (!needsOnboarding) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Navigo!</h2>
          <p className="text-text-secondary">Onboarding complete. Taking you to your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Onboarding page error:', error, errorInfo);
      }}
    >
      <div className="min-h-screen bg-background">
        <ChatOnboard onComplete={handleOnboardingComplete} />
      </div>
    </ErrorBoundary>
  );
};

export default OnboardingPage;