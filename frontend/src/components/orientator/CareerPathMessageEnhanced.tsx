import React, { useState } from 'react';
import { MessageComponent, ComponentAction } from '../chat/MessageComponent';

interface CareerPathMessageProps {
  component: MessageComponent;
  onAction: (action: ComponentAction, componentId: string) => void;
}

export const CareerPathMessageEnhanced: React.FC<CareerPathMessageProps> = ({
  component,
  onAction,
}) => {
  const [selectedMilestone, setSelectedMilestone] = useState<number | null>(null);

  if (!component.data || !component.data.milestones) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Unable to load career path data</p>
      </div>
    );
  }

  const TimelineVisualization = () => (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-green-400 to-purple-400"></div>
      
      <div className="space-y-8">
        {component.data.milestones?.map((milestone: any, index: number) => (
          <div key={index} className="relative flex items-start">
            {/* Timeline node */}
            <div 
              className="relative z-10 w-16 h-16 rounded-full border-4 border-white shadow-lg flex items-center justify-center cursor-pointer transition-all hover:scale-110"
              style={{ backgroundColor: milestone.color }}
              onClick={() => setSelectedMilestone(selectedMilestone === index ? null : index)}
            >
              <div className="text-white font-bold text-sm">
                {index + 1}
              </div>
            </div>
            
            {/* Content */}
            <div className="ml-6 flex-1">
              <div 
                className={`bg-white border border-gray-200 rounded-lg p-6 shadow-md transition-all ${
                  selectedMilestone === index ? 'ring-2 ring-blue-300 shadow-lg' : ''
                }`}
                style={{ borderLeftColor: milestone.color, borderLeftWidth: '4px' }}
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-bold text-gray-900">{milestone.title}</h4>
                  <span className="text-sm font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                    {milestone.duration}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4">{milestone.stage}</p>
                
                {/* Skills */}
                <div className="mb-4">
                  <h5 className="font-medium text-gray-800 mb-2">Key Skills to Develop:</h5>
                  <div className="flex flex-wrap gap-2">
                    {milestone.skills?.map((skill: string, skillIndex: number) => (
                      <span 
                        key={skillIndex}
                        className="px-3 py-1 text-sm rounded-full border"
                        style={{ 
                          backgroundColor: `${milestone.color}20`,
                          borderColor: milestone.color,
                          color: milestone.color
                        }}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                {/* Actions */}
                {selectedMilestone === index && milestone.actions && (
                  <div className="border-t border-gray-100 pt-4">
                    <h5 className="font-medium text-gray-800 mb-2">Recommended Actions:</h5>
                    <ul className="space-y-2">
                      {milestone.actions.map((action: string, actionIndex: number) => (
                        <li key={actionIndex} className="flex items-start">
                          <div className="w-2 h-2 rounded-full mt-2 mr-3" style={{ backgroundColor: milestone.color }}></div>
                          <span className="text-gray-700">{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Progress bar */}
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{milestone.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${milestone.progress}%`,
                        backgroundColor: milestone.color 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const SalaryInsight = () => (
    component.data.estimated_salary && (
      <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
        <h4 className="font-semibold text-green-900 mb-3">💰 Salary Expectations</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700">{component.data.estimated_salary.entry}</div>
            <div className="text-sm text-green-600">Entry Level</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700">{component.data.estimated_salary.mid}</div>
            <div className="text-sm text-green-600">Mid Level</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700">{component.data.estimated_salary.senior}</div>
            <div className="text-sm text-green-600">Senior Level</div>
          </div>
        </div>
      </div>
    )
  );

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 flex items-center">
          🚀 Career Journey: {component.data.career_goal}
        </h3>
        <p className="text-gray-600 mt-2">
          Your personalized roadmap to becoming a {component.data.career_goal}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Timeline: {component.data.timeline} • Click milestones to see details
        </p>
      </div>

      {/* Timeline */}
      <TimelineVisualization />

      {/* Salary Insight */}
      <SalaryInsight />

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