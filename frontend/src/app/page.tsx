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
      
      // If user is authenticated, redirect to dashboard
      if (userId) {
        console.log('🔄 User authenticated, redirecting to dashboard');
        router.push('/dashboard');
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

  // Show landing page for unauthenticated users
  if (!userId) {
    return <LandingPage />;
  }

  // If we get here, user is authenticated but hasn't been redirected yet
  // Show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p className="ml-3 text-gray-600">Redirecting to dashboard...</p>
    </div>
  );
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