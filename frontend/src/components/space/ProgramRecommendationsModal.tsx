import React from 'react';

interface ProgramRecommendationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  goalId: number;
  jobTitle: string;
}

const ProgramRecommendationsModal: React.FC<ProgramRecommendationsModalProps> = ({
  isOpen,
  onClose,
  goalId,
  jobTitle
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto" style={{ backgroundColor: 'var(--card)' }}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text)' }}>
            Educational Programs for {jobTitle}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-lg p-4" style={{ backgroundColor: 'var(--background-secondary)' }}>
            <h3 className="font-medium mb-2" style={{ color: 'var(--text)' }}>
              Recommended Programs
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Program recommendations will be displayed here based on your career goal.
            </p>
          </div>
          
          <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
            <p>Loading program recommendations...</p>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProgramRecommendationsModal;