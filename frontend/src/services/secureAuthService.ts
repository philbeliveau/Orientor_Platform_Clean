// SECURE AUTHENTICATION SERVICE - JWT Integration
// =====================================================
// 
// This service replaces the insecure base64 authentication with 
// enterprise-grade JWT token management for the Orientor Platform.
// 
// Features:
// ✅ JWT token storage and management
// ✅ Automatic token refresh
// ✅ Secure API communication
// ✅ Comprehensive error handling
// ✅ Token expiration handling
// ✅ Logout with token cleanup

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Types and Interfaces
interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserInfo;
}

interface UserInfo {
  id: number;
  email: string;
  onboarding_completed: boolean;
  created_at?: string;
}

interface RefreshTokenRequest {
  refresh_token: string;
}

interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const TOKEN_STORAGE_KEY = 'orientor_access_token';
const REFRESH_TOKEN_STORAGE_KEY = 'orientor_refresh_token';
const USER_STORAGE_KEY = 'orientor_user';

class SecureAuthService {
  private apiClient: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private user: UserInfo | null = null;
  private tokenRefreshPromise: Promise<string> | null = null;

  constructor() {
    // Initialize API client
    this.apiClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load tokens from storage
    this.loadTokensFromStorage();

    // Setup request interceptor for authentication
    this.apiClient.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Setup response interceptor for token refresh
    this.apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.apiClient(originalRequest);
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Load tokens and user data from localStorage
   */
  private loadTokensFromStorage(): void {
    try {
      if (typeof window !== 'undefined') {
        this.accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        this.refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
        const userString = localStorage.getItem(USER_STORAGE_KEY);
        this.user = userString ? JSON.parse(userString) : null;
      }
    } catch (error) {
      console.error('Failed to load tokens from storage:', error);
      this.clearTokens();
    }
  }

  /**
   * Save tokens and user data to localStorage
   */
  private saveTokensToStorage(tokenResponse: TokenResponse): void {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_STORAGE_KEY, tokenResponse.access_token);
        localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokenResponse.refresh_token);
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(tokenResponse.user));
        
        this.accessToken = tokenResponse.access_token;
        this.refreshToken = tokenResponse.refresh_token;
        this.user = tokenResponse.user;
      }
    } catch (error) {
      console.error('Failed to save tokens to storage:', error);
    }
  }

  /**
   * Clear all tokens and user data
   */
  private clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
    }
    
    this.accessToken = null;
    this.refreshToken = null;
    this.user = null;
  }

  /**
   * Register a new user
   */
  async register(credentials: RegisterCredentials): Promise<TokenResponse> {
    try {
      const response: AxiosResponse<TokenResponse> = await this.apiClient.post(
        '/auth/register',
        credentials
      );

      this.saveTokensToStorage(response.data);
      console.log('✅ User registered successfully');
      return response.data;
    } catch (error: any) {
      console.error('❌ Registration failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const response: AxiosResponse<TokenResponse> = await this.apiClient.post(
        '/auth/login',
        credentials
      );

      this.saveTokensToStorage(response.data);
      console.log('✅ User logged in successfully');
      return response.data;
    } catch (error: any) {
      console.error('❌ Login failed:', error.response?.data || error.message);
      
      if (error.response?.status === 429) {
        throw new Error('Too many login attempts. Please try again in 15 minutes.');
      }
      
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * Logout user and clear all tokens
   */
  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint to blacklist tokens
      if (this.accessToken) {
        await this.apiClient.post('/auth/logout');
      }
    } catch (error) {
      console.error('❌ Logout API call failed:', error);
      // Continue with local cleanup even if API call fails
    } finally {
      // Always clear local tokens
      this.clearTokens();
      console.log('✅ User logged out successfully');
    }
  }

  /**
   * Refresh the access token using refresh token
   */
  async refreshAccessToken(): Promise<string> {
    // Prevent multiple simultaneous refresh requests
    if (this.tokenRefreshPromise) {
      return this.tokenRefreshPromise;
    }

    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    this.tokenRefreshPromise = (async () => {
      try {
        const response: AxiosResponse<RefreshTokenResponse> = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: this.refreshToken } as RefreshTokenRequest,
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000,
          }
        );

        this.accessToken = response.data.access_token;
        
        if (typeof window !== 'undefined') {
          localStorage.setItem(TOKEN_STORAGE_KEY, response.data.access_token);
        }

        console.log('✅ Access token refreshed successfully');
        return response.data.access_token;
      } catch (error: any) {
        console.error('❌ Token refresh failed:', error.response?.data || error.message);
        this.clearTokens();
        throw new Error('Token refresh failed');
      } finally {
        this.tokenRefreshPromise = null;
      }
    })();

    return this.tokenRefreshPromise;
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<UserInfo> {
    try {
      const response: AxiosResponse<UserInfo> = await this.apiClient.get('/auth/me');
      
      // Update stored user information
      this.user = response.data;
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.data));
      }
      
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to get current user:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to get user information');
    }
  }

  /**
   * Change user password
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      await this.apiClient.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      });
      
      console.log('✅ Password changed successfully');
      
      // Clear tokens as user needs to log in again with new password
      this.clearTokens();
    } catch (error: any) {
      console.error('❌ Password change failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Password change failed');
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!(this.accessToken && this.refreshToken);
  }

  /**
   * Get current user from memory (cached)
   */
  getCurrentUserFromMemory(): UserInfo | null {
    return this.user;
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return this.accessToken;
  }

  /**
   * Get authenticated API client instance
   */
  getApiClient(): AxiosInstance {
    return this.apiClient;
  }

  /**
   * Make authenticated API request
   */
  async authenticatedRequest<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
  ): Promise<T> {
    try {
      const config: any = { method, url };
      if (data) {
        config.data = data;
      }

      const response: AxiosResponse<T> = await this.apiClient(config);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Authenticated ${method} request failed:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `${method} request failed`);
    }
  }
}

// Create and export singleton instance
const secureAuthService = new SecureAuthService();

export default secureAuthService;
export type { LoginCredentials, RegisterCredentials, TokenResponse, UserInfo };

// Export convenience functions
export const {
  register,
  login,
  logout,
  getCurrentUser,
  changePassword,
  isAuthenticated,
  getCurrentUserFromMemory,
  getAccessToken,
  getApiClient,
  authenticatedRequest,
} = secureAuthService;