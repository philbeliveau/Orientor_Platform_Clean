'use client';

import React, { useState, useEffect } from 'react';

interface ResponsiveGridProps {
  children: React.ReactNode;
  columns?: {
    mobile: number;
    tablet: number;
    desktop: number;
  };
  gap?: string;
  className?: string;
}

export function ResponsiveGrid({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 'var(--white-sheet-space-lg)',
  className = ''
}: ResponsiveGridProps) {
  return (
    <div
      className={`responsive-grid ${className}`}
      style={{
        '--grid-columns-mobile': columns.mobile,
        '--grid-columns-tablet': columns.tablet,
        '--grid-columns-desktop': columns.desktop,
        '--grid-gap': gap
      } as React.CSSProperties}
    >
      {children}
    </div>
  );
}

interface AdaptiveTextProps {
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  weight?: 'light' | 'normal' | 'medium' | 'semibold' | 'bold';
  color?: 'primary' | 'secondary' | 'subtle' | 'accent';
  className?: string;
}

export function AdaptiveText({
  children,
  size = 'medium',
  weight = 'normal',
  color = 'primary',
  className = ''
}: AdaptiveTextProps) {
  return (
    <span className={`adaptive-text adaptive-text-${size} adaptive-text-${weight} adaptive-text-${color} ${className}`}>
      {children}
    </span>
  );
}

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
}

export function MobileDrawer({ isOpen, onClose, children, className = '' }: MobileDrawerProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="mobile-drawer-overlay" onClick={onClose}>
      <div className={`mobile-drawer ${className}`} onClick={(e) => e.stopPropagation()}>
        <div className="mobile-drawer-header">
          <button className="mobile-drawer-close" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div className="mobile-drawer-content">
          {children}
        </div>
      </div>
    </div>
  );
}

interface TouchFriendlyButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  className?: string;
}

export function TouchFriendlyButton({
  children,
  onClick,
  variant = 'secondary',
  size = 'medium',
  disabled = false,
  className = ''
}: TouchFriendlyButtonProps) {
  return (
    <button
      className={`touch-friendly-button touch-friendly-button-${variant} touch-friendly-button-${size} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}

export function SwipeableCard({ children, onSwipeLeft, onSwipeRight, className = '' }: SwipeableCardProps) {
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft();
    }
    if (isRightSwipe && onSwipeRight) {
      onSwipeRight();
    }
  };

  return (
    <div
      className={`swipeable-card ${className}`}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {children}
    </div>
  );
}

// Responsive elements styles
const responsiveElementsStyles = `
/* Responsive Grid */
.responsive-grid {
  display: grid;
  gap: var(--grid-gap);
  grid-template-columns: repeat(var(--grid-columns-mobile), 1fr);
}

@media (min-width: 768px) {
  .responsive-grid {
    grid-template-columns: repeat(var(--grid-columns-tablet), 1fr);
  }
}

@media (min-width: 1024px) {
  .responsive-grid {
    grid-template-columns: repeat(var(--grid-columns-desktop), 1fr);
  }
}

/* Adaptive Text */
.adaptive-text {
  font-family: var(--white-sheet-font-primary);
  line-height: 1.6;
  transition: all var(--white-sheet-transition-fast);
}

.adaptive-text-small {
  font-size: 0.875rem;
}

.adaptive-text-medium {
  font-size: 1rem;
}

.adaptive-text-large {
  font-size: 1.125rem;
}

.adaptive-text-xlarge {
  font-size: 1.25rem;
}

.adaptive-text-light {
  font-weight: 300;
}

.adaptive-text-normal {
  font-weight: 400;
}

.adaptive-text-medium {
  font-weight: 500;
}

.adaptive-text-semibold {
  font-weight: 600;
}

.adaptive-text-bold {
  font-weight: 700;
}

.adaptive-text-primary {
  color: var(--white-sheet-text);
}

.adaptive-text-secondary {
  color: var(--white-sheet-text-secondary);
}

.adaptive-text-subtle {
  color: var(--white-sheet-text-subtle);
}

.adaptive-text-accent {
  color: var(--white-sheet-accent);
}

/* Mobile Drawer */
.mobile-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  animation: fadeIn 0.3s ease-out;
}

.mobile-drawer {
  background: var(--white-sheet-primary);
  border-radius: var(--white-sheet-radius-lg) var(--white-sheet-radius-lg) 0 0;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

.mobile-drawer-header {
  display: flex;
  justify-content: flex-end;
  padding: var(--white-sheet-space-md);
  border-bottom: 1px solid var(--white-sheet-border-subtle);
}

.mobile-drawer-close {
  background: none;
  border: none;
  color: var(--white-sheet-text-secondary);
  cursor: pointer;
  padding: var(--white-sheet-space-sm);
  border-radius: var(--white-sheet-radius-sm);
  transition: all var(--white-sheet-transition-fast);
}

.mobile-drawer-close:hover {
  background: var(--white-sheet-hover);
  color: var(--white-sheet-text);
}

.mobile-drawer-content {
  padding: var(--white-sheet-space-lg);
}

/* Touch Friendly Button */
.touch-friendly-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--white-sheet-radius-sm);
  font-family: var(--white-sheet-font-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--white-sheet-transition-fast);
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.touch-friendly-button-small {
  padding: var(--white-sheet-space-sm) var(--white-sheet-space-md);
  font-size: 0.875rem;
  min-height: 36px;
}

.touch-friendly-button-medium {
  padding: var(--white-sheet-space-md) var(--white-sheet-space-lg);
  font-size: 1rem;
  min-height: 44px;
}

.touch-friendly-button-large {
  padding: var(--white-sheet-space-lg) var(--white-sheet-space-xl);
  font-size: 1.125rem;
  min-height: 52px;
}

.touch-friendly-button-primary {
  background: var(--white-sheet-accent);
  color: var(--white-sheet-primary);
}

.touch-friendly-button-primary:hover {
  background: var(--white-sheet-text-secondary);
}

.touch-friendly-button-secondary {
  background: var(--white-sheet-primary);
  color: var(--white-sheet-text);
  border: 1px solid var(--white-sheet-border);
}

.touch-friendly-button-secondary:hover {
  background: var(--white-sheet-hover);
  border-color: var(--white-sheet-text-subtle);
}

.touch-friendly-button-ghost {
  background: transparent;
  color: var(--white-sheet-text-secondary);
}

.touch-friendly-button-ghost:hover {
  background: var(--white-sheet-hover);
  color: var(--white-sheet-text);
}

.touch-friendly-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.touch-friendly-button:disabled:hover {
  background: var(--white-sheet-primary);
  transform: none;
}

/* Swipeable Card */
.swipeable-card {
  touch-action: pan-x;
  cursor: grab;
  user-select: none;
  transition: transform var(--white-sheet-transition-fast);
}

.swipeable-card:active {
  cursor: grabbing;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* Responsive text scaling */
@media (max-width: 768px) {
  .adaptive-text-large {
    font-size: 1rem;
  }
  
  .adaptive-text-xlarge {
    font-size: 1.125rem;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .touch-friendly-button {
    border: 2px solid currentColor;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .mobile-drawer-overlay,
  .mobile-drawer {
    animation: none;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = responsiveElementsStyles;
  document.head.appendChild(styleSheet);
}