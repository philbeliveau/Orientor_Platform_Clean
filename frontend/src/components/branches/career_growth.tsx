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
import { SkillNode } from '@/components/branches/career_growth_skill';
import { MarkerType } from 'reactflow';

function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return 'bg-gradient-to-r from-amber-600 to-yellow-400 text-white shadow-lg';
    case 'outcome':
      return 'bg-white text-gray-800 border border-gray-300 shadow-md';
    default:
      return 'bg-gradient-to-r from-gray-700 to-gray-900 text-white shadow-md group relative';
  }
}

function convertToFlowGraph(root: SkillNode): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const yGap = 350;
  const xGap = 300;
  const skillMap: Record<string, { x: number, y: number }> = {};

  const queue: { node: SkillNode; depth: number; column: number; parentId?: string; type?: string }[] = [
    { node: root, depth: 0, column: 2, type: 'root' },
  ];

  while (queue.length > 0) {
    const { node, depth, column, parentId, type = 'skill' } = queue.shift()!;
    const id = node.id;
    const position = { x: column * xGap, y: depth * yGap };

    skillMap[id] = position;

    nodes.push({
      id,
      type: 'default',
      position,
      draggable: true,
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
        markerEnd: {
          type: 'arrowclosed' as MarkerType,
        },
      });
    }

    node.nextSkills?.forEach((child: SkillNode, index: number) => {
      const verticalNudge = child.reachableJobs?.length ? 0.3 : 0; // offset if outcome will push it down visually
      queue.push({
        node: child,
        depth: depth + 1 + verticalNudge,
        column: column + index - Math.floor((node.nextSkills?.length ?? 1) / 2),
        parentId: id,
      });
    });

    if (node.reachableJobs?.length) {
      const jobId = `${id}-outcome`;
      const metaSkillId = `${id}-meta-skill`;
      const finalId = `${id}-final-outcome`;

      // const jobY = position.y + 150;
      const siblingOffset = (node.id.endsWith('-1') ? -1 : node.id.endsWith('-x') ? 1 : 0) * 60;
      const jobY = position.y + 180 + siblingOffset;
      const metaY = jobY + 100;
      const finalY = metaY + 100;

      nodes.push({
        id: jobId,
        type: 'default',
        position: { x: position.x, y: jobY },
        draggable: true,
        data: {
          label: (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className={`rounded-xl px-4 py-3 text-sm text-center ${getNodeStyle('outcome')}`}
            >
              <strong className="text-md font-semibold">Outcome</strong>
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
        markerEnd: {
          type: 'arrowclosed' as MarkerType,
        },
      });

      if (node.nextSkills?.length) {
        edges.push({
          id: `${jobId}-${metaSkillId}`,
          source: jobId,
          target: metaSkillId,
          type: 'smoothstep',
          markerEnd: {
            type: 'arrowclosed' as MarkerType,
          },
        });

        edges.push({
          id: `${metaSkillId}-${finalId}`,
          source: metaSkillId,
          target: finalId,
          type: 'smoothstep',
          markerEnd: {
            type: 'arrowclosed' as MarkerType,
          },
        });
      }
    }

    // 🧠 NEW: auto-detect and link similar skills across paths
    for (const targetId in skillMap) {
      if (targetId !== id && node.skillDescription === nodes.find(n => n.id === targetId)?.data?.label?.props?.children?.[0]) {
        edges.push({
          id: `${id}-nudge-${targetId}`,
          source: id,
          target: targetId,
          type: 'step',
          animated: true,
          style: { stroke: '#4ade80', strokeDasharray: '2 2' },
          markerEnd: { type: 'arrowclosed' as MarkerType },
        });
      }
    }
  }
  return { nodes, edges };
}
const root: SkillNode = {
  id: 'root',
  skillDescription: 'You’re just starting to explore. You’re curious—and that’s powerful.',
  nextSkills: [
    {
      id: 's1',
      skillDescription: 'You listen and support others',
      improvementSuggestion: 'Practice noticing and validating people’s feelings',
      taskSuggestion: 'Organize a peer support activity at school or online',
      nextSkills: [
        {
          id: 's1-1',
          skillDescription: 'You take initiative when others need it',
          taskSuggestion: 'Coordinate a mental wellness week or empathy circle',
          reachableJobs: [
            { jobTitle: 'Trusted Friend', jobDomain: 'People & Emotions', requiredSkills: [] },
            { jobTitle: 'Go-To Listener', jobDomain: 'Support & Empathy', requiredSkills: [] },
          ],
        }
      ]
    },
    {
      id: 's2',
      skillDescription: 'You stay sharp under pressure',
      improvementSuggestion: 'Find moments of calm while being active',
      taskSuggestion: 'Join a first aid or crisis simulation workshop',
      nextSkills: [
        {
          id: 's2-1',
          skillDescription: 'You act quickly and think clearly in urgent moments',
          taskSuggestion: 'Help lead a safety or preparedness event',
          reachableJobs: [
            { jobTitle: 'Calm-in-the-Storm', jobDomain: 'Urgent Situations', requiredSkills: [] },
            { jobTitle: 'Fast Thinker', jobDomain: 'Quick Action', requiredSkills: [] }
          ],
        }
      ]
    },
    {
      id: 's3',
      skillDescription: 'You express yourself clearly',
      improvementSuggestion: 'Experiment with different ways to explain your thoughts',
      taskSuggestion: 'Host a lunch & learn on a topic that excites you',
      nextSkills: [
        {
          id: 's3-1',
          skillDescription: 'You adapt your message for different people',
          taskSuggestion: 'interview people and present what you learned in a visual way',
          reachableJobs: [
            { jobTitle: 'Clear Speaker', jobDomain: 'Ideas & Expression', requiredSkills: [] },
            { jobTitle: 'Learning Spark', jobDomain: 'Group Learning', requiredSkills: [] },
          ]
        },
        {
          id: 's3-x',
          skillDescription: 'You communicate in moments that matter',
          taskSuggestion: 'Design instructions or communication for a group under pressure',
          reachableJobs: [
            { jobTitle: 'Calm Voice', jobDomain: 'Critical Communication', requiredSkills: [] }
          ]
        }
      ]
    },
    {
      id: 's4',
      skillDescription: 'You write with clarity and meaning',
      improvementSuggestion: 'Refine your writing by asking for feedback',
      taskSuggestion: 'Write 3 posts on a theme that matters to you and share them',
      nextSkills: [
        {
          id: 's4-1',
          skillDescription: 'You shape your ideas to influence and inform others',
          taskSuggestion: 'Participate in a youth debate or writing contest',
          reachableJobs: [
            { jobTitle: 'Thought Sharer', jobDomain: 'Writing & Media', requiredSkills: [] },
            { jobTitle: 'Idea Organizer', jobDomain: 'Clarity & Knowledge', requiredSkills: [] },
          ],
          nextSkills: [
            {
              id: 's4-1-a',
              skillDescription: 'You tell stories that move people to act',
              taskSuggestion: 'Create a campaign with a message you care about',
              reachableJobs: [
                { jobTitle: 'Voice for a Cause', jobDomain: 'Social Impact', requiredSkills: [] },
              ]
            },
            {
              id: 's4-1-b',
              skillDescription: 'You make complicated things easy to grasp',
              taskSuggestion: 'Write an illustrated how-to or zine on something technical',
              reachableJobs: [
                { jobTitle: 'Explainer-in-Chief', jobDomain: 'Learning Design', requiredSkills: [] },
              ]
            }
          ]
        }
      ]
    }
  ]
};


export default function SkillTreeFlow() {
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
