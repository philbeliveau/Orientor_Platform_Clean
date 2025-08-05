'use client';
import React, { useState, useRef, useEffect } from 'react';

interface TouchOptimizedProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onTap?: () => void;
  onLongPress?: () => void;
  className?: string;
  disabled?: boolean;
}

const TouchOptimized: React.FC<TouchOptimizedProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onTap,
  onLongPress,
  className = '',
  disabled = false,
}) => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number; time: number } | null>(null);
  const [isLongPressing, setIsLongPressing] = useState(false);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const elementRef = useRef<HTMLDivElement>(null);

  const SWIPE_THRESHOLD = 50; // minimum distance for swipe
  const LONG_PRESS_DURATION = 500; // milliseconds

  useEffect(() => {
    return () => {
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current);
      }
    };
  }, []);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled) return;

    const touch = e.touches[0];
    setTouchStart({
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    });

    // Start long press timer
    if (onLongPress) {
      longPressTimer.current = setTimeout(() => {
        setIsLongPressing(true);
        onLongPress();
        // Add haptic feedback if available
        if (navigator.vibrate) {
          navigator.vibrate(50);
        }
      }, LONG_PRESS_DURATION);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (disabled || !touchStart) return;

    // Cancel long press if finger moves too much
    if (longPressTimer.current) {
      const touch = e.touches[0];
      const deltaX = Math.abs(touch.clientX - touchStart.x);
      const deltaY = Math.abs(touch.clientY - touchStart.y);
      
      if (deltaX > 10 || deltaY > 10) {
        clearTimeout(longPressTimer.current);
        longPressTimer.current = null;
      }
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (disabled || !touchStart) return;

    // Clear long press timer
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    // Skip if this was a long press
    if (isLongPressing) {
      setIsLongPressing(false);
      return;
    }

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    const deltaTime = Date.now() - touchStart.time;
    
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    // Determine if this is a swipe or tap
    if (absDeltaX > SWIPE_THRESHOLD || absDeltaY > SWIPE_THRESHOLD) {
      // This is a swipe
      if (absDeltaX > absDeltaY) {
        // Horizontal swipe
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight();
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft();
        }
      } else {
        // Vertical swipe
        if (deltaY > 0 && onSwipeDown) {
          onSwipeDown();
        } else if (deltaY < 0 && onSwipeUp) {
          onSwipeUp();
        }
      }
    } else if (deltaTime < 300 && onTap) {
      // This is a tap (quick touch)
      onTap();
    }

    setTouchStart(null);
    setIsLongPressing(false);
  };

  return (
    <div
      ref={elementRef}
      className={className}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        touchAction: 'manipulation',
        WebkitTapHighlightColor: 'transparent',
        userSelect: 'none',
      }}
    >
      {children}
    </div>
  );
};

export default TouchOptimized;