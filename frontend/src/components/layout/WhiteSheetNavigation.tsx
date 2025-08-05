'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface NavigationItem {
  id: string;
  label: string;
  href: string;
  description?: string;
  icon?: React.ReactNode;
}

interface WhiteSheetNavigationProps {
  currentPath: string;
  className?: string;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'home',
    label: 'Home',
    href: '/',
    description: 'Your personal space',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9,22 9,12 15,12 15,22"></polyline>
      </svg>
    )
  },
  {
    id: 'discover',
    label: 'Discover',
    href: '/discover',
    description: 'Explore your potential',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"></circle>
        <polygon points="16.24,7.76 14.12,14.12 7.76,16.24 9.88,9.88 16.24,7.76"></polygon>
      </svg>
    )
  },
  {
    id: 'reflect',
    label: 'Reflect',
    href: '/reflect',
    description: 'Understand yourself',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
      </svg>
    )
  },
  {
    id: 'grow',
    label: 'Grow',
    href: '/grow',
    description: 'Develop your path',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
      </svg>
    )
  },
  {
    id: 'connect',
    label: 'Connect',
    href: '/connect',
    description: 'Find your community',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
        <circle cx="9" cy="7" r="4"></circle>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
      </svg>
    )
  }
];

export default function WhiteSheetNavigation({ currentPath, className = '' }: WhiteSheetNavigationProps) {
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const isActiveItem = (href: string) => {
    if (href === '/' && currentPath === '/') return true;
    if (href !== '/' && currentPath.startsWith(href)) return true;
    return false;
  };

  return (
    <nav className={`white-sheet-navigation ${className}`}>
      <div className="white-sheet-nav-container">
        {navigationItems.map((item) => {
          const isActive = isActiveItem(item.href);
          const isExpanded = expandedItem === item.id;
          
          return (
            <div key={item.id} className="white-sheet-nav-item-container">
              <Link
                href={item.href}
                className={`white-sheet-nav-item ${isActive ? 'active' : ''}`}
                onMouseEnter={() => setExpandedItem(item.id)}
                onMouseLeave={() => setExpandedItem(null)}
              >
                <div className="white-sheet-nav-item-content">
                  {item.icon && (
                    <span className="white-sheet-nav-icon">
                      {item.icon}
                    </span>
                  )}
                  <span className="white-sheet-nav-label">{item.label}</span>
                </div>
                
                {item.description && isExpanded && (
                  <div className="white-sheet-nav-description white-sheet-fade-in">
                    {item.description}
                  </div>
                )}
              </Link>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

// Navigation-specific styles
const navigationStyles = `
.white-sheet-navigation {
  margin-bottom: var(--white-sheet-space-xl);
}

.white-sheet-nav-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--white-sheet-space-sm);
  padding: var(--white-sheet-space-md) 0;
  border-bottom: 1px solid var(--white-sheet-border-subtle);
}

.white-sheet-nav-item-container {
  position: relative;
}

.white-sheet-nav-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: var(--white-sheet-space-sm) var(--white-sheet-space-md);
  border-radius: var(--white-sheet-radius-sm);
  color: var(--white-sheet-text-secondary);
  text-decoration: none;
  transition: all var(--white-sheet-transition-fast);
  min-width: 120px;
  background: var(--white-sheet-primary);
  border: 1px solid transparent;
}

.white-sheet-nav-item:hover {
  background: var(--white-sheet-hover);
  color: var(--white-sheet-text);
  border-color: var(--white-sheet-border-subtle);
}

.white-sheet-nav-item.active {
  background: var(--white-sheet-tertiary);
  color: var(--white-sheet-accent);
  border-color: var(--white-sheet-border);
}

.white-sheet-nav-item-content {
  display: flex;
  align-items: center;
  gap: var(--white-sheet-space-sm);
  width: 100%;
}

.white-sheet-nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.white-sheet-nav-label {
  font-weight: 500;
  font-size: 0.875rem;
}

.white-sheet-nav-description {
  font-size: 0.75rem;
  color: var(--white-sheet-text-subtle);
  margin-top: var(--white-sheet-space-xs);
  line-height: 1.4;
}

@media (max-width: 768px) {
  .white-sheet-nav-container {
    justify-content: center;
    gap: var(--white-sheet-space-xs);
  }
  
  .white-sheet-nav-item {
    min-width: auto;
    padding: var(--white-sheet-space-xs) var(--white-sheet-space-sm);
  }
  
  .white-sheet-nav-label {
    display: none;
  }
  
  .white-sheet-nav-description {
    display: none;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = navigationStyles;
  document.head.appendChild(styleSheet);
}