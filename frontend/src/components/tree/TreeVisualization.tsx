import React, { useRef, useEffect, useState, useCallback } from 'react';
import { TreeNode } from './TreeNode';
import { PositionedNode, CompetenceNode, TreeViewport } from './types';

interface TreeVisualizationProps {
  nodes: PositionedNode[];
  edges: { source: string; target: string; weight?: number; type?: string }[];
  onNodeClick: (node: PositionedNode) => void;
  onNodeComplete: (nodeId: string) => void;
  savedNodes?: string[];
}

export const TreeVisualization: React.FC<TreeVisualizationProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeComplete,
  savedNodes = []
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [viewport, setViewport] = useState<TreeViewport>({ x: 0, y: 0, zoom: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Calculate SVG bounds
  const calculateBounds = useCallback(() => {
    if (nodes.length === 0) return { minX: 0, maxX: 800, minY: 0, maxY: 600 };
    
    const xCoords = nodes.map(n => n.x);
    const yCoords = nodes.map(n => n.y);
    
    return {
      minX: Math.min(...xCoords) - 100,
      maxX: Math.max(...xCoords) + 100,
      minY: Math.min(...yCoords) - 100,
      maxY: Math.max(...yCoords) + 100
    };
  }, [nodes]);

  const bounds = calculateBounds();
  const width = bounds.maxX - bounds.minX;
  const height = bounds.maxY - bounds.minY;

  // Pan and zoom handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - viewport.x, y: e.clientY - viewport.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setViewport({
      ...viewport,
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const scaleFactor = 0.1;
    const delta = e.deltaY > 0 ? -scaleFactor : scaleFactor;
    const newZoom = Math.min(Math.max(0.1, viewport.zoom + delta), 3);
    
    // Zoom towards mouse position
    const rect = svgRef.current?.getBoundingClientRect();
    if (rect) {
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      const zoomRatio = newZoom / viewport.zoom;
      const newX = mouseX - (mouseX - viewport.x) * zoomRatio;
      const newY = mouseY - (mouseY - viewport.y) * zoomRatio;
      
      setViewport({
        x: newX,
        y: newY,
        zoom: newZoom
      });
    }
  };

  // Center view on mount
  useEffect(() => {
    if (svgRef.current && nodes.length > 0) {
      const rect = svgRef.current.getBoundingClientRect();
      const centerX = rect.width / 2 - (bounds.minX + width / 2);
      const centerY = rect.height / 2 - (bounds.minY + height / 2);
      setViewport({ x: centerX, y: centerY, zoom: 1 });
    }
  }, [nodes.length]);

  return (
    <div className="relative w-full h-full overflow-hidden bg-gray-50 rounded-lg">
      <svg
        ref={svgRef}
        className="w-full h-full"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <defs>
          {/* Shadow filter */}
          <filter id="shadowFilter">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.1" />
          </filter>
          
          {/* Gradient definitions */}
          <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#9ca3af" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#6b7280" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#9ca3af" stopOpacity="0.3" />
          </linearGradient>
        </defs>

        <g transform={`translate(${viewport.x}, ${viewport.y}) scale(${viewport.zoom})`}>
          {/* Render edges */}
          <g className="edges">
            {edges.map((edge, index) => {
              const sourceNode = nodes.find(n => n.id === edge.source);
              const targetNode = nodes.find(n => n.id === edge.target);
              
              if (!sourceNode || !targetNode) return null;
              
              const dx = targetNode.x - sourceNode.x;
              const dy = targetNode.y - sourceNode.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              
              // Create curved path
              const midX = (sourceNode.x + targetNode.x) / 2;
              const midY = (sourceNode.y + targetNode.y) / 2;
              const curvature = 0.2;
              const controlX = midX - dy * curvature;
              const controlY = midY + dx * curvature;
              
              return (
                <g key={`edge-${index}`}>
                  <path
                    d={`M ${sourceNode.x} ${sourceNode.y} Q ${controlX} ${controlY} ${targetNode.x} ${targetNode.y}`}
                    fill="none"
                    stroke="url(#edgeGradient)"
                    strokeWidth={Math.max(1, 3 - distance / 200)}
                    opacity={0.6}
                  />
                  {edge.weight && edge.weight > 0.7 && (
                    <circle r="3" fill="#3b82f6">
                      <animateMotion
                        dur="3s"
                        repeatCount="indefinite"
                        path={`M ${sourceNode.x} ${sourceNode.y} Q ${controlX} ${controlY} ${targetNode.x} ${targetNode.y}`}
                      />
                    </circle>
                  )}
                </g>
              );
            })}
          </g>

          {/* Render nodes */}
          <g className="nodes">
            {nodes.map(node => (
              <TreeNode
                key={node.id}
                node={node}
                onComplete={onNodeComplete}
                onNodeClick={onNodeClick}
                isSaved={savedNodes.includes(node.id)}
              />
            ))}
          </g>
        </g>
      </svg>

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2">
        <button
          onClick={() => setViewport({ ...viewport, zoom: Math.min(3, viewport.zoom + 0.2) })}
          className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
          aria-label="Zoom in"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          onClick={() => setViewport({ ...viewport, zoom: Math.max(0.1, viewport.zoom - 0.2) })}
          className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
          aria-label="Zoom out"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>
        <button
          onClick={() => {
            const rect = svgRef.current?.getBoundingClientRect();
            if (rect) {
              const centerX = rect.width / 2 - (bounds.minX + width / 2);
              const centerY = rect.height / 2 - (bounds.minY + height / 2);
              setViewport({ x: centerX, y: centerY, zoom: 1 });
            }
          }}
          className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
          aria-label="Reset view"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default TreeVisualization;