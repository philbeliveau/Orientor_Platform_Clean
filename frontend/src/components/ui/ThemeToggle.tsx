'use client';

import React from 'react';
import { useTheme } from '@/hooks/useTheme';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme, mounted } = useTheme();

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        );
      case 'dark':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        );
      case 'system':
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
        );
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light': return 'Clair';
      case 'dark': return 'Sombre';
      case 'system': return 'Système';
      default: return 'Système';
    }
  };

  if (!mounted) {
    return (
      <div className="w-12 h-12 rounded-lg bg-gray-200 animate-pulse"></div>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle-button group relative flex items-center justify-center w-10 h-10 rounded-md transition-all duration-300 ease-in-out hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30"
      title={`Mode actuel: ${getThemeLabel()}. Cliquer pour changer.`}
      aria-label={`Changer le thème. Mode actuel: ${getThemeLabel()}`}
    >
      <div className="transition-transform duration-300 group-hover:rotate-12">
        {getThemeIcon()}
      </div>
      
      {/* Tooltip */}
      <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 px-2 py-1 text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50 bg-stitch-primary border border-stitch-border text-stitch-sage">
        {getThemeLabel()}
      </div>
    </button>
  );
};

export default ThemeToggle;