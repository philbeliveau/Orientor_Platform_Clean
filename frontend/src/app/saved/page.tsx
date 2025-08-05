'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';

export default function SavedPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl md:text-4xl font-bold text-stitch-accent mb-6 font-departure">Éléments sauvegardés</h1>
        
        <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 md:p-8 shadow-soft">
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="64px" height="64px" fill="currentColor" viewBox="0 0 256 256" className="text-stitch-sage mb-4">
              <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
            </svg>
            <h2 className="text-xl md:text-2xl font-bold text-stitch-accent mb-2 font-departure">Aucun élément sauvegardé</h2>
            <p className="text-stitch-sage mb-6">Sauvegardez des ressources, des parcours ou des compétences pour y accéder facilement plus tard.</p>
            <button className="btn btn-primary">Explorer les ressources</button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}