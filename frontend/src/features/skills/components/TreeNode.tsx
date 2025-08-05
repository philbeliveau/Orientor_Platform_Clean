import React, { useState } from 'react';
import { TreeNodeProps, NodeStyles } from '../types/competence.types';

// Utility function to get node styles based on type
export const getNodeStyles = (node: TreeNodeProps['node'], isSaved: boolean): NodeStyles => {
  if (node.type === "occupation") {
    return {
      primary: isSaved ? "#f59e0b" : "#3b82f6",
      secondary: isSaved ? "#fef3c7" : "#dbeafe",
      text: "#1f2937",
      border: isSaved ? "#d97706" : "#2563eb",
      shadow: isSaved ? "0 4px 20px rgba(245, 158, 11, 0.3)" : "0 4px 20px rgba(59, 130, 246, 0.3)"
    };
  }
  if (node.type === "skillgroup") {
    return {
      primary: "#10b981",
      secondary: "#d1fae5",
      text: "#1f2937",
      border: "#059669",
      shadow: "0 4px 20px rgba(16, 185, 129, 0.3)"
    };
  }
  if (node.is_anchor) {
    return {
      primary: "#8b5cf6",
      secondary: "#ede9fe",
      text: "#1f2937",
      border: "#7c3aed",
      shadow: "0 6px 25px rgba(139, 92, 246, 0.4)"
    };
  }
  return {
    primary: "#6b7280",
    secondary: "#f3f4f6",
    text: "#1f2937",
    border: "#4b5563",
    shadow: "0 4px 15px rgba(107, 114, 128, 0.2)"
  };
};

// Utility function to get node icon
export const getNodeIcon = (node: TreeNodeProps['node'], isSaved: boolean): string => {
  if (node.type === "occupation") return isSaved ? "⭐" : "💼";
  if (node.type === "skillgroup") return "📚";
  if (node.is_anchor) return "🎯";
  return "🔧";
};

// Tree Node Component
export const TreeNode: React.FC<TreeNodeProps> = ({ node, onComplete, onNodeClick, isSaved = false }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  
  const styles = getNodeStyles(node, isSaved);
  const icon = getNodeIcon(node, isSaved);
  
  const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
  const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);

  return (
    <g
      transform={`translate(${node.x - cardWidth / 2},${node.y - cardHeight / 2})`}
      onClick={() => onNodeClick(node)}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      style={{ cursor: 'pointer' }}
    >
      {/* Card Background with gradient */}
      <defs>
        <linearGradient id={`gradient-${node.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: styles.secondary, stopOpacity: 0.9 }} />
          <stop offset="100%" style={{ stopColor: styles.secondary, stopOpacity: 0.7 }} />
        </linearGradient>
        <filter id={`shadow-${node.id}`}>
          <feDropShadow dx="0" dy="4" stdDeviation="8" floodOpacity="0.15" />
        </filter>
      </defs>
      
      <rect
        width={cardWidth}
        height={cardHeight}
        rx="16"
        ry="16"
        fill={`url(#gradient-${node.id})`}
        stroke={styles.border}
        strokeWidth="2"
        filter={`url(#shadow-${node.id})`}
        style={{
          transition: 'all 0.3s ease',
          boxShadow: styles.shadow
        }}
      />
      
      {/* Icon Badge */}
      <circle
        cx="30"
        cy="30"
        r="20"
        fill={styles.primary}
        opacity="0.1"
      />
      <text
        x="30"
        y="38"
        fontSize="20"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {icon}
      </text>
      
      {/* Main Label */}
      <text
        x={cardWidth / 2}
        y={cardHeight / 2 - 10}
        fontSize={node.is_anchor ? "16" : "14"}
        fontWeight="600"
        fill={styles.text}
        textAnchor="middle"
        style={{ 
          fontFamily: 'Inter, system-ui, sans-serif',
          userSelect: 'none'
        }}
      >
        {displayLabel.length > 20 ? displayLabel.substring(0, 20) + '...' : displayLabel}
      </text>
      
      {/* XP Reward Badge */}
      {node.xp_reward && (
        <>
          <rect
            x={cardWidth - 70}
            y={cardHeight - 35}
            width="60"
            height="25"
            rx="12"
            fill={styles.primary}
            opacity="0.9"
          />
          <text
            x={cardWidth - 40}
            y={cardHeight - 18}
            fontSize="12"
            fontWeight="500"
            fill="white"
            textAnchor="middle"
          >
            +{node.xp_reward} XP
          </text>
        </>
      )}
      
      {/* State Indicator */}
      {node.state === 'completed' && (
        <circle
          cx={cardWidth - 20}
          cy="20"
          r="8"
          fill="#10b981"
          stroke="white"
          strokeWidth="2"
        />
      )}
      
      {/* Tooltip */}
      {showTooltip && displayLabel.length > 20 && (
        <g>
          <rect
            x="0"
            y={cardHeight + 10}
            width={Math.min(displayLabel.length * 8 + 20, 300)}
            height="30"
            rx="6"
            fill="rgba(31, 41, 55, 0.95)"
          />
          <text
            x="10"
            y={cardHeight + 30}
            fontSize="12"
            fill="white"
          >
            {displayLabel}
          </text>
        </g>
      )}
    </g>
  );
};