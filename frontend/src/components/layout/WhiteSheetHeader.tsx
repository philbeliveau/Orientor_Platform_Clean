'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface WhiteSheetHeaderProps {
  className?: string;
}

export default function WhiteSheetHeader({ className = '' }: WhiteSheetHeaderProps) {
  const pathname = usePathname();

  return (
    <header className={`white-sheet-nav ${className}`}>
      <div className="white-sheet-content">
        <div className="white-sheet-header-container">
          {/* Logo/Brand */}
          <Link href="/" className="white-sheet-brand">
            <h1 className="white-sheet-brand-text">Navigo</h1>
          </Link>

          {/* Navigation Links */}
          <nav className="white-sheet-nav-links">
            <Link 
              href="/discover" 
              className={`white-sheet-nav-item ${pathname === '/discover' ? 'active' : ''}`}
            >
              Discover
            </Link>
            <Link 
              href="/reflect" 
              className={`white-sheet-nav-item ${pathname === '/reflect' ? 'active' : ''}`}
            >
              Reflect
            </Link>
            <Link 
              href="/grow" 
              className={`white-sheet-nav-item ${pathname === '/grow' ? 'active' : ''}`}
            >
              Grow
            </Link>
          </nav>

          {/* User Actions */}
          <div className="white-sheet-user-actions">
            <button className="white-sheet-button white-sheet-button-minimal">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

// Header-specific styles
const headerStyles = `
.white-sheet-header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--white-sheet-space-lg);
}

.white-sheet-brand {
  text-decoration: none;
  color: var(--white-sheet-accent);
  transition: all var(--white-sheet-transition-fast);
}

.white-sheet-brand:hover {
  opacity: 0.8;
}

.white-sheet-brand-text {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.02em;
}

.white-sheet-nav-links {
  display: flex;
  align-items: center;
  gap: var(--white-sheet-space-md);
}

.white-sheet-user-actions {
  display: flex;
  align-items: center;
  gap: var(--white-sheet-space-sm);
}

.white-sheet-button-minimal {
  background: transparent;
  border: none;
  padding: var(--white-sheet-space-sm);
  border-radius: var(--white-sheet-radius-sm);
  color: var(--white-sheet-text-secondary);
  cursor: pointer;
  transition: all var(--white-sheet-transition-fast);
}

.white-sheet-button-minimal:hover {
  background: var(--white-sheet-hover);
  color: var(--white-sheet-text);
}

@media (max-width: 768px) {
  .white-sheet-header-container {
    padding: 0 var(--white-sheet-space-md);
  }
  
  .white-sheet-nav-links {
    display: none;
  }
  
  .white-sheet-brand-text {
    font-size: 1.25rem;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = headerStyles;
  document.head.appendChild(styleSheet);
}