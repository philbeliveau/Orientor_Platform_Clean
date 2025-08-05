'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import hexacoTestService, { HexacoScoreResponse } from '@/services/hexacoTestService';
import HexacoChart from '@/components/hexaco-test/HexacoChart';
import { useRouter } from 'next/navigation';
import LoadingScreen from '@/components/ui/LoadingScreen';

const HexacoResultsView: React.FC = () => {
  const router = useRouter();
  const [profile, setProfile] = useState<HexacoScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPercentiles, setShowPercentiles] = useState(false);

  // Charger le profil HEXACO de l'utilisateur
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const userProfile = await hexacoTestService.getMyProfile();
        setProfile(userProfile);
      } catch (err) {
        console.error('Erreur lors du chargement du profil HEXACO:', err);
        setError('Impossible de charger votre profil HEXACO.');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  // Descriptions des domaines HEXACO (version courte pour le profil)
  const domainDescriptions: Record<string, { title: string; shortDesc: string }> = {
    'honesty_humility': {
      title: 'Honnêteté-Humilité',
      shortDesc: 'Sincérité, modestie et équité'
    },
    'emotionality': {
      title: 'Émotivité',
      shortDesc: 'Sensibilité émotionnelle et anxiété'
    },
    'extraversion': {
      title: 'eXtraversion',
      shortDesc: 'Sociabilité et assertivité'
    },
    'agreeableness': {
      title: 'Agréabilité',
      shortDesc: 'Indulgence et coopération'
    },
    'conscientiousness': {
      title: 'Conscienciosité',
      shortDesc: 'Organisation et discipline'
    },
    'openness': {
      title: 'Ouverture',
      shortDesc: 'Créativité et curiosité intellectuelle'
    }
  };

  if (loading) {
    return <LoadingScreen message="Chargement de votre profil HEXACO..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 max-w-md mx-auto">
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Erreur de chargement
          </h3>
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-8 max-w-md mx-auto">
          <div className="text-6xl mb-4">🧠</div>
          <h3 className="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">
            Aucun résultat HEXACO
          </h3>
          <p className="text-blue-600 dark:text-blue-400 mb-6">
            Vous n'avez pas encore passé le test de personnalité HEXACO-PI-R. 
            Découvrez votre profil de personnalité en six dimensions !
          </p>
          <button
            onClick={() => router.push('/hexaco-test/select')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Passer le test HEXACO
          </button>
        </div>
      </div>
    );
  }

  // Obtenir le domaine dominant
  const dominantDomain = Object.entries(profile.domains).reduce((a, b) => 
    profile.domains[a[0]] > profile.domains[b[0]] ? a : b
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Statistiques générales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {profile.total_responses}
            </div>
            <div className="text-gray-600 dark:text-gray-400">
              Questions répondues
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {(profile.completion_rate * 100).toFixed(0)}%
            </div>
            <div className="text-gray-600 dark:text-gray-400">
              Test complété
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {domainDescriptions[dominantDomain[0]]?.title || 'N/A'}
            </div>
            <div className="text-gray-600 dark:text-gray-400">
              Trait dominant
            </div>
          </div>
        </div>
      </div>

      {/* Graphique radar principal */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
            Votre profil HEXACO
          </h3>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowPercentiles(!showPercentiles)}
              className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
            >
              {showPercentiles ? 'Scores bruts' : 'Percentiles'}
            </button>
            <button
              onClick={() => router.push('/hexaco-test/select')}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Refaire le test
            </button>
          </div>
        </div>
        
        <HexacoChart scores={profile} showPercentiles={showPercentiles} size="large" />
      </div>

      {/* Résumé des domaines */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(profile.domains).map(([domain, value]) => {
          const info = domainDescriptions[domain];
          if (!info) return null;

          const percentile = profile.percentiles[domain] || 0;
          const isHigh = value >= 3.5;
          const isLow = value <= 2.5;

          return (
            <motion.div
              key={domain}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-gray-800 dark:text-white">
                    {info.title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {info.shortDesc}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-blue-600">
                    {value.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {percentile.toFixed(0)}e percentile
                  </div>
                </div>
              </div>
              
              <div className="mt-3 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    isHigh 
                      ? 'bg-green-500' 
                      : isLow 
                      ? 'bg-orange-500' 
                      : 'bg-blue-500'
                  }`}
                  style={{ width: `${(value / 5) * 100}%` }}
                />
              </div>
              
              <div className="mt-2 text-xs text-center">
                <span className={`px-2 py-1 rounded-full ${
                  isHigh 
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                    : isLow
                    ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200'
                    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
                }`}>
                  {isHigh ? 'Élevé' : isLow ? 'Faible' : 'Modéré'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Description narrative */}
      {profile.narrative_description && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
            Analyse personnalisée de votre profil
          </h3>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            {profile.narrative_description}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={() => router.push('/hexaco-test/select')}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Refaire le test
        </button>
        <button
          onClick={() => window.print()}
          className="px-6 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
        >
          Imprimer les résultats
        </button>
      </div>
    </motion.div>
  );
};

export default HexacoResultsView;