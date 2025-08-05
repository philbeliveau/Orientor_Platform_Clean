'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import HollandResultsView from '@/components/profile/HollandResultsView';

export default function HollandResultsPage() {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Résultats du test Holland Code (RIASEC)</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Découvrez votre profil de personnalité professionnelle basé sur le modèle RIASEC (Réaliste, Investigateur, Artistique, Social, Entreprenant, Conventionnel).
          </p>
        </div>
        
        <HollandResultsView />
      </div>
    </MainLayout>
  );
}