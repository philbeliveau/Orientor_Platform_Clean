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

export interface OnboardingErrorDetails {
  type: 'network' | 'auth' | 'validation' | 'server' | 'unknown';
  message: string;
  code?: string;
  retryable: boolean;
}

export class OnboardingError extends Error {
  public details: OnboardingErrorDetails;
  
  constructor(message: string, details: OnboardingErrorDetails) {
    super(message);
    this.name = 'OnboardingError';
    this.details = details;
  }
}

// Legacy service class removed - now using hook-based pattern

// Hook-based wrapper simplified per CLAUDE.md requirements
export const useOnboardingService = () => {
  const { getToken, isSignedIn, isLoaded } = useAuth();
  
  // Helper to create structured errors
  const createError = (error: any, operation: string): OnboardingError => {
    console.error(`Onboarding ${operation} error:`, error);
    
    if (error?.response?.status === 401 || error?.message?.includes('401')) {
      return new OnboardingError(`Authentication failed during ${operation}`, {
        type: 'auth',
        message: 'Please sign in again',
        code: 'AUTH_REQUIRED',
        retryable: false
      });
    }
    
    if (error?.response?.status === 500 || error?.message?.includes('500')) {
      return new OnboardingError(`Server error during ${operation}`, {
        type: 'server',
        message: 'Server encountered an error. Please try again.',
        code: 'SERVER_ERROR',
        retryable: true
      });
    }
    
    if (!navigator.onLine) {
      return new OnboardingError(`Network error during ${operation}`, {
        type: 'network',
        message: 'Check your internet connection and try again',
        code: 'NETWORK_ERROR',
        retryable: true
      });
    }
    
    return new OnboardingError(`Failed to ${operation}`, {
      type: 'unknown',
      message: error?.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
      retryable: true
    });
  };

  // Simple authentication check as required by CLAUDE.md
  const checkAuth = async () => {
    if (!isLoaded) {
      // Wait a bit for auth to load instead of throwing immediately
      await new Promise(resolve => setTimeout(resolve, 100));
      if (!isLoaded) {
        throw new OnboardingError('Authentication still loading', {
          type: 'auth',
          message: 'Please wait for authentication to load',
          retryable: true
        });
      }
    }
    if (!isSignedIn) {
      throw new OnboardingError('User not authenticated', {
        type: 'auth',
        message: 'Please sign in to continue',
        retryable: false
      });
    }
    
    // ✅ CORRECT - Use Clerk hooks as per CLAUDE.md
    const token = await getToken();
    if (!token) {
      throw new OnboardingError('No authentication token available', {
        type: 'auth',
        message: 'Authentication token missing',
        retryable: false
      });
    }
    return token;
  };

  return {
    getStatus: async (): Promise<OnboardingStatus> => {
      try {
        console.log('Checking onboarding status...');
        const token = await checkAuth();
        const response = await clerkApiService.getOnboardingStatus(token);
        console.log('Onboarding status response:', response);
        
        // Extract data from API response wrapper
        const data = response.data || response;
        console.log('Extracted data:', data);
        
        // STANDARDIZED: Both endpoints now return same format
        const isComplete = data.onboarding_completed || data.is_complete;
        const hasStarted = data.has_started || isComplete;
        
        console.log('🔍 ONBOARDING SERVICE MAPPING:', {
          raw_response: response,
          extracted_data: data,
          raw_onboarding_completed: data.onboarding_completed,
          raw_is_complete: data.is_complete,
          raw_has_started: data.has_started,
          mapped_isComplete: isComplete,
          mapped_hasStarted: hasStarted
        });
        
        return {
          isComplete: isComplete,
          hasStarted: hasStarted,
        };
      } catch (error: any) {
        const onboardingError = createError(error, 'get status');
        if (onboardingError.details.type === 'auth') {
          throw onboardingError;
        }
        // For non-auth errors, return safe defaults
        console.warn('Onboarding status check failed, returning safe defaults');
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
        throw createError(error, 'start onboarding');
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
        throw createError(error, 'save response');
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
        throw createError(error, 'complete onboarding');
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
        const response = await clerkApiService.getOnboardingStatus(token);
        console.log('Onboarding status check result:', response);
        
        // Extract data from API response wrapper
        const data = response.data || response;
        
        // STANDARDIZED: Both endpoints now return same format
        const isComplete = data.onboarding_completed || data.is_complete;
        
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
      } catch (error: any) {
        console.error('Failed to mark onboarding complete:', error);
        
        // Enhanced error handling for specific error types
        if (error.message?.includes('personalityprofile')) {
          throw new Error('Database configuration error. Please contact support.');
        } else if (error.message?.includes('500')) {
          throw new Error('Server error occurred. Please try again in a moment.');
        } else if (error.message?.includes('401') || error.message?.includes('403')) {
          throw new Error('Authentication error. Please sign in again.');
        } else {
          throw new Error('Failed to complete onboarding. Please try again.');
        }
      }
    }
  };
};

// Default export no longer available - use useOnboardingService hook instead
export default useOnboardingService;