# Competence Tree D3.js Technical Specification

## 📐 Architecture Overview

This document provides detailed technical specifications for the new D3.js-based competence tree visualization system that will replace the current over-engineered WebGL implementation.

### System Context

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│   React + D3.js │◄──►│   FastAPI        │◄──►│   Services      │
│                 │    │   competenceTree │    │   (ESCO, LLM)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 🏗️ Component Architecture

### Core Components Hierarchy

```typescript
CompetenceTreeD3
├── TreeContainer
│   ├── TreeVisualization (D3.js integration)
│   │   ├── TreeLayout (d3.tree, d3.cluster)
│   │   ├── NodeRenderer
│   │   │   ├── TreeNode (individual nodes)
│   │   │   └── NodeGroup (clustered nodes)
│   │   ├── EdgeRenderer
│   │   │   ├── TreeEdge (connections)
│   │   │   └── PathHighlight (selected paths)
│   │   └── InteractionLayer
│   │       ├── ZoomHandler (d3.zoom)
│   │       ├── PanHandler
│   │       └── SelectionHandler
│   ├── TreeControls
│   │   ├── ZoomControls (+/- buttons)
│   │   ├── LayoutSelector (tree vs cluster)
│   │   ├── FilterControls (skill types)
│   │   └── ResetViewButton
│   └── ProgressIndicators
│       ├── LoadingSpinner
│       ├── ProgressBar
│       └── StatusMessages
├── NodeModal (detail popup)
│   ├── NodeInfo (title, description)
│   ├── NodeActions (complete, save)
│   ├── RelatedNodes (connections)
│   └── ProgressIndicator
└── ErrorBoundary
    ├── ErrorDisplay
    └── RetryMechanism
```

---

## 🔧 D3.js Integration Patterns

### 1. React + D3 Integration Strategy

**Pattern: React for Structure, D3 for Visualization**

```typescript
// TreeVisualization.tsx - Main D3 integration component
import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';

interface TreeVisualizationProps {
  data: CompetenceTreeData;
  width: number;
  height: number;
  onNodeClick: (node: TreeNodeData) => void;
  onNodeHover: (node: TreeNodeData | null) => void;
}

export const TreeVisualization: React.FC<TreeVisualizationProps> = ({
  data,
  width,
  height,
  onNodeClick,
  onNodeHover
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // D3 selections and scales
  const [svg, setSvg] = useState<d3.Selection<SVGSVGElement, unknown, null, undefined> | null>(null);
  const [zoom, setZoom] = useState<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  
  // Initialize D3 components
  useEffect(() => {
    if (!svgRef.current) return;
    
    const svgSelection = d3.select(svgRef.current);
    setSvg(svgSelection);
    
    // Initialize zoom behavior
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 3])
      .on('zoom', handleZoom);
    
    svgSelection.call(zoomBehavior);
    setZoom(zoomBehavior);
    
    return () => {
      svgSelection.selectAll('*').remove();
    };
  }, []);
  
  // Update visualization when data changes
  useEffect(() => {
    if (!svg || !data) return;
    updateVisualization();
  }, [svg, data, width, height]);
  
  const handleZoom = useCallback((event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
    if (!svg) return;
    
    const { transform } = event;
    svg.select('.tree-group')
      .attr('transform', transform.toString());
  }, [svg]);
  
  const updateVisualization = useCallback(() => {
    // D3 visualization logic here
    renderTree();
  }, [data, width, height]);
  
  return (
    <div ref={containerRef} className="tree-visualization">
      <svg 
        ref={svgRef}
        width={width}
        height={height}
        className="tree-svg"
      >
        <g className="tree-group">
          {/* D3 will populate this */}
        </g>
      </svg>
    </div>
  );
};
```

### 2. Data Transformation Pipeline

```typescript
// utils/dataTransformation.ts
export class TreeDataTransformer {
  static flatToHierarchy(flatData: CompetenceTreeData): d3.HierarchyNode<TreeNodeData> {
    // Convert flat node/edge structure to hierarchical data
    const nodeMap = new Map<string, TreeNodeData>();
    flatData.nodes.forEach(node => nodeMap.set(node.id, node));
    
    // Build parent-child relationships
    const hierarchy = d3.stratify<TreeNodeData>()
      .id(d => d.id)
      .parentId(d => this.findParentId(d, flatData.edges))
      (flatData.nodes);
    
    return hierarchy;
  }
  
  static findParentId(node: TreeNodeData, edges: TreeEdge[]): string | null {
    // Find parent based on edges (simplified logic)
    const parentEdge = edges.find(edge => edge.target === node.id);
    return parentEdge ? parentEdge.source : null;
  }
  
  static calculateNodePositions(
    hierarchyData: d3.HierarchyNode<TreeNodeData>,
    layoutType: 'tree' | 'cluster',
    dimensions: { width: number; height: number }
  ): d3.HierarchyPointNode<TreeNodeData> {
    
    const layout = layoutType === 'tree' 
      ? d3.tree<TreeNodeData>()
      : d3.cluster<TreeNodeData>();
    
    layout.size([dimensions.height - 100, dimensions.width - 200]);
    
    // Apply separation logic for better spacing
    layout.separation((a, b) => {
      return a.parent === b.parent ? 1 : 2;
    });
    
    return layout(hierarchyData);
  }
}
```

### 3. Performance Optimization Strategies

```typescript
// hooks/useVirtualizedTree.ts
export const useVirtualizedTree = (
  allNodes: d3.HierarchyPointNode<TreeNodeData>[],
  viewport: { x: number; y: number; width: number; height: number },
  zoomScale: number
) => {
  return useMemo(() => {
    const margin = 100; // Buffer around viewport
    const expandedViewport = {
      x: viewport.x - margin,
      y: viewport.y - margin,
      width: viewport.width + 2 * margin,
      height: viewport.height + 2 * margin
    };
    
    return allNodes.filter(node => {
      const screenX = node.x * zoomScale;
      const screenY = node.y * zoomScale;
      
      return screenX >= expandedViewport.x &&
             screenX <= expandedViewport.x + expandedViewport.width &&
             screenY >= expandedViewport.y &&
             screenY <= expandedViewport.y + expandedViewport.height;
    }).slice(0, 500); // Maximum visible nodes for performance
  }, [allNodes, viewport, zoomScale]);
};

// utils/performanceOptimization.ts
export class TreePerformanceOptimizer {
  private static readonly MAX_VISIBLE_NODES = 500;
  private static readonly ANIMATION_THRESHOLD = 100;
  
  static shouldUseAnimations(nodeCount: number): boolean {
    return nodeCount < this.ANIMATION_THRESHOLD;
  }
  
  static optimizeNodeRendering(
    nodes: d3.HierarchyPointNode<TreeNodeData>[],
    zoomLevel: number
  ): d3.HierarchyPointNode<TreeNodeData>[] {
    
    // Level-of-detail: show fewer details at lower zoom levels
    if (zoomLevel < 0.5) {
      return nodes.filter(node => node.depth <= 2); // Show only first 2 levels
    }
    
    if (zoomLevel < 1) {
      return nodes.filter(node => node.depth <= 4); // Show first 4 levels
    }
    
    return nodes.slice(0, this.MAX_VISIBLE_NODES);
  }
  
  static debounceZoom = debounce((callback: () => void) => {
    callback();
  }, 16); // ~60fps
}
```

---

## 🎨 Rendering Engine

### 1. Node Rendering System

```typescript
// components/tree/NodeRenderer.tsx
export class NodeRenderer {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private nodeGroup: d3.Selection<SVGGElement, unknown, null, undefined>;
  
  constructor(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) {
    this.svg = svg;
    this.nodeGroup = svg.select('.tree-group').append('g').attr('class', 'nodes');
  }
  
  renderNodes(
    nodes: d3.HierarchyPointNode<TreeNodeData>[],
    onNodeClick: (node: TreeNodeData) => void,
    onNodeHover: (node: TreeNodeData | null) => void
  ) {
    const nodeSelection = this.nodeGroup
      .selectAll<SVGGElement, d3.HierarchyPointNode<TreeNodeData>>('.node')
      .data(nodes, d => d.data.id);
    
    // Enter selection - new nodes
    const nodeEnter = nodeSelection
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .style('opacity', 0);
    
    // Add circles for nodes
    nodeEnter
      .append('circle')
      .attr('r', d => this.getNodeRadius(d.data))
      .attr('fill', d => this.getNodeColor(d.data))
      .attr('stroke', d => this.getNodeStroke(d.data))
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');
    
    // Add labels
    nodeEnter
      .append('text')
      .attr('dy', '.35em')
      .attr('x', d => d.children ? -13 : 13)
      .style('text-anchor', d => d.children ? 'end' : 'start')
      .text(d => d.data.label)
      .style('font-size', d => this.getFontSize(d.data))
      .style('fill', '#333');
    
    // Add status indicators
    nodeEnter
      .append('circle')
      .attr('class', 'status-indicator')
      .attr('r', 4)
      .attr('cx', 12)
      .attr('cy', -12)
      .attr('fill', d => this.getStatusColor(d.data))
      .style('opacity', d => d.data.state === 'completed' ? 1 : 0);
    
    // Update selection - existing nodes
    const nodeUpdate = nodeEnter.merge(nodeSelection);
    
    nodeUpdate
      .transition()
      .duration(750)
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .style('opacity', 1);
    
    // Interactive behaviors
    nodeUpdate
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeClick(d.data);
      })
      .on('mouseover', (event, d) => {
        onNodeHover(d.data);
        this.highlightNode(d3.select(event.currentTarget));
      })
      .on('mouseout', (event, d) => {
        onNodeHover(null);
        this.unhighlightNode(d3.select(event.currentTarget));
      });
    
    // Exit selection - removed nodes
    nodeSelection
      .exit()
      .transition()
      .duration(750)
      .style('opacity', 0)
      .remove();
  }
  
  private getNodeRadius(node: TreeNodeData): number {
    const baseRadius = 8;
    const typeMultipliers = {
      'anchor': 1.5,
      'skill': 1.0,
      'occupation': 1.2
    };
    return baseRadius * (typeMultipliers[node.type] || 1.0);
  }
  
  private getNodeColor(node: TreeNodeData): string {
    const stateColors = {
      'locked': '#94a3b8',     // gray
      'available': '#3b82f6',   // blue
      'completed': '#10b981',   // green
      'anchor': '#f59e0b'       // amber
    };
    return stateColors[node.state] || stateColors['available'];
  }
  
  private highlightNode(nodeSelection: d3.Selection<any, any, any, any>) {
    nodeSelection
      .select('circle')
      .transition()
      .duration(200)
      .attr('stroke-width', 4)
      .attr('r', function(d: any) { 
        return +d3.select(this).attr('r') * 1.2; 
      });
  }
  
  private unhighlightNode(nodeSelection: d3.Selection<any, any, any, any>) {
    nodeSelection
      .select('circle')
      .transition()
      .duration(200)
      .attr('stroke-width', 2)
      .attr('r', function(d: any) { 
        return +d3.select(this).attr('r') / 1.2; 
      });
  }
}
```

### 2. Edge Rendering System

```typescript
// components/tree/EdgeRenderer.tsx
export class EdgeRenderer {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private linkGroup: d3.Selection<SVGGElement, unknown, null, undefined>;
  
  constructor(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) {
    this.svg = svg;
    this.linkGroup = svg.select('.tree-group').insert('g', '.nodes').attr('class', 'links');
  }
  
  renderEdges(
    links: d3.HierarchyPointLink<TreeNodeData>[],
    highlightedPaths?: string[]
  ) {
    const linkSelection = this.linkGroup
      .selectAll<SVGPathElement, d3.HierarchyPointLink<TreeNodeData>>('.link')
      .data(links, d => `${d.source.data.id}-${d.target.data.id}`);
    
    // Enter selection
    const linkEnter = linkSelection
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d => this.createLinkPath(d.source, d.source)) // Start from source
      .style('fill', 'none')
      .style('stroke', '#64748b')
      .style('stroke-width', 2)
      .style('opacity', 0);
    
    // Update selection
    const linkUpdate = linkEnter.merge(linkSelection);
    
    linkUpdate
      .transition()
      .duration(750)
      .attr('d', d => this.createLinkPath(d.source, d.target))
      .style('stroke', d => {
        const isHighlighted = highlightedPaths?.includes(`${d.source.data.id}-${d.target.data.id}`);
        return isHighlighted ? '#f59e0b' : '#64748b';
      })
      .style('stroke-width', d => {
        const isHighlighted = highlightedPaths?.includes(`${d.source.data.id}-${d.target.data.id}`);
        return isHighlighted ? 4 : 2;
      })
      .style('opacity', 1);
    
    // Exit selection
    linkSelection
      .exit()
      .transition()
      .duration(750)
      .attr('d', d => this.createLinkPath(d.target, d.target))
      .style('opacity', 0)
      .remove();
  }
  
  private createLinkPath(
    source: d3.HierarchyPointNode<TreeNodeData>,
    target: d3.HierarchyPointNode<TreeNodeData>
  ): string {
    // Create smooth curved path between nodes
    const sourceX = source.y;
    const sourceY = source.x;
    const targetX = target.y;
    const targetY = target.x;
    
    // Control point for smooth curve
    const midX = (sourceX + targetX) / 2;
    
    return `M${sourceX},${sourceY}
            C${midX},${sourceY}
             ${midX},${targetY}
             ${targetX},${targetY}`;
  }
}
```

---

## 🔄 State Management

### 1. React Query Integration

```typescript
// hooks/useTreeData.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { competenceTreeService } from '@/services/competenceTreeService';

export const useTreeData = (graphId: string) => {
  const queryClient = useQueryClient();
  
  const {
    data: treeData,
    isLoading,
    error,
    refetch
  } = useQuery(
    ['competence-tree', graphId],
    () => competenceTreeService.getTree(graphId),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    }
  );
  
  const nodeCompletionMutation = useMutation(
    (nodeId: string) => competenceTreeService.completeNode(graphId, nodeId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['competence-tree', graphId]);
      }
    }
  );
  
  const generateTreeMutation = useMutation(
    () => competenceTreeService.generateTree(),
    {
      onSuccess: (newTreeData) => {
        queryClient.setQueryData(['competence-tree', newTreeData.graph_id], newTreeData);
      }
    }
  );
  
  return {
    treeData,
    isLoading,
    error,
    refetch,
    completeNode: nodeCompletionMutation.mutate,
    generateTree: generateTreeMutation.mutate,
    isGenerating: generateTreeMutation.isLoading
  };
};
```

### 2. Tree State Management

```typescript
// stores/treeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface TreeState {
  // View state
  selectedNodeId: string | null;
  highlightedNodeIds: string[];
  expandedNodeIds: Set<string>;
  zoomLevel: number;
  panPosition: { x: number; y: number };
  layoutType: 'tree' | 'cluster';
  
  // Filter state
  visibleNodeTypes: Set<string>;
  completedNodesVisible: boolean;
  
  // UI state
  isModalOpen: boolean;
  modalNodeId: string | null;
  
  // Actions
  setSelectedNode: (nodeId: string | null) => void;
  toggleNodeExpansion: (nodeId: string) => void;
  setHighlightedNodes: (nodeIds: string[]) => void;
  updateViewport: (zoom: number, pan: { x: number; y: number }) => void;
  setLayoutType: (type: 'tree' | 'cluster') => void;
  toggleNodeTypeVisibility: (nodeType: string) => void;
  openModal: (nodeId: string) => void;
  closeModal: () => void;
}

export const useTreeStore = create<TreeState>()(
  persist(
    (set, get) => ({
      // Initial state
      selectedNodeId: null,
      highlightedNodeIds: [],
      expandedNodeIds: new Set(),
      zoomLevel: 1,
      panPosition: { x: 0, y: 0 },
      layoutType: 'tree',
      visibleNodeTypes: new Set(['skill', 'occupation', 'anchor']),
      completedNodesVisible: true,
      isModalOpen: false,
      modalNodeId: null,
      
      // Actions
      setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
      
      toggleNodeExpansion: (nodeId) => set((state) => {
        const newExpanded = new Set(state.expandedNodeIds);
        if (newExpanded.has(nodeId)) {
          newExpanded.delete(nodeId);
        } else {
          newExpanded.add(nodeId);
        }
        return { expandedNodeIds: newExpanded };
      }),
      
      setHighlightedNodes: (nodeIds) => set({ highlightedNodeIds: nodeIds }),
      
      updateViewport: (zoom, pan) => set({ 
        zoomLevel: zoom, 
        panPosition: pan 
      }),
      
      setLayoutType: (type) => set({ layoutType: type }),
      
      toggleNodeTypeVisibility: (nodeType) => set((state) => {
        const newVisible = new Set(state.visibleNodeTypes);
        if (newVisible.has(nodeType)) {
          newVisible.delete(nodeType);
        } else {
          newVisible.add(nodeType);
        }
        return { visibleNodeTypes: newVisible };
      }),
      
      openModal: (nodeId) => set({ 
        isModalOpen: true, 
        modalNodeId: nodeId 
      }),
      
      closeModal: () => set({ 
        isModalOpen: false, 
        modalNodeId: null 
      })
    }),
    {
      name: 'tree-store',
      partialize: (state) => ({
        layoutType: state.layoutType,
        visibleNodeTypes: state.visibleNodeTypes,
        completedNodesVisible: state.completedNodesVisible
      })
    }
  )
);
```

---

## 📱 Responsive Design System

### 1. Viewport Management

```typescript
// hooks/useResponsiveTree.ts
export const useResponsiveTree = () => {
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [isMobile, setIsMobile] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { offsetWidth, offsetHeight } = containerRef.current;
        setDimensions({ width: offsetWidth, height: offsetHeight });
        setIsMobile(offsetWidth < 768);
      }
    };
    
    updateDimensions();
    
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    
    return () => resizeObserver.disconnect();
  }, []);
  
  // Mobile-specific optimizations
  const treeConfig = useMemo(() => ({
    nodeSize: isMobile ? 12 : 16,
    fontSize: isMobile ? '12px' : '14px',
    minZoom: isMobile ? 0.25 : 0.1,
    maxZoom: isMobile ? 2 : 3,
    touchGestures: isMobile,
    showLabels: !isMobile || dimensions.width > 480
  }), [isMobile, dimensions]);
  
  return {
    dimensions,
    isMobile,
    containerRef,
    treeConfig
  };
};
```

### 2. Touch Gesture Handling

```typescript
// utils/touchGestures.ts
export class TouchGestureHandler {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private zoom: d3.ZoomBehavior<SVGSVGElement, unknown>;
  private lastTap = 0;
  
  constructor(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    zoom: d3.ZoomBehavior<SVGSVGElement, unknown>
  ) {
    this.svg = svg;
    this.zoom = zoom;
    this.setupGestures();
  }
  
  private setupGestures() {
    // Enable touch gestures
    this.svg
      .on('touchstart', this.handleTouchStart.bind(this))
      .on('touchmove', this.handleTouchMove.bind(this))
      .on('touchend', this.handleTouchEnd.bind(this));
    
    // Double-tap to zoom
    this.svg.on('touchend', (event) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - this.lastTap;
      
      if (tapLength < 500 && tapLength > 0) {
        // Double tap detected
        event.preventDefault();
        this.handleDoubleTap(event);
      }
      
      this.lastTap = currentTime;
    });
  }
  
  private handleTouchStart(event: TouchEvent) {
    if (event.touches.length === 1) {
      // Single finger - potential pan start
      event.preventDefault();
    }
  }
  
  private handleTouchMove(event: TouchEvent) {
    if (event.touches.length === 1) {
      // Single finger pan
      event.preventDefault();
    }
  }
  
  private handleDoubleTap(event: TouchEvent) {
    const [x, y] = d3.pointer(event, this.svg.node());
    const currentTransform = d3.zoomTransform(this.svg.node()!);
    const newScale = currentTransform.k < 1.5 ? 2 : 0.5;
    
    this.svg
      .transition()
      .duration(300)
      .call(
        this.zoom.transform,
        d3.zoomIdentity.translate(x, y).scale(newScale).translate(-x, -y)
      );
  }
}
```

---

## 🎯 Interaction System

### 1. Node Interaction Patterns

```typescript
// components/tree/InteractionLayer.tsx
export const InteractionLayer: React.FC<{
  nodes: d3.HierarchyPointNode<TreeNodeData>[];
  onNodeClick: (node: TreeNodeData) => void;
  onPathHighlight: (path: string[]) => void;
}> = ({ nodes, onNodeClick, onPathHighlight }) => {
  
  const handleNodeInteraction = useCallback((
    action: 'click' | 'hover' | 'focus',
    node: TreeNodeData
  ) => {
    switch (action) {
      case 'click':
        onNodeClick(node);
        break;
        
      case 'hover':
        // Highlight path to root
        const pathToRoot = getPathToRoot(node.id, nodes);
        onPathHighlight(pathToRoot);
        break;
        
      case 'focus':
        // Accessibility focus - similar to hover
        const focusPath = getPathToRoot(node.id, nodes);
        onPathHighlight(focusPath);
        break;
    }
  }, [nodes, onNodeClick, onPathHighlight]);
  
  const getPathToRoot = useCallback((nodeId: string, allNodes: d3.HierarchyPointNode<TreeNodeData>[]) => {
    const node = allNodes.find(n => n.data.id === nodeId);
    if (!node) return [];
    
    const path: string[] = [];
    let current = node;
    
    while (current) {
      path.push(current.data.id);
      current = current.parent;
    }
    
    return path;
  }, []);
  
  return null; // This component handles interactions through D3
};
```

### 2. Keyboard Navigation

```typescript
// hooks/useKeyboardNavigation.ts
export const useKeyboardNavigation = (
  nodes: d3.HierarchyPointNode<TreeNodeData>[],
  selectedNodeId: string | null,
  onNodeSelect: (nodeId: string) => void,
  onNodeActivate: (nodeId: string) => void
) => {
  
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!selectedNodeId) return;
      
      const currentNode = nodes.find(n => n.data.id === selectedNodeId);
      if (!currentNode) return;
      
      let targetNode: d3.HierarchyPointNode<TreeNodeData> | null = null;
      
      switch (event.key) {
        case 'ArrowUp':
          targetNode = currentNode.parent;
          break;
          
        case 'ArrowDown':
          targetNode = currentNode.children?.[0] || null;
          break;
          
        case 'ArrowLeft':
          targetNode = getPreviousSibling(currentNode);
          break;
          
        case 'ArrowRight':
          targetNode = getNextSibling(currentNode);
          break;
          
        case 'Enter':
        case ' ':
          onNodeActivate(selectedNodeId);
          event.preventDefault();
          return;
          
        case 'Escape':
          onNodeSelect('');
          return;
      }
      
      if (targetNode) {
        onNodeSelect(targetNode.data.id);
        event.preventDefault();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [nodes, selectedNodeId, onNodeSelect, onNodeActivate]);
  
  const getPreviousSibling = (node: d3.HierarchyPointNode<TreeNodeData>) => {
    if (!node.parent) return null;
    const siblings = node.parent.children || [];
    const currentIndex = siblings.indexOf(node);
    return currentIndex > 0 ? siblings[currentIndex - 1] : null;
  };
  
  const getNextSibling = (node: d3.HierarchyPointNode<TreeNodeData>) => {
    if (!node.parent) return null;
    const siblings = node.parent.children || [];
    const currentIndex = siblings.indexOf(node);
    return currentIndex < siblings.length - 1 ? siblings[currentIndex + 1] : null;
  };
};
```

---

## 🔍 Search & Filter System

### 1. Tree Search Implementation

```typescript
// hooks/useTreeSearch.ts
export const useTreeSearch = (nodes: TreeNodeData[]) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<TreeNodeData[]>([]);
  const [filters, setFilters] = useState({
    types: new Set<string>(['skill', 'occupation', 'anchor']),
    states: new Set<string>(['available', 'completed', 'locked']),
    difficulty: { min: 1, max: 5 }
  });
  
  // Fuzzy search implementation
  const searchNodes = useMemo(() => {
    if (!searchQuery.trim()) {
      return nodes.filter(node => 
        filters.types.has(node.type) &&
        filters.states.has(node.state)
      );
    }
    
    const fuse = new Fuse(nodes, {
      keys: ['label', 'description', 'metadata.keywords'],
      threshold: 0.3,
      includeScore: true
    });
    
    const results = fuse.search(searchQuery);
    return results
      .map(result => result.item)
      .filter(node => 
        filters.types.has(node.type) &&
        filters.states.has(node.state)
      );
  }, [nodes, searchQuery, filters]);
  
  const highlightSearchMatches = useCallback((
    text: string,
    query: string
  ): React.ReactNode => {
    if (!query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={index} className="bg-yellow-200 text-yellow-900">
          {part}
        </mark>
      ) : part
    );
  }, []);
  
  return {
    searchQuery,
    setSearchQuery,
    searchResults: searchNodes,
    filters,
    setFilters,
    highlightSearchMatches
  };
};
```

### 2. Filter Controls Component

```typescript
// components/tree/FilterControls.tsx
export const FilterControls: React.FC<{
  filters: TreeFilters;
  onFiltersChange: (filters: TreeFilters) => void;
  nodeStats: { [key: string]: number };
}> = ({ filters, onFiltersChange, nodeStats }) => {
  
  const toggleTypeFilter = (type: string) => {
    const newTypes = new Set(filters.types);
    if (newTypes.has(type)) {
      newTypes.delete(type);
    } else {
      newTypes.add(type);
    }
    onFiltersChange({ ...filters, types: newTypes });
  };
  
  const toggleStateFilter = (state: string) => {
    const newStates = new Set(filters.states);
    if (newStates.has(state)) {
      newStates.delete(state);
    } else {
      newStates.add(state);
    }
    onFiltersChange({ ...filters, states: newStates });
  };
  
  return (
    <div className="filter-controls bg-white rounded-lg shadow-sm p-4 space-y-4">
      {/* Node Types */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Node Types</h3>
        <div className="flex flex-wrap gap-2">
          {['skill', 'occupation', 'anchor'].map(type => (
            <button
              key={type}
              onClick={() => toggleTypeFilter(type)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filters.types.has(type)
                  ? 'bg-blue-100 text-blue-800 border-blue-200'
                  : 'bg-gray-100 text-gray-600 border-gray-200'
              } border`}
            >
              {type} ({nodeStats[type] || 0})
            </button>
          ))}
        </div>
      </div>
      
      {/* Node States */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Progress</h3>
        <div className="flex flex-wrap gap-2">
          {['available', 'completed', 'locked'].map(state => (
            <button
              key={state}
              onClick={() => toggleStateFilter(state)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filters.states.has(state)
                  ? 'bg-green-100 text-green-800 border-green-200'
                  : 'bg-gray-100 text-gray-600 border-gray-200'
              } border`}
            >
              {state} ({nodeStats[state] || 0})
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

## 🚀 Performance Optimization

### 1. Rendering Performance

```typescript
// utils/renderingOptimizations.ts
export class RenderingOptimizer {
  private static readonly PERFORMANCE_THRESHOLDS = {
    NODE_COUNT_FOR_VIRTUALIZATION: 200,
    ANIMATION_DISABLE_THRESHOLD: 500,
    LOD_SWITCH_THRESHOLD: 100
  };
  
  static shouldVirtualizeNodes(nodeCount: number): boolean {
    return nodeCount > this.PERFORMANCE_THRESHOLDS.NODE_COUNT_FOR_VIRTUALIZATION;
  }
  
  static shouldDisableAnimations(nodeCount: number): boolean {
    return nodeCount > this.PERFORMANCE_THRESHOLDS.ANIMATION_DISABLE_THRESHOLD;
  }
  
  static getOptimalRenderStrategy(
    nodeCount: number,
    zoomLevel: number,
    deviceType: 'mobile' | 'tablet' | 'desktop'
  ): RenderStrategy {
    
    if (deviceType === 'mobile' && nodeCount > 50) {
      return {
        useVirtualization: true,
        useLOD: true,
        animationsEnabled: false,
        maxVisibleNodes: 50
      };
    }
    
    if (nodeCount > this.PERFORMANCE_THRESHOLDS.LOD_SWITCH_THRESHOLD) {
      return {
        useVirtualization: this.shouldVirtualizeNodes(nodeCount),
        useLOD: true,
        animationsEnabled: !this.shouldDisableAnimations(nodeCount),
        maxVisibleNodes: Math.min(nodeCount, 300)
      };
    }
    
    return {
      useVirtualization: false,
      useLOD: false,
      animationsEnabled: true,
      maxVisibleNodes: nodeCount
    };
  }
  
  static optimizeNodeVisibility(
    allNodes: d3.HierarchyPointNode<TreeNodeData>[],
    viewport: ViewportBounds,
    zoomLevel: number
  ): d3.HierarchyPointNode<TreeNodeData>[] {
    
    // Frustum culling - only render nodes in viewport
    const visibleNodes = allNodes.filter(node => {
      const screenPos = this.transformToScreen(node, zoomLevel);
      return this.isInViewport(screenPos, viewport);
    });
    
    // Level of detail - reduce detail at low zoom levels
    if (zoomLevel < 0.5) {
      return visibleNodes.filter(node => node.depth <= 2);
    }
    
    return visibleNodes;
  }
  
  private static transformToScreen(
    node: d3.HierarchyPointNode<TreeNodeData>, 
    zoomLevel: number
  ): { x: number; y: number } {
    return {
      x: node.x * zoomLevel,
      y: node.y * zoomLevel
    };
  }
  
  private static isInViewport(
    screenPos: { x: number; y: number },
    viewport: ViewportBounds
  ): boolean {
    return screenPos.x >= viewport.left &&
           screenPos.x <= viewport.right &&
           screenPos.y >= viewport.top &&
           screenPos.y <= viewport.bottom;
  }
}

interface RenderStrategy {
  useVirtualization: boolean;
  useLOD: boolean;
  animationsEnabled: boolean;
  maxVisibleNodes: number;
}

interface ViewportBounds {
  left: number;
  right: number;
  top: number;
  bottom: number;
}
```

### 2. Memory Management

```typescript
// utils/memoryManagement.ts
export class MemoryManager {
  private static nodeCache = new Map<string, d3.HierarchyPointNode<TreeNodeData>>();
  private static renderCache = new Map<string, SVGElement>();
  private static readonly MAX_CACHE_SIZE = 1000;
  
  static cacheNode(nodeId: string, node: d3.HierarchyPointNode<TreeNodeData>) {
    if (this.nodeCache.size >= this.MAX_CACHE_SIZE) {
      // LRU eviction - remove oldest entries
      const firstKey = this.nodeCache.keys().next().value;
      this.nodeCache.delete(firstKey);
    }
    this.nodeCache.set(nodeId, node);
  }
  
  static getCachedNode(nodeId: string): d3.HierarchyPointNode<TreeNodeData> | null {
    return this.nodeCache.get(nodeId) || null;
  }
  
  static clearNodeCache() {
    this.nodeCache.clear();
  }
  
  static optimizeMemoryUsage() {
    // Remove unused cached elements
    const unusedKeys: string[] = [];
    
    this.renderCache.forEach((element, key) => {
      if (!document.contains(element)) {
        unusedKeys.push(key);
      }
    });
    
    unusedKeys.forEach(key => {
      this.renderCache.delete(key);
    });
    
    // Force garbage collection hint
    if ((window as any).gc) {
      (window as any).gc();
    }
  }
  
  static getMemoryUsage(): MemoryStats {
    return {
      nodeCacheSize: this.nodeCache.size,
      renderCacheSize: this.renderCache.size,
      estimatedMemoryMB: (this.nodeCache.size * 0.001) + (this.renderCache.size * 0.002)
    };
  }
}

interface MemoryStats {
  nodeCacheSize: number;
  renderCacheSize: number;
  estimatedMemoryMB: number;
}
```

---

## 🔒 Error Handling & Recovery

### 1. Error Boundary System

```typescript
// components/tree/TreeErrorBoundary.tsx
interface TreeErrorState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryCount: number;
}

export class TreeErrorBoundary extends Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  TreeErrorState
> {
  private maxRetries = 3;
  
  constructor(props: any) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    };
  }
  
  static getDerivedStateFromError(error: Error): Partial<TreeErrorState> {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error to monitoring service
    console.error('Tree visualization error:', error);
    console.error('Error info:', errorInfo);
    
    // Report to error tracking service
    this.props.onError?.(error);
  }
  
  handleRetry = () => {
    if (this.state.retryCount < this.maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1
      }));
    }
  }
  
  render() {
    if (this.state.hasError) {
      const canRetry = this.state.retryCount < this.maxRetries;
      
      return (
        <div className="tree-error-boundary bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-800">
                Visualization Error
              </h3>
              <p className="text-red-600">
                The skill tree encountered an unexpected error
              </p>
            </div>
          </div>
          
          <div className="bg-red-100 rounded p-3 mb-4 font-mono text-sm text-red-800">
            {this.state.error?.message}
          </div>
          
          <div className="flex space-x-4">
            {canRetry && (
              <button
                onClick={this.handleRetry}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Try Again ({this.maxRetries - this.state.retryCount} attempts left)
              </button>
            )}
            
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Reload Page
            </button>
          </div>
          
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-4">
              <summary className="cursor-pointer text-red-700">
                Error Details (Development)
              </summary>
              <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 2. Graceful Degradation

```typescript
// hooks/useGracefulDegradation.ts
export const useGracefulDegradation = () => {
  const [capabilities, setCapabilities] = useState({
    webgl: true,
    svg: true,
    animations: true,
    complexInteractions: true
  });
  
  const [fallbackMode, setFallbackMode] = useState<'none' | 'simple' | 'minimal'>('none');
  
  useEffect(() => {
    detectCapabilities();
  }, []);
  
  const detectCapabilities = () => {
    const newCapabilities = {
      webgl: detectWebGLSupport(),
      svg: detectSVGSupport(),
      animations: detectAnimationSupport(),
      complexInteractions: detectInteractionSupport()
    };
    
    setCapabilities(newCapabilities);
    
    // Determine fallback mode based on capabilities
    if (!newCapabilities.svg) {
      setFallbackMode('minimal');
    } else if (!newCapabilities.animations || !newCapabilities.complexInteractions) {
      setFallbackMode('simple');
    } else {
      setFallbackMode('none');
    }
  };
  
  const handleRenderError = useCallback((error: Error) => {
    console.warn('Render error, falling back:', error);
    
    // Progressive degradation
    if (fallbackMode === 'none') {
      setFallbackMode('simple');
    } else if (fallbackMode === 'simple') {
      setFallbackMode('minimal');
    }
  }, [fallbackMode]);
  
  const getRenderConfig = (): TreeRenderConfig => {
    switch (fallbackMode) {
      case 'minimal':
        return {
          renderer: 'canvas',
          animationsEnabled: false,
          interactionsEnabled: false,
          maxNodes: 50,
          useWebWorkers: false
        };
        
      case 'simple':
        return {
          renderer: 'svg',
          animationsEnabled: false,
          interactionsEnabled: true,
          maxNodes: 200,
          useWebWorkers: false
        };
        
      default:
        return {
          renderer: 'svg',
          animationsEnabled: true,
          interactionsEnabled: true,
          maxNodes: 500,
          useWebWorkers: true
        };
    }
  };
  
  return {
    capabilities,
    fallbackMode,
    renderConfig: getRenderConfig(),
    onRenderError: handleRenderError
  };
};

function detectWebGLSupport(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
  } catch {
    return false;
  }
}

function detectSVGSupport(): boolean {
  return typeof SVGElement !== 'undefined';
}

function detectAnimationSupport(): boolean {
  return 'animate' in document.documentElement;
}

function detectInteractionSupport(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

interface TreeRenderConfig {
  renderer: 'svg' | 'canvas';
  animationsEnabled: boolean;
  interactionsEnabled: boolean;
  maxNodes: number;
  useWebWorkers: boolean;
}
```

---

## 📊 Analytics & Monitoring

### 1. Performance Monitoring

```typescript
// utils/performanceMonitoring.ts
export class TreePerformanceMonitor {
  private static metrics: PerformanceMetric[] = [];
  private static readonly MAX_METRICS = 100;
  
  static startMeasure(name: string): PerformanceMeasurement {
    const startTime = performance.now();
    performance.mark(`${name}-start`);
    
    return {
      name,
      startTime,
      end: () => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        performance.mark(`${name}-end`);
        performance.measure(name, `${name}-start`, `${name}-end`);
        
        this.recordMetric({
          name,
          duration,
          timestamp: Date.now(),
          type: 'performance'
        });
        
        return duration;
      }
    };
  }
  
  static recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);
    
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics.shift();
    }
    
    // Send to analytics if enabled
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalytics(metric);
    }
  }
  
  static getMetrics(): PerformanceReport {
    const now = Date.now();
    const recentMetrics = this.metrics.filter(m => now - m.timestamp < 300000); // Last 5 minutes
    
    return {
      totalMeasurements: recentMetrics.length,
      averageRenderTime: this.calculateAverage(recentMetrics, 'tree-render'),
      averageInteractionTime: this.calculateAverage(recentMetrics, 'node-interaction'),
      memoryUsage: this.getMemoryUsage(),
      timestamp: now
    };
  }
  
  private static calculateAverage(metrics: PerformanceMetric[], nameFilter: string): number {
    const filtered = metrics.filter(m => m.name.includes(nameFilter));
    if (filtered.length === 0) return 0;
    
    const sum = filtered.reduce((acc, m) => acc + m.duration, 0);
    return sum / filtered.length;
  }
  
  private static getMemoryUsage(): MemoryUsage {
    const memInfo = (performance as any).memory;
    return {
      used: memInfo?.usedJSHeapSize || 0,
      total: memInfo?.totalJSHeapSize || 0,
      limit: memInfo?.jsHeapSizeLimit || 0
    };
  }
  
  private static sendToAnalytics(metric: PerformanceMetric) {
    // Integration with analytics service
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'tree_performance', {
        metric_name: metric.name,
        duration: metric.duration,
        custom_map: { metric_type: metric.type }
      });
    }
  }
}

interface PerformanceMeasurement {
  name: string;
  startTime: number;
  end: () => number;
}

interface PerformanceMetric {
  name: string;
  duration: number;
  timestamp: number;
  type: 'performance' | 'interaction' | 'error';
}

interface PerformanceReport {
  totalMeasurements: number;
  averageRenderTime: number;
  averageInteractionTime: number;
  memoryUsage: MemoryUsage;
  timestamp: number;
}

interface MemoryUsage {
  used: number;
  total: number;
  limit: number;
}
```

---

## 🧪 Testing Strategy

### 1. Component Testing

```typescript
// __tests__/TreeVisualization.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TreeVisualization } from '@/components/tree/TreeVisualization';
import { mockTreeData } from '@/test-utils/mockData';

describe('TreeVisualization', () => {
  const defaultProps = {
    data: mockTreeData,
    width: 800,
    height: 600,
    onNodeClick: jest.fn(),
    onNodeHover: jest.fn()
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders tree structure correctly', async () => {
    render(<TreeVisualization {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('tree-svg')).toBeInTheDocument();
    });
    
    // Check if nodes are rendered
    const nodes = screen.getAllByTestId(/tree-node-/);
    expect(nodes).toHaveLength(mockTreeData.nodes.length);
  });
  
  test('handles node click interactions', async () => {
    render(<TreeVisualization {...defaultProps} />);
    
    await waitFor(() => {
      const firstNode = screen.getByTestId('tree-node-1');
      fireEvent.click(firstNode);
    });
    
    expect(defaultProps.onNodeClick).toHaveBeenCalledWith(
      expect.objectContaining({ id: '1' })
    );
  });
  
  test('handles zoom and pan operations', async () => {
    render(<TreeVisualization {...defaultProps} />);
    
    const svg = screen.getByTestId('tree-svg');
    
    // Simulate wheel event for zoom
    fireEvent.wheel(svg, { deltaY: -100 });
    
    await waitFor(() => {
      const treeGroup = screen.getByTestId('tree-group');
      expect(treeGroup).toHaveStyle(/transform: scale/);
    });
  });
  
  test('responds to data updates', async () => {
    const { rerender } = render(<TreeVisualization {...defaultProps} />);
    
    const updatedData = {
      ...mockTreeData,
      nodes: [...mockTreeData.nodes, { 
        id: 'new-node', 
        label: 'New Node', 
        type: 'skill',
        state: 'available'
      }]
    };
    
    rerender(<TreeVisualization {...defaultProps} data={updatedData} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('tree-node-new-node')).toBeInTheDocument();
    });
  });
  
  test('handles performance degradation gracefully', async () => {
    const largeDataset = {
      ...mockTreeData,
      nodes: Array.from({ length: 1000 }, (_, i) => ({
        id: `node-${i}`,
        label: `Node ${i}`,
        type: 'skill',
        state: 'available'
      }))
    };
    
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
    
    render(<TreeVisualization {...defaultProps} data={largeDataset} />);
    
    await waitFor(() => {
      // Should still render, but might log performance warnings
      expect(screen.getByTestId('tree-svg')).toBeInTheDocument();
    });
    
    consoleSpy.mockRestore();
  });
});
```

### 2. Integration Testing

```typescript
// __tests__/TreeSystem.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { CompetenceTreeD3 } from '@/components/tree/CompetenceTreeD3';
import { mockApiResponse } from '@/test-utils/mockApi';

// Mock API service
jest.mock('@/services/competenceTreeService', () => ({
  getTree: jest.fn(() => Promise.resolve(mockApiResponse)),
  completeNode: jest.fn(() => Promise.resolve({ success: true }))
}));

describe('Tree System Integration', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    });
  });
  
  test('complete user workflow: load tree, interact with nodes, complete challenge', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <CompetenceTreeD3 graphId="test-graph-1" />
      </QueryClientProvider>
    );
    
    // 1. Tree should load
    await waitFor(() => {
      expect(screen.getByTestId('tree-visualization')).toBeInTheDocument();
    });
    
    // 2. Click on a node to open modal
    const skillNode = screen.getByTestId('tree-node-skill-1');
    fireEvent.click(skillNode);
    
    await waitFor(() => {
      expect(screen.getByTestId('node-modal')).toBeInTheDocument();
    });
    
    // 3. Complete the node challenge
    const completeButton = screen.getByTestId('complete-node-button');
    fireEvent.click(completeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/completed/i)).toBeInTheDocument();
    });
    
    // 4. Verify node state updated in tree
    await waitFor(() => {
      const completedNode = screen.getByTestId('tree-node-skill-1');
      expect(completedNode).toHaveClass('node-completed');
    });
  });
  
  test('handles API errors gracefully', async () => {
    // Mock API failure
    require('@/services/competenceTreeService').getTree.mockRejectedValue(
      new Error('Network error')
    );
    
    render(
      <QueryClientProvider client={queryClient}>
        <CompetenceTreeD3 graphId="invalid-graph" />
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/error loading tree/i)).toBeInTheDocument();
    });
    
    // Should show retry button
    const retryButton = screen.getByText(/retry/i);
    expect(retryButton).toBeInTheDocument();
  });
});
```

---

## 📱 Accessibility Implementation

### 1. ARIA Support

```typescript
// components/tree/AccessibleTreeVisualization.tsx
export const AccessibleTreeVisualization: React.FC<TreeVisualizationProps> = ({
  data,
  selectedNodeId,
  onNodeSelect,
  onNodeActivate
}) => {
  
  const treeRef = useRef<HTMLDivElement>(null);
  
  // Generate accessible tree description
  const treeDescription = useMemo(() => {
    const totalNodes = data.nodes.length;
    const completedNodes = data.nodes.filter(n => n.state === 'completed').length;
    const availableNodes = data.nodes.filter(n => n.state === 'available').length;
    
    return `Interactive skill tree with ${totalNodes} nodes. ${completedNodes} completed, ${availableNodes} available to explore. Use arrow keys to navigate, Enter to select, Space to activate.`;
  }, [data]);
  
  return (
    <div 
      ref={treeRef}
      role="tree"
      aria-label="Competence Tree"
      aria-description={treeDescription}
      tabIndex={0}
      className="tree-visualization"
    >
      <div className="sr-only" aria-live="polite">
        {selectedNodeId && (
          <span>
            Selected: {data.nodes.find(n => n.id === selectedNodeId)?.label}
          </span>
        )}
      </div>
      
      {data.nodes.map(node => (
        <TreeNodeAccessible
          key={node.id}
          node={node}
          isSelected={selectedNodeId === node.id}
          onSelect={onNodeSelect}
          onActivate={onNodeActivate}
        />
      ))}
    </div>
  );
};

const TreeNodeAccessible: React.FC<{
  node: TreeNodeData;
  isSelected: boolean;
  onSelect: (nodeId: string) => void;
  onActivate: (nodeId: string) => void;
}> = ({ node, isSelected, onSelect, onActivate }) => {
  
  const nodeDescription = useMemo(() => {
    const parts = [
      `${node.type} node`,
      `Status: ${node.state}`,
      node.xp_reward ? `Reward: ${node.xp_reward} XP` : null,
      node.description || null
    ].filter(Boolean);
    
    return parts.join('. ');
  }, [node]);
  
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onActivate(node.id);
    }
  };
  
  return (
    <div
      role="treeitem"
      tabIndex={isSelected ? 0 : -1}
      aria-selected={isSelected}
      aria-label={node.label}
      aria-description={nodeDescription}
      onClick={() => onSelect(node.id)}
      onKeyDown={handleKeyDown}
      className={`tree-node ${isSelected ? 'selected' : ''} ${node.state}`}
    >
      <span className="node-label">{node.label}</span>
      {node.state === 'completed' && (
        <span className="sr-only">Completed</span>
      )}
      {node.state === 'locked' && (
        <span className="sr-only">Locked - prerequisites required</span>
      )}
    </div>
  );
};
```

### 2. Screen Reader Optimization

```typescript
// hooks/useScreenReaderSupport.ts
export const useScreenReaderSupport = (
  treeData: CompetenceTreeData,
  currentPath: string[]
) => {
  const [announcements, setAnnouncements] = useState<string[]>([]);
  
  const announceNavigation = useCallback((fromNodeId: string, toNodeId: string) => {
    const fromNode = treeData.nodes.find(n => n.id === fromNodeId);
    const toNode = treeData.nodes.find(n => n.id === toNodeId);
    
    if (!fromNode || !toNode) return;
    
    const relationship = getNodeRelationship(fromNode, toNode, treeData.edges);
    const announcement = `Moved from ${fromNode.label} to ${toNode.label}. ${relationship}`;
    
    setAnnouncements(prev => [...prev, announcement].slice(-5)); // Keep last 5
  }, [treeData]);
  
  const announcePathUpdate = useCallback((newPath: string[]) => {
    if (newPath.length === 0) return;
    
    const pathNodes = newPath.map(id => 
      treeData.nodes.find(n => n.id === id)?.label
    ).filter(Boolean);
    
    const announcement = `Current path: ${pathNodes.join(' leads to ')}`;
    setAnnouncements(prev => [...prev, announcement].slice(-5));
  }, [treeData]);
  
  const announceNodeCompletion = useCallback((nodeId: string) => {
    const node = treeData.nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const announcement = `${node.label} completed! ${node.xp_reward ? `Earned ${node.xp_reward} XP.` : ''}`;
    setAnnouncements(prev => [...prev, announcement].slice(-5));
  }, [treeData]);
  
  // Clear old announcements
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnnouncements([]);
    }, 10000);
    
    return () => clearTimeout(timer);
  }, [announcements]);
  
  return {
    announcements,
    announceNavigation,
    announcePathUpdate,
    announceNodeCompletion
  };
};

function getNodeRelationship(
  fromNode: TreeNodeData,
  toNode: TreeNodeData,
  edges: TreeEdge[]
): string {
  
  const isParent = edges.some(e => e.source === fromNode.id && e.target === toNode.id);
  const isChild = edges.some(e => e.source === toNode.id && e.target === fromNode.id);
  
  if (isParent) return `${toNode.label} is a child of ${fromNode.label}`;
  if (isChild) return `${toNode.label} is the parent of ${fromNode.label}`;
  
  return `${toNode.label} is a sibling of ${fromNode.label}`;
}
```

---

## 📋 Migration Implementation Guide

### 1. Phase-by-Phase Migration

```typescript
// Phase 1: Core D3.js Components
const PHASE_1_COMPONENTS = [
  'src/components/tree/d3/TreeVisualization.tsx',
  'src/components/tree/d3/hooks/useD3Tree.ts',
  'src/components/tree/d3/utils/treeLayout.ts',
  'src/hooks/useTreeData.ts'
];

// Phase 2: User Interactions
const PHASE_2_COMPONENTS = [
  'src/components/tree/d3/TreeControls.tsx',
  'src/components/tree/d3/NodeModal.tsx',
  'src/components/tree/d3/hooks/useTreeInteractions.ts'
];

// Phase 3: Performance & Polish
const PHASE_3_COMPONENTS = [
  'src/components/tree/d3/utils/performanceOptimizations.ts',
  'src/components/tree/d3/AccessibleTreeVisualization.tsx',
  'src/hooks/useResponsiveTree.ts'
];

// Files to be removed after migration
const DEPRECATED_FILES = [
  'src/components/tree/extreme/ExtremeCompetenceTreeView.tsx',
  'src/components/tree/extreme/WebGLTreeRenderer.tsx',
  'src/components/tree/extreme/UltraLightFallback.tsx',
  'src/components/tree/extreme/PerformanceTracker.ts',
  'src/components/tree/extreme/SpatialIndex.ts',
  'src/components/tree/extreme/WorkerManager.ts',
  'src/components/tree/extreme/ExtremeCache.ts',
  'src/components/tree/extreme/ThrottledEventHandler.ts',
  'src/components/tree/useCompetenceTree.ts'
];
```

### 2. Migration Utilities

```typescript
// utils/migration.ts
export class MigrationUtilities {
  static migrateTreeDataFormat(
    oldFormat: any
  ): CompetenceTreeData {
    // Convert old format to new standardized format
    return {
      nodes: oldFormat.nodes.map((node: any) => ({
        id: node.id,
        label: node.title || node.label,
        type: node.type || 'skill',
        depth: node.depth || 0,
        visible: node.visible !== false,
        revealed: node.revealed !== false,
        state: this.mapNodeState(node.status),
        challenge: node.challenge,
        xp_reward: node.xp_reward,
        metadata: node.metadata
      })),
      edges: oldFormat.edges.map((edge: any) => ({
        source: edge.from || edge.source,
        target: edge.to || edge.target,
        weight: edge.weight || 1,
        type: edge.type
      })),
      graph_id: oldFormat.graph_id || oldFormat.id,
      anchors: oldFormat.anchors || [],
      anchor_metadata: oldFormat.anchor_metadata
    };
  }
  
  private static mapNodeState(oldStatus: string): 'locked' | 'available' | 'completed' {
    const statusMap: { [key: string]: 'locked' | 'available' | 'completed' } = {
      'locked': 'locked',
      'disabled': 'locked',
      'available': 'available',
      'unlocked': 'available',
      'completed': 'completed',
      'finished': 'completed'
    };
    
    return statusMap[oldStatus] || 'available';
  }
  
  static validateMigration(
    originalData: any,
    migratedData: CompetenceTreeData
  ): MigrationValidationResult {
    const issues: string[] = [];
    
    // Check node count
    if (originalData.nodes.length !== migratedData.nodes.length) {
      issues.push(`Node count mismatch: ${originalData.nodes.length} -> ${migratedData.nodes.length}`);
    }
    
    // Check edge count
    if (originalData.edges.length !== migratedData.edges.length) {
      issues.push(`Edge count mismatch: ${originalData.edges.length} -> ${migratedData.edges.length}`);
    }
    
    // Check for missing required fields
    migratedData.nodes.forEach(node => {
      if (!node.id) issues.push(`Node missing ID: ${JSON.stringify(node)}`);
      if (!node.label) issues.push(`Node missing label: ${node.id}`);
    });
    
    return {
      isValid: issues.length === 0,
      issues,
      migrationScore: 1 - (issues.length / 10) // Rough quality score
    };
  }
}

interface MigrationValidationResult {
  isValid: boolean;
  issues: string[];
  migrationScore: number;
}
```

---

*Document Version: 1.0*  
*Last Updated: 2025-08-11*  
*Next Review: Implementation Phase 2*  
*Total Components: 15+ with comprehensive D3.js integration*  
*Estimated Development Time: 4-6 weeks*