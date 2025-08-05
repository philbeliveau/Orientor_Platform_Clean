import { CompetenceNode, PositionedNode } from './types';

interface Edge {
  source: string;
  target: string;
  weight?: number;
}

export class TreeLayoutAlgorithm {
  private nodes: CompetenceNode[];
  private edges: Edge[];
  private nodeMap: Map<string, CompetenceNode>;
  private adjacencyList: Map<string, string[]>;
  private levels: Map<string, number>;
  private positions: Map<string, { x: number; y: number }>;

  constructor(nodes: CompetenceNode[], edges: Edge[]) {
    this.nodes = nodes;
    this.edges = edges;
    this.nodeMap = new Map(nodes.map(n => [n.id, n]));
    this.adjacencyList = new Map();
    this.levels = new Map();
    this.positions = new Map();
    this.buildAdjacencyList();
  }

  private buildAdjacencyList() {
    // Initialize adjacency list
    this.nodes.forEach(node => {
      this.adjacencyList.set(node.id, []);
    });

    // Build adjacency list from edges
    this.edges.forEach(edge => {
      const neighbors = this.adjacencyList.get(edge.source) || [];
      neighbors.push(edge.target);
      this.adjacencyList.set(edge.source, neighbors);
    });
  }

  private calculateLevels() {
    // BFS to assign levels
    const visited = new Set<string>();
    const queue: { id: string; level: number }[] = [];

    // Find root nodes (nodes with no incoming edges)
    const hasIncoming = new Set(this.edges.map(e => e.target));
    const roots = this.nodes.filter(n => !hasIncoming.has(n.id));

    // Start BFS from root nodes
    roots.forEach(root => {
      queue.push({ id: root.id, level: 0 });
      this.levels.set(root.id, 0);
      visited.add(root.id);
    });

    while (queue.length > 0) {
      const { id, level } = queue.shift()!;
      const neighbors = this.adjacencyList.get(id) || [];

      neighbors.forEach(neighborId => {
        if (!visited.has(neighborId)) {
          visited.add(neighborId);
          this.levels.set(neighborId, level + 1);
          queue.push({ id: neighborId, level: level + 1 });
        }
      });
    }

    // Handle disconnected nodes
    this.nodes.forEach(node => {
      if (!visited.has(node.id)) {
        this.levels.set(node.id, 0);
      }
    });
  }

  private forceDirectedLayout(): PositionedNode[] {
    const iterations = 100;
    const k = 150; // Ideal spring length
    const c = 0.1; // Spring constant
    const damping = 0.9;

    // Initialize random positions
    this.nodes.forEach(node => {
      this.positions.set(node.id, {
        x: Math.random() * 800 - 400,
        y: Math.random() * 600 - 300
      });
    });

    // Force-directed iterations
    for (let iter = 0; iter < iterations; iter++) {
      const forces = new Map<string, { fx: number; fy: number }>();

      // Initialize forces
      this.nodes.forEach(node => {
        forces.set(node.id, { fx: 0, fy: 0 });
      });

      // Repulsive forces between all nodes
      for (let i = 0; i < this.nodes.length; i++) {
        for (let j = i + 1; j < this.nodes.length; j++) {
          const node1 = this.nodes[i];
          const node2 = this.nodes[j];
          const pos1 = this.positions.get(node1.id)!;
          const pos2 = this.positions.get(node2.id)!;

          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          const repulsion = (k * k) / distance;
          const fx = (dx / distance) * repulsion;
          const fy = (dy / distance) * repulsion;

          const force1 = forces.get(node1.id)!;
          const force2 = forces.get(node2.id)!;

          force1.fx -= fx;
          force1.fy -= fy;
          force2.fx += fx;
          force2.fy += fy;
        }
      }

      // Attractive forces along edges
      this.edges.forEach(edge => {
        const pos1 = this.positions.get(edge.source);
        const pos2 = this.positions.get(edge.target);

        if (pos1 && pos2) {
          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          const attraction = c * (distance - k);
          const fx = (dx / distance) * attraction;
          const fy = (dy / distance) * attraction;

          const force1 = forces.get(edge.source)!;
          const force2 = forces.get(edge.target)!;

          force1.fx += fx;
          force1.fy += fy;
          force2.fx -= fx;
          force2.fy -= fy;
        }
      });

      // Apply forces with damping
      this.nodes.forEach(node => {
        const pos = this.positions.get(node.id)!;
        const force = forces.get(node.id)!;

        pos.x += force.fx * damping;
        pos.y += force.fy * damping;
      });
    }

    // Convert to positioned nodes
    return this.nodes.map(node => ({
      ...node,
      ...this.positions.get(node.id)!
    }));
  }

  private hierarchicalLayout(): PositionedNode[] {
    this.calculateLevels();

    // Group nodes by level
    const levelGroups = new Map<number, CompetenceNode[]>();
    this.nodes.forEach(node => {
      const level = this.levels.get(node.id) || 0;
      const group = levelGroups.get(level) || [];
      group.push(node);
      levelGroups.set(level, group);
    });

    // Calculate positions
    const levelHeight = 150;
    const nodeSpacing = 120;

    levelGroups.forEach((nodes, level) => {
      const totalWidth = (nodes.length - 1) * nodeSpacing;
      const startX = -totalWidth / 2;

      nodes.forEach((node, index) => {
        this.positions.set(node.id, {
          x: startX + index * nodeSpacing,
          y: level * levelHeight
        });
      });
    });

    // Apply force-directed adjustments within levels
    const iterations = 20;
    for (let iter = 0; iter < iterations; iter++) {
      levelGroups.forEach((nodes, level) => {
        // Apply repulsive forces within the same level
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const pos1 = this.positions.get(nodes[i].id)!;
            const pos2 = this.positions.get(nodes[j].id)!;

            const dx = pos2.x - pos1.x;
            const distance = Math.abs(dx) || 1;

            if (distance < nodeSpacing) {
              const repulsion = (nodeSpacing - distance) / 2;
              pos1.x -= Math.sign(dx) * repulsion;
              pos2.x += Math.sign(dx) * repulsion;
            }
          }
        }
      });
    }

    return this.nodes.map(node => ({
      ...node,
      ...this.positions.get(node.id)!
    }));
  }

  public layout(algorithm: 'force' | 'hierarchical' = 'hierarchical'): PositionedNode[] {
    if (algorithm === 'force') {
      return this.forceDirectedLayout();
    } else {
      return this.hierarchicalLayout();
    }
  }
}

export const calculateNodePositions = (
  nodes: CompetenceNode[],
  edges: Edge[],
  algorithm: 'force' | 'hierarchical' = 'hierarchical'
): PositionedNode[] => {
  const layoutEngine = new TreeLayoutAlgorithm(nodes, edges);
  return layoutEngine.layout(algorithm);
};