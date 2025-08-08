'use client';

import React from 'react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import SocraticChat from '@/components/chat/SocraticChat';

export default function SocraticChatPage() {
  const router = useRouter();
  const { isLoaded, isSignedIn } = useAuth();

  useEffect(() => {
    if (!isLoaded) return; // Wait for auth to load

    if (!isSignedIn) {
      router.push('/sign-in');
      return;
    }
  }, [isLoaded, isSignedIn, router]);

  return <SocraticChat />;
}