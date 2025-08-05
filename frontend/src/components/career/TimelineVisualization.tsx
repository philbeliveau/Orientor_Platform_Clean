'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface SkillNode {
  id: string;
  label: string;
  confidence_score: number;
  type: 'domain' | 'family' | 'skill';
  level: number;
  children?: SkillNode[];
  relationships?: string[];
  metadata?: {
    description?: string;
    estimated_months?: number;
    prerequisites?: string[];
    learning_resources?: string[];
  };
}

interface TimelineTier {
  id: string;
  title: string;
  level: number;
  timeline_months: number;
  skills: SkillNode[];
  confidence_threshold: number;
}

interface TimelineVisualizationProps {
  tiers: TimelineTier[];
  onSkillClick?: (skill: SkillNode) => void;
  className?: string;
}

// Calculate visual prominence based on GraphSage confidence score
const getScoreVisualization = (score: number) => {
  const intensity = Math.max(0.3, Math.min(1, score)); // Clamp between 0.3 and 1
  const size = 40 + (intensity * 60); // Scale from 40px to 100px
  const opacity = 0.6 + (intensity * 0.4); // Scale from 60% to 100% opacity
  const borderWidth = 2 + (intensity * 4); // Scale from 2px to 6px border
  
  return {
    size,
    opacity,
    borderWidth,
    intensity,
    backgroundColor: `rgba(59, 130, 246, ${opacity})`, // Blue with variable opacity
    borderColor: `rgba(37, 99, 235, ${intensity})`, // Darker blue border
  };
};

// Skill relationship connector component (simplified)
// Note: Full connector visualization can be implemented when motion components are re-enabled

// Individual skill node component
const SkillNodeComponent: React.FC<{
  skill: SkillNode;
  onClick?: () => void;
  isHighlighted?: boolean;
}> = ({ skill, onClick, isHighlighted = false }) => {
  const visualization = getScoreVisualization(skill.confidence_score);
  
  return (
    <div
      className={`relative cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95 ${
        isHighlighted ? 'ring-2 ring-yellow-400 ring-offset-2' : ''
      }`}
      onClick={onClick}
      style={{
        width: visualization.size,
        height: visualization.size,
      }}
    >
      <div
        className="w-full h-full rounded-lg shadow-md flex items-center justify-center text-white font-medium text-xs text-center leading-tight p-1"
        style={{
          backgroundColor: visualization.backgroundColor,
          borderWidth: visualization.borderWidth,
          borderColor: visualization.borderColor,
          borderStyle: 'solid',
        }}
      >
        {skill.label}
      </div>
      
      {/* Confidence score indicator */}
      <div className="absolute -top-2 -right-2 bg-white rounded-full border-2 border-gray-300 w-6 h-6 flex items-center justify-center text-xs font-bold text-gray-700">
        {Math.round(skill.confidence_score * 100)}
      </div>
      
      {/* Hover tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
        Confidence: {Math.round(skill.confidence_score * 100)}%
      </div>
    </div>
  );
};

// Expandable tier component
const TierComponent: React.FC<{
  tier: TimelineTier;
  isExpanded: boolean;
  onToggle: () => void;
  onSkillClick?: (skill: SkillNode) => void;
  highlightedSkills?: Set<string>;
}> = ({ tier, isExpanded, onToggle, onSkillClick, highlightedSkills = new Set() }) => {
  const highConfidenceSkills = tier.skills.filter(s => s.confidence_score >= tier.confidence_threshold);
  const mediumConfidenceSkills = tier.skills.filter(s => s.confidence_score >= 0.5 && s.confidence_score < tier.confidence_threshold);
  const lowConfidenceSkills = tier.skills.filter(s => s.confidence_score < 0.5);
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Tier Header */}
      <div
        className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 cursor-pointer flex items-center justify-between hover:from-blue-100 hover:to-indigo-100 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
            {tier.level}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{tier.title}</h3>
            <p className="text-sm text-gray-600">
              {tier.timeline_months} months • {tier.skills.length} skills
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {highConfidenceSkills.length} high confidence
            </div>
            <div className="text-xs text-gray-500">
              {mediumConfidenceSkills.length} medium • {lowConfidenceSkills.length} low
            </div>
          </div>
          {isExpanded ? (
            <ChevronDownIcon className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronRightIcon className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>
      
      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 animate-in slide-in-from-top duration-300">
            {/* High Confidence Skills */}
            {highConfidenceSkills.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-green-700 mb-2">
                  High Confidence ({tier.confidence_threshold * 100}%+)
                </h4>
                <div className="flex flex-wrap gap-3">
                  {highConfidenceSkills.map((skill) => (
                    <div key={skill.id} className="group">
                      <SkillNodeComponent
                        skill={skill}
                        onClick={() => onSkillClick?.(skill)}
                        isHighlighted={highlightedSkills.has(skill.id)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Medium Confidence Skills */}
            {mediumConfidenceSkills.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-yellow-700 mb-2">
                  Medium Confidence (50-{tier.confidence_threshold * 100}%)
                </h4>
                <div className="flex flex-wrap gap-3">
                  {mediumConfidenceSkills.map((skill) => (
                    <div key={skill.id} className="group">
                      <SkillNodeComponent
                        skill={skill}
                        onClick={() => onSkillClick?.(skill)}
                        isHighlighted={highlightedSkills.has(skill.id)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Low Confidence Skills */}
            {lowConfidenceSkills.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-red-700 mb-2">
                  Low Confidence (&lt; 50%)
                </h4>
                <div className="flex flex-wrap gap-3">
                  {lowConfidenceSkills.map((skill) => (
                    <div key={skill.id} className="group">
                      <SkillNodeComponent
                        skill={skill}
                        onClick={() => onSkillClick?.(skill)}
                        isHighlighted={highlightedSkills.has(skill.id)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
};

// Main Timeline Visualization Component
const TimelineVisualization: React.FC<TimelineVisualizationProps> = ({
  tiers,
  onSkillClick,
  className = '',
}) => {
  const [expandedTiers, setExpandedTiers] = useState<Set<string>>(new Set([tiers[0]?.id]));
  const [selectedSkill, setSelectedSkill] = useState<SkillNode | null>(null);
  const [highlightedSkills, setHighlightedSkills] = useState<Set<string>>(new Set());
  
  const toggleTier = useCallback((tierId: string) => {
    setExpandedTiers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tierId)) {
        newSet.delete(tierId);
      } else {
        newSet.add(tierId);
      }
      return newSet;
    });
  }, []);
  
  const handleSkillClick = useCallback((skill: SkillNode) => {
    setSelectedSkill(skill);
    
    // Highlight related skills
    const relatedIds = new Set(skill.relationships || []);
    relatedIds.add(skill.id);
    setHighlightedSkills(relatedIds);
    
    onSkillClick?.(skill);
  }, [onSkillClick]);
  
  // Timeline progress calculation
  const totalMonths = useMemo(() => {
    return tiers.reduce((sum, tier) => sum + tier.timeline_months, 0);
  }, [tiers]);
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Timeline Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-xl">
        <h2 className="text-2xl font-bold mb-2">Career Progression Timeline</h2>
        <p className="text-blue-100">
          {tiers.length} tiers • {totalMonths} months total • GraphSage confidence scoring
        </p>
      </div>
      
      {/* Timeline Progress Bar */}
      <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
        {tiers.map((tier, index) => {
          const widthPercentage = (tier.timeline_months / totalMonths) * 100;
          const colors = ['bg-green-500', 'bg-blue-500', 'bg-purple-500', 'bg-indigo-500', 'bg-pink-500'];
          
          return (
            <div
              key={tier.id}
              className={`h-full float-left ${colors[index % colors.length]}`}
              style={{ width: `${widthPercentage}%` }}
              title={`${tier.title}: ${tier.timeline_months} months`}
            />
          );
        })}
      </div>
      
      {/* Tier Components */}
      <div className="space-y-4">
        {tiers.map((tier) => (
          <TierComponent
            key={tier.id}
            tier={tier}
            isExpanded={expandedTiers.has(tier.id)}
            onToggle={() => toggleTier(tier.id)}
            onSkillClick={handleSkillClick}
            highlightedSkills={highlightedSkills}
          />
        ))}
      </div>
      
      {/* Skill Detail Modal */}
      {selectedSkill && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
             onClick={() => setSelectedSkill(null)}>
          <div className="bg-white rounded-xl max-w-md w-full p-6 animate-in zoom-in-95 duration-200"
               onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">{selectedSkill.label}</h3>
                <button
                  onClick={() => setSelectedSkill(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Confidence Score</div>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${selectedSkill.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {Math.round(selectedSkill.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
                
                {selectedSkill.metadata?.description && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">Description</div>
                    <p className="text-sm text-gray-600">{selectedSkill.metadata.description}</p>
                  </div>
                )}
                
                {selectedSkill.metadata?.estimated_months && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">Estimated Time</div>
                    <p className="text-sm text-gray-600">{selectedSkill.metadata.estimated_months} months</p>
                  </div>
                )}
                
                {selectedSkill.relationships && selectedSkill.relationships.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">Related Skills</div>
                    <div className="flex flex-wrap gap-2">
                      {selectedSkill.relationships.map((relId) => (
                        <span key={relId} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {relId}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineVisualization;
export type { SkillNode, TimelineTier };