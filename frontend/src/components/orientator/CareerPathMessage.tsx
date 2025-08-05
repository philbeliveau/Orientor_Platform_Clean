import React, { useState } from 'react';
import { Target, Calendar, TrendingUp, CheckCircle, Circle, AlertCircle } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface CareerMilestone {
  id: string;
  title: string;
  description?: string;
  duration?: string;
  skills_required?: string[];
  status?: 'completed' | 'current' | 'future';
  order: number;
}

interface CareerPathData {
  career_goal: string;
  current_position?: string;
  milestones: CareerMilestone[];
  estimated_timeline?: string;
  difficulty_level?: 'easy' | 'moderate' | 'challenging';
}

interface CareerPathMessageProps {
  data: CareerPathData;
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const statusIcons = {
  completed: <CheckCircle className="w-5 h-5 text-green-600" />,
  current: <Circle className="w-5 h-5 text-blue-600 fill-blue-600" />,
  future: <Circle className="w-5 h-5 text-gray-400" />
};

const difficultyColors = {
  easy: 'bg-green-100 text-green-700',
  moderate: 'bg-orange-100 text-orange-700',
  challenging: 'bg-red-100 text-red-700'
};

export const CareerPathMessage: React.FC<CareerPathMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const [expandedMilestone, setExpandedMilestone] = useState<string | null>(null);

  const handleSave = async () => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction(saveAction);
    }
  };

  const toggleMilestone = (id: string) => {
    setExpandedMilestone(expandedMilestone === id ? null : id);
  };

  return (
    <div className={`border border-gray-200 rounded-lg p-4 bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Target className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Path to {data.career_goal}</h3>
            {data.current_position && (
              <p className="text-sm text-gray-600">From: {data.current_position}</p>
            )}
          </div>
        </div>
        <SaveActionButton onSave={handleSave} saved={saved} size="sm" variant="outline" />
      </div>

      {/* Timeline Info */}
      <div className="flex items-center gap-4 mb-4 text-sm">
        {data.estimated_timeline && (
          <div className="flex items-center gap-1 text-gray-600">
            <Calendar className="w-4 h-4" />
            <span>{data.estimated_timeline}</span>
          </div>
        )}
        {data.difficulty_level && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColors[data.difficulty_level]}`}>
            {data.difficulty_level}
          </span>
        )}
      </div>

      {/* Career Path Timeline */}
      <div className="space-y-3">
        {data.milestones.map((milestone, index) => (
          <div key={milestone.id} className="relative">
            {/* Connecting Line */}
            {index < data.milestones.length - 1 && (
              <div className="absolute left-[18px] top-8 bottom-0 w-0.5 bg-gray-300"></div>
            )}
            
            {/* Milestone */}
            <div className="flex gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {statusIcons[milestone.status || 'future']}
              </div>
              <div className="flex-1">
                <button
                  onClick={() => toggleMilestone(milestone.id)}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <h4 className="font-medium text-gray-900">{milestone.title}</h4>
                  {milestone.duration && (
                    <p className="text-sm text-gray-600 mt-1">{milestone.duration}</p>
                  )}
                </button>
                
                {/* Expanded Content */}
                {expandedMilestone === milestone.id && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    {milestone.description && (
                      <p className="text-sm text-gray-700 mb-2">{milestone.description}</p>
                    )}
                    {milestone.skills_required && milestone.skills_required.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-600 mb-1">Key Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {milestone.skills_required.map((skill, idx) => (
                            <span key={idx} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
        {actions.filter(a => a.type !== 'save').map((action, index) => (
          <button
            key={index}
            onClick={() => onAction(action)}
            className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Progress Indicator */}
      <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
        <TrendingUp className="w-3 h-3" />
        <span>
          {data.milestones.filter(m => m.status === 'completed').length} of {data.milestones.length} milestones completed
        </span>
      </div>
    </div>
  );
};