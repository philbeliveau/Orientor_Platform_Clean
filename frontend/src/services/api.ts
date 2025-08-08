import axios from 'axios'
import { useClerkAuth } from '../contexts/ClerkAuthContext'

// Create basic axios client with proper base URL
const apiClient = axios.create({
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

  async request<T>(endpoint: string, options?: RequestInit & { token?: string }): Promise<T> {
    const { token, ...fetchOptions } = options || {};
    const headers = await this.getHeaders(token);
    
    // Clean up endpoint to avoid double slashes and ensure proper API path
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${this.baseURL}${cleanEndpoint}`;
    
    console.log(`[API] Making request to: ${url}`); // Debug logging
    
    const response = await fetch(url, {
      ...fetchOptions,
      headers: { ...headers, ...fetchOptions?.headers },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] Error ${response.status}: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return response.json();
  }

  // Specific API methods
  async getJobRecommendations(token: string, topK: number = 3) {
    return this.request(`/api/v1/jobs/recommendations/me?top_k=${topK}`, {
      method: 'GET',
      token,
    });
  }

  async getUserProfile(token: string) {
    return this.request('/user/profile', {
      method: 'GET',
      token,
    });
  }

  async getUserNotes(token: string) {
    return this.request('/api/v1/space/notes', {
      method: 'GET',
      token,
    });
  }

  async getHollandResults(token: string) {
    return this.request('/api/v1/tests/holland/user-results', {
      method: 'GET',
      token,
    });
  }

  // Additional API methods that were missing
  async getAllJobRecommendations(token: string, limit?: number) {
    const queryParam = limit ? `?limit=${limit}` : '';
    return this.request(`/api/v1/jobs/recommendations${queryParam}`, {
      method: 'GET',
      token,
    });
  }

  async getCareerRecommendations(token: string) {
    return this.request('/api/v1/career/recommendations', {
      method: 'GET',
      token,
    });
  }

  async saveCareer(token: string, careerData: any) {
    return this.request('/api/v1/career/save', {
      method: 'POST',
      token,
      body: JSON.stringify(careerData),
    });
  }

  async getJobSkillsTree(token: string, jobId: string) {
    return this.request(`/api/v1/jobs/${jobId}/skills-tree`, {
      method: 'GET',
      token,
    });
  }
}

// Create singleton instance
export const clerkApiService = new ClerkApiService();

// React hook for using the API service with Clerk authentication
export const useClerkApi = () => {
  const { getAuthToken, isAuthenticated, isLoading } = useClerkAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<T>,
    ...args: any[]
  ): Promise<T> => {
    try {
      // Check if user is authenticated first
      if (!isAuthenticated) {
        console.error('[Auth] User not authenticated');
        throw new Error('User not authenticated - please sign in');
      }

      if (isLoading) {
        console.log('[Auth] Authentication still loading, waiting...');
        // Wait a bit for auth to load
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // CRITICAL: Request JWT token with the template we created
      console.log('[Auth] Requesting JWT token with orientor-jwt template...');
      
      if (!getAuthToken) {
        console.error('[Auth] getAuthToken function is undefined');
        throw new Error('Authentication service not properly initialized');
      }

      const token = await getAuthToken();
      
      if (!token) {
        console.error('[Auth] No token returned from Clerk');
        throw new Error('No authentication token available');
      }
      
      // Validate token format - reject session tokens
      if (token.startsWith('sess_')) {
        console.error('[Auth] ❌ Got session token instead of JWT:', token.substring(0, 20));
        throw new Error('Invalid token type - got session token instead of JWT');
      }
      
      if (!token.startsWith('eyJ')) {
        console.error('[Auth] ❌ Invalid JWT format:', token.substring(0, 20));
        throw new Error('Invalid JWT token format');
      }
      
      console.log('[Auth] ✅ JWT token obtained:', token.substring(0, 30) + '...');
      return apiMethod(token, ...args);
    } catch (error) {
      console.error('[Auth] Token acquisition failed:', error);
      throw error;
    }
  };

  return {
    getJobRecommendations: (topK?: number) => 
      apiCall(clerkApiService.getJobRecommendations.bind(clerkApiService), topK),
    getAllJobRecommendations: (limit?: number) => 
      apiCall(clerkApiService.getAllJobRecommendations.bind(clerkApiService), limit),
    getCareerRecommendations: () => 
      apiCall(clerkApiService.getCareerRecommendations.bind(clerkApiService)),
    saveCareer: (careerData: any) => 
      apiCall(clerkApiService.saveCareer.bind(clerkApiService), careerData),
    getJobSkillsTree: (jobId: string) => 
      apiCall(clerkApiService.getJobSkillsTree.bind(clerkApiService), jobId),
    getUserProfile: () => 
      apiCall(clerkApiService.getUserProfile.bind(clerkApiService)),
    getUserNotes: () => 
      apiCall(clerkApiService.getUserNotes.bind(clerkApiService)),
    getHollandResults: () => 
      apiCall(clerkApiService.getHollandResults.bind(clerkApiService)),
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

// Named exports for backward compatibility - these throw helpful error messages
export const getJobRecommendations = async (topK: number = 3) => {
  throw new Error('getJobRecommendations moved to useClerkApi hook - use const { getJobRecommendations } = useClerkApi()');
};

export const getAllJobRecommendations = async (limit?: number) => {
  throw new Error('getAllJobRecommendations moved to useClerkApi hook - use const { getAllJobRecommendations } = useClerkApi()');
};

export const getCareerRecommendations = async () => {
  throw new Error('getCareerRecommendations moved to useClerkApi hook - use const { getCareerRecommendations } = useClerkApi()');
};

export const saveCareer = async (careerData: any) => {
  throw new Error('saveCareer moved to useClerkApi hook - use const { saveCareer } = useClerkApi()');
};

export const getJobSkillsTree = async (jobId: string) => {
  throw new Error('getJobSkillsTree moved to useClerkApi hook - use const { getJobSkillsTree } = useClerkApi()');
};

// Legacy compatibility export - NOTE: Use useClerkApi() for authenticated requests
export default apiClient
