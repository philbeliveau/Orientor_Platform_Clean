'use client';

import React, { useState, useEffect, useRef } from 'react';

interface FlowingTransitionsProps {
  children: React.ReactNode;
  direction?: 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right' | 'scale';
  duration?: number;
  delay?: number;
  className?: string;
  trigger?: 'scroll' | 'mount' | 'hover';
}

export default function FlowingTransitions({
  children,
  direction = 'fade',
  duration = 500,
  delay = 0,
  className = '',
  trigger = 'mount'
}: FlowingTransitionsProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (trigger === 'mount') {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, delay);
      return () => clearTimeout(timer);
    }

    if (trigger === 'scroll') {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              setIsVisible(true);
            }, delay);
          }
        },
        { threshold: 0.1 }
      );

      if (elementRef.current) {
        observer.observe(elementRef.current);
      }

      return () => observer.disconnect();
    }
  }, [delay, trigger]);

  const getTransitionStyles = () => {
    const baseStyles = {
      transition: `all ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`,
      willChange: 'transform, opacity'
    };

    if (!isVisible && trigger !== 'hover') {
      switch (direction) {
        case 'fade':
          return { ...baseStyles, opacity: 0 };
        case 'slide-up':
          return { ...baseStyles, opacity: 0, transform: 'translateY(20px)' };
        case 'slide-down':
          return { ...baseStyles, opacity: 0, transform: 'translateY(-20px)' };
        case 'slide-left':
          return { ...baseStyles, opacity: 0, transform: 'translateX(20px)' };
        case 'slide-right':
          return { ...baseStyles, opacity: 0, transform: 'translateX(-20px)' };
        case 'scale':
          return { ...baseStyles, opacity: 0, transform: 'scale(0.95)' };
        default:
          return { ...baseStyles, opacity: 0 };
      }
    }

    if (trigger === 'hover') {
      const hoverScale = isHovered ? 1.02 : 1;
      const hoverOpacity = isHovered ? 1 : 0.9;
      return {
        ...baseStyles,
        opacity: hoverOpacity,
        transform: `scale(${hoverScale})`,
        filter: isHovered ? 'brightness(1.02)' : 'brightness(1)'
      };
    }

    return {
      ...baseStyles,
      opacity: 1,
      transform: 'translateX(0) translateY(0) scale(1)'
    };
  };

  return (
    <div
      ref={elementRef}
      className={`flowing-transition ${className}`}
      style={getTransitionStyles()}
      onMouseEnter={() => trigger === 'hover' && setIsHovered(true)}
      onMouseLeave={() => trigger === 'hover' && setIsHovered(false)}
    >
      {children}
    </div>
  );
}

// Floating elements component for ambient animation
interface FloatingElementsProps {
  count?: number;
  className?: string;
}

export function FloatingElements({ count = 8, className = '' }: FloatingElementsProps) {
  const elements = Array.from({ length: count }, (_, i) => ({
    id: i,
    size: Math.random() * 3 + 1,
    duration: Math.random() * 20 + 10,
    delay: Math.random() * 5,
    opacity: Math.random() * 0.3 + 0.1
  }));

  return (
    <div className={`floating-elements ${className}`}>
      {elements.map((element) => (
        <div
          key={element.id}
          className="floating-element"
          style={{
            width: `${element.size}px`,
            height: `${element.size}px`,
            animationDuration: `${element.duration}s`,
            animationDelay: `${element.delay}s`,
            opacity: element.opacity
          }}
        />
      ))}
    </div>
  );
}

// Breathing animation component
interface BreathingAnimationProps {
  children: React.ReactNode;
  intensity?: number;
  duration?: number;
  className?: string;
}

export function BreathingAnimation({
  children,
  intensity = 0.02,
  duration = 4000,
  className = ''
}: BreathingAnimationProps) {
  return (
    <div
      className={`breathing-animation ${className}`}
      style={{
        animation: `breathe ${duration}ms ease-in-out infinite`,
        '--breathing-intensity': intensity
      } as React.CSSProperties}
    >
      {children}
    </div>
  );
}

// Inject styles for all transition components
const transitionStyles = `
.flowing-transition {
  display: block;
}

.floating-elements {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.floating-element {
  position: absolute;
  background: var(--white-sheet-text-subtle);
  border-radius: 50%;
  animation: float linear infinite;
  top: 100%;
  left: calc(var(--random-x, 50%) * 1%);
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: var(--opacity, 0.3);
  }
  90% {
    opacity: var(--opacity, 0.3);
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

.breathing-animation {
  animation: breathe 4s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(calc(1 + var(--breathing-intensity)));
  }
}

/* Stagger animation for multiple elements */
.stagger-animation > * {
  animation-delay: calc(var(--stagger-delay, 0.1s) * var(--stagger-index, 0));
}

/* Gentle pulse for interactive elements */
.gentle-pulse {
  animation: gentlePulse 2s ease-in-out infinite;
}

@keyframes gentlePulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* Smooth hover effects */
.smooth-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.smooth-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Text reveal animation */
.text-reveal {
  overflow: hidden;
  position: relative;
}

.text-reveal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--white-sheet-primary);
  transform: translateX(-100%);
  animation: textReveal 1s ease-out forwards;
}

@keyframes textReveal {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .flowing-transition,
  .floating-element,
  .breathing-animation,
  .gentle-pulse,
  .smooth-hover,
  .text-reveal::before {
    animation: none !important;
    transition: none !important;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = transitionStyles;
  document.head.appendChild(styleSheet);
}