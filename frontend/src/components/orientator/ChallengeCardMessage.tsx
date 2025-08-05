import React, { useState } from 'react';
import { Target, Clock, Trophy, Zap, CheckCircle, Circle, AlertCircle } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface Challenge {
  id: string;
  title: string;
  description: string;
  skill_focus: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  xp_reward: number;
  estimated_time: string;
  prerequisites?: string[];
  objectives?: string[];
  status?: 'not_started' | 'in_progress' | 'completed';
  progress?: number;
  deadline?: string;
}

interface ChallengeCardMessageProps {
  data: Challenge | Challenge[];
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const difficultyConfig = {
  beginner: {
    label: 'Beginner',
    color: 'bg-green-100 text-green-700 border-green-300',
    icon: '🌱'
  },
  intermediate: {
    label: 'Intermediate',
    color: 'bg-orange-100 text-orange-700 border-orange-300',
    icon: '🚀'
  },
  advanced: {
    label: 'Advanced',
    color: 'bg-red-100 text-red-700 border-red-300',
    icon: '🔥'
  }
};

const ChallengeCard: React.FC<{
  challenge: Challenge;
  onStart: () => void;
  onSave: () => Promise<void>;
  saved?: boolean;
}> = ({ challenge, onStart, onSave, saved }) => {
  const [showDetails, setShowDetails] = useState(false);
  const config = difficultyConfig[challenge.difficulty];

  const getStatusIcon = () => {
    switch (challenge.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'in_progress':
        return <Circle className="w-5 h-5 text-blue-600 fill-blue-600" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="flex-shrink-0 mt-0.5">
            {getStatusIcon()}
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">{challenge.title}</h4>
            <p className="text-sm text-gray-600 mt-1">{challenge.description}</p>
          </div>
        </div>
        <SaveActionButton 
          onSave={onSave} 
          saved={saved} 
          size="sm" 
          variant="ghost" 
        />
      </div>

      {/* Challenge Info */}
      <div className="flex flex-wrap items-center gap-3 mb-3 text-sm">
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${config.color}`}>
          {config.icon} {config.label}
        </span>
        <div className="flex items-center gap-1 text-gray-600">
          <Zap className="w-4 h-4 text-yellow-500" />
          <span className="font-medium">{challenge.xp_reward} XP</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <Clock className="w-4 h-4" />
          <span>{challenge.estimated_time}</span>
        </div>
      </div>

      {/* Progress Bar (if in progress) */}
      {challenge.status === 'in_progress' && challenge.progress !== undefined && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-600">Progress</span>
            <span className="font-medium text-blue-600">{challenge.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${challenge.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Skills Focus */}
      <div className="mb-3">
        <p className="text-xs font-medium text-gray-600 mb-1">Skills you'll develop:</p>
        <div className="flex flex-wrap gap-1">
          {challenge.skill_focus.map((skill, idx) => (
            <span key={idx} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Show Details Button */}
      {(challenge.objectives || challenge.prerequisites) && (
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium mb-3"
        >
          {showDetails ? 'Hide details' : 'View details'}
        </button>
      )}

      {/* Expanded Details */}
      {showDetails && (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg space-y-3">
          {challenge.objectives && challenge.objectives.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">Objectives:</p>
              <ul className="space-y-1">
                {challenge.objectives.map((objective, idx) => (
                  <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                    <Target className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span>{objective}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {challenge.prerequisites && challenge.prerequisites.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">Prerequisites:</p>
              <ul className="space-y-0.5">
                {challenge.prerequisites.map((prereq, idx) => (
                  <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                    <AlertCircle className="w-3 h-3 text-orange-500 mt-0.5 flex-shrink-0" />
                    <span>{prereq}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Deadline */}
      {challenge.deadline && (
        <div className="mb-3 text-sm text-orange-600 flex items-center gap-1">
          <Clock className="w-4 h-4" />
          <span>Deadline: {new Date(challenge.deadline).toLocaleDateString()}</span>
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={onStart}
        disabled={challenge.status === 'completed'}
        className={`w-full px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
          challenge.status === 'completed'
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : challenge.status === 'in_progress'
            ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
      >
        {challenge.status === 'completed' && (
          <span className="flex items-center justify-center gap-2">
            <Trophy className="w-4 h-4" />
            Completed
          </span>
        )}
        {challenge.status === 'in_progress' && 'Continue Challenge'}
        {(!challenge.status || challenge.status === 'not_started') && 'Start Challenge'}
      </button>
    </div>
  );
};

export const ChallengeCardMessage: React.FC<ChallengeCardMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const challenges = Array.isArray(data) ? data : [data];
  const [savedChallenges, setSavedChallenges] = useState<Set<string>>(new Set());

  const handleSaveChallenge = async (challengeId: string) => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction({ ...saveAction, params: { challengeId } });
      setSavedChallenges(new Set(Array.from(savedChallenges).concat(challengeId)));
    }
  };

  const handleStartChallenge = (challengeId: string) => {
    const startAction = actions.find(a => a.type === 'start' || a.label === 'Start Challenge');
    if (startAction) {
      onAction({ ...startAction, params: { challengeId } });
    }
  };

  return (
    <div className={`${className}`}>
      {/* Header for multiple challenges */}
      {challenges.length > 1 && (
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5 text-purple-600" />
          <h3 className="font-medium text-gray-900">
            {challenges.length} challenges to boost your skills
          </h3>
        </div>
      )}

      {/* Challenge Cards */}
      <div className="space-y-3">
        {challenges.map((challenge) => (
          <ChallengeCard
            key={challenge.id}
            challenge={challenge}
            onStart={() => handleStartChallenge(challenge.id)}
            onSave={() => handleSaveChallenge(challenge.id)}
            saved={savedChallenges.has(challenge.id) || saved}
          />
        ))}
      </div>

      {/* Aggregate Actions */}
      {challenges.length > 1 && (
        <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
          <button
            onClick={() => {
              const saveAllAction = actions.find(a => a.label === 'Save All Challenges');
              if (saveAllAction) onAction(saveAllAction);
            }}
            className="px-3 py-1.5 text-sm font-medium text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
          >
            Save All Challenges
          </button>
          {actions.filter(a => a.type !== 'save' && a.type !== 'start' && a.label !== 'Save All Challenges').map((action, index) => (
            <button
              key={index}
              onClick={() => onAction(action)}
              className="px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {challenges.length > 1 && (
        <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3 text-yellow-500" />
            <span>Total XP: {challenges.reduce((sum, c) => sum + c.xp_reward, 0)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>
              Estimated time: {
                challenges.reduce((sum, c) => {
                  const hours = parseInt(c.estimated_time) || 0;
                  return sum + hours;
                }, 0)
              } hours total
            </span>
          </div>
        </div>
      )}
    </div>
  );
};