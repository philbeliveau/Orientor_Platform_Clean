// React and Next.js imports
import React from 'react';
import { useRouter } from 'next/navigation';
import { onboardingService } from '../services/onboardingService';

/**
 * Check if the current user needs onboarding
 * This can be used in pages that require completed onboarding
 */
export const checkOnboardingRequired = async (): Promise<boolean> => {
  try {
    const status = await onboardingService.getStatus();
    return !status.isComplete;
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

    React.useEffect(() => {
      const checkOnboarding = async () => {
        const required = await checkOnboardingRequired();
        if (required) {
          router.push('/onboarding');
        } else {
          setNeedsOnboarding(false);
        }
      };

      checkOnboarding();
    }, [router]);

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