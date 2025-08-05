import React, { useState } from 'react';
import { UnifiedJob, isESCOJob, isOaSISJob } from '@/types/unifiedJob';
import { JobCardChat } from '@/components/jobs/JobCardChat';
import { Job } from '@/components/jobs/JobCard';

interface UnifiedJobCardProps {
  job: UnifiedJob;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const UnifiedJobCard: React.FC<UnifiedJobCardProps> = ({
  job,
  isSelected,
  onSelect,
  onDelete
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const getSourceBadge = () => {
    if (isESCOJob(job)) {
      return (
        <div className="flex items-center gap-1">
          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            ESCO
          </span>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-1">
          <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
            OaSIS
          </span>
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
        </div>
      );
    }
  };

  const getCardStyle = () => {
    const baseStyle = {
      backgroundColor: isSelected ? 'var(--card-hover)' : 'var(--card)',
      transition: 'all 0.2s ease-in-out'
    };

    if (isESCOJob(job)) {
      return {
        ...baseStyle,
        border: `2px solid ${isSelected ? '#3B82F6' : 'var(--border)'}`,
        borderLeftWidth: '4px',
        borderLeftColor: '#3B82F6'
      };
    } else {
      return {
        ...baseStyle,
        border: `2px solid ${isSelected ? '#8B5CF6' : 'var(--border)'}`,
        borderLeftWidth: '4px',
        borderLeftColor: '#8B5CF6'
      };
    }
  };

  const renderJobSpecificInfo = () => {
    if (isESCOJob(job)) {
      return (
        <>
          {job.skillsRequired && job.skillsRequired.length > 0 && (
            <div className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
              <span className="font-medium">Skills:</span>{' '}
              {job.skillsRequired.slice(0, 3).join(', ')}
              {job.skillsRequired.length > 3 && ` +${job.skillsRequired.length - 3} more`}
            </div>
          )}
          {job.educationLevel && (
            <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              <span className="font-medium">Education:</span> {job.educationLevel}
            </div>
          )}
          {job.regulatedProfession && (
            <div className="flex items-center gap-1 mt-1">
              <span className="text-xs text-orange-600 font-medium">⚖️ Regulated Profession</span>
            </div>
          )}
        </>
      );
    } else if (isOaSISJob(job)) {
      return (
        <>
          <div className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            <span className="font-medium">Code:</span> {job.oasisCode}
          </div>
          {job.roleLeadership && (
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Leadership: {job.roleLeadership}/5
              </span>
              <div className="flex-1 h-1 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-400 to-purple-600"
                  style={{ width: `${(job.roleLeadership / 5) * 100}%` }}
                />
              </div>
            </div>
          )}
          {job.personalAnalysis && (
            <div className="flex items-center gap-1 mt-1">
              <span className="text-xs text-green-600 font-medium">✨ AI Analysis Available</span>
            </div>
          )}
        </>
      );
    }
    return null;
  };

  return (
    <div
      className="p-4 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md"
      style={getCardStyle()}
      onMouseEnter={(e) => {
        if (!isSelected) {
          e.currentTarget.style.transform = 'translateY(-2px)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div onClick={onSelect}>
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-medium text-sm leading-tight flex-1 mr-2" style={{ color: 'var(--text)' }}>
            {job.title}
          </h3>
          {getSourceBadge()}
        </div>

        {job.description && (
          <p className="text-xs line-clamp-2 mb-2" style={{ color: 'var(--text-secondary)' }}>
            {job.description}
          </p>
        )}

        {renderJobSpecificInfo()}

        {job.relevanceScore && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span style={{ color: 'var(--text-secondary)' }}>Match Score</span>
              <span className="font-medium" style={{ color: job.relevanceScore > 0.7 ? '#10B981' : '#F59E0B' }}>
                {Math.round(job.relevanceScore * 100)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full transition-all duration-300"
                style={{
                  width: `${job.relevanceScore * 100}%`,
                  background: job.relevanceScore > 0.7 
                    ? 'linear-gradient(to right, #10B981, #059669)'
                    : 'linear-gradient(to right, #F59E0B, #DC2626)'
                }}
              />
            </div>
          </div>
        )}

        {job.savedAt && (
          <div className="text-xs mt-2 flex items-center gap-1" style={{ color: 'var(--text-secondary)' }}>
            <span>📅</span>
            <span>Saved: {new Date(job.savedAt).toLocaleDateString()}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsChatOpen(true);
          }}
          className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors flex items-center gap-1"
        >
          💬 Ask Questions
        </button>
        
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="text-xs font-medium text-gray-500 hover:text-red-500 transition-colors"
        >
          🗑️ Remove
        </button>
      </div>

      {/* LLM Chat Interface */}
      {isChatOpen && (
        <JobCardChat
          job={{
            id: job.id,
            metadata: {
              title: job.title,
              preferred_label: job.title,
              description: job.description || '',
              skills: isESCOJob(job) ? job.skillsRequired : undefined,
              education_level: isESCOJob(job) ? job.educationLevel : undefined,
              oasis_code: isOaSISJob(job) ? job.oasisCode : undefined,
              ...('allFields' in job ? job.allFields : {})
            },
            score: job.relevanceScore || 0
          } as Job}
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />
      )}
    </div>
  );
};

export default UnifiedJobCard;