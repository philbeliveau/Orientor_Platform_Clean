'use client';

import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Error boundary specifically for data processing errors
 * Catches TypeError: data.forEach is not a function and similar issues
 */
export class DataProcessingErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Check if this is a data processing error
    const isDataProcessingError = 
      error.message.includes('forEach is not a function') ||
      error.message.includes('map is not a function') ||
      error.message.includes('filter is not a function') ||
      error.message.includes('Cannot read properties of undefined') ||
      error.message.includes('Cannot read property') ||
      error.message.includes('is not iterable');

    if (isDataProcessingError) {
      console.error('[DataProcessingErrorBoundary] Data processing error caught:', error.message);
      return { hasError: true, error };
    }

    // For other errors, let them bubble up
    throw error;
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[DataProcessingErrorBoundary] Error details:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack
    });

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Data Processing Error
              </h3>
              <p className="text-sm text-red-700 mt-1">
                There was an issue processing the response from the server. The data format may be unexpected.
              </p>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded border border-red-200">
            <h4 className="text-sm font-medium text-red-800 mb-2">What happened?</h4>
            <p className="text-sm text-red-700 mb-3">
              The application received data in an unexpected format and couldn't process it properly.
            </p>
            
            <h4 className="text-sm font-medium text-red-800 mb-2">What can you do?</h4>
            <ul className="text-sm text-red-700 list-disc list-inside space-y-1">
              <li>Try refreshing the page</li>
              <li>Check your internet connection</li>
              <li>If the problem persists, contact support</li>
            </ul>
          </div>

          <div className="mt-4 flex space-x-3">
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700 transition-colors"
            >
              Refresh Page
            </button>
            <button
              onClick={() => this.setState({ hasError: false, error: undefined })}
              className="bg-gray-600 text-white px-4 py-2 rounded text-sm hover:bg-gray-700 transition-colors"
            >
              Try Again
            </button>
          </div>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-medium text-red-800">
                Debug Information (Development Only)
              </summary>
              <pre className="mt-2 p-3 bg-red-100 text-red-800 text-xs overflow-x-auto rounded">
                {this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component wrapper for easier usage
export function withDataProcessingErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  const WrappedComponent = (props: P) => (
    <DataProcessingErrorBoundary fallback={fallback}>
      <Component {...props} />
    </DataProcessingErrorBoundary>
  );

  WrappedComponent.displayName = `withDataProcessingErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

export default DataProcessingErrorBoundary;