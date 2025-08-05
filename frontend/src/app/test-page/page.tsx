'use client';

import React from 'react';
import Link from 'next/link';

export default function TestPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-4">Test Page</h1>
      <p className="mb-6">This is a test page to check Next.js routing</p>
      
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">Try these links:</h2>
          <div className="flex flex-col space-y-2">
            <Link href="/space" className="text-blue-600 hover:underline">
              Go to Space
            </Link>
            <Link href="/tree-path" className="text-blue-600 hover:underline">
              Go to Tree Path
            </Link>
            <Link href="/" className="text-blue-600 hover:underline">
              Go Home
            </Link>
          </div>
        </div>
      </div>
      
      <div className="mt-8 p-4 bg-gray-100 rounded">
        <h2 className="text-xl font-semibold mb-2">Manual Navigation Test</h2>
        <button 
          onClick={() => {
            console.log('Manually navigating to /space');
            window.location.href = '/space';
          }}
          className="px-4 py-2 bg-blue-500 text-white rounded mr-2"
        >
          Navigate to Space
        </button>
        
        <button 
          onClick={() => {
            console.log('Manually navigating to /tree-path');
            window.location.href = '/tree-path';
          }}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          Navigate to Tree Path
        </button>
      </div>
    </div>
  );
} 