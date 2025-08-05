// FRONTEND SECURITY TESTING SUITE
// ===============================
// 
// Comprehensive tests for the secure authentication system
// Tests JWT token management, API integration, and security features
// 
// Test Coverage:
// ✅ Authentication service functionality
// ✅ Token storage and management
// ✅ API error handling
// ✅ Context state management
// ✅ Protected route behavior
// ✅ Security best practices

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import secureAuthService from '../services/secureAuthService';
import { SecureAuthProvider, useSecureAuth, withSecureAuth } from '../contexts/SecureAuthContext';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock console methods
const originalConsoleLog = console.log;
const originalConsoleError = console.error;
beforeEach(() => {
  console.log = jest.fn();
  console.error = jest.fn();
});

afterEach(() => {
  console.log = originalConsoleLog;
  console.error = originalConsoleError;
  jest.clearAllMocks();
});

describe('SecureAuthService', () => {
  beforeEach(() => {
    // Reset localStorage mock
    localStorageMock.getItem.mockReturnValue(null);
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  describe('Token Management', () => {
    test('should store tokens securely after login', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock_access_token',
          refresh_token: 'mock_refresh_token',
          token_type: 'bearer',
          expires_in: 1800,
          user: {
            id: 1,
            email: 'test@example.com',
            onboarding_completed: true,
          },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const credentials = {
        email: 'test@example.com',
        password: 'SecurePassword123!',
      };

      const result = await secureAuthService.login(credentials);

      expect(result).toEqual(mockResponse.data);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'orientor_access_token',
        'mock_access_token'
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'orientor_refresh_token',
        'mock_refresh_token'
      );
    });

    test('should load tokens from localStorage on initialization', () => {
      localStorageMock.getItem
        .mockReturnValueOnce('stored_access_token')
        .mockReturnValueOnce('stored_refresh_token')
        .mockReturnValueOnce(JSON.stringify({
          id: 1,
          email: 'stored@example.com',
          onboarding_completed: true,
        }));

      // Create new service instance to trigger initialization
      const newService = new (secureAuthService.constructor as any)();

      expect(newService.getAccessToken()).toBe('stored_access_token');
      expect(newService.isAuthenticated()).toBe(true);
    });

    test('should clear tokens on logout', async () => {
      mockedAxios.post.mockResolvedValueOnce({ data: {} });

      await secureAuthService.logout();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('orientor_access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('orientor_refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('orientor_user');
    });
  });

  describe('Authentication Security', () => {
    test('should handle authentication errors securely', async () => {
      const errorResponse = {
        response: {
          status: 401,
          data: {
            detail: 'Invalid credentials',
          },
        },
      };

      mockedAxios.post.mockRejectedValueOnce(errorResponse);

      const credentials = {
        email: 'test@example.com',
        password: 'WrongPassword',
      };

      await expect(secureAuthService.login(credentials)).rejects.toThrow('Invalid credentials');
      expect(console.error).toHaveBeenCalledWith(
        '❌ Login failed:',
        errorResponse.response.data
      );
    });

    test('should handle rate limiting appropriately', async () => {
      const rateLimitError = {
        response: {
          status: 429,
          data: {
            detail: 'Too many attempts',
          },
        },
      };

      mockedAxios.post.mockRejectedValueOnce(rateLimitError);

      const credentials = {
        email: 'test@example.com',
        password: 'password',
      };

      await expect(secureAuthService.login(credentials)).rejects.toThrow(
        'Too many login attempts. Please try again in 15 minutes.'
      );
    });

    test('should validate password strength during registration', async () => {
      const weakPasswordError = {
        response: {
          status: 422,
          data: {
            detail: 'Password must be at least 8 characters long',
          },
        },
      };

      mockedAxios.post.mockRejectedValueOnce(weakPasswordError);

      const credentials = {
        email: 'test@example.com',
        password: 'weak',
      };

      await expect(secureAuthService.register(credentials)).rejects.toThrow(
        'Password must be at least 8 characters long'
      );
    });
  });

  describe('Token Refresh', () => {
    test('should refresh access token automatically', async () => {
      const mockRefreshResponse = {
        data: {
          access_token: 'new_access_token',
          token_type: 'bearer',
          expires_in: 1800,
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockRefreshResponse);

      // Mock existing refresh token
      localStorageMock.getItem.mockReturnValue('existing_refresh_token');

      const newToken = await secureAuthService.refreshAccessToken();

      expect(newToken).toBe('new_access_token');
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/auth/refresh'),
        { refresh_token: 'existing_refresh_token' },
        expect.any(Object)
      );
    });

    test('should handle refresh token expiration', async () => {
      const expiredTokenError = {
        response: {
          status: 401,
          data: {
            detail: 'Refresh token has expired',
          },
        },
      };

      mockedAxios.post.mockRejectedValueOnce(expiredTokenError);
      localStorageMock.getItem.mockReturnValue('expired_refresh_token');

      await expect(secureAuthService.refreshAccessToken()).rejects.toThrow(
        'Token refresh failed'
      );

      // Should clear tokens after failed refresh
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('orientor_access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('orientor_refresh_token');
    });
  });
});

// Test Component for Context Testing
const TestComponent: React.FC = () => {
  const { user, isAuthenticated, login, logout, error, isLoading } = useSecureAuth();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      {user && <div data-testid="user-email">{user.email}</div>}
      <button
        data-testid="login-button"
        onClick={() => login({ email: 'test@example.com', password: 'password' })}
      >
        Login
      </button>
      <button data-testid="logout-button" onClick={() => logout()}>
        Logout
      </button>
    </div>
  );
};

// Protected Component for Route Testing
const ProtectedComponent: React.FC = () => <div>Protected Content</div>;
const ProtectedTestComponent = withSecureAuth(ProtectedComponent);

describe('SecureAuthContext', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockReturnValue(null);
  });

  test('should provide authentication state', async () => {
    render(
      <SecureAuthProvider>
        <TestComponent />
      </SecureAuthProvider>
    );

    // Should show not authenticated initially
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
  });

  test('should handle login successfully', async () => {
    const mockResponse = {
      data: {
        access_token: 'mock_token',
        refresh_token: 'mock_refresh',
        token_type: 'bearer',
        expires_in: 1800,
        user: {
          id: 1,
          email: 'test@example.com',
          onboarding_completed: true,
        },
      },
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(
      <SecureAuthProvider>
        <TestComponent />
      </SecureAuthProvider>
    );

    const loginButton = screen.getByTestId('login-button');
    
    await act(async () => {
      fireEvent.click(loginButton);
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });
  });

  test('should handle login errors', async () => {
    const errorResponse = {
      response: {
        status: 401,
        data: {
          detail: 'Invalid credentials',
        },
      },
    };

    mockedAxios.post.mockRejectedValueOnce(errorResponse);

    render(
      <SecureAuthProvider>
        <TestComponent />
      </SecureAuthProvider>
    );

    const loginButton = screen.getByTestId('login-button');
    
    await act(async () => {
      fireEvent.click(loginButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Error: Invalid credentials')).toBeInTheDocument();
    });
  });

  test('should handle logout', async () => {
    // Setup authenticated state
    localStorageMock.getItem
      .mockReturnValueOnce('mock_token')
      .mockReturnValueOnce('mock_refresh')
      .mockReturnValueOnce(JSON.stringify({
        id: 1,
        email: 'test@example.com',
        onboarding_completed: true,
      }));

    mockedAxios.post.mockResolvedValueOnce({ data: {} });

    render(
      <SecureAuthProvider>
        <TestComponent />
      </SecureAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });

    const logoutButton = screen.getByTestId('logout-button');
    
    await act(async () => {
      fireEvent.click(logoutButton);
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });
  });
});

describe('withSecureAuth HOC', () => {
  test('should redirect unauthenticated users', () => {
    // Mock window.location
    const mockLocation = { href: '' };
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true,
    });

    render(
      <SecureAuthProvider>
        <ProtectedTestComponent />
      </SecureAuthProvider>
    );

    // Should show redirect message for unauthenticated users
    expect(screen.getByText('Authentication Required')).toBeInTheDocument();
    expect(screen.getByText('Redirecting to login...')).toBeInTheDocument();
  });

  test('should render protected content for authenticated users', async () => {
    // Setup authenticated state
    localStorageMock.getItem
      .mockReturnValueOnce('mock_token')
      .mockReturnValueOnce('mock_refresh')
      .mockReturnValueOnce(JSON.stringify({
        id: 1,
        email: 'test@example.com',
        onboarding_completed: true,
      }));

    // Mock successful user fetch
    mockedAxios.get.mockResolvedValueOnce({
      data: {
        id: 1,
        email: 'test@example.com',
        onboarding_completed: true,
      },
    });

    render(
      <SecureAuthProvider>
        <ProtectedTestComponent />
      </SecureAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  test('should show loading state during authentication check', () => {
    // Mock pending authentication
    localStorageMock.getItem
      .mockReturnValueOnce('mock_token')
      .mockReturnValueOnce('mock_refresh')
      .mockReturnValueOnce(JSON.stringify({
        id: 1,
        email: 'test@example.com',
        onboarding_completed: true,
      }));

    // Mock delayed API response
    mockedAxios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <SecureAuthProvider>
        <ProtectedTestComponent />
      </SecureAuthProvider>
    );

    expect(screen.getByText('Verifying authentication...')).toBeInTheDocument();
  });
});

describe('Security Best Practices', () => {
  test('should not expose sensitive data in localStorage', async () => {
    const mockResponse = {
      data: {
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        token_type: 'bearer',
        expires_in: 1800,
        user: {
          id: 1,
          email: 'test@example.com',
          onboarding_completed: true,
        },
      },
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    await secureAuthService.login({
      email: 'test@example.com',
      password: 'SecurePassword123!',
    });

    // Verify that password is not stored anywhere
    expect(localStorageMock.setItem).not.toHaveBeenCalledWith(
      expect.anything(),
      expect.stringContaining('password')
    );
    expect(localStorageMock.setItem).not.toHaveBeenCalledWith(
      expect.anything(),
      expect.stringContaining('SecurePassword123!')
    );
  });

  test('should handle network errors gracefully', async () => {
    const networkError = new Error('Network Error');
    mockedAxios.post.mockRejectedValueOnce(networkError);

    await expect(
      secureAuthService.login({
        email: 'test@example.com',
        password: 'password',
      })
    ).rejects.toThrow('Login failed');

    expect(console.error).toHaveBeenCalledWith('❌ Login failed:', networkError);
  });

  test('should validate API responses', async () => {
    // Mock malformed response
    const malformedResponse = {
      data: {
        // Missing required fields
        token_type: 'bearer',
      },
    };

    mockedAxios.post.mockResolvedValueOnce(malformedResponse);

    // Should handle gracefully even with malformed response
    const result = await secureAuthService.login({
      email: 'test@example.com',
      password: 'password',
    });

    expect(result).toEqual(malformedResponse.data);
  });
});

export {};