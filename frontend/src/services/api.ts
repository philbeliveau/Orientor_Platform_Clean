import axios from 'axios'
import { useAuth } from '@clerk/nextjs'

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
    return this.request('/api/v1/user/profile', {
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
}

// Create singleton instance
export const clerkApiService = new ClerkApiService();

// React hook for using the API service with Clerk authentication
export const useClerkApi = () => {
  const { getToken } = useAuth();

  const apiCall = async <T>(
    apiMethod: (token: string, ...args: any[]) => Promise<T>,
    ...args: any[]
  ): Promise<T> => {
    const token = await getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }
    return apiMethod(token, ...args);
  };

  return {
    getJobRecommendations: (topK?: number) => 
      apiCall(clerkApiService.getJobRecommendations.bind(clerkApiService), topK),
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

// Named exports for backward compatibility
export const getJobRecommendations = async (topK: number = 3) => {
  throw new Error('getJobRecommendations moved to useClerkApi hook - use const { getJobRecommendations } = useClerkApi()');
};

// Legacy compatibility export - NOTE: Use useClerkApi() for authenticated requests
export default apiClient
