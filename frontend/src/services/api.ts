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
