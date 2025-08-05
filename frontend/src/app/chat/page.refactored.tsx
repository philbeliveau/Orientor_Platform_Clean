'use client';

import React, { useEffect, useState } from 'react';
import { ChatInterface } from '@/features/chat';
import { LazyWrapper } from '@/features/shared/components/LazyWrapper';

export default function ChatPage() {
  // This is an example of how to refactor the chat page to use the new modular components
  // The ChatInterface is now lazy loaded and split into smaller components
  
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  
  useEffect(() => {
    // Get user ID from auth/session
    const userId = localStorage.getItem('user_id');
    if (userId) {
      setCurrentUserId(parseInt(userId));
    }
  }, []);
  
  if (!currentUserId) {
    return <div>Loading...</div>;
  }
  
  return (
    <LazyWrapper>
      <ChatInterface currentUserId={currentUserId} />
    </LazyWrapper>
  );
}