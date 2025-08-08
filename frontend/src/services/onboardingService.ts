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

class OnboardingService {
  private baseURL = '/api/v1/onboarding';

  /**
   * Get the current onboarding status for the authenticated user
   */
  async getStatus(token: string): Promise<OnboardingStatus> {
    try {
      console.log('Checking onboarding status...');
      const response = await clerkApiService.request(`/auth/onboarding-status`, {
        method: 'GET',
        token
      });
      console.log('Onboarding status response:', response);
      console.log('Checking response.completed:', response.completed);
      console.log('Full response data keys:', Object.keys(response));

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
  }

  /**
   * Start a new onboarding session
   */
  async startOnboarding(token: string): Promise<OnboardingSessionResponse> {
    try {
      const response = await clerkApiService.request(`${this.baseURL}/start`, {
        method: 'POST',
        token
      });
      return response;
    } catch (error) {
      console.error('Failed to start onboarding:', error);
      throw error;
    }
  }

  /**
   * Save a single onboarding response
   */
  async saveResponse(token: string, responseData: OnboardingResponse): Promise<OnboardingProgressResponse> {
    try {
      const response = await clerkApiService.request(`${this.baseURL}/response`, {
        method: 'POST',
        token,
        body: JSON.stringify(responseData)
      });
      return response;
    } catch (error) {
      console.error('Failed to save onboarding response:', error);
      throw error;
    }
  }

  /**
   * Complete the onboarding process
   */
  async completeOnboarding(token: string, data: {
    responses: OnboardingResponse[];
    psychProfile?: PsychProfile;
  }): Promise<OnboardingCompleteResponse> {
    try {
      console.log('Sending onboarding completion data:', {
        responses: data.responses.length,
        psychProfile: data.psychProfile ? 'Present' : 'Missing',
        data: data
      });
      const response = await clerkApiService.request(`${this.baseURL}/complete`, {
        method: 'POST',
        token,
        body: JSON.stringify(data)
      });
      console.log('Onboarding completion response:', response);
      return response;
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      throw error;
    }
  }

  /**
   * Get the user's onboarding psychological profile
   */
  async getProfile(token: string): Promise<OnboardingProfileResponse> {
    try {
      const response = await clerkApiService.request(`${this.baseURL}/profile`, {
        method: 'GET',
        token
      });
      return response;
    } catch (error) {
      console.error('Failed to get onboarding profile:', error);
      throw error;
    }
  }

  /**
   * Get all onboarding responses for the user
   */
  async getResponses(token: string): Promise<OnboardingResponsesData> {
    try {
      const response = await clerkApiService.request(`${this.baseURL}/responses`, {
        method: 'GET',
        token
      });
      return response;
    } catch (error) {
      console.error('Failed to get onboarding responses:', error);
      throw error;
    }
  }

  /**
   * Reset onboarding progress for the user
   */
  async resetOnboarding(token: string): Promise<{ message: string }> {
    try {
      const response = await clerkApiService.request(`${this.baseURL}/reset`, {
        method: 'DELETE',
        token
      });
      return response;
    } catch (error) {
      console.error('Failed to reset onboarding:', error);
      throw error;
    }
  }

  /**
   * Check if user needs onboarding
   */
  async needsOnboarding(token: string): Promise<boolean> {
    try {
      const status = await this.getStatus(token);
      console.log('Onboarding status check result:', { isComplete: status.isComplete, hasStarted: status.hasStarted });
      return !status.isComplete;
    } catch (error: any) {
      // If it's an auth error, re-throw it
      if (error.message?.includes('401') || error.message?.includes('403')) {
        throw error;
      }
      
      // For other errors, assume they need onboarding
      console.warn('Could not check onboarding status, assuming onboarding needed:', error.message);
      return true;
    }
  }

  /**
   * Get onboarding progress percentage
   */
  async getProgress(token: string): Promise<number> {
    try {
      const responsesData = await this.getResponses(token);
      if (responsesData.total_items === 0) return 0;
      return Math.round((responsesData.completed_items / responsesData.total_items) * 100);
    } catch (error) {
      console.error('Failed to get onboarding progress:', error);
      return 0;
    }
  }

  /**
   * Skip onboarding for a user by creating a default profile
   */
  async skipOnboarding(token: string): Promise<OnboardingCompleteResponse> {
    try {
      console.log('Skipping onboarding...');
      const response = await clerkApiService.request(`${this.baseURL}/skip`, {
        method: 'POST',
        token
      });
      console.log('Skip onboarding response:', response);
      return response;
    } catch (error) {
      console.error('Failed to skip onboarding:', error);
      throw error;
    }
  }

  /**
   * Mark onboarding as complete in the database
   */
  async markOnboardingComplete(token: string): Promise<{ message: string; onboarding_completed: boolean }> {
    try {
      console.log('Marking onboarding as complete...');
      const response = await clerkApiService.request('/auth/onboarding-complete', {
        method: 'POST',
        token
      });
      console.log('Onboarding completion response:', response);
      return response;
    } catch (error) {
      console.error('Failed to mark onboarding complete:', error);
      throw error;
    }
  }
}

export const onboardingService = new OnboardingService();

// Hook-based wrapper following Clerk pattern
export const useOnboardingService = () => {
  const { request } = useClerkApi();

  return {
    getStatus: async (): Promise<OnboardingStatus> => {
      try {
        console.log('Checking onboarding status...');
        const response = await request('/auth/onboarding-status');
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
        const response = await request('/api/v1/onboarding/start', { method: 'POST' });
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
        });
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
        });
        console.log('Onboarding completion response:', response);
        return response;
      } catch (error) {
        console.error('Failed to complete onboarding:', error);
        throw error;
      }
    },

    getProfile: async (): Promise<OnboardingProfileResponse> => {
      try {
        const response = await request('/api/v1/onboarding/profile');
        return response;
      } catch (error) {
        console.error('Failed to get onboarding profile:', error);
        throw error;
      }
    },

    getResponses: async (): Promise<OnboardingResponsesData> => {
      try {
        const response = await request('/api/v1/onboarding/responses');
        return response;
      } catch (error) {
        console.error('Failed to get onboarding responses:', error);
        throw error;
      }
    },

    resetOnboarding: async (): Promise<{ message: string }> => {
      try {
        const response = await request('/api/v1/onboarding/reset', { method: 'DELETE' });
        return response;
      } catch (error) {
        console.error('Failed to reset onboarding:', error);
        throw error;
      }
    },

    needsOnboarding: async (): Promise<boolean> => {
      try {
        const status = await request('/auth/onboarding-status');
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
        const responsesData = await request('/api/v1/onboarding/responses');
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
        const response = await request('/api/v1/onboarding/skip', { method: 'POST' });
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
        const response = await request('/auth/onboarding-complete', { method: 'POST' });
        console.log('Onboarding completion response:', response);
        return response;
      } catch (error) {
        console.error('Failed to mark onboarding complete:', error);
        throw error;
      }
    }
  };
};

export default onboardingService;