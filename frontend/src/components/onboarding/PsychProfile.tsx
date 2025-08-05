'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Star, TrendingUp } from 'lucide-react';
import { PsychProfile as PsychProfileType } from '../../types/onboarding';

interface PsychProfileProps {
  profile: PsychProfileType;
}

const PsychProfile: React.FC<PsychProfileProps> = ({ profile }) => {
  const { topTraits, description, hexaco, riasec } = profile;

  // Get top HEXACO traits
  const topHexacoTraits = Object.entries(hexaco)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 2)
    .map(([trait, score]) => ({
      name: trait.charAt(0).toUpperCase() + trait.slice(1),
      score: Math.round(score)
    }));

  // Get top RIASEC interests
  const topRiasecInterests = Object.entries(riasec)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 2)
    .map(([interest, score]) => ({
      name: interest.charAt(0).toUpperCase() + interest.slice(1),
      score: Math.round(score)
    }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-gradient-to-br from-primary/5 to-accent/5 rounded-3xl p-6 border border-primary/10"
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-primary/10 rounded-full">
          <Brain className="w-6 h-6 text-primary" />
        </div>
        <h3 className="text-xl font-semibold text-text-primary">
          Your Psychological Profile
        </h3>
      </div>

      <motion.p 
        className="text-text-secondary mb-6 leading-relaxed"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {description}
      </motion.p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Personality Traits */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100"
        >
          <div className="flex items-center space-x-2 mb-3">
            <Star className="w-5 h-5 text-accent" />
            <h4 className="font-semibold text-text-primary">Top Traits</h4>
          </div>
          <div className="space-y-2">
            {topTraits.map((trait, index) => (
              <motion.div
                key={trait}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-center space-x-2"
              >
                <div className="w-2 h-2 bg-accent rounded-full" />
                <span className="text-sm text-text-primary">{trait}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Career Interests */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100"
        >
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h4 className="font-semibold text-text-primary">Career Interests</h4>
          </div>
          <div className="space-y-3">
            {topRiasecInterests.map((interest, index) => (
              <motion.div
                key={interest.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="space-y-1"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-text-primary">
                    {interest.name}
                  </span>
                  <span className="text-xs text-text-secondary">
                    {interest.score}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="bg-primary h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${interest.score}%` }}
                    transition={{ delay: 0.7 + index * 0.1, duration: 0.8 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Personality Dimensions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-6 bg-white rounded-2xl p-4 shadow-sm border border-gray-100"
      >
        <h4 className="font-semibold text-text-primary mb-3">
          Personality Dimensions
        </h4>
        <div className="grid grid-cols-2 gap-3">
          {topHexacoTraits.map((trait, index) => (
            <motion.div
              key={trait.name}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.9 + index * 0.1 }}
              className="bg-surface rounded-xl p-3 text-center"
            >
              <div className="text-2xl font-bold text-primary">
                {trait.score}%
              </div>
              <div className="text-sm text-text-secondary">
                {trait.name}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default PsychProfile;