'use client';

import { useState, useEffect, useCallback } from 'react';

interface UseSmartLoadingOptions {
  minLoadingTime?: number;
  maxLoadingTime?: number;
  showProgressAfter?: number;
}

interface SmartLoadingState {
  isLoading: boolean;
  showProgress: boolean;
  hasTimedOut: boolean;
  elapsedTime: number;
}

export const useSmartLoading = (options: UseSmartLoadingOptions = {}) => {
  const {
    minLoadingTime = 500,
    maxLoadingTime = 30000,
    showProgressAfter = 2000
  } = options;

  const [state, setState] = useState<SmartLoadingState>({
    isLoading: false,
    showProgress: false,
    hasTimedOut: false,
    elapsedTime: 0
  });

  const [startTime, setStartTime] = useState<number | null>(null);

  useEffect(() => {
    let progressTimer: NodeJS.Timeout;
    let timeoutTimer: NodeJS.Timeout;
    let elapsedTimer: NodeJS.Timeout;

    if (state.isLoading && startTime) {
      // Show progress indicator after delay
      progressTimer = setTimeout(() => {
        setState(prev => ({ ...prev, showProgress: true }));
      }, showProgressAfter);

      // Set timeout for maximum loading time
      timeoutTimer = setTimeout(() => {
        setState(prev => ({ ...prev, hasTimedOut: true }));
      }, maxLoadingTime);

      // Update elapsed time every second
      elapsedTimer = setInterval(() => {
        if (startTime) {
          const elapsed = Date.now() - startTime;
          setState(prev => ({ ...prev, elapsedTime: elapsed }));
        }
      }, 1000);
    }

    return () => {
      clearTimeout(progressTimer);
      clearTimeout(timeoutTimer);
      clearInterval(elapsedTimer);
    };
  }, [state.isLoading, startTime, showProgressAfter, maxLoadingTime]);

  const startLoading = useCallback(() => {
    const now = Date.now();
    setStartTime(now);
    setState({
      isLoading: true,
      showProgress: false,
      hasTimedOut: false,
      elapsedTime: 0
    });
  }, []);

  const stopLoading = useCallback(() => {
    if (startTime) {
      const elapsed = Date.now() - startTime;
      const remainingTime = Math.max(0, minLoadingTime - elapsed);

      if (remainingTime > 0) {
        setTimeout(() => {
          setState({
            isLoading: false,
            showProgress: false,
            hasTimedOut: false,
            elapsedTime: 0
          });
          setStartTime(null);
        }, remainingTime);
      } else {
        setState({
          isLoading: false,
          showProgress: false,
          hasTimedOut: false,
          elapsedTime: 0
        });
        setStartTime(null);
      }
    }
  }, [startTime, minLoadingTime]);

  const getLoadingMessage = useCallback(() => {
    const { elapsedTime, hasTimedOut } = state;

    if (hasTimedOut) {
      return "This is taking longer than expected. The AI models are still loading...";
    }

    if (elapsedTime > 15000) {
      return "Still processing... Large AI models take time to initialize.";
    }

    if (elapsedTime > 5000) {
      return "Loading AI models and processing your request...";
    }

    return "Loading...";
  }, [state]);

  return {
    ...state,
    startLoading,
    stopLoading,
    getLoadingMessage,
    getEstimatedTime: () => {
      if (state.elapsedTime > 10000) return "~30 seconds";
      if (state.elapsedTime > 5000) return "~15 seconds";
      return "~10 seconds";
    }
  };
};

export default useSmartLoading;