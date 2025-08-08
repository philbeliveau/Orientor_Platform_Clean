'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'primary-purple',
  className = '',
  message
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const getColorClass = () => {
    if (color !== 'primary-purple') {
      return color;
    }
    return '#6366f1';
  };

  const spinnerColor = getColorClass();

  return (
    <div className={`flex flex-col justify-center items-center ${className}`}>
      <div 
        className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-gray-200`}
        style={{
          borderTopColor: spinnerColor,
          borderRightColor: spinnerColor
        }}
      />
      {message && (
        <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner; 