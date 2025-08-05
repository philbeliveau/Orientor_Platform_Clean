import React, { useState, useEffect } from 'react';
import { SavedJob, getJobDetails } from '@/services/spaceService';
import ProgramRecommendationsModal from './ProgramRecommendationsModal';
import SetCareerGoalButton from '@/components/common/SetCareerGoalButton';
import CareerFitAnalyzer from './CareerFitAnalyzer';

interface SavedJobDetailProps {
  job: SavedJob;
}

interface JobDetails {
  esco_id: string;
  title: string;
  description: string;
  skills: string[];
  education_level: string;
  experience_years: string;
  industry: string;
}

const SavedJobDetail: React.FC<SavedJobDetailProps> = ({
  job
}) => {
  const [jobDetails, setJobDetails] = useState<JobDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showProgramsModal, setShowProgramsModal] = useState(false);
  const [mockGoalId] = useState(1); // Mock career goal ID - in real app, this would come from user's actual career goals

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        const details = await getJobDetails(job.esco_id);
        setJobDetails(details);
      } catch (err: any) {
        setError('Failed to load job details');
        console.error('Error fetching job details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [job.esco_id]);

  const getDiscoverySourceDisplay = (source: string) => {
    switch (source) {
      case 'tree':
        return '🌳 Competence Tree Exploration';
      case 'search':
        return '🔍 Search Results';
      default:
        return source;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: 'var(--accent)' }}></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Career Fit Analyzer - For OaSIS jobs (SwipeMyWay) */}
      <CareerFitAnalyzer job={job} jobSource="oasis" />
      
      {/* Header */}
      <div className="border-b pb-4" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text)' }}>
              {job.job_title}
            </h1>
            <div className="flex items-center gap-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
              <span>💼 Job Opportunity</span>
              <span>{getDiscoverySourceDisplay(job.discovery_source)}</span>
              {job.relevance_score && (
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                  {Math.round(job.relevance_score * 100)}% Match
                </span>
              )}
            </div>
          </div>
          
          <div className="flex space-x-2">
            <SetCareerGoalButton 
              job={{
                esco_id: job.esco_id,
                title: job.job_title,
                description: jobDetails?.description || ''
              }}
              variant="primary"
              source="saved"
            />
            
            <button
              onClick={() => window.open('/goals', '_blank')}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
            >
              📈 View Career Timeline
            </button>
          </div>
        </div>
      </div>

      {/* Job Details */}
      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">⚠️ {error}</p>
          <p className="text-red-600 text-sm mt-1">Showing basic information from tree exploration.</p>
        </div>
      ) : jobDetails && (
        <div className="bg-gray-50 rounded-lg p-6" style={{ backgroundColor: 'var(--card)' }}>
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Job Description
          </h2>
          <p className="text-sm leading-relaxed mb-4" style={{ color: 'var(--text-secondary)' }}>
            {jobDetails.description}
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-medium mb-2" style={{ color: 'var(--text)' }}>Education Level</h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{jobDetails.education_level}</p>
            </div>
            <div>
              <h3 className="font-medium mb-2" style={{ color: 'var(--text)' }}>Experience Required</h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{jobDetails.experience_years}</p>
            </div>
            <div>
              <h3 className="font-medium mb-2" style={{ color: 'var(--text)' }}>Industry</h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{jobDetails.industry}</p>
            </div>
          </div>
        </div>
      )}

      {/* Skills Required */}
      {(job.skills_required.length > 0 || (jobDetails?.skills.length ?? 0) > 0) && (
        <div>
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Required Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {(jobDetails?.skills ?? job.skills_required).map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Discovery Information */}
      <div className="bg-yellow-50 rounded-lg p-4" style={{ backgroundColor: 'var(--card)' }}>
        <h2 className="text-lg font-semibold mb-3" style={{ color: 'var(--text)' }}>
          Discovery Information
        </h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-secondary)' }}>Discovered through:</span>
            <span style={{ color: 'var(--text)' }}>{getDiscoverySourceDisplay(job.discovery_source)}</span>
          </div>
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-secondary)' }}>ESCO ID:</span>
            <span className="font-mono text-xs" style={{ color: 'var(--text)' }}>{job.esco_id}</span>
          </div>
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-secondary)' }}>Saved on:</span>
            <span style={{ color: 'var(--text)' }}>{new Date(job.saved_at).toLocaleDateString()}</span>
          </div>
          {job.tree_graph_id && (
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>Tree ID:</span>
              <span className="font-mono text-xs" style={{ color: 'var(--text)' }}>{job.tree_graph_id}</span>
            </div>
          )}
        </div>
      </div>

      {/* Metadata */}
      {Object.keys(job.metadata).length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Additional Information
          </h2>
          <div className="bg-gray-50 rounded-lg p-4" style={{ backgroundColor: 'var(--card)' }}>
            <pre className="text-sm overflow-x-auto" style={{ color: 'var(--text-secondary)' }}>
              {JSON.stringify(job.metadata, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={() => window.open(`https://esco.ec.europa.eu/en/classification/occupations/${job.esco_id}`, '_blank')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors"
        >
          🔗 View in ESCO
        </button>
        
        <button
          onClick={() => setShowProgramsModal(true)}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
        >
          📚 Explore Programs
        </button>
      </div>

      {/* Program Recommendations Modal */}
      <ProgramRecommendationsModal
        isOpen={showProgramsModal}
        onClose={() => setShowProgramsModal(false)}
        goalId={mockGoalId}
        jobTitle={job.job_title}
      />
    </div>
  );
};

export default SavedJobDetail;