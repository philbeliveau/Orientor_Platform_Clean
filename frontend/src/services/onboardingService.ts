import { useAuth } from '@clerk/nextjs';
import { clerkApiService } from './api';
import { PsychProfile, OnboardingResponse } from '../types/onboarding';

export interface OnboardingStatus {
  isComplete: boolean;
  hasStarted: boolean;
  currentStep?: string;
  completedAt?: string;
}

export interface OnboardingSessionResponse {
  session_id: string;
  message: string;
}

export interface OnboardingProgressResponse {
  message: string;
  progress: number;
  total: number;
}

export interface OnboardingCompleteResponse {
  message: string;
  assessment_id: number;
  profile_created: boolean;
}

export interface OnboardingProfileResponse {
  profile: PsychProfile;
  description: string;
  created_at: string;
  assessment_version: string;
}

export interface OnboardingResponsesData {
  responses: OnboardingResponse[];
  assessment_status: string;
  completed_items: number;
  total_items: number;
}

// Legacy service class removed - now using hook-based pattern

// Hook-based wrapper simplified per CLAUDE.md requirements
export const useOnboardingService = () => {
  const { getToken, isSignedIn, isLoaded } = useAuth();
  
  // Simple authentication check as required by CLAUDE.md
  const checkAuth = async () => {
    if (!isLoaded) {
      // Wait a bit for auth to load instead of throwing immediately
      await new Promise(resolve => setTimeout(resolve, 100));
      if (!isLoaded) {
        throw new Error('Authentication still loading');
      }
    }
    if (!isSignedIn) {
      throw new Error('User not authenticated - please sign in');
    }
    
    // ✅ CORRECT - Use Clerk hooks as per CLAUDE.md
    const token = await getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }
    return token;
  };

  return {
    getStatus: async (): Promise<OnboardingStatus> => {
      try {
        console.log('Checking onboarding status...');
        const token = await checkAuth();
        const response = await clerkApiService.getOnboardingStatus(token) as { onboarding_completed: boolean } | { isComplete: boolean; hasStarted: boolean };
        console.log('Onboarding status response:', response);
        
        // Handle both response formats from different endpoints
        let isComplete: boolean;
        let hasStarted: boolean;
        
        if ('onboarding_completed' in response) {
          // User router format: {onboarding_completed: boolean}
          isComplete = response.onboarding_completed;
          hasStarted = isComplete;
        } else if ('isComplete' in response) {
          // Onboarding router format: {isComplete: boolean, hasStarted: boolean}
          isComplete = response.isComplete;
          hasStarted = response.hasStarted;
        } else {
          // Fallback for unexpected format
          console.warn('Unexpected response format:', response);
          isComplete = false;
          hasStarted = false;
        }
        
        return {
          isComplete: isComplete,
          hasStarted: hasStarted,
        };
      } catch (error: any) {
        console.error('Failed to get onboarding status:', error);
        if (error.message?.includes('401') || error.message?.includes('403')) {
          console.error('Authentication error while checking onboarding status');
          throw error;
        }
        return {
          isComplete: false,
          hasStarted: false,
        };
      }
    },

    startOnboarding: async (): Promise<OnboardingSessionResponse> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/start', { method: 'POST', token }) as OnboardingSessionResponse;
        return response;
      } catch (error) {
        console.error('Failed to start onboarding:', error);
        throw error;
      }
    },

    saveResponse: async (responseData: OnboardingResponse): Promise<OnboardingProgressResponse> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/response', {
          method: 'POST',
          body: JSON.stringify(responseData),
          token
        }) as OnboardingProgressResponse;
        return response;
      } catch (error) {
        console.error('Failed to save onboarding response:', error);
        throw error;
      }
    },

    completeOnboarding: async (data: {
      responses: OnboardingResponse[];
      psychProfile?: PsychProfile;
    }): Promise<OnboardingCompleteResponse> => {
      try {
        console.log('Sending onboarding completion data:', {
          responses: data.responses.length,
          psychProfile: data.psychProfile ? 'Present' : 'Missing',
          data: data
        });
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/complete', {
          method: 'POST',
          body: JSON.stringify(data),
          token
        }) as OnboardingCompleteResponse;
        console.log('Onboarding completion response:', response);
        return response;
      } catch (error) {
        console.error('Failed to complete onboarding:', error);
        throw error;
      }
    },

    getProfile: async (): Promise<OnboardingProfileResponse> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/profile', {
          method: 'GET',
          token
        }) as OnboardingProfileResponse;
        return response;
      } catch (error) {
        console.error('Failed to get onboarding profile:', error);
        throw error;
      }
    },

    getResponses: async (): Promise<OnboardingResponsesData> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/responses', {
          method: 'GET',
          token
        }) as OnboardingResponsesData;
        return response;
      } catch (error) {
        console.error('Failed to get onboarding responses:', error);
        throw error;
      }
    },

    resetOnboarding: async (): Promise<{ message: string }> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/reset', { 
          method: 'DELETE',
          token
        }) as { message: string };
        return response;
      } catch (error) {
        console.error('Failed to reset onboarding:', error);
        throw error;
      }
    },

    needsOnboarding: async (): Promise<boolean> => {
      try {
        const token = await checkAuth();
        const response = await clerkApiService.getOnboardingStatus(token) as { onboarding_completed: boolean } | { isComplete: boolean; hasStarted: boolean };
        console.log('Onboarding status check result:', response);
        
        // Handle both response formats from different endpoints
        let isComplete: boolean;
        
        if ('onboarding_completed' in response) {
          // User router format: {onboarding_completed: boolean}
          isComplete = response.onboarding_completed;
        } else if ('isComplete' in response) {
          // Onboarding router format: {isComplete: boolean, hasStarted: boolean}
          isComplete = response.isComplete;
        } else {
          // Fallback for unexpected format
          console.warn('Unexpected response format:', response);
          isComplete = false;
        }
        
        return !isComplete;
      } catch (error: any) {
        if (error.message?.includes('401') || error.message?.includes('403')) {
          throw error;
        }
        console.warn('Could not check onboarding status, assuming onboarding needed:', error.message);
        return true;
      }
    },

    getProgress: async (): Promise<number> => {
      try {
        const token = await checkAuth();
        const responsesData = await clerkApiService.request('/api/v1/onboarding/responses', {
          method: 'GET',
          token
        }) as OnboardingResponsesData;
        if (responsesData.total_items === 0) return 0;
        return Math.round((responsesData.completed_items / responsesData.total_items) * 100);
      } catch (error) {
        console.error('Failed to get onboarding progress:', error);
        return 0;
      }
    },

    skipOnboarding: async (): Promise<OnboardingCompleteResponse> => {
      try {
        console.log('Skipping onboarding...');
        const token = await checkAuth();
        const response = await clerkApiService.request('/api/v1/onboarding/skip', { 
          method: 'POST',
          token
        }) as OnboardingCompleteResponse;
        console.log('Skip onboarding response:', response);
        return response;
      } catch (error) {
        console.error('Failed to skip onboarding:', error);
        throw error;
      }
    },

    markOnboardingComplete: async (): Promise<{ message: string; onboarding_completed: boolean }> => {
      try {
        console.log('Marking onboarding as complete...');
        const token = await checkAuth();
        
        // Send proper data structure with empty responses array (now that responses is optional)
        const data = {
          responses: [], // Empty responses array - backend now accepts this
          psychProfile: null
        };
        
        const response = await clerkApiService.request('/api/v1/onboarding/complete', { 
          method: 'POST',
          body: JSON.stringify(data),
          token
        }) as { message: string; assessment_id: number; profile_created: boolean };
        
        console.log('Onboarding completion response:', response);
        
        // Transform response to match expected interface
        return {
          message: response.message,
          onboarding_completed: true
        };
      } catch (error) {
        console.error('Failed to mark onboarding complete:', error);
        throw error;
      }
    }
  };
};

// Default export no longer available - use useOnboardingService hook instead
export default useOnboardingService;