'use client';

import React, { useEffect, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import LandingPage from '@/components/landing/LandingPage';

function HomePageContent() {
  const { isLoaded, userId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded) {
      console.log('🔍 Root route auth check - User ID:', userId);
      
      // Allow both authenticated and unauthenticated users to see root page
      if (userId) {
        console.log('🏠 Authenticated user accessing root page');
      } else {
        console.log('🏠 Showing landing page for unauthenticated user');
      }
    }
  }, [isLoaded, userId, router]);

  // Show loading while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading...</p>
      </div>
    );
  }

  // Show landing page for all users (authenticated and unauthenticated)
  // The landing page can conditionally render different content based on auth state
  return <LandingPage />;
}

export default function HomePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading...</p>
      </div>
    }>
      <HomePageContent />
    </Suspense>
  );
}