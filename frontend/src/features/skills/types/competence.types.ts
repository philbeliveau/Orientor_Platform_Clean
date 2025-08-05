// Competence Tree Types
export interface CompetenceNode {
  id: string;
  skill_id?: string;
  skill_label?: string;
  label?: string;
  type?: string;
  challenge?: string;
  xp_reward?: number;
  visible?: boolean;
  revealed?: boolean;
  state?: 'locked' | 'available' | 'completed' | 'hidden';
  notes?: string;
  is_anchor?: boolean;
  depth?: number;
  metadata?: any;
}

export interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string; weight?: number; type?: string }[];
  graph_id: string;
}

export interface PositionedNode extends CompetenceNode {
  x: number;
  y: number;
}

export interface NodeStyles {
  primary: string;
  secondary: string;
  text: string;
  border: string;
  shadow: string;
}

export interface TreeNodeProps {
  node: PositionedNode;
  onComplete: (nodeId: string) => void;
  onNodeClick: (node: PositionedNode) => void;
  isSaved?: boolean;
}