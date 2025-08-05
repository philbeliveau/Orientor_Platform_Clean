'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import hexacoTestService, { HexacoVersion } from '@/services/hexacoTestService';

export default function HexacoSelectPage() {
  const router = useRouter();
  
  // États pour gérer la sélection
  const [availableVersions, setAvailableVersions] = useState<Record<string, HexacoVersion>>({});
  const [selectedLanguage, setSelectedLanguage] = useState<string>('fr');
  const [selectedVersion, setSelectedVersion] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Charger les versions disponibles au chargement de la page
  useEffect(() => {
    const loadVersions = async () => {
      try {
        setLoading(true);
        const versions = await hexacoTestService.getAvailableVersions();
        setAvailableVersions(versions);
        
        // Sélectionner automatiquement la première version française si disponible
        const frenchVersions = Object.entries(versions).filter(
          ([_, version]) => version.language === 'fr' && version.active
        );
        if (frenchVersions.length > 0) {
          setSelectedVersion(frenchVersions[0][0]);
        }
      } catch (err) {
        console.error('Erreur lors du chargement des versions:', err);
        setError('Impossible de charger les versions du test. Veuillez réessayer plus tard.');
      } finally {
        setLoading(false);
      }
    };

    loadVersions();
  }, []);

  // Filtrer les versions par langue sélectionnée
  const filteredVersions = Object.entries(availableVersions).filter(
    ([_, version]) => version.language === selectedLanguage && version.active
  );

  // Gérer le changement de langue
  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language);
    setSelectedVersion(''); // Réinitialiser la sélection de version
    
    // Sélectionner automatiquement la première version de la nouvelle langue
    const versionsForLanguage = Object.entries(availableVersions).filter(
      ([_, version]) => version.language === language && version.active
    );
    if (versionsForLanguage.length > 0) {
      setSelectedVersion(versionsForLanguage[0][0]);
    }
  };

  // Démarrer le test avec la version sélectionnée
  const handleStartTest = () => {
    if (selectedVersion) {
      router.push(`/hexaco-test?version=${selectedVersion}`);
    }
  };

  // Afficher un écran de chargement
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-xl">Chargement des versions du test HEXACO...</p>
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div 
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* En-tête */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Test de Personnalité HEXACO-PI-R
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Découvrez votre profil de personnalité selon le modèle HEXACO à six dimensions : 
            Honnêteté-Humilité, Émotivité, eXtraversion, Agréabilité, Conscienciosité et Ouverture à l'expérience.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          {/* Sélection de la langue */}
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              1. Choisissez votre langue
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => handleLanguageChange('fr')}
                className={`p-4 rounded-lg border-2 transition-colors ${
                  selectedLanguage === 'fr'
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                }`}
              >
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Français</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Version française du test</p>
                </div>
              </button>
              
              <button
                onClick={() => handleLanguageChange('en')}
                className={`p-4 rounded-lg border-2 transition-colors ${
                  selectedLanguage === 'en'
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                }`}
              >
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 dark:text-white">English</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">English version of the test</p>
                </div>
              </button>
            </div>
          </div>

          {/* Sélection de la version */}
          <div className="p-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              2. Choisissez la version du test
            </h2>
            
            {filteredVersions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400">
                  Aucune version disponible pour la langue sélectionnée.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredVersions.map(([versionId, version]) => (
                  <motion.button
                    key={versionId}
                    onClick={() => setSelectedVersion(versionId)}
                    className={`w-full p-6 rounded-lg border-2 text-left transition-colors ${
                      selectedVersion === versionId
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                          {version.title}
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-3">
                          {version.description}
                        </p>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
                          <span>
                            <strong>Questions:</strong> {version.item_count}
                          </span>
                          <span>
                            <strong>Durée estimée:</strong> {version.estimated_duration} minutes
                          </span>
                          <span>
                            <strong>Langue:</strong> {version.language === 'fr' ? 'Français' : 'English'}
                          </span>
                        </div>
                      </div>
                      {selectedVersion === versionId && (
                        <div className="ml-4">
                          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            )}
          </div>

          {/* Boutons d'action */}
          <div className="p-6 bg-gray-50 dark:bg-gray-700 flex flex-col sm:flex-row justify-between gap-4">
            <button
              onClick={() => router.push('/')}
              className="flex-1 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
            >
              Retour à l'accueil
            </button>
            
            <button
              onClick={handleStartTest}
              disabled={!selectedVersion}
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
            >
              Commencer le test
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}