import React, { useState } from 'react';

interface InsightCardProps {
  title: string;
  content: string;
  fullContent?: string;
  onSave?: () => void;
  onRewrite?: () => void;
  feedback?: string;
  setFeedback?: (feedback: string) => void;
  saving?: boolean;
  rewriting?: boolean;
}

const InsightCard: React.FC<InsightCardProps> = ({
  title,
  content,
  fullContent,
  onSave,
  onRewrite,
  feedback,
  setFeedback,
  saving = false,
  rewriting = false
}) => {
  const [showFullContent, setShowFullContent] = useState(false);
  const [showRewriteSection, setShowRewriteSection] = useState(false);

  return (
    <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl border border-gray-700/50 shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="p-6 sm:p-8 border-b border-gray-700/50">
        <h3 className="text-2xl font-light text-white mb-4">{title}</h3>
        <p className="text-gray-300 leading-relaxed text-lg">
          {content}
        </p>
      </div>

      {/* Full Content */}
      {fullContent && (
        <div className="p-6 sm:p-8 border-b border-gray-700/50">
          <button
            onClick={() => setShowFullContent(!showFullContent)}
            className="flex items-center justify-between w-full mb-4 text-left"
          >
            <h4 className="text-lg font-medium text-gray-200">Complete Analysis</h4>
            <svg
              className={`w-5 h-5 text-gray-400 transform transition-transform duration-200 ${
                showFullContent ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showFullContent && (
            <div className="text-gray-300 leading-relaxed whitespace-pre-wrap bg-gray-800/50 rounded-2xl p-6 border border-gray-700/30">
              {fullContent}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row gap-4">
          {onSave && (
            <button
              onClick={onSave}
              disabled={saving}
              className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Save Analysis</span>
                </>
              )}
            </button>
          )}
          
          <button
            onClick={() => setShowRewriteSection(!showRewriteSection)}
            className="flex-1 bg-gray-700/50 hover:bg-gray-700/70 text-gray-200 font-medium py-3 px-6 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 border border-gray-600/50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <span>Request Rewrite</span>
          </button>
        </div>

        {/* Rewrite Section */}
        {showRewriteSection && (
          <div className="mt-6 p-6 bg-gray-800/50 rounded-2xl border border-gray-700/30">
            <h4 className="text-lg font-medium text-gray-200 mb-4">
              Want a different perspective?
            </h4>
            <textarea
              value={feedback || ''}
              onChange={(e) => setFeedback?.(e.target.value)}
              placeholder="Describe what you'd like to explore differently..."
              rows={4}
              className="w-full bg-gray-700/50 border border-gray-600/50 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-transparent resize-none"
            />
            <div className="flex justify-end mt-4">
              <button
                onClick={onRewrite}
                disabled={rewriting || !feedback?.trim()}
                className="bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded-xl transition-all duration-200 flex items-center space-x-2"
              >
                {rewriting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Rewriting...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>Rewrite</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightCard;