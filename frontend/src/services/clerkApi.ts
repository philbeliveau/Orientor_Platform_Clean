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
 * Generic API service class with Clerk authentication
 */
export class ClerkApiService {
  private api: AxiosInstance;

  constructor(getToken: () => Promise<string | null>) {
    this.api = createClerkApiInstance(getToken);
  }

  async get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get<T>(endpoint, config);
    return response.data;
  }

  async post<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post<T>(endpoint, data, config);
    return response.data;
  }

  async put<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.put<T>(endpoint, data, config);
    return response.data;
  }

  async delete<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.delete<T>(endpoint, config);
    return response.data;
  }

  async patch<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.patch<T>(endpoint, data, config);
    return response.data;
  }
}