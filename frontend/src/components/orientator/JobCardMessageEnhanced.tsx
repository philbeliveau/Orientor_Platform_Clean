import React, { useState } from 'react';
import { MessageComponent, ComponentAction } from '../chat/MessageComponent';

interface JobCardMessageProps {
  component: MessageComponent;
  onAction: (action: ComponentAction, componentId: string) => void;
}

export const JobCardMessageEnhanced: React.FC<JobCardMessageProps> = ({
  component,
  onAction,
}) => {
  const [selectedFilters, setSelectedFilters] = useState<{[key: string]: string}>({});
  const [expandedJob, setExpandedJob] = useState<number | null>(null);

  if (!component.data || !component.data.top_jobs) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Unable to load job opportunities</p>
      </div>
    );
  }

  const handleFilterChange = (filterType: string, value: string) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterType]: prev[filterType] === value ? '' : value
    }));
  };

  const JobCard = ({ job, index }: { job: any, index: number }) => {
    const isExpanded = expandedJob === index;
    
    return (
      <div 
        className={`bg-white border border-gray-200 rounded-lg p-6 shadow-md hover:shadow-lg transition-all cursor-pointer ${
          isExpanded ? 'ring-2 ring-blue-300' : ''
        }`}
        onClick={() => setExpandedJob(isExpanded ? null : index)}
        style={{ borderLeftColor: job.color, borderLeftWidth: '4px' }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h4 className="text-lg font-bold text-gray-900">{job.title}</h4>
            <p className="text-gray-600">{job.company}</p>
            <p className="text-sm text-gray-500">{job.location}</p>
          </div>
          <div className="text-right">
            <div 
              className="text-2xl font-bold mb-1"
              style={{ color: job.color }}
            >
              {job.match_score}%
            </div>
            <div className="text-xs text-gray-500">match</div>
          </div>
        </div>

        {/* Salary and Growth */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="text-sm text-green-600 font-medium">Salary Range</div>
            <div className="text-lg font-bold text-green-700">{job.salary_range}</div>
          </div>
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="text-sm text-blue-600 font-medium">Growth Rate</div>
            <div className="text-lg font-bold text-blue-700">{job.growth_rate}</div>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-700 mb-4">{job.description}</p>

        {/* Skills */}
        <div className="space-y-3">
          <div>
            <h5 className="font-medium text-gray-800 mb-2">Required Skills:</h5>
            <div className="flex flex-wrap gap-2">
              {job.required_skills?.map((skill: string, skillIndex: number) => (
                <span 
                  key={skillIndex}
                  className="px-3 py-1 text-sm font-medium text-red-700 bg-red-100 border border-red-200 rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
          
          {isExpanded && job.nice_to_have && (
            <div>
              <h5 className="font-medium text-gray-800 mb-2">Nice to Have:</h5>
              <div className="flex flex-wrap gap-2">
                {job.nice_to_have.map((skill: string, skillIndex: number) => (
                  <span 
                    key={skillIndex}
                    className="px-3 py-1 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Match Score Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>Compatibility</span>
            <span>{job.match_score}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="h-2 rounded-full transition-all duration-500"
              style={{ 
                width: `${job.match_score}%`,
                backgroundColor: job.color 
              }}
            ></div>
          </div>
        </div>

        {/* Action buttons for this job */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-100 flex gap-2">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Apply Now
            </button>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
              Save Job
            </button>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
              Learn More
            </button>
          </div>
        )}
      </div>
    );
  };

  const FilterBar = () => (
    component.data.filters && (
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="font-medium text-gray-800 mb-3">🔍 Filter Opportunities</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(component.data.filters).map(([filterType, options]: [string, any]) => (
            <div key={filterType}>
              <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                {filterType.replace('_', ' ')}
              </label>
              <div className="flex flex-wrap gap-2">
                {options.map((option: string) => (
                  <button
                    key={option}
                    onClick={() => handleFilterChange(filterType, option)}
                    className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                      selectedFilters[filterType] === option
                        ? 'bg-blue-100 text-blue-700 border-blue-300'
                        : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  );

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 flex items-center">
          💼 Job Opportunities
        </h3>
        <p className="text-gray-600 mt-1">
          Found {component.data.total_matches} matching positions • Click cards to expand
        </p>
      </div>

      {/* Filters */}
      <FilterBar />

      {/* Job Cards */}
      <div className="grid gap-4">
        {component.data.top_jobs?.map((job: any, index: number) => (
          <JobCard key={index} job={job} index={index} />
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-3">📊 Market Insights</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-700">{component.data.total_matches}</div>
            <div className="text-sm text-blue-600">Total Matches</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-700">
              {Math.round(component.data.top_jobs?.reduce((sum: number, job: any) => sum + job.match_score, 0) / component.data.top_jobs?.length)}%
            </div>
            <div className="text-sm text-blue-600">Avg Match</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-700">
              {component.data.top_jobs?.filter((job: any) => parseInt(job.growth_rate) > 20).length}
            </div>
            <div className="text-sm text-blue-600">High Growth</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-700">
              {component.data.top_jobs?.filter((job: any) => job.match_score > 90).length}
            </div>
            <div className="text-sm text-blue-600">Perfect Fits</div>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-3 mt-6 pt-4 border-t border-gray-100">
        {component.actions?.map((action, index) => (
          <button
            key={index}
            onClick={() => onAction(action, component.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-all transform hover:scale-105 ${
              action.type === 'save'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg hover:shadow-xl'
                : action.type === 'start'
                ? 'bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg hover:shadow-xl'
                : action.type === 'explore'
                ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg hover:shadow-xl'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300'
            }`}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
};