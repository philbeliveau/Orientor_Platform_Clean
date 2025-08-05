import React, { useState } from 'react';
import { ChevronRight, ChevronDown, TreePine, Star, Info } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface Skill {
  id: string;
  name: string;
  description?: string;
  proficiency_level?: string;
  importance?: 'required' | 'preferred' | 'optional';
  children?: Skill[];
}

interface SkillTreeData {
  job_title: string;
  skills: Skill[];
  total_skills?: number;
  source?: string;
}

interface SkillTreeMessageProps {
  data: SkillTreeData;
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const importanceColors = {
  required: 'text-red-600 bg-red-50 border-red-200',
  preferred: 'text-orange-600 bg-orange-50 border-orange-200',
  optional: 'text-blue-600 bg-blue-50 border-blue-200'
};

const SkillNode: React.FC<{ skill: Skill; level: number }> = ({ skill, level }) => {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = skill.children && skill.children.length > 0;

  return (
    <div className="mb-2">
      <div 
        className={`flex items-start space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer ${
          level === 0 ? 'font-medium' : ''
        }`}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center mt-0.5">
          {hasChildren ? (
            isExpanded ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />
          ) : (
            <div className="w-4" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-gray-800">{skill.name}</span>
            {skill.proficiency_level && (
              <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                {skill.proficiency_level}
              </span>
            )}
            {skill.importance && (
              <span className={`text-xs px-2 py-0.5 rounded-full border ${importanceColors[skill.importance]}`}>
                {skill.importance}
              </span>
            )}
          </div>
          {skill.description && (
            <p className="text-sm text-gray-600 mt-1">{skill.description}</p>
          )}
        </div>
      </div>
      {hasChildren && isExpanded && (
        <div className="ml-6 border-l-2 border-gray-200 pl-2">
          {skill.children!.map((child, index) => (
            <SkillNode key={child.id || index} skill={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const SkillTreeMessage: React.FC<SkillTreeMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const [showAll, setShowAll] = useState(false);
  const displaySkills = showAll ? data.skills : data.skills.slice(0, 5);
  const hasMore = data.skills.length > 5;

  const handleSave = async () => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction(saveAction);
    }
  };

  return (
    <div className={`border border-gray-200 rounded-lg p-4 bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <TreePine className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Skills for {data.job_title}</h3>
            {data.total_skills && (
              <p className="text-sm text-gray-600">{data.total_skills} skills identified</p>
            )}
          </div>
        </div>
        <SaveActionButton onSave={handleSave} saved={saved} size="sm" variant="outline" />
      </div>

      {/* Skills Tree */}
      <div className="space-y-1">
        {displaySkills.map((skill, index) => (
          <SkillNode key={skill.id || index} skill={skill} level={0} />
        ))}
      </div>

      {/* Show More */}
      {hasMore && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Show {data.skills.length - 5} more skills
        </button>
      )}

      {/* Actions */}
      <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
        {actions.filter(a => a.type !== 'save').map((action, index) => (
          <button
            key={index}
            onClick={() => onAction(action)}
            className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Source */}
      {data.source && (
        <div className="mt-3 flex items-center gap-1 text-xs text-gray-500">
          <Info className="w-3 h-3" />
          <span>Source: {data.source}</span>
        </div>
      )}
    </div>
  );
};