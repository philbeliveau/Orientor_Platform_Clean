'use client';

import { useState, useEffect } from 'react';

export type Theme = 'light' | 'dark' | 'system';

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    // Récupérer le thème sauvegardé
    const savedTheme = (localStorage.getItem('theme') as Theme) || 'system';
    setTheme(savedTheme);
    
    // Appliquer le thème initial
    applyTheme(savedTheme);
    updateResolvedTheme(savedTheme);
  }, []);

  const updateResolvedTheme = (currentTheme: Theme) => {
    if (currentTheme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setResolvedTheme(prefersDark ? 'dark' : 'light');
    } else {
      setResolvedTheme(currentTheme);
    }
  };

  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement;
    
    // Supprimer les classes existantes
    root.classList.remove('light', 'dark');
    
    if (newTheme === 'system') {
      // Laisser CSS gérer avec prefers-color-scheme
      localStorage.removeItem('theme');
    } else {
      // Appliquer le thème spécifique
      root.classList.add(newTheme);
      localStorage.setItem('theme', newTheme);
    }
    
    updateResolvedTheme(newTheme);
  };

  const setThemeValue = (newTheme: Theme) => {
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  const toggleTheme = () => {
    const themes: Theme[] = ['system', 'light', 'dark'];
    const currentIndex = themes.indexOf(theme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    setThemeValue(nextTheme);
  };

  // Écouter les changements de préférence système
  useEffect(() => {
    if (!mounted) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        updateResolvedTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, mounted]);

  return {
    theme,
    resolvedTheme,
    setTheme: setThemeValue,
    toggleTheme,
    mounted
  };
};