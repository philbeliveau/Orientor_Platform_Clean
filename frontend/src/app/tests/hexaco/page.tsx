'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TestsHexacoPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the main HEXACO test page
    router.push('/hexaco-test');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirection vers le test HEXACO...</p>
      </div>
    </div>
  );
}