import React, { useState } from 'react';
import { Briefcase, MapPin, DollarSign, TrendingUp, Star, ExternalLink } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface JobData {
  id: string;
  title: string;
  company?: string;
  location?: string;
  salary_range?: {
    min: number;
    max: number;
    currency: string;
  };
  match_score?: number;
  required_skills?: string[];
  description?: string;
  job_type?: string;
  experience_level?: string;
  posted_date?: string;
  url?: string;
}

interface JobCardMessageProps {
  data: JobData | JobData[];
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const JobCard: React.FC<{ 
  job: JobData; 
  onSave: () => Promise<void>; 
  saved?: boolean;
  onExplore?: () => void;
}> = ({ job, onSave, saved, onExplore }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatSalary = (salary: JobData['salary_range']) => {
    if (!salary) return null;
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: salary.currency,
      maximumFractionDigits: 0
    });
    return `${formatter.format(salary.min)} - ${formatter.format(salary.max)}`;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{job.title}</h4>
          {job.company && <p className="text-sm text-gray-600">{job.company}</p>}
        </div>
        <SaveActionButton 
          onSave={onSave} 
          saved={saved} 
          size="sm" 
          variant="ghost" 
        />
      </div>

      {/* Job Details */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-3">
        {job.location && (
          <div className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            <span>{job.location}</span>
          </div>
        )}
        {job.salary_range && (
          <div className="flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            <span>{formatSalary(job.salary_range)}</span>
          </div>
        )}
        {job.job_type && (
          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
            {job.job_type}
          </span>
        )}
      </div>

      {/* Match Score */}
      {job.match_score && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-600">Match Score</span>
            <span className="font-medium text-green-600">{job.match_score}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${job.match_score}%` }}
            />
          </div>
        </div>
      )}

      {/* Description Preview */}
      {job.description && (
        <div className="mb-3">
          <p className="text-sm text-gray-700 line-clamp-2">
            {job.description}
          </p>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-1"
          >
            {isExpanded ? 'Show less' : 'Read more'}
          </button>
        </div>
      )}

      {/* Expanded Content */}
      {isExpanded && job.description && (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{job.description}</p>
        </div>
      )}

      {/* Required Skills */}
      {job.required_skills && job.required_skills.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-600 mb-1">Required Skills:</p>
          <div className="flex flex-wrap gap-1">
            {job.required_skills.slice(0, 5).map((skill, idx) => (
              <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                {skill}
              </span>
            ))}
            {job.required_skills.length > 5 && (
              <span className="text-xs text-gray-500">+{job.required_skills.length - 5} more</span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3">
        {onExplore && (
          <button
            onClick={onExplore}
            className="flex-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Explore Path
          </button>
        )}
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            View Job <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
};

export const JobCardMessage: React.FC<JobCardMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const jobs = Array.isArray(data) ? data : [data];
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  const handleSaveJob = async (jobId: string) => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction({ ...saveAction, params: { jobId } });
      setSavedJobs(new Set(Array.from(savedJobs).concat(jobId)));
    }
  };

  const handleExploreJob = (jobId: string) => {
    const exploreAction = actions.find(a => a.type === 'explore');
    if (exploreAction) {
      onAction({ ...exploreAction, params: { jobId } });
    }
  };

  return (
    <div className={`${className}`}>
      {/* Header for multiple jobs */}
      {jobs.length > 1 && (
        <div className="flex items-center gap-2 mb-4">
          <Briefcase className="w-5 h-5 text-blue-600" />
          <h3 className="font-medium text-gray-900">
            Found {jobs.length} job opportunities
          </h3>
        </div>
      )}

      {/* Job Cards */}
      <div className="space-y-3">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onSave={() => handleSaveJob(job.id)}
            saved={savedJobs.has(job.id) || saved}
            onExplore={() => handleExploreJob(job.id)}
          />
        ))}
      </div>

      {/* Aggregate Actions */}
      {jobs.length > 1 && (
        <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
          <button
            onClick={() => {
              const saveAllAction = actions.find(a => a.label === 'Save All');
              if (saveAllAction) onAction(saveAllAction);
            }}
            className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Save All Jobs
          </button>
          {actions.filter(a => a.type !== 'save' && a.label !== 'Save All').map((action, index) => (
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
    </div>
  );
};