'use client';

import React, { useState } from 'react';
import { HexacoScoreResponse } from '@/services/hexacoTestService';
import HexacoChart from './HexacoChart';
import { motion } from 'framer-motion';

// Descriptions des domaines HEXACO
const domainDescriptions: Record<string, { title: string; description: string; high: string; low: string }> = {
  'honesty_humility': {
    title: 'Honnêteté-Humilité',
    description: 'Tendance à être sincère et modeste versus manipulateur et prétentieux.',
    high: 'Vous êtes sincère, honnête, fidèle, loyal, modeste et sans prétention.',
    low: 'Vous pouvez être manipulateur, narcissique, prétentieux et avoir tendance à enfreindre les règles pour un gain personnel.'
  },
  'emotionality': {
    title: 'Émotivité',
    description: 'Tendance à éprouver de la peur, de l\'anxiété, de la dépendance et de la sensibilité émotionnelle.',
    high: 'Vous êtes émotionnellement réactif, anxieux, vulnérable et avez besoin de soutien émotionnel.',
    low: 'Vous êtes émotionnellement stable, courageux, résistant au stress et indépendant.'
  },
  'extraversion': {
    title: 'eXtraversion',
    description: 'Tendance à être sociable, énergique, assertif et à rechercher l\'attention.',
    high: 'Vous êtes sociable, vivant, extraverti, assertif et aimez être le centre d\'attention.',
    low: 'Vous êtes introverti, réservé, social uniquement avec des amis proches et évitez d\'être le centre d\'attention.'
  },
  'agreeableness': {
    title: 'Agréabilité',
    description: 'Tendance à être indulgent, gentil et coopératif versus critique et antagoniste.',
    high: 'Vous êtes indulgent, gentil, coopératif, flexible et contrôlez votre colère.',
    low: 'Vous êtes critique, querelleur, têtu, exigeant et vous vous mettez facilement en colère.'
  },
  'conscientiousness': {
    title: 'Conscienciosité',
    description: 'Tendance à être organisé, discipliné et prudent versus désordonné et impulsif.',
    high: 'Vous êtes organisé, discipliné, diligent, prudent et perfectionniste.',
    low: 'Vous êtes désordonné, négligent, impulsif, irresponsable et prenez des décisions hâtives.'
  },
  'openness': {
    title: 'Ouverture à l\'expérience',
    description: 'Tendance à apprécier l\'art, la nature, la réflexion et les idées non conventionnelles.',
    high: 'Vous êtes créatif, innovant, curieux intellectuellement et appréciez l\'art et la beauté.',
    low: 'Vous êtes conventionnel, traditionnel, préférez la familiarité et êtes moins intéressé par l\'art.'
  }
};

interface ResultScreenProps {
  score: HexacoScoreResponse;
  onRetakeTest: () => void;
}

const ResultScreen: React.FC<ResultScreenProps> = ({ score, onRetakeTest }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'domains' | 'facets'>('overview');
  const [showPercentiles, setShowPercentiles] = useState(false);

  // Obtenir le domaine dominant
  const dominantDomain = Object.entries(score.domains).reduce((a, b) => 
    score.domains[a[0]] > score.domains[b[0]] ? a : b
  );

  // Obtenir les domaines les plus élevés et les plus bas
  const sortedDomains = Object.entries(score.domains).sort((a, b) => b[1] - a[1]);
  const highestDomains = sortedDomains.slice(0, 2);
  const lowestDomains = sortedDomains.slice(-2).reverse();

  return (
    <motion.div 
      className="flex flex-col items-center justify-center w-full max-w-6xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold text-center mb-6 text-gray-800 dark:text-white">
        Vos résultats du test HEXACO-PI-R
      </h2>
      
      {/* Statistiques de completion */}
      <div className="flex justify-center space-x-6 mb-8 text-sm text-gray-600 dark:text-gray-400">
        <div className="text-center">
          <div className="font-semibold text-lg text-blue-600">{score.total_responses}</div>
          <div>Réponses</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-lg text-green-600">{(score.completion_rate * 100).toFixed(1)}%</div>
          <div>Complété</div>
        </div>
      </div>

      {/* Navigation par onglets */}
      <div className="flex space-x-1 mb-8 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
        {[
          { key: 'overview', label: 'Vue d\'ensemble' },
          { key: 'domains', label: 'Domaines' },
          { key: 'facets', label: 'Facettes' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-white dark:bg-gray-800 text-blue-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenu des onglets */}
      <div className="w-full">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Graphique radar principal */}
            <div className="text-center">
              <div className="flex justify-center items-center space-x-4 mb-4">
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
                  Profil HEXACO
                </h3>
                <button
                  onClick={() => setShowPercentiles(!showPercentiles)}
                  className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  {showPercentiles ? 'Scores bruts' : 'Percentiles'}
                </button>
              </div>
              <HexacoChart scores={score} showPercentiles={showPercentiles} size="large" />
            </div>

            {/* Trait dominant */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-3 text-blue-900 dark:text-blue-100">
                Votre trait dominant : {domainDescriptions[dominantDomain[0]]?.title}
              </h3>
              <p className="text-blue-800 dark:text-blue-200 mb-3">
                {domainDescriptions[dominantDomain[0]]?.description}
              </p>
              <p className="text-blue-700 dark:text-blue-300">
                <strong>Score : {dominantDomain[1].toFixed(2)}/5</strong> - {
                  dominantDomain[1] >= 3.5 
                    ? domainDescriptions[dominantDomain[0]]?.high
                    : dominantDomain[1] <= 2.5
                    ? domainDescriptions[dominantDomain[0]]?.low
                    : 'Vous présentez un niveau modéré dans ce domaine.'
                }
              </p>
            </div>

            {/* Description narrative générée par l'IA */}
            {score.narrative_description && (
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">
                  Analyse personnalisée de votre profil
                </h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  {score.narrative_description}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'domains' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(score.domains).map(([domain, value]) => {
                const info = domainDescriptions[domain];
                if (!info) return null;

                const percentile = score.percentiles[domain] || 0;
                const isHigh = value >= 3.5;
                const isLow = value <= 2.5;

                return (
                  <motion.div
                    key={domain}
                    className="bg-white dark:bg-gray-700 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600"
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="text-lg font-semibold text-gray-800 dark:text-white">
                        {info.title}
                      </h4>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue-600">
                          {value.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {percentile.toFixed(0)}e percentile
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                      {info.description}
                    </p>
                    
                    <div className={`p-3 rounded text-sm ${
                      isHigh 
                        ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                        : isLow
                        ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-800 dark:text-orange-200'
                        : 'bg-gray-50 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                    }`}>
                      {isHigh ? info.high : isLow ? info.low : 'Vous présentez un niveau modéré dans ce domaine.'}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'facets' && (
          <div className="space-y-4">
            <p className="text-center text-gray-600 dark:text-gray-400 mb-6">
              Scores détaillés par facette (sous-dimensions de chaque domaine)
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(score.facets).map(([facet, value]) => (
                <div
                  key={facet}
                  className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600"
                >
                  <div className="flex justify-between items-center">
                    <h5 className="font-medium text-gray-800 dark:text-white text-sm">
                      {facet.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h5>
                    <span className="text-lg font-bold text-blue-600">
                      {value.toFixed(1)}
                    </span>
                  </div>
                  <div className="mt-2 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(value / 5) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Boutons d'action */}
      <div className="flex flex-col sm:flex-row gap-4 mt-8 w-full max-w-md">
        <button
          onClick={onRetakeTest}
          className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Refaire le test
        </button>
        <button
          onClick={() => window.print()}
          className="flex-1 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
        >
          Imprimer les résultats
        </button>
      </div>
    </motion.div>
  );
};

export default ResultScreen;