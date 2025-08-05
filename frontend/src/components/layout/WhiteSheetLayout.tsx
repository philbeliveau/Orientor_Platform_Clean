'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import WhiteSheetNavigation from './WhiteSheetNavigation';
import WhiteSheetHeader from './WhiteSheetHeader';
import '../../styles/white-sheet-theme.css';

interface WhiteSheetLayoutProps {
  children: React.ReactNode;
  showNavigation?: boolean;
  showHeader?: boolean;
  className?: string;
}

export default function WhiteSheetLayout({
  children,
  showNavigation = true,
  showHeader = true,
  className = ''
}: WhiteSheetLayoutProps) {
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsLoading(false);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className={`white-sheet-container ${className}`}>
      {/* Header */}
      {showHeader && (
        <WhiteSheetHeader />
      )}

      {/* Main Content Area */}
      <div className="white-sheet-page">
        <div className="white-sheet-content">
          {/* Navigation */}
          {showNavigation && (
            <WhiteSheetNavigation currentPath={pathname || '/'} />
          )}

          {/* Page Content */}
          <main className="white-sheet-main">
            {isLoading ? (
              <div className="white-sheet-loading">
                <div className="white-sheet-loading-spinner" />
                <p className="white-sheet-text-secondary">Loading your space...</p>
              </div>
            ) : (
              <div className="white-sheet-fade-in">
                {children}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

// Loading styles
const loadingStyles = `
.white-sheet-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: var(--white-sheet-space-md);
}

.white-sheet-loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--white-sheet-border);
  border-top: 2px solid var(--white-sheet-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.white-sheet-main {
  flex: 1;
  padding: var(--white-sheet-space-xl) 0;
}

@media (max-width: 768px) {
  .white-sheet-main {
    padding: var(--white-sheet-space-lg) 0;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = loadingStyles;
  document.head.appendChild(styleSheet);
}