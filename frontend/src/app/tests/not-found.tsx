'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';

export default function TestsNotFound() {
  const router = useRouter();

  return (
    <MainLayout>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-9xl font-bold text-gray-300">404</h1>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Test non trouvé
            </h2>
            <p className="text-gray-600 mb-8">
              Le test que vous recherchez n'existe pas ou n'est pas disponible.
            </p>
          </div>
          
          <div className="space-y-4">
            <button
              onClick={() => router.push('/tests')}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors duration-200"
            >
              Voir tous les tests
            </button>
            
            <button
              onClick={() => router.push('/space')}
              className="w-full bg-gray-200 text-gray-800 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition-colors duration-200"
            >
              Retour à l'accueil
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}