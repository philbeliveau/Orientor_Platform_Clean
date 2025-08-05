'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { SkillNode } from './TimelineVisualization';

interface GraphNode extends SkillNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
  connections: string[];
}

interface GraphEdge {
  source: string;
  target: string;
  strength: number;
}

interface SkillRelationshipGraphProps {
  skills: SkillNode[];
  onSkillClick?: (skill: SkillNode) => void;
  highlightedSkills?: Set<string>;
  className?: string;
}

// Force-directed graph simulation
class ForceSimulation {
  private nodes: GraphNode[];
  private edges: GraphEdge[];
  private width: number;
  private height: number;
  private alpha: number = 1;
  private alphaDecay: number = 0.99;
  private velocityDecay: number = 0.4;

  constructor(nodes: GraphNode[], edges: GraphEdge[], width: number, height: number) {
    this.nodes = nodes;
    this.edges = edges;
    this.width = width;
    this.height = height;
    
    // Initialize positions randomly
    this.nodes.forEach(node => {
      if (!node.x) node.x = Math.random() * width;
      if (!node.y) node.y = Math.random() * height;
      node.vx = 0;
      node.vy = 0;
    });
  }

  tick() {
    if (this.alpha < 0.001) return false;

    // Apply forces
    this.applyRepulsionForce();
    this.applyAttractionForce();
    this.applyCenteringForce();
    
    // Update positions
    this.nodes.forEach(node => {
      node.vx *= this.velocityDecay;
      node.vy *= this.velocityDecay;
      node.x += node.vx;
      node.y += node.vy;
      
      // Boundary constraints
      if (node.x < 50) { node.x = 50; node.vx = 0; }
      if (node.x > this.width - 50) { node.x = this.width - 50; node.vx = 0; }
      if (node.y < 50) { node.y = 50; node.vy = 0; }
      if (node.y > this.height - 50) { node.y = this.height - 50; node.vy = 0; }
    });
    
    this.alpha *= this.alphaDecay;
    return true;
  }

  private applyRepulsionForce() {
    const strength = -300;
    
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const nodeA = this.nodes[i];
        const nodeB = this.nodes[j];
        
        const dx = nodeB.x - nodeA.x;
        const dy = nodeB.y - nodeA.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;
        
        const force = strength / (distance * distance);
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        
        nodeA.vx -= fx;
        nodeA.vy -= fy;
        nodeB.vx += fx;
        nodeB.vy += fy;
      }
    }
  }

  private applyAttractionForce() {
    const strength = 50;
    
    this.edges.forEach(edge => {
      const source = this.nodes.find(n => n.id === edge.source);
      const target = this.nodes.find(n => n.id === edge.target);
      
      if (!source || !target) return;
      
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const distance = Math.sqrt(dx * dx + dy * dy) || 1;
      
      const force = strength * edge.strength;
      const fx = (dx / distance) * force * 0.01;
      const fy = (dy / distance) * force * 0.01;
      
      source.vx += fx;
      source.vy += fy;
      target.vx -= fx;
      target.vy -= fy;
    });
  }

  private applyCenteringForce() {
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const strength = 0.01;
    
    this.nodes.forEach(node => {
      const fx = (centerX - node.x) * strength;
      const fy = (centerY - node.y) * strength;
      
      node.vx += fx;
      node.vy += fy;
    });
  }

  getNodes() {
    return this.nodes;
  }
}

const SkillRelationshipGraph: React.FC<SkillRelationshipGraphProps> = ({
  skills,
  onSkillClick,
  highlightedSkills = new Set(),
  className = '',
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const simulationRef = useRef<ForceSimulation | null>(null);
  const animationRef = useRef<number | null>(null);

  // Convert skills to graph nodes and edges
  useEffect(() => {
    const nodes: GraphNode[] = skills.map(skill => ({
      ...skill,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      connections: skill.relationships || [],
    }));

    const edges: GraphEdge[] = [];
    skills.forEach(skill => {
      if (skill.relationships) {
        skill.relationships.forEach(relatedId => {
          if (skills.find(s => s.id === relatedId)) {
            edges.push({
              source: skill.id,
              target: relatedId,
              strength: 1,
            });
          }
        });
      }
    });

    setGraphNodes(nodes);
    setGraphEdges(edges);
  }, [skills]);

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        setDimensions({
          width: rect.width || 800,
          height: rect.height || 600,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Start simulation when nodes/edges change
  useEffect(() => {
    if (graphNodes.length === 0) return;

    simulationRef.current = new ForceSimulation(
      graphNodes,
      graphEdges,
      dimensions.width,
      dimensions.height
    );

    const animate = () => {
      if (simulationRef.current?.tick()) {
        setGraphNodes([...simulationRef.current.getNodes()]);
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [graphNodes.length, graphEdges.length, dimensions]);

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node.id);
    onSkillClick?.(node);
  }, [onSkillClick]);

  const getNodeSize = (confidence: number) => {
    return 20 + (confidence * 40); // Scale from 20px to 60px
  };

  const getNodeColor = (node: GraphNode) => {
    if (highlightedSkills.has(node.id)) {
      return '#fbbf24'; // Yellow for highlighted
    }
    if (selectedNode === node.id) {
      return '#ef4444'; // Red for selected
    }
    
    // Color based on confidence score
    const hue = 220; // Blue hue
    const saturation = 70;
    const lightness = 30 + (node.confidence_score * 40); // 30% to 70% lightness
    
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  const getEdgeOpacity = (edge: GraphEdge) => {
    const sourceHighlighted = highlightedSkills.has(edge.source);
    const targetHighlighted = highlightedSkills.has(edge.target);
    const sourceSelected = selectedNode === edge.source;
    const targetSelected = selectedNode === edge.target;
    
    if (sourceHighlighted || targetHighlighted || sourceSelected || targetSelected) {
      return 0.8;
    }
    
    return 0.2;
  };

  return (
    <div className={`relative w-full h-96 bg-gray-50 rounded-xl overflow-hidden ${className}`}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        className="absolute inset-0"
      >
        {/* Grid background */}
        <defs>
          <pattern
            id="grid"
            width="20"
            height="20"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 20 0 L 0 0 0 20"
              fill="none"
              stroke="rgba(0,0,0,0.05)"
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        {/* Edges */}
        <g className="edges">
          {graphEdges.map((edge, index) => {
            const sourceNode = graphNodes.find(n => n.id === edge.source);
            const targetNode = graphNodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;
            
            return (
              <line
                key={`${edge.source}-${edge.target}-${index}`}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke="#6b7280"
                strokeWidth={1 + edge.strength}
                strokeOpacity={getEdgeOpacity(edge)}
                className="transition-opacity duration-300"
              />
            );
          })}
        </g>
        
        {/* Nodes */}
        <g className="nodes">
          {graphNodes.map((node) => {
            const size = getNodeSize(node.confidence_score);
            const color = getNodeColor(node);
            
            return (
              <g key={node.id}>
                {/* Node circle */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={size / 2}
                  fill={color}
                  stroke="white"
                  strokeWidth={2}
                  className="cursor-pointer hover:stroke-4 transition-all duration-200 hover:scale-110"
                  onClick={() => handleNodeClick(node)}
                />
                
                {/* Confidence score badge */}
                <circle
                  cx={node.x + size / 3}
                  cy={node.y - size / 3}
                  r={8}
                  fill="white"
                  stroke="#374151"
                  strokeWidth={1}
                />
                <text
                  x={node.x + size / 3}
                  y={node.y - size / 3}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize="8"
                  fontWeight="bold"
                  fill="#374151"
                >
                  {Math.round(node.confidence_score * 100)}
                </text>
                
                {/* Node label */}
                <text
                  x={node.x}
                  y={node.y + size / 2 + 16}
                  textAnchor="middle"
                  fontSize="12"
                  fontWeight="medium"
                  fill="#374151"
                  className="pointer-events-none select-none"
                >
                  {node.label.length > 15 ? `${node.label.slice(0, 15)}...` : node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-md p-3 space-y-2">
        <div className="text-sm font-medium text-gray-900">Legend</div>
        <div className="space-y-1 text-xs text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-blue-300"></div>
            <span>Low Confidence (&lt; 50%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 rounded-full bg-blue-500"></div>
            <span>Medium Confidence (50-80%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-full bg-blue-700"></div>
            <span>High Confidence (80%+)</span>
          </div>
        </div>
      </div>
      
      {/* Controls */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-md p-3">
        <button
          onClick={() => {
            // Reset simulation
            if (simulationRef.current) {
              simulationRef.current = new ForceSimulation(
                graphNodes,
                graphEdges,
                dimensions.width,
                dimensions.height
              );
            }
          }}
          className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
        >
          Reset Layout
        </button>
      </div>
    </div>
  );
};

export default SkillRelationshipGraph;