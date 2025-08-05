'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';

export default function ChallengesPage() {
  // Exemple de défis
  const challenges = [
    {
      title: 'Apprendre React Flow',
      description: 'Créez un graphe interactif avec React Flow et intégrez-le dans un projet existant.',
      xpReward: 150,
      progress: 75,
      isCompleted: false,
      difficulty: 'medium',
      domain: 'builder'
    },
    {
      title: 'Maîtriser Framer Motion',
      description: 'Implémentez des animations complexes avec Framer Motion pour améliorer l\'expérience utilisateur.',
      xpReward: 200,
      progress: 30,
      isCompleted: false,
      difficulty: 'hard',
      domain: 'builder'
    },
    {
      title: 'Présentation de projet',
      description: 'Préparez et délivrez une présentation de 10 minutes sur votre dernier projet à l\'équipe.',
      xpReward: 100,
      progress: 100,
      isCompleted: true,
      difficulty: 'easy',
      domain: 'communicator'
    }
  ];

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl md:text-4xl font-bold text-stitch-accent mb-6 font-departure">Défis</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {challenges.map((challenge, index) => (
            <div key={index} className="bg-stitch-primary border border-stitch-border rounded-lg p-6 shadow-soft hover:border-stitch-accent transition-colors">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-stitch-accent font-departure">{challenge.title}</h2>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  challenge.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                  challenge.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {challenge.difficulty === 'easy' ? 'Facile' :
                   challenge.difficulty === 'medium' ? 'Moyen' : 'Difficile'}
                </div>
              </div>
              
              <p className="text-stitch-sage mb-4 line-clamp-2">{challenge.description}</p>
              
              <div className="mb-4">
                <div className="flex justify-between text-sm text-stitch-sage mb-1">
                  <span>Progression</span>
                  <span>{challenge.progress}%</span>
                </div>
                <div className="h-2 bg-stitch-track rounded-full">
                  <div 
                    className="h-full bg-stitch-accent rounded-full" 
                    style={{ width: `${challenge.progress}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" fill="currentColor" viewBox="0 0 256 256" className="text-stitch-accent mr-1">
                    <path d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Z"></path>
                  </svg>
                  <span className="text-stitch-accent font-bold">{challenge.xpReward} XP</span>
                </div>
                <button className="btn btn-sm btn-primary">
                  {challenge.isCompleted ? 'Voir détails' : 'Continuer'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </MainLayout>
  );
}