'use client';

import { ThemeProvider } from '@/contexts/ThemeContext';
import { ClerkAuthProvider } from '@/contexts/ClerkAuthContext';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkAuthProvider>
      <ThemeProvider>
        {children}
      </ThemeProvider>
    </ClerkAuthProvider>
  );
}