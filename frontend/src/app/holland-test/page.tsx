'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import hollandTestService, { Question, ScoreResponse, TestMetadata } from '@/services/hollandTestService';
import TestInterface from '@/components/holland-test/TestInterface';
import ResultScreen from '@/components/holland-test/ResultScreen';
import { motion } from 'framer-motion';

export default function HollandTestPage() {
  const router = useRouter();
  
  // États pour gérer le flux du test
  const [testMetadata, setTestMetadata] = useState<TestMetadata | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [attemptId, setAttemptId] = useState<string>('');
  const [testScore, setTestScore] = useState<ScoreResponse | null>(null);
  const [testState, setTestState] = useState<'loading' | 'intro' | 'testing' | 'results'>('loading');
  const [error, setError] = useState<string | null>(null);

  // Charger les métadonnées et les questions du test au chargement de la page
  useEffect(() => {
    const loadTestData = async () => {
      try {
        // Charger les métadonnées du test
        const metadata = await hollandTestService.getTestMetadata();
        setTestMetadata(metadata);
        
        // Charger les questions du test
        const testQuestions = await hollandTestService.getQuestions();
        setQuestions(testQuestions);
        
        // Générer un ID de tentative unique
        const newAttemptId = hollandTestService.generateAttemptId();
        setAttemptId(newAttemptId);
        
        // Passer à l'écran d'introduction
        setTestState('intro');
      } catch (err) {
        console.error('Erreur lors du chargement des données du test:', err);
        setError('Impossible de charger le test. Veuillez réessayer plus tard.');
        setTestState('intro'); // Afficher l'intro même en cas d'erreur pour permettre de réessayer
      }
    };

    loadTestData();
  }, []);

  // Démarrer le test
  const handleStartTest = () => {
    setTestState('testing');
  };

  // Gérer la fin du test
  const handleTestComplete = async (completedAttemptId: string) => {
    try {
      // Récupérer les scores du test
      const score = await hollandTestService.getScore(completedAttemptId, true);
      setTestScore(score);
      setTestState('results');
    } catch (err) {
      console.error('Erreur lors de la récupération des résultats:', err);
      setError('Impossible de récupérer vos résultats. Veuillez réessayer.');
    }
  };

  // Gérer les erreurs pendant le test
  const handleTestError = (err: Error) => {
    console.error('Erreur pendant le test:', err);
    setError(`Une erreur est survenue: ${err.message}`);
  };

  // Recommencer le test
  const handleRetakeTest = () => {
    // Générer un nouvel ID de tentative
    const newAttemptId = hollandTestService.generateAttemptId();
    setAttemptId(newAttemptId);
    setTestScore(null);
    setTestState('intro');
  };

  // Afficher un écran de chargement
  if (testState === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-xl">Chargement du test Holland Code...</p>
        </div>
      </div>
    );
  }

  // Afficher un message d'erreur si nécessaire
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Erreur</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  // Afficher l'écran d'introduction
  if (testState === 'intro' && testMetadata) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* En-tête avec image si disponible */}
          {testMetadata.image_url && (
            <div className="w-full h-48 bg-cover bg-center" style={{ backgroundImage: `url(${testMetadata.image_url})` }}></div>
          )}
          
          <div className="p-6 md:p-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              {testMetadata.title}
            </h1>
            
            <div className="prose dark:prose-invert mb-8">
              <p className="text-lg text-gray-700 dark:text-gray-300">
                {testMetadata.description}
              </p>
              
              <div className="mt-6 space-y-4 text-gray-600 dark:text-gray-400">
                <p>
                  <span className="font-medium">Nombre de questions:</span> {testMetadata.question_count}
                </p>
                <p>
                  <span className="font-medium">Durée estimée:</span> {Math.ceil(testMetadata.question_count * 0.5)} minutes
                </p>
                <p>
                  Ce test vous aidera à découvrir votre code Holland (RIASEC), qui reflète vos intérêts professionnels et votre personnalité.
                </p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row justify-between gap-4">
              <button
                onClick={handleStartTest}
                className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                Commencer le test
              </button>
              
              <button
                onClick={() => router.push('/')}
                className="flex-1 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
              >
                Retour à l'accueil
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Afficher l'interface de test
  if (testState === 'testing' && questions.length > 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <TestInterface
          questions={questions}
          attemptId={attemptId}
          onTestComplete={handleTestComplete}
          onError={handleTestError}
        />
      </div>
    );
  }

  // Afficher les résultats
  if (testState === 'results' && testScore) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4">
        <ResultScreen score={testScore} onRetakeTest={handleRetakeTest} />
      </div>
    );
  }

  // Fallback
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <p className="text-xl">Chargement...</p>
    </div>
  );
}