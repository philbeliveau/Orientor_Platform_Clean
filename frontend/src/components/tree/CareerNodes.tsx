import React, { useState, useRef } from 'react';
import { Handle, Position } from 'reactflow';
import { motion, AnimatePresence } from 'framer-motion';

// Animation variants for nodes - matches the CustomNodes.tsx animations
const nodeVariants = {
  hidden: { opacity: 0, scale: 0.85 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      type: 'spring' as const,
      stiffness: 100,
      damping: 12,
      delay: 0.05
    }
  }
};

// Base node styles - common for career node types
const baseNodeStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center',
  borderRadius: '8px',
  padding: '12px 16px',
  minWidth: '120px',
  maxWidth: '160px',
  minHeight: '80px',
  fontSize: '14px',
  fontWeight: 500,
  lineHeight: 1.4,
  boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
  color: 'white',
  transition: 'box-shadow 0.2s ease, transform 0.1s ease',
  userSelect: 'none',
};

// Common interface for career node types
interface CareerNodeProps {
  data: {
    label: string;
    actions?: string[];
  };
  selected: boolean;
}

// Career Domain Node (Root)
export const CareerDomainNode = ({ data }: { data: any }) => {
  return (
    <div className="px-4 py-2 shadow-lg rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 text-white">
      <Handle type="target" position={Position.Top} className="w-16 !bg-indigo-400" />
      <div className="text-center font-medium">{data.label}</div>
      <Handle type="source" position={Position.Bottom} className="w-16 !bg-indigo-400" />
    </div>
  );
};

// Career Family Node (Skill)
export const CareerFamilyNode = ({ data }: { data: any }) => {
  return (
    <div className="px-4 py-2 shadow-lg rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white">
      <Handle type="target" position={Position.Top} className="w-16 !bg-blue-400" />
      <div className="text-center font-medium">{data.label}</div>
      <Handle type="source" position={Position.Bottom} className="w-16 !bg-blue-400" />
    </div>
  );
};

// Career Skill Node (Career)
export const CareerSkillNode = ({ data }: { data: any }) => {
  return (
    <div className="px-4 py-2 shadow-lg rounded-lg bg-gradient-to-r from-green-500 to-green-600 text-white">
      <Handle type="target" position={Position.Top} className="w-16 !bg-green-400" />
      <div className="text-center font-medium">{data.label}</div>
      <Handle type="source" position={Position.Bottom} className="w-16 !bg-green-400" />
    </div>
  );
};

// Optional: Career Specialization Node (Level 3) - Prepared for future expansion
export function CareerSpecializationNode({ data, selected }: CareerNodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #7e22ce 0%, #a855f7 100%)', // Purple gradient
    color: 'white',
    minHeight: '70px',
    maxWidth: '140px',
    boxShadow: selected 
      ? '0 0 0 2px #d8b4fe, 0 4px 12px rgba(168, 85, 247, 0.25)' 
      : '0 4px 12px rgba(168, 85, 247, 0.2)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(168, 85, 247, 0.25)' }}
    >
      <div>{data.label}</div>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#d8b4fe', border: '2px solid #a855f7', width: '6px', height: '6px' }}
      />
    </motion.div>
  );
} 