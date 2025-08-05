import React, { useState } from 'react';
import { FeasibilityData, Barrier } from '@/types/unifiedJob';

interface FeasibilityBoxProps {
  feasibilityData: FeasibilityData;
  jobTitle: string;
}

const FeasibilityBox: React.FC<FeasibilityBoxProps> = ({
  feasibilityData,
  jobTitle
}) => {
  const [expandedSection, setExpandedSection] = useState<string | null>('barriers');

  const getBarrierIcon = (type: Barrier['type']) => {
    switch (type) {
      case 'education': return '🎓';
      case 'skill': return '💡';
      case 'experience': return '💼';
      case 'certification': return '📜';
      case 'financial': return '💰';
      default: return '⚠️';
    }
  };

  const getSeverityColor = (severity: Barrier['severity']) => {
    switch (severity) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getFeasibilityScoreColor = (score: number) => {
    if (score >= 70) return '#10B981';
    if (score >= 40) return '#F59E0B';
    return '#EF4444';
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-xl p-6 shadow-lg">
      {/* Header with Feasibility Score */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold" style={{ color: 'var(--text)' }}>
          Career Transition Feasibility
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Overall Score:
          </span>
          <div className="relative">
            <div className="w-16 h-16">
              <svg className="transform -rotate-90 w-16 h-16">
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="var(--border)"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke={getFeasibilityScoreColor(feasibilityData.feasibilityScore)}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${(feasibilityData.feasibilityScore / 100) * 176} 176`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span 
                  className="text-lg font-bold"
                  style={{ color: getFeasibilityScoreColor(feasibilityData.feasibilityScore) }}
                >
                  {feasibilityData.feasibilityScore}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Barriers Section */}
      <div className="mb-4">
        <button
          onClick={() => toggleSection('barriers')}
          className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">🚧</span>
            <span className="font-medium" style={{ color: 'var(--text)' }}>
              Barriers & Challenges ({feasibilityData.barriers.length})
            </span>
          </div>
          <span className="text-gray-400">
            {expandedSection === 'barriers' ? '−' : '+'}
          </span>
        </button>
        
        {expandedSection === 'barriers' && (
          <div className="mt-3 space-y-2">
            {feasibilityData.barriers.map((barrier, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-lg p-4 border-l-4"
                style={{ borderLeftColor: getSeverityColor(barrier.severity) }}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{getBarrierIcon(barrier.type)}</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm mb-1" style={{ color: 'var(--text)' }}>
                      {barrier.description}
                    </p>
                    {barrier.estimatedTimeToOvercome && (
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        ⏱️ Estimated time: {barrier.estimatedTimeToOvercome}
                      </p>
                    )}
                    {barrier.suggestedActions && barrier.suggestedActions.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                          Suggested actions:
                        </p>
                        <ul className="text-xs space-y-0.5">
                          {barrier.suggestedActions.map((action, i) => (
                            <li key={i} className="flex items-start gap-1" style={{ color: 'var(--text-secondary)' }}>
                              <span>•</span>
                              <span>{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <span
                    className="px-2 py-1 text-xs font-medium rounded-full"
                    style={{
                      backgroundColor: `${getSeverityColor(barrier.severity)}20`,
                      color: getSeverityColor(barrier.severity)
                    }}
                  >
                    {barrier.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Timeline Section */}
      <div className="mb-4">
        <button
          onClick={() => toggleSection('timeline')}
          className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">📅</span>
            <span className="font-medium" style={{ color: 'var(--text)' }}>
              Career Timeline ({feasibilityData.timeline.length} phases)
            </span>
          </div>
          <span className="text-gray-400">
            {expandedSection === 'timeline' ? '−' : '+'}
          </span>
        </button>
        
        {expandedSection === 'timeline' && (
          <div className="mt-3 space-y-3">
            {feasibilityData.timeline.map((phase, index) => (
              <div key={index} className="relative">
                {index < feasibilityData.timeline.length - 1 && (
                  <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-600" />
                )}
                <div className="bg-white dark:bg-gray-800 rounded-lg p-4 relative">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium" style={{ color: 'var(--text)' }}>
                          {phase.phase}
                        </h4>
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                          {phase.duration}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <p className="font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                            Activities:
                          </p>
                          <ul className="space-y-0.5">
                            {phase.activities.map((activity, i) => (
                              <li key={i} style={{ color: 'var(--text-secondary)' }}>
                                • {activity}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                            Milestones:
                          </p>
                          <ul className="space-y-0.5">
                            {phase.milestones.map((milestone, i) => (
                              <li key={i} style={{ color: 'var(--text-secondary)' }}>
                                ✓ {milestone}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Requirements Section */}
      <div>
        <button
          onClick={() => toggleSection('requirements')}
          className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">📋</span>
            <span className="font-medium" style={{ color: 'var(--text)' }}>
              Requirements Checklist
            </span>
          </div>
          <span className="text-gray-400">
            {expandedSection === 'requirements' ? '−' : '+'}
          </span>
        </button>
        
        {expandedSection === 'requirements' && (
          <div className="mt-3 space-y-2">
            {['mandatory', 'recommended', 'nice-to-have'].map((category) => {
              const reqs = feasibilityData.requirements.filter(r => r.category === category);
              if (reqs.length === 0) return null;
              
              return (
                <div key={category} className="bg-white dark:bg-gray-800 rounded-lg p-4">
                  <h5 className="font-medium text-sm mb-2 capitalize" style={{ color: 'var(--text)' }}>
                    {category.replace('-', ' ')} Requirements
                  </h5>
                  <div className="space-y-2">
                    {reqs.map((req, index) => (
                      <div key={index} className="flex items-start gap-2 text-sm">
                        <span className="mt-0.5">
                          {req.currentStatus === 'met' ? '✅' : 
                           req.currentStatus === 'partial' ? '🟡' : '❌'}
                        </span>
                        <div className="flex-1">
                          <p style={{ color: 'var(--text-secondary)' }}>
                            {req.description}
                          </p>
                          {req.details && (
                            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                              {req.details}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Action Button */}
      <div className="mt-6 flex justify-center">
        <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transform hover:-translate-y-0.5 transition-all">
          📊 Generate Detailed Feasibility Report
        </button>
      </div>
    </div>
  );
};

export default FeasibilityBox;