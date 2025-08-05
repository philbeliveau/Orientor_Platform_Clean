import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ConnectionLineType,
  Panel,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { SkillNode, OutcomeNode, RootNode } from './CustomNodes';
import { motion } from 'framer-motion';
import { careerTreeService, CareerTreeNode } from '../../services/careerTreeService';
import { convertToFlowGraph, TreeNode } from '../../utils/convertToFlowGraph';
import { saveTreePath, getTreePath } from '../../utils/treeStorage';
import XPProgress from '../ui/XPProgress';
import { useSearchParams } from 'next/navigation';
import LoadingScreen from '@/components/ui/LoadingScreen';

// Define custom node types
const nodeTypes: NodeTypes = {
  rootNode: RootNode,
  skillNode: SkillNode,
  outcomeNode: OutcomeNode,
};

// Animation variants for the title
const titleVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { 
    opacity: 1, 
    y: 0, 
    transition: { 
      duration: 0.8, 
      ease: "easeOut" as const
    } 
  }
};

// Default profile placeholder text
const PROFILE_PLACEHOLDER = `Tell us about your interests and aspirations.
For example:
- What subjects do you enjoy?
- What skills are you good at?
- What careers are you curious about?`;

// Convert CareerTreeNode to TreeNode
function convertCareerToTreeNode(careerNode: CareerTreeNode): TreeNode {
  let nodeType: "root" | "skill" | "outcome";
  
  // Map career node types to TreeNode types
  switch (careerNode.type) {
    case "root":
      nodeType = "root";
      break;
    case "domain":
      nodeType = "outcome";
      break;
    case "family":
      nodeType = "skill";
      break;
    case "skill":
      nodeType = "skill";
      break;
    default:
      nodeType = "skill"; // Default fallback
  }
  
  return {
    id: careerNode.id,
    label: careerNode.label,
    type: nodeType,
    level: careerNode.level || 0,
    actions: careerNode.actions,
    children: careerNode.children?.map(child => convertCareerToTreeNode(child))
  };
}

export default function CareerTree() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isCareerPathVisible, setIsCareerPathVisible] = useState(true); // State to manage visibility
  const searchParams = useSearchParams();
  const treeId = searchParams?.get('treeId') || null;

  // Load saved tree if treeId is provided
  useEffect(() => {
    const loadSavedTree = async () => {
      if (!treeId) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        console.log('Loading tree with ID:', treeId);
        const savedTree = await getTreePath(treeId);
        console.log('Loaded tree data:', savedTree);
        
        if (savedTree && savedTree.tree_json) {
          // Convert tree data to ReactFlow format
          const { nodes: treeNodes, edges: treeEdges } = convertToFlowGraph(savedTree.tree_json);
          setNodes(treeNodes);
          setEdges(treeEdges);
          setIsSubmitted(true);
        } else {
          throw new Error('Invalid tree data received');
        }
      } catch (err: any) {
        console.error('Error loading saved tree:', err);
        setError(err.message || 'Failed to load saved tree. Please try again later.');
        setIsSubmitted(false);
      } finally {
        setIsLoading(false);
      }
    };

    loadSavedTree();
  }, [treeId, setNodes, setEdges]);

  // Generate tree using the profile input
  const generateTree = useCallback(async () => {
    if (!profile.trim()) {
      setError('Please enter your profile information first');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setIsSubmitted(true);
    
    try {
      const careerTree = await careerTreeService.generateCareerTree(profile);
      
      // Convert CareerTreeNode to TreeNode
      const treeNode = convertCareerToTreeNode(careerTree);
      
      // Convert tree data to ReactFlow format using the utility function
      const { nodes: treeNodes, edges: treeEdges } = convertToFlowGraph(treeNode);
      
      setNodes(treeNodes);
      setEdges(treeEdges);
    } catch (err: any) {
      console.error('Error generating career tree:', err);
      setError(err.message || 'Failed to load career tree. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, [profile, setNodes, setEdges]);

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // Function to save tree to user's path
  const handleSaveTree = async () => {
    if (!nodes.length) return;
    
    setIsSaving(true);
    setSaveSuccess(false);
    
    try {
      // Find the root node
      const rootNodeId = nodes.find(node => node.type === 'rootNode')?.id || 'root';
      const rootNode = nodes.find(node => node.id === rootNodeId);
      
      if (!rootNode) throw new Error('Root node not found');
      
      // Create a TreeNode structure from the ReactFlow nodes
      const createTreeStructure = (nodeId: string): any => {
        const node = nodes.find(n => n.id === nodeId);
        if (!node) return null;
        
        // Find all child edges
        const childEdges = edges.filter(e => e.source === nodeId);
        const children = childEdges
          .map(edge => createTreeStructure(edge.target))
          .filter(Boolean);
        
        return {
          id: node.id,
          label: node.data?.label || '',
          type: node.type === 'rootNode' ? 'root' : 
                node.type === 'skillNode' ? 'skill' : 'outcome',
          level: node.data?.level || 0,
          actions: node.data?.actions || [],
          children: children.length > 0 ? children : undefined
        };
      };
      
      // Create tree structure starting from root
      const treeStructure = createTreeStructure(rootNodeId);
      
      // Save to backend
      await saveTreePath(treeStructure, 'career');
      setSaveSuccess(true);
      
      // Hide success message after a few seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (err: any) {
      console.error('Error saving tree:', err);
      setError(err.message || 'Failed to save tree');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="w-full h-[calc(100vh-6rem)] bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden flex flex-col">
      <motion.div 
        className="p-4 text-2xl font-light text-gray-800 dark:text-gray-100 border-b border-gray-100 dark:border-gray-700"
        initial="hidden"
        animate="visible"
        variants={titleVariants}
      >
      </motion.div>
      
      {!isSubmitted ? (
        <div className="flex-1 p-6 flex flex-col items-center justify-center">
          <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-medium text-gray-800 dark:text-gray-100 mb-4">Tell us about your career journey</h2>
            <textarea 
              className="w-full h-40 p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
              placeholder={PROFILE_PLACEHOLDER}
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={generateTree}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                Generate Career Path
              </button>
            </div>
          </div>
        </div>
      ) : isLoading ? (
        <LoadingScreen message="Generating your personal career tree..." />
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-red-50 p-4 rounded-lg border border-red-200 max-w-md">
            <p className="text-red-700 mb-4">{error}</p>
            <div className="flex space-x-3">
              <button 
                onClick={() => setIsSubmitted(false)}
                className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                Edit Profile
              </button>
              <button 
                onClick={generateTree}
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            connectionLineType={ConnectionLineType.SmoothStep}
            defaultViewport={{ x: 0, y: 0, zoom: 0.6 }}
            fitView
            minZoom={0.4}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#f8fafc" gap={16} size={1} className="dark:bg-gray-800" />
            <Controls className="dark:bg-gray-800 dark:text-gray-100" />
            <Panel position="top-right" className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-md border border-gray-100 dark:border-gray-700 flex flex-col space-y-2">
              <div className="text-sm text-gray-600 dark:text-gray-300">
                <div className="font-medium mb-2 flex justify-between items-center">
                  <span>Your Career Path:</span>
                  <button 
                    onClick={() => setIsCareerPathVisible(!isCareerPathVisible)} 
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {isCareerPathVisible ? 'Hide' : 'Show'}
                  </button>
                </div>
                {isCareerPathVisible && (
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Follow the connections between career options</li>
                    <li>Click on a skill to see recommended actions</li>
                    <li>Complete all actions before progressing</li>
                  </ul>
                )}
                <div className="flex flex-col space-y-2 mt-3">
                  <button
                    onClick={() => setIsSubmitted(false)}
                    className="w-full text-blue-600 dark:text-blue-400 border border-blue-600 dark:border-blue-400 px-2 py-1 rounded-md hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors text-sm"
                  >
                    Edit Profile
                  </button>
                  <button
                    onClick={handleSaveTree}
                    disabled={isSaving}
                    className="w-full bg-blue-600 text-white px-2 py-1 rounded-md hover:bg-blue-700 transition-colors text-sm disabled:opacity-50"
                  >
                    {isSaving ? 'Saving...' : 'Save Tree to My Path'}
                  </button>
                  {saveSuccess && (
                    <div className="text-xs text-green-600 dark:text-green-400 font-medium mt-1 text-center">
                      Tree saved successfully!
                    </div>
                  )}
                </div>
              </div>
              
              {/* XP Progress */}
              <XPProgress />
            </Panel>
          </ReactFlow>
        </div>
      )}
    </div>
  );
} 