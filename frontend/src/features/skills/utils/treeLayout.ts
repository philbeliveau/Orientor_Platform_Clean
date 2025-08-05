import { CompetenceNode, PositionedNode } from '../types/competence.types';

interface LayoutConfig {
  centerX: number;
  centerY: number;
  anchorRadius: number;
  levelRadius: number;
  maxLevels: number;
}

// Default layout configuration
const getDefaultConfig = (): LayoutConfig => ({
  centerX: typeof window !== 'undefined' ? Math.max(1600, window.innerWidth * 0.75) : 1600,
  centerY: typeof window !== 'undefined' ? Math.max(1100, window.innerHeight * 0.75) : 1100,
  anchorRadius: typeof window !== 'undefined' ? Math.max(600, window.innerWidth * 0.3) : 600,
  levelRadius: typeof window !== 'undefined' ? Math.max(800, window.innerWidth * 0.4) : 800,
  maxLevels: 5
});

// Build adjacency and parent maps from edges
const buildGraphMaps = (
  edges: { source: string; target: string }[], 
  visibleNodes: CompetenceNode[]
) => {
  const adjacencyMap = new Map<string, string[]>();
  const parentMap = new Map<string, string>();
  
  edges.forEach(edge => {
    const sourceVisible = visibleNodes.find(n => n.id === edge.source);
    const targetVisible = visibleNodes.find(n => n.id === edge.target);
    
    if (sourceVisible && targetVisible) {
      if (!adjacencyMap.has(edge.source)) {
        adjacencyMap.set(edge.source, []);
      }
      adjacencyMap.get(edge.source)!.push(edge.target);
      parentMap.set(edge.target, edge.source);
    }
  });
  
  return { adjacencyMap, parentMap };
};

// Position anchor nodes in a circle
const positionAnchors = (anchors: CompetenceNode[], config: LayoutConfig): PositionedNode[] => {
  return anchors.map((anchor, index) => {
    const angle = (2 * Math.PI * index) / anchors.length;
    return {
      ...anchor,
      x: config.centerX + config.anchorRadius * Math.cos(angle),
      y: config.centerY + config.anchorRadius * Math.sin(angle),
      depth: 0
    };
  });
};

// Build tree hierarchy from anchors
const buildTreeHierarchy = (
  anchors: CompetenceNode[],
  adjacencyMap: Map<string, string[]>,
  visibleNodes: CompetenceNode[],
  maxLevels: number
) => {
  const treeHierarchy = new Map<number, CompetenceNode[]>();
  const processedNodes = new Set<string>();
  
  // Level 0: Anchors
  treeHierarchy.set(0, anchors);
  anchors.forEach(anchor => processedNodes.add(anchor.id));
  
  // Build subsequent levels
  for (let currentLevel = 0; currentLevel < maxLevels - 1; currentLevel++) {
    const currentLevelNodes = treeHierarchy.get(currentLevel) || [];
    const nextLevelNodes: CompetenceNode[] = [];
    
    currentLevelNodes.forEach(parent => {
      const children = (adjacencyMap.get(parent.id) || [])
        .map(childId => visibleNodes.find(n => n.id === childId))
        .filter(child => child && !processedNodes.has(child.id)) as CompetenceNode[];
      
      children.forEach(child => {
        if (child && !processedNodes.has(child.id)) {
          nextLevelNodes.push({ ...child, depth: currentLevel + 1 });
          processedNodes.add(child.id);
        }
      });
    });
    
    if (nextLevelNodes.length > 0) {
      treeHierarchy.set(currentLevel + 1, nextLevelNodes);
    } else {
      break;
    }
  }
  
  return { treeHierarchy, processedNodes };
};

// Position nodes by level with parent-child relationships
const positionNodesByLevel = (
  treeHierarchy: Map<number, CompetenceNode[]>,
  parentMap: Map<string, string>,
  positioned: PositionedNode[],
  config: LayoutConfig
): PositionedNode[] => {
  const newPositioned: PositionedNode[] = [];
  
  for (let level = 1; level < config.maxLevels; level++) {
    const levelNodes = treeHierarchy.get(level) || [];
    const baseRadius = config.levelRadius + (level - 1) * (config.levelRadius * 0.75);
    
    // Group nodes by parent
    const nodesByParent = new Map<string, CompetenceNode[]>();
    levelNodes.forEach(node => {
      const parent = parentMap.get(node.id);
      if (parent) {
        if (!nodesByParent.has(parent)) {
          nodesByParent.set(parent, []);
        }
        nodesByParent.get(parent)!.push(node);
      }
    });
    
    // Position children around their parent
    nodesByParent.forEach((children, parentId) => {
      const parent = positioned.find(p => p.id === parentId);
      if (!parent) return;
      
      const parentAngle = Math.atan2(parent.y - config.centerY, parent.x - config.centerX);
      
      if (children.length === 1) {
        const child = children[0];
        newPositioned.push({
          ...child,
          x: config.centerX + baseRadius * Math.cos(parentAngle),
          y: config.centerY + baseRadius * Math.sin(parentAngle)
        });
      } else {
        const spreadAngle = Math.PI / 2;
        const angleStep = spreadAngle / Math.max(children.length - 1, 1);
        
        children.forEach((child, index) => {
          const childAngle = parentAngle - spreadAngle / 2 + angleStep * index;
          newPositioned.push({
            ...child,
            x: config.centerX + baseRadius * Math.cos(childAngle),
            y: config.centerY + baseRadius * Math.sin(childAngle)
          });
        });
      }
    });
  }
  
  return newPositioned;
};

// Position orphaned nodes
const positionOrphanedNodes = (
  visibleNodes: CompetenceNode[],
  positioned: PositionedNode[],
  config: LayoutConfig
): PositionedNode[] => {
  const orphanedNodes = visibleNodes.filter(
    node => !positioned.find(p => p.id === node.id)
  );
  
  if (orphanedNodes.length === 0) return [];
  
  const currentLevel = Math.max(...positioned.map(n => n.depth || 0)) + 1;
  const outerRadius = config.levelRadius + currentLevel * (config.levelRadius * 0.75);
  
  return orphanedNodes.map((node, index) => {
    const angle = (2 * Math.PI * index) / orphanedNodes.length;
    return {
      ...node,
      x: config.centerX + outerRadius * Math.cos(angle),
      y: config.centerY + outerRadius * Math.sin(angle),
      depth: currentLevel
    };
  });
};

// Main layout calculation function
export const calculateRadialTreeLayout = (
  nodes: CompetenceNode[], 
  edges: { source: string; target: string }[]
): PositionedNode[] => {
  const config = getDefaultConfig();
  const positioned: PositionedNode[] = [];
  
  // Filter visible nodes
  const visibleNodes = nodes.filter(n => n.visible !== false);
  const anchors = visibleNodes.filter(n => n.is_anchor);
  const nonAnchors = visibleNodes.filter(n => !n.is_anchor);
  
  // Build graph structure
  const { adjacencyMap, parentMap } = buildGraphMaps(edges, visibleNodes);
  
  // Position anchor nodes
  const positionedAnchors = positionAnchors(anchors, config);
  positioned.push(...positionedAnchors);
  
  // Build and position tree hierarchy
  const { treeHierarchy, processedNodes } = buildTreeHierarchy(
    anchors,
    adjacencyMap,
    visibleNodes,
    config.maxLevels
  );
  
  const positionedByLevel = positionNodesByLevel(
    treeHierarchy,
    parentMap,
    positioned,
    config
  );
  positioned.push(...positionedByLevel);
  
  // Position orphaned nodes
  const orphaned = positionOrphanedNodes(visibleNodes, positioned, config);
  positioned.push(...orphaned);
  
  return positioned;
};