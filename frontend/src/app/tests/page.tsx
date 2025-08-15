'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import MainLayout from '@/components/layout/MainLayout';

export default function TestsPage() {
  const router = useRouter();

  const assessments = [
    {
      id: 'hexaco',
      title: 'Test HEXACO-PI-R',
      description: 'Évaluation complète de votre personnalité basée sur 6 dimensions principales',
      duration: '15-25 minutes',
      route: '/hexaco-test',
      color: 'from-blue-500 to-purple-600',
    },
    {
      id: 'holland',
      title: 'Test Holland Code',
      description: 'Découvrez votre profil de personnalité professionnelle et vos intérêts de carrière',
      duration: '10-15 minutes',
      route: '/holland-test',
      color: 'from-green-500 to-teal-600',
    },
  ];

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Évaluations de Personnalité
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Découvrez vos traits de personnalité et vos intérêts professionnels grâce à nos tests scientifiquement validés
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            {assessments.map((assessment, index) => (
              <motion.div
                key={assessment.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                className="group relative overflow-hidden rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${assessment.color} opacity-10 group-hover:opacity-20 transition-opacity duration-300`}></div>
                
                <div className="relative p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-gray-900">
                      {assessment.title}
                    </h3>
                    <span className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
                      {assessment.duration}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-8 leading-relaxed">
                    {assessment.description}
                  </p>
                  
                  <button
                    onClick={() => router.push(assessment.route)}
                    className={`w-full bg-gradient-to-r ${assessment.color} text-white py-3 px-6 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200`}
                  >
                    Commencer le test
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}