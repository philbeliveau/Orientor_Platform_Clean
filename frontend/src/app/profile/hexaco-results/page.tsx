'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import HexacoResultsView from '@/components/profile/HexacoResultsView';

export default function HexacoResultsPage() {
  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Résultats du test HEXACO-PI-R
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Découvrez votre profil de personnalité basé sur le modèle HEXACO à six dimensions : 
            Honnêteté-Humilité, Émotivité, eXtraversion, Agréabilité, Conscienciosité et Ouverture à l'expérience.
          </p>
        </div>
        
        <HexacoResultsView />
      </div>
    </MainLayout>
  );
}