'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import hexacoTestService, { HexacoQuestion, HexacoScoreResponse, HexacoVersion } from '@/services/hexacoTestService';
import TestInterface from '@/components/hexaco-test/TestInterface';
import ResultScreen from '@/components/hexaco-test/ResultScreen';
import { motion } from 'framer-motion';

export default function HexacoTestPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const versionId = searchParams?.get('version');
  
  // États pour gérer le flux du test
  const [versionMetadata, setVersionMetadata] = useState<HexacoVersion | null>(null);
  const [questions, setQuestions] = useState<HexacoQuestion[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [testScore, setTestScore] = useState<HexacoScoreResponse | null>(null);
  const [testState, setTestState] = useState<'loading' | 'intro' | 'testing' | 'results'>('loading');
  const [error, setError] = useState<string | null>(null);

  // Charger les données du test au chargement de la page
  useEffect(() => {
    const loadTestData = async () => {
      if (!versionId) {
        router.push('/hexaco-test/select');
        return;
      }

      try {
        // Charger les versions disponibles pour obtenir les métadonnées
        const versions = await hexacoTestService.getAvailableVersions();
        const version = versions[versionId];
        
        if (!version || !version.active) {
          setError('Version de test non trouvée ou inactive.');
          return;
        }
        
        setVersionMetadata(version);
        
        // Charger les questions du test
        const testQuestions = await hexacoTestService.getQuestions(versionId);
        setQuestions(testQuestions);
        
        // Passer à l'écran d'introduction
        setTestState('intro');
      } catch (err) {
        console.error('Erreur lors du chargement des données du test:', err);
        setError('Impossible de charger le test. Veuillez réessayer plus tard.');
        setTestState('intro'); // Afficher l'intro même en cas d'erreur pour permettre de réessayer
      }
    };

    loadTestData();
  }, [versionId, router]);

  // Démarrer le test
  const handleStartTest = async () => {
    if (!versionId) return;
    
    try {
      // Créer une nouvelle session de test
      const session = await hexacoTestService.startTest(versionId);
      setSessionId(session.session_id);
      setTestState('testing');
    } catch (err) {
      console.error('Erreur lors du démarrage du test:', err);
      setError('Impossible de démarrer le test. Veuillez réessayer.');
    }
  };

  // Gérer la fin du test
  const handleTestComplete = async (completedSessionId: string) => {
    try {
      // Récupérer les scores du test
      const score = await hexacoTestService.getScore(completedSessionId, true);
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
    setSessionId('');
    setTestScore(null);
    setTestState('intro');
  };

  // Afficher un écran de chargement
  if (testState === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-xl">Chargement du test HEXACO...</p>
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
          <div className="flex gap-4">
            <button
              onClick={() => window.location.reload()}
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Réessayer
            </button>
            <button
              onClick={() => router.push('/hexaco-test/select')}
              className="flex-1 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
            >
              Changer de version
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Afficher l'écran d'introduction
  if (testState === 'intro' && versionMetadata) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="p-6 md:p-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              {versionMetadata.title}
            </h1>
            
            <div className="prose dark:prose-invert mb-8">
              <p className="text-lg text-gray-700 dark:text-gray-300">
                {versionMetadata.description}
              </p>
              
              <div className="mt-6 space-y-4 text-gray-600 dark:text-gray-400">
                <p>
                  <span className="font-medium">Nombre de questions:</span> {versionMetadata.item_count}
                </p>
                <p>
                  <span className="font-medium">Durée estimée:</span> {versionMetadata.estimated_duration} minutes
                </p>
                <p>
                  <span className="font-medium">Langue:</span> {versionMetadata.language === 'fr' ? 'Français' : 'English'}
                </p>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    À propos du test HEXACO-PI-R
                  </h3>
                  <p className="text-blue-800 dark:text-blue-200 text-sm">
                    Le test HEXACO-PI-R évalue votre personnalité selon six dimensions principales : 
                    Honnêteté-Humilité, Émotivité, eXtraversion, Agréabilité, Conscienciosité et Ouverture à l'expérience. 
                    Chaque question utilise une échelle de 1 (fortement en désaccord) à 5 (fortement d'accord).
                  </p>
                </div>
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
                onClick={() => router.push('/hexaco-test/select')}
                className="flex-1 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
              >
                Changer de version
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Afficher l'interface de test
  if (testState === 'testing' && questions.length > 0 && sessionId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <TestInterface
          questions={questions}
          sessionId={sessionId}
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