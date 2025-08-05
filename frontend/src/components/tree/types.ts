// Types for competence tree components

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

export interface TreeViewport {
  x: number;
  y: number;
  zoom: number;
}