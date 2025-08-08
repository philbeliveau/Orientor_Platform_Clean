import { clerkApiService, useClerkApi } from './api';
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

// Hook-based wrapper following Clerk pattern
export const useOnboardingService = () => {
  const clerkApi = useClerkApi();
  
  // Add null check for the API service
  if (!clerkApi || !clerkApi.request) {
    console.error('useOnboardingService: ClerkApi not properly initialized');
    // Return a service with safe fallbacks
    return {
      getStatus: async (): Promise<OnboardingStatus> => {
        throw new Error('Authentication service not available');
      },
      startOnboarding: async (): Promise<OnboardingSessionResponse> => {
        throw new Error('Authentication service not available');
      },
      saveResponse: async (responseData: OnboardingResponse): Promise<OnboardingProgressResponse> => {
        throw new Error('Authentication service not available');
      },
      completeOnboarding: async (data: any): Promise<OnboardingCompleteResponse> => {
        throw new Error('Authentication service not available');
      },
      getProfile: async (): Promise<OnboardingProfileResponse> => {
        throw new Error('Authentication service not available');
      },
      getResponses: async (): Promise<OnboardingResponsesData> => {
        throw new Error('Authentication service not available');
      },
      resetOnboarding: async (): Promise<{ message: string }> => {
        throw new Error('Authentication service not available');
      },
      needsOnboarding: async (): Promise<boolean> => {
        // Default to true if we can't check
        return true;
      },
      getProgress: async (): Promise<number> => {
        return 0;
      },
      skipOnboarding: async (): Promise<OnboardingCompleteResponse> => {
        throw new Error('Authentication service not available');
      },
      markOnboardingComplete: async (): Promise<{ message: string; onboarding_completed: boolean }> => {
        throw new Error('Authentication service not available');
      }
    };
  }
  
  const { request } = clerkApi;

  return {
    getStatus: async (): Promise<OnboardingStatus> => {
      try {
        console.log('Checking onboarding status...');
        const response = await request('/auth/onboarding-status') as { completed: boolean };
        console.log('Onboarding status response:', response);
        
        const isComplete = response.completed;
        return {
          isComplete: isComplete,
          hasStarted: isComplete,
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
        const response = await request('/api/v1/onboarding/start', { method: 'POST' }) as OnboardingSessionResponse;
        return response;
      } catch (error) {
        console.error('Failed to start onboarding:', error);
        throw error;
      }
    },

    saveResponse: async (responseData: OnboardingResponse): Promise<OnboardingProgressResponse> => {
      try {
        const response = await request('/api/v1/onboarding/response', {
          method: 'POST',
          body: JSON.stringify(responseData)
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
        const response = await request('/api/v1/onboarding/complete', {
          method: 'POST',
          body: JSON.stringify(data)
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
        const response = await request('/api/v1/onboarding/profile') as OnboardingProfileResponse;
        return response;
      } catch (error) {
        console.error('Failed to get onboarding profile:', error);
        throw error;
      }
    },

    getResponses: async (): Promise<OnboardingResponsesData> => {
      try {
        const response = await request('/api/v1/onboarding/responses') as OnboardingResponsesData;
        return response;
      } catch (error) {
        console.error('Failed to get onboarding responses:', error);
        throw error;
      }
    },

    resetOnboarding: async (): Promise<{ message: string }> => {
      try {
        const response = await request('/api/v1/onboarding/reset', { method: 'DELETE' }) as { message: string };
        return response;
      } catch (error) {
        console.error('Failed to reset onboarding:', error);
        throw error;
      }
    },

    needsOnboarding: async (): Promise<boolean> => {
      try {
        const status = await request('/auth/onboarding-status') as { completed: boolean };
        console.log('Onboarding status check result:', { isComplete: status.completed });
        return !status.completed;
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
        const responsesData = await request('/api/v1/onboarding/responses') as OnboardingResponsesData;
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
        const response = await request('/api/v1/onboarding/skip', { method: 'POST' }) as OnboardingCompleteResponse;
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
        const response = await request('/auth/onboarding-complete', { method: 'POST' }) as { message: string; onboarding_completed: boolean };
        console.log('Onboarding completion response:', response);
        return response;
      } catch (error) {
        console.error('Failed to mark onboarding complete:', error);
        throw error;
      }
    }
  };
};

// Default export no longer available - use useOnboardingService hook instead
export default useOnboardingService;