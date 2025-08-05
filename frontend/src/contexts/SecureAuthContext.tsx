// SECURE AUTHENTICATION CONTEXT - JWT Integration
// ===============================================
// 
// React Context for secure authentication state management
// Replaces insecure authentication with JWT token management
// 
// Features:
// ✅ Secure JWT authentication state
// ✅ Automatic token refresh
// ✅ Protected route management
// ✅ User session persistence
// ✅ Comprehensive error handling

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import secureAuthService, { 
  LoginCredentials, 
  RegisterCredentials, 
  TokenResponse, 
  UserInfo 
} from '../services/secureAuthService';

// Authentication Context Types
interface AuthContextType {
  // State
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<TokenResponse>;
  register: (credentials: RegisterCredentials) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<UserInfo>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  clearError: () => void;

  // Utilities
  getAccessToken: () => string | null;
  checkAuthentication: () => boolean;
}

// Create Context
const SecureAuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider Props
interface SecureAuthProviderProps {
  children: ReactNode;
}

// Authentication Provider Component
export const SecureAuthProvider: React.FC<SecureAuthProviderProps> = ({ children }) => {
  // State Management
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Initialize authentication state from stored tokens
   */
  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Check if user is authenticated from stored tokens
      const authenticated = secureAuthService.isAuthenticated();
      
      if (authenticated) {
        // Get user from memory first (fast)
        const cachedUser = secureAuthService.getCurrentUserFromMemory();
        if (cachedUser) {
          setUser(cachedUser);
          setIsAuthenticated(true);
        }

        // Refresh user data from server (accurate)
        try {
          const freshUser = await secureAuthService.getCurrentUser();
          setUser(freshUser);
          setIsAuthenticated(true);
          console.log('✅ Authentication initialized successfully');
        } catch (refreshError: any) {
          console.error('❌ Failed to refresh user data:', refreshError);
          
          // If refresh fails, user might need to re-authenticate
          if (refreshError.message.includes('401') || refreshError.message.includes('Token')) {
            await handleLogout();
          } else {
            // Keep cached user for now, might be network issue
            console.log('⚠️ Using cached user data due to network error');
          }
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
        console.log('🔓 No authentication found');
      }
    } catch (error: any) {
      console.error('❌ Authentication initialization failed:', error);
      setError('Failed to initialize authentication');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle user login
   */
  const handleLogin = async (credentials: LoginCredentials): Promise<TokenResponse> => {
    try {
      setIsLoading(true);
      setError(null);

      const tokenResponse = await secureAuthService.login(credentials);
      
      setUser(tokenResponse.user);
      setIsAuthenticated(true);
      
      console.log('✅ Login successful');
      return tokenResponse;
    } catch (error: any) {
      console.error('❌ Login failed:', error);
      setError(error.message || 'Login failed');
      setUser(null);
      setIsAuthenticated(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle user registration
   */
  const handleRegister = async (credentials: RegisterCredentials): Promise<TokenResponse> => {
    try {
      setIsLoading(true);
      setError(null);

      const tokenResponse = await secureAuthService.register(credentials);
      
      setUser(tokenResponse.user);
      setIsAuthenticated(true);
      
      console.log('✅ Registration successful');
      return tokenResponse;
    } catch (error: any) {
      console.error('❌ Registration failed:', error);
      setError(error.message || 'Registration failed');
      setUser(null);
      setIsAuthenticated(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle user logout
   */
  const handleLogout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);

      await secureAuthService.logout();
      
      setUser(null);
      setIsAuthenticated(false);
      
      console.log('✅ Logout successful');
    } catch (error: any) {
      console.error('❌ Logout failed:', error);
      // Clear local state even if logout API fails
      setUser(null);
      setIsAuthenticated(false);
      setError('Logout completed with errors');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Refresh current user data
   */
  const refreshUser = async (): Promise<UserInfo> => {
    try {
      setError(null);

      const freshUser = await secureAuthService.getCurrentUser();
      setUser(freshUser);
      
      console.log('✅ User data refreshed');
      return freshUser;
    } catch (error: any) {
      console.error('❌ Failed to refresh user:', error);
      setError(error.message || 'Failed to refresh user');
      
      // If refresh fails due to authentication, logout user
      if (error.message.includes('401') || error.message.includes('Token')) {
        await handleLogout();
      }
      
      throw error;
    }
  };

  /**
   * Change user password
   */
  const handleChangePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);

      await secureAuthService.changePassword(oldPassword, newPassword);
      
      // Password change requires re-authentication
      setUser(null);
      setIsAuthenticated(false);
      
      console.log('✅ Password changed successfully - please log in again');
    } catch (error: any) {
      console.error('❌ Password change failed:', error);
      setError(error.message || 'Password change failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear error state
   */
  const clearError = () => {
    setError(null);
  };

  /**
   * Get access token
   */
  const getAccessToken = (): string | null => {
    return secureAuthService.getAccessToken();
  };

  /**
   * Check authentication status
   */
  const checkAuthentication = (): boolean => {
    return secureAuthService.isAuthenticated();
  };

  // Context Value
  const contextValue: AuthContextType = {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,

    // Actions
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    refreshUser,
    changePassword: handleChangePassword,
    clearError,

    // Utilities
    getAccessToken,
    checkAuthentication,
  };

  return (
    <SecureAuthContext.Provider value={contextValue}>
      {children}
    </SecureAuthContext.Provider>
  );
};

/**
 * Custom hook to use secure authentication context
 */
export const useSecureAuth = (): AuthContextType => {
  const context = useContext(SecureAuthContext);
  
  if (context === undefined) {
    throw new Error('useSecureAuth must be used within a SecureAuthProvider');
  }
  
  return context;
};

/**
 * Higher-order component for protected routes
 */
export const withSecureAuth = <P extends object>(
  Component: React.ComponentType<P>
) => {
  const AuthenticatedComponent: React.FC<P> = (props) => {
    const { isAuthenticated, isLoading, user } = useSecureAuth();

    // Show loading spinner while checking authentication
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-lg">Verifying authentication...</span>
        </div>
      );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated || !user) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-gray-600">Redirecting to login...</p>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };

  AuthenticatedComponent.displayName = `withSecureAuth(${Component.displayName || Component.name})`;
  return AuthenticatedComponent;
};

export default SecureAuthContext;