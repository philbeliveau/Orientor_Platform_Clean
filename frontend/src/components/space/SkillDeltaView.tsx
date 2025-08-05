import React, { useState } from 'react';
import { SkillDelta } from '@/types/unifiedJob';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

interface SkillDeltaViewProps {
  skillDeltas: SkillDelta[];
  jobTitle: string;
  onRequestImprovement?: (skillName: string) => void;
}

const SkillDeltaView: React.FC<SkillDeltaViewProps> = ({
  skillDeltas,
  jobTitle,
  onRequestImprovement
}) => {
  const [viewMode, setViewMode] = useState<'chart' | 'list'>('chart');
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);

  const getPriorityColor = (priority: SkillDelta['priority']) => {
    switch (priority) {
      case 'critical': return '#EF4444';
      case 'important': return '#F59E0B';
      case 'beneficial': return '#10B981';
      default: return '#6B7280';
    }
  };

  const getGapSeverity = (gap: number) => {
    if (gap >= 3) return { label: 'Significant Gap', color: '#EF4444' };
    if (gap >= 2) return { label: 'Moderate Gap', color: '#F59E0B' };
    if (gap >= 1) return { label: 'Minor Gap', color: '#3B82F6' };
    return { label: 'On Track', color: '#10B981' };
  };

  // Prepare data for radar chart
  const radarData = skillDeltas.map(delta => ({
    skill: delta.skillName,
    required: delta.requiredLevel,
    current: delta.currentLevel,
    gap: delta.gap
  }));

  const renderChart = () => (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={radarData}>
          <PolarGrid stroke="var(--border)" />
          <PolarAngleAxis 
            dataKey="skill" 
            tick={{ fontSize: 12, fill: 'var(--text-secondary)' }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 5]} 
            tick={{ fontSize: 10, fill: 'var(--text-secondary)' }}
          />
          <Radar
            name="Required Level"
            dataKey="required"
            stroke="#8B5CF6"
            fill="#8B5CF6"
            fillOpacity={0.3}
          />
          <Radar
            name="Current Level"
            dataKey="current"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '0.5rem'
            }}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );

  const renderList = () => (
    <div className="space-y-3">
      {skillDeltas.map((delta, index) => {
        const gapSeverity = getGapSeverity(delta.gap);
        const isExpanded = selectedSkill === delta.skillName;

        return (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-lg p-4 border transition-all hover:shadow-md cursor-pointer"
            style={{ borderColor: isExpanded ? getPriorityColor(delta.priority) : 'var(--border)' }}
            onClick={() => setSelectedSkill(isExpanded ? null : delta.skillName)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div 
                  className="w-2 h-8 rounded-full"
                  style={{ backgroundColor: getPriorityColor(delta.priority) }}
                />
                <div>
                  <h4 className="font-medium" style={{ color: 'var(--text)' }}>
                    {delta.skillName}
                  </h4>
                  <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    Priority: {delta.priority}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span 
                  className="text-sm font-medium px-2 py-1 rounded-full"
                  style={{
                    backgroundColor: `${gapSeverity.color}20`,
                    color: gapSeverity.color
                  }}
                >
                  {gapSeverity.label}
                </span>
              </div>
            </div>

            {/* Skill Level Bars */}
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: 'var(--text-secondary)' }}>Current Level</span>
                  <span style={{ color: 'var(--text)' }}>{delta.currentLevel}/5</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-500"
                    style={{ width: `${(delta.currentLevel / 5) * 100}%` }}
                  />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: 'var(--text-secondary)' }}>Required Level</span>
                  <span style={{ color: 'var(--text)' }}>{delta.requiredLevel}/5</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500 transition-all duration-500"
                    style={{ width: `${(delta.requiredLevel / 5) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Gap Indicator */}
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Gap to close: {delta.gap.toFixed(1)} levels
              </span>
              <span className={`text-xs ${isExpanded ? 'rotate-180' : ''} transition-transform`}>
                ▼
              </span>
            </div>

            {/* Expanded Content */}
            {isExpanded && delta.improvementPath && (
              <div className="mt-4 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
                <h5 className="text-sm font-medium mb-2" style={{ color: 'var(--text)' }}>
                  Suggested Improvement Path:
                </h5>
                <ol className="space-y-2">
                  {delta.improvementPath.map((step, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span className="font-medium text-purple-600">{i + 1}.</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{step}</span>
                    </li>
                  ))}
                </ol>
                {onRequestImprovement && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRequestImprovement(delta.skillName);
                    }}
                    className="mt-3 px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    🎯 Create Improvement Plan
                  </button>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );

  // Calculate overall readiness
  const overallGap = skillDeltas.reduce((sum, delta) => sum + delta.gap, 0) / skillDeltas.length;
  const readinessScore = Math.max(0, 100 - (overallGap * 20));

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-800 dark:to-gray-900 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold" style={{ color: 'var(--text)' }}>
            Skill Gap Analysis
          </h3>
          <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
            Requirements for: {jobTitle}
          </p>
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 bg-white dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setViewMode('chart')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              viewMode === 'chart' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📊 Chart
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              viewMode === 'list' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📋 List
          </button>
        </div>
      </div>

      {/* Readiness Score */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>
            Overall Readiness
          </span>
          <div className="flex items-center gap-3">
            <div className="flex-1 w-48 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full transition-all duration-1000"
                style={{
                  width: `${readinessScore}%`,
                  background: readinessScore >= 70 
                    ? 'linear-gradient(to right, #10B981, #059669)'
                    : readinessScore >= 40
                    ? 'linear-gradient(to right, #F59E0B, #DC2626)'
                    : 'linear-gradient(to right, #EF4444, #991B1B)'
                }}
              />
            </div>
            <span 
              className="text-lg font-bold"
              style={{ 
                color: readinessScore >= 70 ? '#10B981' : 
                       readinessScore >= 40 ? '#F59E0B' : '#EF4444' 
              }}
            >
              {readinessScore.toFixed(0)}%
            </span>
          </div>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-red-500">
              {skillDeltas.filter(d => d.priority === 'critical').length}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              Critical Gaps
            </p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-orange-500">
              {skillDeltas.filter(d => d.priority === 'important').length}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              Important Gaps
            </p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-500">
              {skillDeltas.filter(d => d.gap < 1).length}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              Skills Ready
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      {viewMode === 'chart' ? renderChart() : renderList()}

      {/* Action Buttons */}
      <div className="mt-6 flex flex-wrap gap-3 justify-center">
        <button className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors">
          📚 Find Learning Resources
        </button>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
          🎓 Explore Training Programs
        </button>
        <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 transition-colors">
          💬 Get AI Coaching
        </button>
      </div>
    </div>
  );
};

export default SkillDeltaView;