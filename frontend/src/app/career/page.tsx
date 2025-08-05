'use client';
import React from 'react';
import CareerTree from '@/components/tree/CareerTree';
import MainLayout from '@/components/layout/MainLayout';

export default function CareerTreePage() {
  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-light text-gray-800 dark:text-gray-100">Career Exploration</h1>
          <p className="mt-2 text-base text-gray-600 dark:text-gray-300">
            Discover different career domains and families to find your path
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm border border-gray-100 dark:border-gray-700">
          <CareerTree />
        </div>
      </div>
    </MainLayout>
  );
} 