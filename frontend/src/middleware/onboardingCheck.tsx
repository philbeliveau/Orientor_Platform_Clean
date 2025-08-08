// React and Next.js imports
import React from 'react';
import { useRouter } from 'next/navigation';
import { clerkApiService } from '../services/api';
import { useAuth } from '@clerk/nextjs';

/**
 * Check if the current user needs onboarding
 * This can be used in pages that require completed onboarding
 */
export const checkOnboardingRequired = async (token: string): Promise<boolean> => {
  try {
    const status = await clerkApiService.request('/auth/onboarding-status', {
      method: 'GET',
      token
    }) as { completed: boolean };
    return !status.completed;
  } catch (error) {
    console.error('Error checking onboarding status:', error);
    // If we can't check, assume they need onboarding for safety
    return true;
  }
};

/**
 * Higher-order component to protect routes that require onboarding completion
 */
export const withOnboardingCheck = (WrappedComponent: React.ComponentType<any>) => {
  return function OnboardingProtectedComponent(props: any) {
    const [needsOnboarding, setNeedsOnboarding] = React.useState<boolean | null>(null);
    const router = useRouter();
    const { getToken } = useAuth();

    React.useEffect(() => {
      const checkOnboarding = async () => {
        try {
          const token = await getToken({ template: 'orientor-jwt' });
          if (!token) {
            router.push('/sign-in');
            return;
          }
          
          const required = await checkOnboardingRequired(token);
          if (required) {
            router.push('/onboarding');
          } else {
            setNeedsOnboarding(false);
          }
        } catch (error) {
          console.error('Error checking onboarding:', error);
          router.push('/sign-in');
        }
      };

      checkOnboarding();
    }, [router, getToken]);

    if (needsOnboarding === null) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-text-secondary">Checking onboarding status...</p>
          </div>
        </div>
      );
    }

    if (needsOnboarding) {
      return null; // Will redirect to onboarding
    }

    return <WrappedComponent {...props} />;
  };
};