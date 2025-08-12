'use client';

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuth } from '@clerk/nextjs';

/**
 * Create an axios instance configured for Clerk authentication
 */
export const createClerkApiInstance = (getToken: () => Promise<string | null>): AxiosInstance => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  
  const instance = axios.create({
    baseURL: API_URL.trim(),
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add Clerk token
  instance.interceptors.request.use(
    async (config) => {
      try {
        const token = await getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.warn('Failed to get authentication token:', error);
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        console.error('Authentication failed - redirecting to sign in');
        // In a real app, you might want to trigger a sign-out or redirect
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * Hook to get an authenticated API service
 */
export const useClerkApi = () => {
  const { getToken } = useAuth();
  return new ClerkApiService(getToken);
};

/**
 * Enhanced API service class with Clerk authentication and standardized error handling
 */
export class ClerkApiService {
  private api: AxiosInstance;

  constructor(getToken: () => Promise<string | null>) {
    this.api = createClerkApiInstance(getToken);
  }

  // HTTP method implementations with consistent error handling
  async get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.api.get<T>(endpoint, config);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error, 'GET', endpoint);
    }
  }

  async post<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.api.post<T>(endpoint, data, config);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error, 'POST', endpoint);
    }
  }

  async put<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.api.put<T>(endpoint, data, config);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error, 'PUT', endpoint);
    }
  }

  async delete<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.api.delete<T>(endpoint, config);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error, 'DELETE', endpoint);
    }
  }

  async patch<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.api.patch<T>(endpoint, data, config);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error, 'PATCH', endpoint);
    }
  }

  // Standardized error handling
  private handleApiError(error: any, method: string, endpoint: string): Error {
    console.error(`[ClerkApiService] ${method} ${endpoint} failed:`, error);
    
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      
      // Handle specific HTTP status codes
      switch (status) {
        case 401:
          return new Error('Authentication required - please sign in');
        case 403:
          return new Error('Access forbidden - insufficient permissions');
        case 404:
          return new Error('Resource not found');
        case 422:
          return new Error(data?.detail || 'Validation error');
        case 500:
          return new Error('Internal server error - please try again later');
        default:
          return new Error(data?.detail || data?.message || `HTTP ${status} error`);
      }
    } else if (error.request) {
      return new Error('Network error - please check your connection');
    } else {
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Utility methods for common operations
  async uploadFile<T>(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.post<T>(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // URL building helper
  buildUrl(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(endpoint, this.api.defaults.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    return url.toString();
  }
}