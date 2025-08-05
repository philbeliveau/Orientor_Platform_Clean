'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  NodeChange,
  EdgeChange,
  Connection,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';

// Composant de nœud personnalisé
const CustomNode = ({ data }: { data: any }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div 
      className={`tree-node ${data.active ? 'tree-node-active' : ''}`}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex justify-between items-center">
        <h4 className="text-base font-bold font-departure text-stitch-accent">{data.label}</h4>
        {data.expandable && (
          <button 
            className="text-stitch-sage hover:text-stitch-accent"
            onClick={() => setExpanded(!expanded)}
          >
            <span className="material-icons-outlined text-sm">
              {expanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        )}
      </div>
      
      {data.description && !expanded && (
        <p className="text-xs text-stitch-sage mt-1 line-clamp-2">{data.description}</p>
      )}
      
      <AnimatePresence>
        {expanded && data.description && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <p className="text-sm text-stitch-sage mt-2">{data.description}</p>
            
            {data.skills && data.skills.length > 0 && (
              <div className="mt-2">
                <h5 className="text-xs font-bold text-stitch-sage mb-1">Compétences</h5>
                <div className="flex flex-wrap gap-1">
                  {data.skills.map((skill: string, index: number) => (
                    <span 
                      key={index} 
                      className="text-xs px-2 py-0.5 bg-stitch-primary border border-stitch-border rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {data.actions && (
              <div className="mt-3 flex gap-2">
                {data.actions.map((action: any, index: number) => (
                  <button 
                    key={index}
                    className="text-xs px-3 py-1 bg-stitch-accent text-white rounded-md hover:bg-opacity-90"
                    onClick={action.onClick}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Types pour les props du composant
interface StyledTreeGraphProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange?: (changes: NodeChange[]) => void;
  onEdgesChange?: (changes: EdgeChange[]) => void;
  onConnect?: (connection: Connection) => void;
  onNodeClick?: (event: React.MouseEvent, node: Node) => void;
  className?: string;
  showControls?: boolean;
  showMiniMap?: boolean;
  showBackground?: boolean;
}

// Composant principal
export default function StyledTreeGraph({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onNodeClick,
  className = '',
  showControls = true,
  showMiniMap = false,
  showBackground = true
}: StyledTreeGraphProps) {
  // Gestionnaires d'événements par défaut si non fournis
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange ? onNodesChange(changes) : null;
    },
    [onNodesChange]
  );

  const handleEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      onEdgesChange ? onEdgesChange(changes) : null;
    },
    [onEdgesChange]
  );

  const handleConnect = useCallback(
    (params: Connection) => {
      onConnect ? onConnect(params) : null;
    },
    [onConnect]
  );

  // Définir les types de nœuds personnalisés
  const nodeTypes = {
    custom: CustomNode,
  };

  return (
    <div className={`w-full h-[500px] ${className}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={handleConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-stitch-primary"
      >
        {showControls && <Controls className="bg-stitch-primary border border-stitch-border" />}
        {showMiniMap && <MiniMap className="bg-stitch-primary border border-stitch-border" />}
        {showBackground && (
          <Background
            color="#254625"
            gap={16}
            size={1}
            className="bg-stitch-pattern"
          />
        )}
      </ReactFlow>
    </div>
  );
}