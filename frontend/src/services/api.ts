import axios from 'axios'
import { useAuth } from '@clerk/nextjs'
import {
  ApiResponse,
  ApiError,
  ApiRequestOptions,
  CareerGoal,
  CreateCareerGoalRequest,
  UpdateCareerGoalRequest,
  AvatarData,
  UpdateAvatarRequest,
  UserProfile,
  JobRecommendation,
  HollandResults,
  SkillsTreeData,
  UserNote,
  CompatiblePeer,
  SaveCareerRequest,
  SaveCareerResponse,
  OnboardingStatus
} from '../types/api'
import {
  validateApiResponseFormat,
  extractResponseData,
  validateCareerGoal,
  validateAvatarData,
  validateUserProfile,
  validateJobRecommendation,
  validateHollandResults,
  validateSkillsTreeData,
  validateUserNote,
  validateCompatiblePeer,
  validateOnboardingStatus,
  validateArrayResponse
} from '../utils/validation'

// Create basic axios client with proper base URL
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('Unauthorized request - authentication required')
      // In a Clerk-based app, redirect to sign-in
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
    }
    return Promise.reject(error)
  }
)

// Utility to construct API endpoint URLs
export function endpoint(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

// Get authentication headers for Clerk
export async function getAuthHeader(getToken: () => Promise<string | null>): Promise<Record<string, string>> {
  const token = await getToken()
  if (!token) {
    throw new Error('No authentication token available')
  }
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

// Clerk-integrated API service class
class ClerkApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async getHeaders(token?: string): Promise<Record<string, string>> {
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
  }

  async request<T>(
    endpoint: string, 
    options?: ApiRequestOptions
  ): Promise<ApiResponse<T>> {
    const { token, ...fetchOptions } = options || {};
    const headers = await this.getHeaders(token);
    
    // Clean up endpoint to avoid double slashes and ensure proper API path
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${this.baseURL}${cleanEndpoint}`;
    
    console.log(`[API] Making request to: ${url}`); // Debug logging
    
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers: { ...headers, ...fetchOptions?.headers },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[API] Error ${response.status}: ${errorText}`);
        
        const apiError: ApiError = {
          status: response.status,
          message: errorText || `HTTP ${response.status}`,
          details: `Failed to fetch ${endpoint}`
        };
        
        throw apiError;
      }

      const rawData = await response.json();
      return validateApiResponseFormat<T>(rawData);
    } catch (error) {
      // Re-throw API errors as-is
      if (error && typeof error === 'object' && 'status' in error) {
        throw error;
      }
      
      // Wrap other errors in API error format
      const apiError: ApiError = {
        status: 500,
        message: error instanceof Error ? error.message : 'Unknown error',
        details: `Request to ${endpoint} failed`
      };
      
      throw apiError;
    }
  }

  // Type-safe API methods

  // Career Goals API
  async getCareerGoals(token: string): Promise<ApiResponse<CareerGoal[]>> {
    const response = await this.request<CareerGoal[]>('/api/v1/career-goals', {
      method: 'GET',
      token
    });
    
    // Validate each career goal in the response
    const data = extractResponseData(response);
    const validatedData = validateArrayResponse(data, validateCareerGoal);
    
    return { ...response, data: validatedData };
  }

  async createCareerGoal(token: string, goalData: CreateCareerGoalRequest): Promise<ApiResponse<CareerGoal>> {
    const response = await this.request<CareerGoal>('/api/v1/career-goals', {
      method: 'POST',
      token,
      body: JSON.stringify(goalData)
    });
    
    const data = extractResponseData(response);
    const validatedData = validateCareerGoal(data);
    
    return { ...response, data: validatedData };
  }

  async updateCareerGoal(token: string, goalId: number, goalData: UpdateCareerGoalRequest): Promise<ApiResponse<CareerGoal>> {
    const response = await this.request<CareerGoal>(`/api/v1/career-goals/${goalId}`, {
      method: 'PUT',
      token,
      body: JSON.stringify(goalData)
    });
    
    const data = extractResponseData(response);
    const validatedData = validateCareerGoal(data);
    
    return { ...response, data: validatedData };
  }

  async deleteCareerGoal(token: string, goalId: number): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<{ success: boolean }>(`/api/v1/career-goals/${goalId}`, {
      method: 'DELETE',
      token
    });
  }

  // Avatar API
  async getAvatarData(token: string): Promise<ApiResponse<AvatarData>> {
    const response = await this.request<AvatarData>('/api/v1/avatar/me', {
      method: 'GET',
      token
    });
    
    const data = extractResponseData(response);
    const validatedData = validateAvatarData(data);
    
    return { ...response, data: validatedData };
  }

  async updateAvatarData(token: string, avatarData: UpdateAvatarRequest): Promise<ApiResponse<AvatarData>> {
    const response = await this.request<AvatarData>('/api/v1/avatar/me', {
      method: 'PUT',
      token,
      body: JSON.stringify(avatarData)
    });
    
    const data = extractResponseData(response);
    const validatedData = validateAvatarData(data);
    
    return { ...response, data: validatedData };
  }

  // Enhanced existing methods with proper typing
  async getJobRecommendations(token: string, topK: number = 3): Promise<ApiResponse<JobRecommendation[]>> {
    const response = await this.request<JobRecommendation[]>(`/api/v1/jobs/recommendations/me?top_k=${topK}`, {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateArrayResponse(data, validateJobRecommendation);
    
    return { ...response, data: validatedData };
  }

  async getUserProfile(token: string): Promise<ApiResponse<UserProfile>> {
    const response = await this.request<UserProfile>('/api/v1/profiles/me', {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateUserProfile(data);
    
    return { ...response, data: validatedData };
  }

  async getUserNotes(token: string): Promise<ApiResponse<UserNote[]>> {
    const response = await this.request<UserNote[]>('/api/v1/space/notes', {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateArrayResponse(data, validateUserNote);
    
    return { ...response, data: validatedData };
  }

  async getHollandResults(token: string): Promise<ApiResponse<HollandResults>> {
    const response = await this.request<HollandResults>('/api/v1/tests/holland/user-results', {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateHollandResults(data);
    
    return { ...response, data: validatedData };
  }

  async getCompatiblePeers(token: string): Promise<ApiResponse<CompatiblePeer[]>> {
    const response = await this.request<CompatiblePeer[]>('/api/v1/peers/compatible', {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateArrayResponse(data, validateCompatiblePeer);
    
    return { ...response, data: validatedData };
  }

  async getJobSkillsTree(token: string, jobId: string): Promise<ApiResponse<SkillsTreeData>> {
    const response = await this.request<SkillsTreeData>(`/api/v1/competence-tree/job/${jobId}/skills-tree`, {
      method: 'POST',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateSkillsTreeData(data);
    
    return { ...response, data: validatedData };
  }

  async saveCareer(token: string, careerData: SaveCareerRequest): Promise<ApiResponse<SaveCareerResponse>> {
    return this.request<SaveCareerResponse>(`/api/v1/careers/save/${careerData.id}`, {
      method: 'POST',
      token,
      body: JSON.stringify(careerData)
    });
  }

  async getOnboardingStatus(token: string): Promise<ApiResponse<OnboardingStatus>> {
    const response = await this.request<OnboardingStatus>('/api/v1/onboarding/status', {
      method: 'GET',
      token,
    });
    
    const data = extractResponseData(response);
    const validatedData = validateOnboardingStatus(data);
    
    return { ...response, data: validatedData };
  }
}

// Create singleton instance
export const clerkApiService = new ClerkApiService();

// React hook for using the API service with Clerk authentication - SIMPLIFIED per CLAUDE.md
export const useClerkApi = () => {
  const { getToken, isSignedIn, isLoaded } = useAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<ApiResponse<T>>,
    ...args: any[]
  ): Promise<ApiResponse<T>> => {
    try {
      // Simple authentication check as required by CLAUDE.md
      if (!isLoaded) {
        throw new Error('Authentication still loading');
      }

      if (!isSignedIn) {
        throw new Error('User not authenticated - please sign in');
      }

      // ✅ CORRECT - Use Clerk hooks as per CLAUDE.md: const { getToken } = useAuth(); const token = await getToken();
      const token = await getToken();
      
      if (!token) {
        throw new Error('No authentication token available');
      }
      
      console.log('[Auth] ✅ JWT token obtained:', token.substring(0, 30) + '...');
      return apiMethod(token, ...args);
    } catch (error) {
      console.error('[Auth] Token acquisition failed:', error);
      throw error;
    }
  };

  return {
    // Career Goals API
    getCareerGoals: (): Promise<ApiResponse<CareerGoal[]>> => 
      apiCall(clerkApiService.getCareerGoals.bind(clerkApiService)),
    createCareerGoal: (goalData: CreateCareerGoalRequest): Promise<ApiResponse<CareerGoal>> => 
      apiCall(clerkApiService.createCareerGoal.bind(clerkApiService), goalData),
    updateCareerGoal: (goalId: number, goalData: UpdateCareerGoalRequest): Promise<ApiResponse<CareerGoal>> => 
      apiCall(clerkApiService.updateCareerGoal.bind(clerkApiService), goalId, goalData),
    deleteCareerGoal: (goalId: number): Promise<ApiResponse<{ success: boolean }>> => 
      apiCall(clerkApiService.deleteCareerGoal.bind(clerkApiService), goalId),
    
    // Avatar API
    getAvatarData: (): Promise<ApiResponse<AvatarData>> => 
      apiCall(clerkApiService.getAvatarData.bind(clerkApiService)),
    updateAvatarData: (avatarData: UpdateAvatarRequest): Promise<ApiResponse<AvatarData>> => 
      apiCall(clerkApiService.updateAvatarData.bind(clerkApiService), avatarData),
    
    // Enhanced existing methods
    getJobRecommendations: (topK?: number) => 
      apiCall(clerkApiService.getJobRecommendations.bind(clerkApiService), topK),
    getAllJobRecommendations: (topK?: number) => 
      apiCall(clerkApiService.getJobRecommendations.bind(clerkApiService), topK),
    getCareerRecommendations: (topK?: number) => 
      apiCall(clerkApiService.getJobRecommendations.bind(clerkApiService), topK),
    getUserProfile: () => 
      apiCall(clerkApiService.getUserProfile.bind(clerkApiService)),
    getUserNotes: () => 
      apiCall(clerkApiService.getUserNotes.bind(clerkApiService)),
    getHollandResults: () => 
      apiCall(clerkApiService.getHollandResults.bind(clerkApiService)),
    getCompatiblePeers: () => 
      apiCall(clerkApiService.getCompatiblePeers.bind(clerkApiService)),
    getJobSkillsTree: (jobId: string) => 
      apiCall(clerkApiService.getJobSkillsTree.bind(clerkApiService), jobId),
    saveCareer: (careerData: SaveCareerRequest) => 
      apiCall(clerkApiService.saveCareer.bind(clerkApiService), careerData),
    getOnboardingStatus: () => 
      apiCall(clerkApiService.getOnboardingStatus.bind(clerkApiService)),
    
    // Generic method for custom API calls
    request: <T>(endpoint: string, options?: RequestInit) => 
      apiCall((token: string) => clerkApiService.request<T>(endpoint, { ...options, token }))
  };
};

// Server-side API helper (for use in API routes)
export const serverApiClient = (token?: string) => {
  const client = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  return client
}
