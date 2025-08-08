'use client';

import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface SmartLoadingStateProps {
  isLoading: boolean;
  children: React.ReactNode;
  loadingMessage?: string;
  showProgressHint?: boolean;
  minLoadingTime?: number; // Minimum time to show loading state
  className?: string;
}

const SmartLoadingState: React.FC<SmartLoadingStateProps> = ({
  isLoading,
  children,
  loadingMessage = 'Loading...',
  showProgressHint = false,
  minLoadingTime = 500,
  className = ''
}) => {
  const [shouldShowLoading, setShouldShowLoading] = useState(isLoading);
  const [startTime, setStartTime] = useState<number | null>(null);

  useEffect(() => {
    if (isLoading && !startTime) {
      setStartTime(Date.now());
      setShouldShowLoading(true);
    } else if (!isLoading && startTime) {
      const elapsed = Date.now() - startTime;
      const remainingTime = Math.max(0, minLoadingTime - elapsed);
      
      if (remainingTime > 0) {
        // Wait for minimum loading time before hiding
        setTimeout(() => {
          setShouldShowLoading(false);
          setStartTime(null);
        }, remainingTime);
      } else {
        setShouldShowLoading(false);
        setStartTime(null);
      }
    }
  }, [isLoading, startTime, minLoadingTime]);

  if (shouldShowLoading) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
        <LoadingSpinner 
          size="lg" 
          message={showProgressHint ? 'Processing your request...' : undefined}
        />
        <p className="mt-6 text-gray-600 dark:text-gray-400 text-center">
          {loadingMessage}
        </p>
        {showProgressHint && (
          <div className="mt-4 text-center">
            <div className="text-sm text-gray-500">
              AI models are processing your data
            </div>
            <div className="mt-1 text-xs text-gray-400">
              This may take a moment on first load
            </div>
          </div>
        )}
      </div>
    );
  }

  return <>{children}</>;
};

export default SmartLoadingState;