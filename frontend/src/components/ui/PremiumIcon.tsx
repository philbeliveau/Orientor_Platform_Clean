'use client';

import React from 'react';

interface PremiumIconProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'gold' | 'blue' | 'white';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const PremiumIcon: React.FC<PremiumIconProps> = ({
  children,
  className = '',
  glowColor = 'gold',
  size = 'md',
  animated = true
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  const glowClasses = {
    gold: 'premium-icon',
    blue: 'premium-icon-blue',
    white: 'premium-icon-white'
  };

  const baseClasses = `
    ${sizeClasses[size]}
    ${glowClasses[glowColor]}
    flex items-center justify-center
    rounded-lg
    transition-all duration-300 ease-in-out
    ${animated ? 'hover:scale-110' : ''}
    ${className}
  `;

  return (
    <div className={baseClasses}>
      {children}
    </div>
  );
};

export default PremiumIcon;