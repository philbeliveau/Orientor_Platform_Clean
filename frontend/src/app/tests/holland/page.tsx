'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TestsHollandPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the main Holland test page
    router.push('/holland-test');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirection vers le test Holland...</p>
      </div>
    </div>
  );
}