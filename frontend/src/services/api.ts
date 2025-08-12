import axios from 'axios'
import { useAuth } from '@clerk/nextjs'

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
    return this.request('/api/v1/profiles/me', {
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

  async getCompatiblePeers(token: string) {
    return this.request('/api/v1/peers/compatible', {
      method: 'GET',
      token,
    });
  }

  async getJobSkillsTree(token: string, jobId: string) {
    const response = await this.request(`/api/v1/competence-tree/job/${jobId}/skills-tree`, {
      method: 'POST',
      token,
    });
    
    // Extract tree_data from the response
    return response.tree_data || response;
  }

  async saveCareer(token: string, careerData: { id: number; title: string }) {
    return this.request(`/api/v1/careers/save/${careerData.id}`, {
      method: 'POST',
      token,
    });
  }

  async getOnboardingStatus(token: string) {
    return this.request('/user/onboarding-status', {
      method: 'GET',
      token,
    });
  }
}

// Create singleton instance
export const clerkApiService = new ClerkApiService();

// React hook for using the API service with Clerk authentication - SIMPLIFIED per CLAUDE.md
export const useClerkApi = () => {
  const { getToken, isSignedIn, isLoaded } = useAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<T>,
    ...args: any[]
  ): Promise<T> => {
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
    saveCareer: (careerData: { id: number; title: string }) => 
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
