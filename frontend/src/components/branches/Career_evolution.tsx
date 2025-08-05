'use client';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  Position,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';
import { MarkerType } from 'reactflow';

function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg';
    case 'outcome':
      return 'bg-white text-gray-800 border border-gray-300 shadow-md';
    default:
      return 'bg-gradient-to-r from-sky-700 to-sky-900 text-white shadow-md group relative';
  }
}

interface TechNode {
  id: string;
  skillDescription: string;
  improvementSuggestion?: string;
  taskSuggestion?: string;
  nextSkills?: TechNode[];
  reachableJobs?: { jobTitle: string; jobDomain: string }[];
}

function convertToFlowGraph(root: TechNode): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const yGap = 250;
  const xGap = 300;

  const queue: { node: TechNode; depth: number; column: number; parentId?: string; type?: string }[] = [
    { node: root, depth: 0, column: 2, type: 'root' },
  ];

  while (queue.length > 0) {
    const { node, depth, column, parentId, type = 'skill' } = queue.shift()!;
    const id = node.id;
    const position = { x: column * xGap, y: depth * yGap };

    nodes.push({
      id,
      type: 'default',
      position,
      data: {
        label: (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className={`text-sm font-medium text-center rounded-xl px-4 py-3 ${getNodeStyle(type)}`}
          >
            {node.skillDescription}
            {node.improvementSuggestion && (
              <div className="text-xs italic mt-2 text-white/80">
                {node.improvementSuggestion}
              </div>
            )}
            {node.taskSuggestion && (
              <div className="absolute hidden group-hover:block text-[11px] bg-black/90 text-white px-2 py-1 rounded bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap z-50">
                💡 {node.taskSuggestion}
              </div>
            )}
          </motion.div>
        ),
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    });

    if (parentId) {
      edges.push({
        id: `${parentId}-${id}`,
        source: parentId,
        target: id,
        animated: true,
        type: 'smoothstep',
        style: { stroke: '#6b7280' },
        markerEnd: { type: 'arrowclosed' as MarkerType },
      });
    }

    node.nextSkills?.forEach((child, index) => {
      queue.push({
        node: child,
        depth: depth + 1,
        column: column + index - Math.floor((node.nextSkills?.length ?? 1) / 2),
        parentId: id,
      });
    });

    if (node.reachableJobs) {
      const jobId = `${id}-outcome`;
      nodes.push({
        id: jobId,
        type: 'default',
        position: { x: position.x, y: position.y + 200 },
        data: {
          label: (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className={`rounded-xl px-4 py-3 text-sm text-center ${getNodeStyle('outcome')}`}
            >
              <strong className="text-md font-semibold">Career Path</strong>
              <div className="mt-1">
                {node.reachableJobs.map((j) => (
                  <div key={j.jobTitle} className="text-xs text-gray-600">
                    {j.jobTitle} in {j.jobDomain}
                  </div>
                ))}
              </div>
            </motion.div>
          ),
        },
        sourcePosition: Position.Top,
        targetPosition: Position.Bottom,
      });

      edges.push({
        id: `${id}-${jobId}`,
        source: id,
        target: jobId,
        type: 'smoothstep',
        style: { stroke: '#d1d5db', strokeDasharray: '4 2' },
        markerEnd: { type: 'arrowclosed' as MarkerType },
      });
    }
  }

  return { nodes, edges };
}

const root: TechNode = {
  id: 'start',
  skillDescription: 'Excel + SQL user in Finance Ops',
  nextSkills: [
    {
      id: 'python',
      skillDescription: 'Basic Python + pandas for data cleaning',
      taskSuggestion: 'Automate Excel reports with Python scripts',
      nextSkills: [
        {
          id: 'dash',
          skillDescription: 'Dash/Streamlit for internal tools',
          taskSuggestion: 'Learn scikit-learn for basic machine learning',
          reachableJobs: [
            { jobTitle: 'Junior Data Analyst', jobDomain: 'Analytics' },
          ],
        },
        {
          id: 'sklearn',
          skillDescription: 'Learn scikit-learn for regression and classification',
          taskSuggestion: 'Build models on historical sales data',
          reachableJobs: [
            { jobTitle: 'Data Scientist', jobDomain: 'Machine Learning' },
          ],
        },
      ],
    },
    {
      id: 'dash',
      skillDescription: 'Dash/Streamlit for internal tools',
      taskSuggestion: 'Create dashboards to explore data',
      nextSkills: [
        {
          id: 'dashboards-sql',
          skillDescription: 'interactive dashboards + advanced SQL queries',
          taskSuggestion: 'Design real-time dashboards for business metrics',
          reachableJobs: [
            { jobTitle: 'Business Intelligence Analyst', jobDomain: 'Analytics & Reporting' },
            { jobTitle: 'Product Analyst', jobDomain: 'Tech & Product Teams' },
          ],
        }
      ],
      reachableJobs: [
        { jobTitle: 'Junior Data Analyst', jobDomain: 'Analytics' },
      ],
    },
    {
      id: 'python',
      skillDescription: 'Basic Python + pandas for data cleaning',
      taskSuggestion: 'Automate Excel reports with Python scripts',
      nextSkills: [
        {
          id: 'dash',
          skillDescription: 'Dash/Streamlit for internal tools',
          taskSuggestion: 'Create dashboards to explore data',
          reachableJobs: [
            { jobTitle: 'Junior Data Analyst', jobDomain: 'Analytics' },
          ],
        },
      ],
    },
    {
      id: 'valuation',
      skillDescription: 'Advanced Excel: modeling + DCF',
      taskSuggestion: 'Audit valuation models',
      nextSkills: [
        {
          id: 'python-finance',
          skillDescription: 'Python for finance (yfinance, quantlib)',
          taskSuggestion: 'Automate company screening',
          reachableJobs: [
            { jobTitle: 'Equity Research Analyst', jobDomain: 'Investment Banking' },
          ],
        },
        {
          id: 'dealmaking',
          skillDescription: 'Pitchbook + CIMs + CapIQ fluency',
          taskSuggestion: 'Draft summary for pitch deck',
          reachableJobs: [
            { jobTitle: 'Investment Banking Analyst', jobDomain: 'M&A' },
          ],
        },
      ],
    },
  ],
};

export default function CareerTechTree() {
  const { nodes, edges } = convertToFlowGraph(root);
  
  // Calculate the bounds of the graph
  const minX = Math.min(...nodes.map(node => node.position.x)) - 100;
  const maxX = Math.max(...nodes.map(node => node.position.x + 200)) + 100;
  const minY = Math.min(...nodes.map(node => node.position.y)) - 100;
  const maxY = Math.max(...nodes.map(node => node.position.y + 250)) + 100;
  
  const width = maxX - minX;
  const height = maxY - minY;

  return (
    <div style={{ 
      width: '100%', 
      height: '80vh',
      maxHeight: '800px',
      overflow: 'hidden',
      borderRadius: '12px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }}>
      <ReactFlowProvider>
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          fitView 
          panOnScroll 
          zoomOnScroll 
          fitViewOptions={{ padding: 0.2, maxZoom: 1.5 }}
          minZoom={0.2}
          maxZoom={1.5}
          translateExtent={[[minX, minY], [maxX, maxY]]} // This limits the pan area
        >
          <MiniMap nodeStrokeWidth={3} zoomable pannable />
          <Background color="#f3f4f6" gap={24} />
          <Controls showInteractive={false} position="bottom-right" />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
