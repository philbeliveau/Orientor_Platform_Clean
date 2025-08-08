import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface LoadingScreenProps {
  message?: string;
  className?: string;
  showProgressHint?: boolean;
  estimatedTime?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'Loading...',
  className = '',
  showProgressHint = false,
  estimatedTime
}) => {
  return (
    <div className={`min-h-screen flex flex-col items-center justify-center ${className}`}>
      <LoadingSpinner size="xl" message={showProgressHint ? 'Processing your request...' : undefined} />
      {message && (
        <p className="mt-8 text-lg text-gray-600 dark:text-gray-400 text-center max-w-md">
          {message}
        </p>
      )}
      {estimatedTime && (
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-500">
          Estimated time: {estimatedTime}
        </p>
      )}
      {showProgressHint && (
        <div className="mt-6 text-center">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
            <span>Loading AI models and processing data...</span>
          </div>
          <div className="mt-2 text-xs text-gray-400">
            First-time loading may take longer
          </div>
        </div>
      )}
    </div>
  );
};

export default LoadingScreen; 