import React from 'react';
import { SavedJob } from '@/services/spaceService';

interface SavedJobsListProps {
  jobs: SavedJob[];
  selectedJobId?: number;
  onSelect: (job: SavedJob) => void;
  onDelete: (id: number) => void;
  loading: boolean;
  error: string | null;
}

const SavedJobsList: React.FC<SavedJobsListProps> = ({
  jobs,
  selectedJobId,
  onSelect,
  onDelete,
  loading,
  error
}) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: 'var(--accent)' }}></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-center p-4" style={{ color: '#ef4444' }}>{error}</div>;
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center p-4" style={{ color: 'var(--text-secondary)' }}>
        <div className="mb-2">🌳</div>
        <div>No saved jobs from tree exploration yet.</div>
        <div className="text-xs mt-1">Explore your competence tree to discover career opportunities!</div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="p-4 rounded-lg cursor-pointer transition-all duration-200"
          style={{
            backgroundColor: selectedJobId === job.id ? 'var(--card-hover)' : 'var(--card)',
            border: `1px solid ${selectedJobId === job.id ? 'var(--accent)' : 'var(--border)'}`,
          }}
          onMouseEnter={(e) => {
            if (selectedJobId !== job.id) {
              e.currentTarget.style.borderColor = 'var(--accent)';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedJobId !== job.id) {
              e.currentTarget.style.borderColor = 'var(--border)';
            }
          }}
        >
          <div onClick={() => onSelect(job)}>
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-sm leading-tight" style={{ color: 'var(--text)' }}>
                {job.job_title}
              </h3>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 ml-2 shrink-0">
                💼
              </span>
            </div>
            
            <div className="space-y-1">
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span className="font-medium">Source:</span> {job.discovery_source === 'tree' ? '🌳 Competence Tree' : job.discovery_source}
              </p>
              
              {job.relevance_score && (
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  <span className="font-medium">Relevance:</span> {Math.round(job.relevance_score * 100)}%
                </p>
              )}
              
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span className="font-medium">Saved:</span> {new Date(job.saved_at).toLocaleDateString()}
              </p>
              
              {job.skills_required.length > 0 && (
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  <span className="font-medium">Skills:</span> {job.skills_required.slice(0, 2).join(', ')}
                  {job.skills_required.length > 2 && ` +${job.skills_required.length - 2} more`}
                </div>
              )}
            </div>
          </div>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(job.id);
            }}
            className="mt-3 text-xs font-medium transition-colors duration-200 hover:text-red-500"
            style={{ color: 'var(--text-secondary)' }}
          >
            🗑️ Remove
          </button>
        </div>
      ))}
    </div>
  );
};

export default SavedJobsList;