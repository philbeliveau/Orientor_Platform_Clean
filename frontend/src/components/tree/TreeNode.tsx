import React from 'react';
import { PositionedNode } from './types';

interface TreeNodeProps {
  node: PositionedNode;
  onComplete: (nodeId: string) => void;
  onNodeClick: (node: PositionedNode) => void;
  isSaved?: boolean;
}

// Custom Node Component for SVG rendering with modern card design
export const TreeNode: React.FC<TreeNodeProps> = ({ 
  node, 
  onComplete, 
  onNodeClick, 
  isSaved = false 
}) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  
  // Modern, semantic color scheme
  const getNodeStyles = () => {
    if (node.type === "occupation") {
      return {
        primary: isSaved ? "#f59e0b" : "#3b82f6", // Amber for saved, blue for occupations
        secondary: isSaved ? "#fef3c7" : "#dbeafe", // Light backgrounds
        text: "#1f2937",
        border: isSaved ? "#d97706" : "#2563eb",
        shadow: isSaved ? "0 4px 20px rgba(245, 158, 11, 0.3)" : "0 4px 20px rgba(59, 130, 246, 0.3)"
      };
    }
    if (node.type === "skillgroup") {
      return {
        primary: "#10b981", // Emerald for skill groups
        secondary: "#d1fae5",
        text: "#1f2937", 
        border: "#059669",
        shadow: "0 4px 20px rgba(16, 185, 129, 0.3)"
      };
    }
    if (node.is_anchor) {
      return {
        primary: "#8b5cf6", // Purple for anchors
        secondary: "#ede9fe",
        text: "#1f2937",
        border: "#7c3aed", 
        shadow: "0 6px 25px rgba(139, 92, 246, 0.4)"
      };
    }
    // Default skill nodes
    return {
      primary: "#6b7280", // Gray for regular skills
      secondary: "#f3f4f6",
      text: "#1f2937",
      border: "#4b5563",
      shadow: "0 4px 15px rgba(107, 114, 128, 0.2)"
    };
  };

  const getNodeIcon = () => {
    if (node.type === "occupation") return isSaved ? "⭐" : "💼";
    if (node.type === "skillgroup") return "📚";
    if (node.is_anchor) return "🎯";
    return "🔧";
  };

  const styles = getNodeStyles();
  const icon = getNodeIcon();
  const nodeRadius = node.is_anchor ? 60 : 50;

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onNodeClick(node);
  };

  const handleComplete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onComplete(node.id);
  };

  return (
    <g 
      transform={`translate(${node.x}, ${node.y})`}
      onClick={handleClick}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      style={{ cursor: 'pointer' }}
    >
      {/* Node shadow/glow effect */}
      <circle
        r={nodeRadius + 2}
        fill={styles.primary}
        opacity={0.2}
        filter="url(#shadowFilter)"
      />
      
      {/* Main node circle */}
      <circle
        r={nodeRadius}
        fill={styles.secondary}
        stroke={styles.border}
        strokeWidth={3}
        style={{
          transition: 'all 0.3s ease',
          filter: `drop-shadow(${styles.shadow})`
        }}
      />
      
      {/* Icon */}
      <text
        y={-10}
        textAnchor="middle"
        fontSize={24}
        style={{ userSelect: 'none' }}
      >
        {icon}
      </text>
      
      {/* Label */}
      <text
        y={20}
        textAnchor="middle"
        fontSize={14}
        fontWeight={600}
        fill={styles.text}
        style={{ userSelect: 'none' }}
      >
        {displayLabel.length > 20 ? displayLabel.substring(0, 17) + '...' : displayLabel}
      </text>
      
      {/* XP Reward badge */}
      {node.xp_reward && (
        <g transform={`translate(${nodeRadius - 10}, ${-nodeRadius + 10})`}>
          <circle r={16} fill="#fbbf24" />
          <text
            textAnchor="middle"
            fontSize={12}
            fontWeight="bold"
            fill="#78350f"
          >
            +{node.xp_reward}
          </text>
        </g>
      )}
      
      {/* State indicator */}
      {node.state === 'completed' && (
        <circle
          r={nodeRadius + 5}
          fill="none"
          stroke="#10b981"
          strokeWidth={3}
          strokeDasharray="5 5"
          opacity={0.8}
        />
      )}
      
      {/* Tooltip */}
      {showTooltip && node.challenge && (
        <g transform="translate(0, -80)">
          <rect
            x={-150}
            y={-30}
            width={300}
            height={60}
            rx={8}
            fill="#1f2937"
            fillOpacity={0.95}
          />
          <text
            textAnchor="middle"
            fill="white"
            fontSize={12}
            style={{ userSelect: 'none' }}
          >
            <tspan x={0} dy={-5}>{node.challenge}</tspan>
            {node.xp_reward && (
              <tspan x={0} dy={20} fontSize={10} fill="#fbbf24">
                Reward: {node.xp_reward} XP
              </tspan>
            )}
          </text>
        </g>
      )}
    </g>
  );
};

export default TreeNode;