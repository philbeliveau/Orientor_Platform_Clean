import { Node, Edge } from 'reactflow';

// Define the TreeNode interface that matches the backend schema
export interface TreeNode {
  id: string;
  label: string;
  type: "root" | "skill" | "outcome" | "career";
  level: number;
  actions?: string[];
  children?: TreeNode[];
}

// Define the node types for custom styling
export const NODE_TYPES = {
  root: 'rootNode',
  skill: 'skillNode',
  outcome: 'outcomeNode',
  career: 'careerNode',
};

// Map TreeNode types to ReactFlow node types
const nodeTypeMap: Record<TreeNode["type"], string> = {
  root: "rootNode",
  skill: "skillNode",
  outcome: "skillNode",
  career: "careerNode"
};

// Helper to convert the tree to ReactFlow nodes and edges
export function convertToFlowGraph(tree: TreeNode) {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  // Layout constants - optimized for compact layout
  const X_SPACING = 180; // Reduced horizontal spacing 
  const Y_SPACING = 120; // Reduced vertical spacing
  
  // Mapping to track node positions
  const nodePositions = new Map();
  
  // First pass: gather tree structure information
  function analyzeTree(node: TreeNode, depth = 0) {
    if (!node) return { width: 0, count: 0 };
    
    if (!node.children || node.children.length === 0) {
      return { width: X_SPACING, count: 1 };
    }
    
    let totalWidth = 0;
    let childCount = 0;
    
    node.children.forEach(child => {
      const { width, count } = analyzeTree(child, depth + 1);
      totalWidth += width;
      childCount += count;
    });
    
    // Ensure minimum width for nodes with few children
    return { 
      width: Math.max(totalWidth, X_SPACING), 
      count: Math.max(childCount, 1) 
    };
  }
  
  // Analyze the tree first
  const treeInfo = analyzeTree(tree);
  
  // Second pass: position nodes with balanced layout
  function processNode(
    node: TreeNode, 
    depth: number, 
    xOffset = 0, 
    parentId?: string, 
    siblingIndex = 0, 
    siblingCount = 1
  ) {
    if (!node) return { width: 0 };
    
    const id = node.id;
    
    // Calculate horizontal position - center node relative to its children
    let nodeX = xOffset;
    
    // Create node with appropriate type and data
    nodes.push({
      id,
      type: NODE_TYPES[node.type],
      data: { 
        label: node.label, 
        actions: node.actions,
        nodeType: node.type,
      },
      position: { x: nodeX, y: depth * Y_SPACING },
      draggable: true, // Allow nodes to be dragged 
    });
    
    // Record node position for edge creation
    nodePositions.set(id, { x: nodeX, y: depth * Y_SPACING });
    
    // Create edge from parent to this node
    if (parentId) {
      edges.push({
        id: `${parentId}-${id}`,
        source: parentId,
        target: id,
        type: 'smoothstep',
        animated: true,
        style: { 
          stroke: '#94a3b8',
          strokeWidth: 1.5,
          strokeDasharray: '6 3',
        },
      });
    }
    
    if (!node.children || node.children.length === 0) {
      return { width: X_SPACING };
    }
    
    // Determine width needed for all children
    const childCount = node.children.length;
    let childTotalWidth = 0;
    
    // First compute total required width
    node.children.forEach(child => {
      const analysis = analyzeTree(child);
      childTotalWidth += analysis.width;
    });
    
    // Apply compact positioning for children
    let currentChildX = nodeX - (childTotalWidth / 2) + (X_SPACING / 2);
    
    node.children.forEach((child, index) => {
      const childInfo = processNode(
        child, 
        depth + 1, 
        currentChildX, 
        id, 
        index, 
        childCount
      );
      
      // Move to next child position
      currentChildX += childInfo.width;
    });
    
    return { width: Math.max(childTotalWidth, X_SPACING) };
  }
  
  // Process the tree
  processNode(tree, 0);
  
  return { nodes, edges };
}

// Premium Node Styling (matching frontend premium upgrade)
export function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return {
        background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)', // Indigo gradient
        color: 'white',
        borderRadius: '20px',
        padding: '20px',
        fontSize: '16px',
        fontWeight: 600,
        boxShadow: '0 8px 24px rgba(99, 102, 241, 0.3)',
      };
    case 'skill':
      return {
        background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', // Cyan/blue gradient
        color: 'white',
        borderRadius: '16px',
        padding: '18px',
        fontSize: '14px',
        fontWeight: 500,
        boxShadow: '0 6px 18px rgba(59, 130, 246, 0.2)',
      };
    case 'outcome':
      return {
        background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)', // Green gradient
        color: 'white',
        borderRadius: '16px',
        padding: '18px',
        fontSize: '15px',
        fontWeight: 600,
        boxShadow: '0 6px 18px rgba(16, 185, 129, 0.25)',
      };
    case 'career':
      return {
        background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)', // Gold gradient
        color: 'white',
        borderRadius: '16px',
        padding: '16px',
        fontSize: '13px',
        fontWeight: 500,
        boxShadow: '0 6px 18px rgba(245, 158, 11, 0.25)',
      };
    default:
      return {
        background: '#9ca3af', // Neutral fallback
        color: 'white',
        borderRadius: '12px',
        padding: '16px',
      };
  }
}
