'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import SelfReflectionSection from '@/components/reflection/SelfReflectionSection';
import Link from 'next/link';

export default function SelfReflectionPage() {
  return (
    <MainLayout showNav={true}>
      <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
        <div className="relative z-10 w-full flex h-full grow">
          {/* Main Content */}
          <div className="flex flex-col flex-1 w-full">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
              <div className="flex items-center gap-4">
                <Link 
                  href="/"
                  className="premium-button-icon"
                  title="Retour à l'accueil"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Link>
                <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight">
                  Self-Reflection
                </h1>
              </div>
            </div>

            {/* Main Content Container */}
            <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
              <div className="mb-6">
                <p className="premium-text-secondary text-lg">
                  Explorez vos forces et talents naturels à travers une série de questions de réflexion personnalisées. 
                  Ces insights vous aideront à mieux comprendre vos aptitudes uniques et à orienter votre développement professionnel.
                </p>
              </div>
              
              <SelfReflectionSection />
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}