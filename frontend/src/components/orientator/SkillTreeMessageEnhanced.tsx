import React, { useState } from 'react';
import { MessageComponent, ComponentAction } from '../chat/MessageComponent';

interface SkillTreeMessageProps {
  component: MessageComponent;
  onAction: (action: ComponentAction, componentId: string) => void;
}

export const SkillTreeMessageEnhanced: React.FC<SkillTreeMessageProps> = ({
  component,
  onAction,
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [selectedView, setSelectedView] = useState<'grid' | 'radar'>('grid');

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  if (!component.data || !component.data.categories) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Unable to load skill tree data</p>
      </div>
    );
  }

  const SkillRadarChart = () => {
    const categories = component.data.categories || [];
    const centerX = 150;
    const centerY = 150;
    const radius = 100;
    const angleStep = (2 * Math.PI) / categories.length;

    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-6">
        <svg width="300" height="300" className="mx-auto">
          {/* Background circles */}
          {[20, 40, 60, 80, 100].map((r, i) => (
            <circle
              key={i}
              cx={centerX}
              cy={centerY}
              r={r}
              fill="none"
              stroke="#E5E7EB"
              strokeWidth="1"
              opacity={0.5}
            />
          ))}
          
          {/* Category spokes */}
          {categories.map((category: any, index: number) => {
            const angle = index * angleStep - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            return (
              <g key={index}>
                <line
                  x1={centerX}
                  y1={centerY}
                  x2={x}
                  y2={y}
                  stroke="#E5E7EB"
                  strokeWidth="1"
                />
                <text
                  x={x + 20 * Math.cos(angle)}
                  y={y + 20 * Math.sin(angle)}
                  textAnchor="middle"
                  className="text-xs font-medium fill-gray-700"
                >
                  {category.name}
                </text>
                
                {/* Skill points */}
                {category.skills?.map((skill: any, skillIndex: number) => {
                  const skillRadius = (skill.importance / 100) * radius;
                  const skillX = centerX + skillRadius * Math.cos(angle);
                  const skillY = centerY + skillRadius * Math.sin(angle);
                  
                  return (
                    <circle
                      key={skillIndex}
                      cx={skillX}
                      cy={skillY}
                      r="4"
                      fill={category.color}
                      className="opacity-80 hover:opacity-100 cursor-pointer"
                    >
                      <title>{`${skill.name} - ${skill.importance}% importance`}</title>
                    </circle>
                  );
                })}
              </g>
            );
          })}
          
          {/* Center point */}
          <circle cx={centerX} cy={centerY} r="3" fill="#1F2937" />
        </svg>
      </div>
    );
  };

  const SkillGrid = () => (
    <div className="space-y-4">
      {component.data.categories?.map((category: any, index: number) => (
        <div key={index} className="border border-gray-200 rounded-lg overflow-hidden shadow-sm">
          <button
            onClick={() => toggleCategory(category.name)}
            className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
            style={{ borderLeft: `4px solid ${category.color}` }}
          >
            <div className="flex items-center space-x-3">
              <div 
                className="w-4 h-4 rounded-full shadow-sm"
                style={{ backgroundColor: category.color }}
              ></div>
              <span className="font-semibold text-gray-900">{category.name}</span>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                {category.skills?.length || 0} skills
              </span>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${
                expandedCategories.has(category.name) ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {expandedCategories.has(category.name) && (
            <div className="px-4 pb-4 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {category.skills?.map((skill: any, skillIndex: number) => (
                  <div
                    key={skillIndex}
                    className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-100 hover:shadow-md transition-shadow"
                  >
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{skill.name}</div>
                      <div className="text-sm text-gray-600 capitalize">{skill.level}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Proficiency: {skill.proficiency}%
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className="flex items-center space-x-2">
                        <div className="text-lg font-bold" style={{ color: category.color }}>
                          {skill.importance}%
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">importance</div>
                      
                      {/* Importance bar */}
                      <div className="w-16 h-2 bg-gray-200 rounded-full mt-2">
                        <div 
                          className="h-full rounded-full transition-all duration-300"
                          style={{ 
                            width: `${skill.importance}%`,
                            backgroundColor: category.color 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )) || (
        <div className="text-center py-8 text-gray-500">
          No skill categories available
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            🎯 Skills Roadmap: {component.data.career || 'Your Career'}
          </h3>
          <p className="text-gray-600 mt-1">
            {component.data.total_skills} essential skills across {component.data.categories?.length} categories
          </p>
        </div>
        
        {/* View Toggle */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setSelectedView('grid')}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'grid' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📋 Grid
          </button>
          <button
            onClick={() => setSelectedView('radar')}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'radar' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            🎯 Radar
          </button>
        </div>
      </div>

      {/* Content */}
      {selectedView === 'grid' ? <SkillGrid /> : <SkillRadarChart />}

      {/* Learning Resources */}
      {component.data.learning_resources && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-3">📚 Recommended Learning Resources</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h5 className="font-medium text-blue-800 mb-2">Online Courses</h5>
              <ul className="text-sm text-blue-700 space-y-1">
                {component.data.learning_resources.online_courses?.map((course: string, i: number) => (
                  <li key={i}>• {course}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="font-medium text-blue-800 mb-2">Books</h5>
              <ul className="text-sm text-blue-700 space-y-1">
                {component.data.learning_resources.books?.map((book: string, i: number) => (
                  <li key={i}>• {book}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="font-medium text-blue-800 mb-2">Practice</h5>
              <ul className="text-sm text-blue-700 space-y-1">
                {component.data.learning_resources.practice?.map((practice: string, i: number) => (
                  <li key={i}>• {practice}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

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