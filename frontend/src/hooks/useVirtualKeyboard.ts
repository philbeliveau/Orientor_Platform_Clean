'use client';
import { useState, useEffect } from 'react';

interface VirtualKeyboardState {
  isVisible: boolean;
  height: number;
}

export const useVirtualKeyboard = (): VirtualKeyboardState => {
  const [isVisible, setIsVisible] = useState(false);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    // Only run on mobile devices
    if (typeof window === 'undefined' || !('visualViewport' in window)) {
      return;
    }

    const visualViewport = window.visualViewport!;
    const initialHeight = window.innerHeight;

    const handleResize = () => {
      const currentHeight = visualViewport.height;
      const diff = initialHeight - currentHeight;
      
      // Keyboard is considered visible if viewport height decreased by more than 150px
      const keyboardVisible = diff > 150;
      
      setIsVisible(keyboardVisible);
      setHeight(keyboardVisible ? diff : 0);
      
      // Adjust viewport for keyboard
      if (keyboardVisible) {
        document.documentElement.style.setProperty('--vh', `${currentHeight * 0.01}px`);
      } else {
        document.documentElement.style.setProperty('--vh', `${initialHeight * 0.01}px`);
      }
    };

    // Set initial viewport height
    document.documentElement.style.setProperty('--vh', `${initialHeight * 0.01}px`);

    visualViewport.addEventListener('resize', handleResize);

    return () => {
      visualViewport.removeEventListener('resize', handleResize);
    };
  }, []);

  return { isVisible, height };
};