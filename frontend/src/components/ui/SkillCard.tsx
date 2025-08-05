'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

interface SkillCardProps {
  skill: {
    id: string;
    esco_label: string;
    esco_description: string;
    category: string;
    confidence: number;
    applications?: string[];
  };
  className?: string;
}

const SkillCard: React.FC<SkillCardProps> = ({ skill, className = '' }) => {
  const router = useRouter();

  const handleExploreClick = () => {
    router.push('/competence-tree');
  };

  // Get category icon and color
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'technical':
        return '⚙️';
      case 'interpersonal':
        return '🤝';
      case 'cognitive':
        return '🧠';
      case 'creative':
        return '🎨';
      case 'leadership':
        return '👑';
      default:
        return '💼';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'technical':
        return 'bg-blue-500';
      case 'interpersonal':
        return 'bg-green-500';
      case 'cognitive':
        return 'bg-purple-500';
      case 'creative':
        return 'bg-pink-500';
      case 'leadership':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div 
      className={`relative overflow-hidden rounded-lg border transition-all duration-300 hover:shadow-lg hover:scale-105 ${className}`}
      style={{
        backgroundColor: 'var(--primary-color)',
        borderColor: 'var(--border-color)',
      }}
    >
      {/* Category badge */}
      <div className="absolute top-3 right-3">
        <div 
          className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs text-white ${getCategoryColor(skill.category)}`}
        >
          <span>{getCategoryIcon(skill.category)}</span>
          <span className="font-medium">{skill.category}</span>
        </div>
      </div>

      {/* Confidence indicator */}
      <div className="absolute top-3 left-3">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-xs" style={{ color: 'var(--text-color)' }}>
            {Math.round(skill.confidence * 100)}%
          </span>
        </div>
      </div>

      <div className="p-6 pt-12">
        {/* Skill icon */}
        <div className="mb-4">
          <div 
            className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
            style={{ backgroundColor: 'var(--accent-color)' }}
          >
            {getCategoryIcon(skill.category)}
          </div>
        </div>

        {/* Skill title */}
        <h3 
          className="text-lg font-semibold mb-2 line-clamp-2"
          style={{ color: 'var(--accent-color)' }}
        >
          {skill.esco_label}
        </h3>

        {/* Skill description */}
        <p 
          className="text-sm mb-4 line-clamp-3"
          style={{ color: 'var(--text-color)' }}
        >
          {skill.esco_description}
        </p>

        {/* Applications preview */}
        {skill.applications && skill.applications.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {skill.applications.slice(0, 2).map((app, index) => (
                <span 
                  key={index}
                  className="text-xs px-2 py-1 rounded-full"
                  style={{ 
                    backgroundColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                >
                  {app}
                </span>
              ))}
              {skill.applications.length > 2 && (
                <span 
                  className="text-xs px-2 py-1 rounded-full"
                  style={{ 
                    backgroundColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                >
                  +{skill.applications.length - 2} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* CTA Button */}
        <button
          onClick={handleExploreClick}
          className="w-full py-2 px-4 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
          style={{ backgroundColor: 'var(--accent-color)' }}
        >
          Explore My Path
        </button>
      </div>

      {/* Hover overlay effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-transparent opacity-0 hover:opacity-10 transition-opacity duration-300 pointer-events-none" />
    </div>
  );
};

export default SkillCard;