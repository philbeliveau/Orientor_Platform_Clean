'use client';

import React, { useEffect, useState } from 'react';
import { ChatInterface } from '@/features/chat';
import { LazyWrapper } from '@/features/shared/components/LazyWrapper';
import { useAuth, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  // This is an example of how to refactor the chat page to use the new modular components
  // The ChatInterface is now lazy loaded and split into smaller components
  
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const router = useRouter();
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  
  useEffect(() => {
    if (!isLoaded) return; // Wait for auth to load
    
    if (!isSignedIn) {
      router.push('/sign-in'); // Always use /sign-in, not /login
      return;
    }

    // Get user ID from Clerk user object
    if (user?.id) {
      // Note: Clerk uses string IDs, but if you need numeric IDs, 
      // you should get them from your backend API using the Clerk ID
      // For now, we'll use a hash of the Clerk ID as a numeric representation
      const numericId = user.id.split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0);
        return a & a;
      }, 0);
      setCurrentUserId(Math.abs(numericId));
    }
  }, [isLoaded, isSignedIn, user, router]);
  
  if (!isLoaded || !isSignedIn || !currentUserId) {
    return <div>Loading...</div>;
  }
  
  return (
    <LazyWrapper>
      <ChatInterface currentUserId={currentUserId} />
    </LazyWrapper>
  );
}