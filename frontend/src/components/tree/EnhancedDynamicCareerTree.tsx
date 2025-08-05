import React, { useState, useCallback, useEffect, useMemo } from 'react';
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
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import { SkillNode, OutcomeNode, RootNode } from './CustomNodes';
import { useDynamicTreeStore } from '../../stores/dynamicTreeStore';
import DynamicDepthControl from './DynamicDepthControl';
import AlternativePathsExplorer from './AlternativePathsExplorer';
import { careerTreeService } from '../../services/careerTreeService';
import { convertToFlowGraph, TreeNode } from '../../utils/convertToFlowGraph';
import LoadingScreen from '../ui/LoadingScreen';
import { useSearchParams } from 'next/navigation';
import { getTreePath } from '../../utils/treeStorage';

// Define custom node types
const nodeTypes: NodeTypes = {
  rootNode: RootNode,
  skillNode: SkillNode,
  outcomeNode: OutcomeNode,
  careerNode: SkillNode, // Reuse SkillNode for career nodes
};

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.5,
      staggerChildren: 0.1
    }
  }
};

const panelVariants = {
  hidden: { x: -300, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.3, ease: "easeOut" as const }
  },
  exit: {
    x: -300,
    opacity: 0,
    transition: { duration: 0.2 }
  }
};

interface EnhancedDynamicCareerTreeProps {
  initialProfile?: string;
  onTreeGenerated?: (nodes: Node[], edges: Edge[]) => void;
}

const PROFILE_PLACEHOLDER = `Tell us about your career interests and aspirations.
For example:
- What subjects excite you?
- What skills do you want to develop?
- What careers are you curious about?
- What kind of impact do you want to make?`;

// Convert CareerTreeNode to TreeNode format
function convertCareerToTreeNode(careerNode: any): TreeNode {
  let nodeType: "root" | "skill" | "outcome" | "career";
  
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
    case "career":
      nodeType = "career";
      break;
    default:
      nodeType = "skill";
  }
  
  return {
    id: careerNode.id,
    label: careerNode.label,
    type: nodeType,
    level: careerNode.level || 0,
    actions: careerNode.actions,
    children: careerNode.children?.map((child: any) => convertCareerToTreeNode(child))
  };
}

const EnhancedDynamicCareerTree: React.FC<EnhancedDynamicCareerTreeProps> = ({
  initialProfile = '',
  onTreeGenerated
}) => {
  // Local state for tree generation
  const [profile, setProfile] = useState(initialProfile);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  // ReactFlow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Dynamic tree store
  const {
    currentNodes,
    currentEdges,
    parameters,
    maxDepth,
    isRecalculating,
    showDynamicControls,
    showAlternativePathsExplorer,
    alternativePaths,
    recalculationError,
    performanceMetrics,
    isAutoRecalculationEnabled,
    pendingChanges,
    
    initializeTree,
    updateDepth,
    toggleAlternativePathsExplorer,
    triggerRecalculation,
    selectAlternativePath,
    toggleDynamicControls,
    enableAutoRecalculation,
    clearError,
    resetToOriginal,
    cleanup
  } = useDynamicTreeStore();
  
  // URL parameters for loading saved trees
  const searchParams = useSearchParams();
  const treeId = searchParams?.get('treeId') || null;
  
  // Sync ReactFlow nodes/edges with store
  useEffect(() => {
    if (currentNodes.length > 0) {
      setNodes(currentNodes);
      setEdges(currentEdges);
    }
  }, [currentNodes, currentEdges, setNodes, setEdges]);
  
  // Load saved tree if treeId is provided
  useEffect(() => {
    const loadSavedTree = async () => {
      if (!treeId) return;
      
      setIsGenerating(true);
      setGenerationError(null);
      
      try {
        console.log('Loading tree with ID:', treeId);
        const savedTree = await getTreePath(treeId);
        
        if (savedTree && savedTree.tree_json) {
          // Convert tree data to ReactFlow format
          const { nodes: treeNodes, edges: treeEdges } = convertToFlowGraph(savedTree.tree_json);
          
          // Initialize dynamic tree store
          initializeTree(treeNodes, treeEdges, savedTree.profile || '');
          setIsSubmitted(true);
          
          // Notify parent component
          onTreeGenerated?.(treeNodes, treeEdges);
        } else {
          throw new Error('Invalid tree data received');
        }
      } catch (err: any) {
        console.error('Error loading saved tree:', err);
        setGenerationError(err.message || 'Failed to load saved tree');
      } finally {
        setIsGenerating(false);
      }
    };
    
    loadSavedTree();
  }, [treeId, initializeTree, onTreeGenerated]);
  
  // Generate new career tree
  const generateTree = useCallback(async () => {
    if (!profile.trim()) {
      setGenerationError('Please enter your career profile first');
      return;
    }
    
    setIsGenerating(true);
    setGenerationError(null);
    setIsSubmitted(true);
    
    try {
      console.log('Generating career tree for profile:', profile.substring(0, 100) + '...');
      
      const careerTree = await careerTreeService.generateCareerTree(profile);
      
      // Convert to TreeNode format
      const treeNode = convertCareerToTreeNode(careerTree);
      
      // Convert to ReactFlow format
      const { nodes: treeNodes, edges: treeEdges } = convertToFlowGraph(treeNode);
      
      // Initialize dynamic tree store
      initializeTree(treeNodes, treeEdges, profile);
      
      // Notify parent component
      onTreeGenerated?.(treeNodes, treeEdges);
      
      console.log(`Tree generated with ${treeNodes.length} nodes and ${treeEdges.length} edges`);
      
    } catch (err: any) {
      console.error('Error generating career tree:', err);
      setGenerationError(err.message || 'Failed to generate career tree');
    } finally {
      setIsGenerating(false);
    }
  }, [profile, initializeTree, onTreeGenerated]);
  
  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);
  
  // Handle depth change from dynamic controls
  const handleDepthChange = useCallback((depth: number) => {
    updateDepth(depth);
  }, [updateDepth]);
  
  // Handle alternative paths toggle
  const handleAlternativePathsToggle = useCallback(() => {
    toggleAlternativePathsExplorer();
  }, [toggleAlternativePathsExplorer]);
  
  // Handle recalculation
  const handleRecalculate = useCallback(async () => {
    await triggerRecalculation(true);
  }, [triggerRecalculation]);
  
  // Handle alternative path selection
  const handlePathSelect = useCallback((path: any) => {
    selectAlternativePath(path);
  }, [selectAlternativePath]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);
  
  // Clear error when clicking retry
  const handleRetry = useCallback(() => {
    clearError();
    setGenerationError(null);
    generateTree();
  }, [clearError, generateTree]);
  
  // Performance indicator component
  const PerformanceIndicator = useMemo(() => {
    if (!isSubmitted || performanceMetrics.totalRecalculations === 0) return null;
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-xs text-gray-500 dark:text-gray-400 space-y-1"
      >
        <div className="flex justify-between">
          <span>Last recalc:</span>
          <span>{performanceMetrics.lastRecalculationTime}ms</span>
        </div>
        <div className="flex justify-between">
          <span>Avg time:</span>
          <span>{Math.round(performanceMetrics.averageRecalculationTime)}ms</span>
        </div>
        <div className="flex justify-between">
          <span>Total calcs:</span>
          <span>{performanceMetrics.totalRecalculations}</span>
        </div>
        {performanceMetrics.errorCount > 0 && (
          <div className="flex justify-between text-red-500">
            <span>Errors:</span>
            <span>{performanceMetrics.errorCount}</span>
          </div>
        )}
      </motion.div>
    );
  }, [isSubmitted, performanceMetrics]);
  
  return (
    <motion.div
      className="w-full h-[calc(100vh-6rem)] bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden flex"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Dynamic Controls Panel */}
      <AnimatePresence>
        {showDynamicControls && isSubmitted && (
          <motion.div
            className="w-80 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 overflow-y-auto"
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <div className="p-4 space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                  Dynamic Controls
                </h3>
                <button
                  onClick={toggleDynamicControls}
                  className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  ×
                </button>
              </div>
              
              {/* Auto Recalculation Toggle */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto Recalculation
                </label>
                <button
                  onClick={() => enableAutoRecalculation(!isAutoRecalculationEnabled)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    isAutoRecalculationEnabled
                      ? 'bg-blue-600'
                      : 'bg-gray-200 dark:bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      isAutoRecalculationEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {/* Pending Changes Indicator */}
              {pendingChanges && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3"
                >
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    <span className="text-sm text-amber-700 dark:text-amber-300">
                      Changes pending recalculation
                    </span>
                  </div>
                </motion.div>
              )}
              
              {/* Dynamic Depth Control */}
              <DynamicDepthControl
                nodes={currentNodes}
                edges={currentEdges}
                onDepthChange={handleDepthChange}
                onAlternativePathsToggle={handleAlternativePathsToggle}
                onRecalculate={handleRecalculate}
                isRecalculating={isRecalculating}
                currentDepth={parameters.depth}
                maxDepth={maxDepth}
                showAlternativePaths={parameters.showAlternativePaths}
                alternativePathsCount={alternativePaths.length}
              />
              
              {/* Error Display */}
              {recalculationError && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3"
                >
                  <div className="text-sm text-red-700 dark:text-red-300 mb-2">
                    {recalculationError}
                  </div>
                  <button
                    onClick={clearError}
                    className="text-xs text-red-600 dark:text-red-400 hover:underline"
                  >
                    Dismiss
                  </button>
                </motion.div>
              )}
              
              {/* Performance Metrics */}
              {PerformanceIndicator}
              
              {/* Reset Button */}
              <button
                onClick={resetToOriginal}
                className="w-full py-2 px-4 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Reset to Original
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Main Tree Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
              Enhanced Dynamic Career Tree
            </h2>
            <div className="flex items-center space-x-2">
              {isSubmitted && (
                <button
                  onClick={toggleDynamicControls}
                  className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  {showDynamicControls ? 'Hide' : 'Show'} Controls
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Content Area */}
        {!isSubmitted ? (
          <div className="flex-1 p-6 flex flex-col items-center justify-center">
            <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-xl font-medium text-gray-800 dark:text-gray-100 mb-4">
                Tell us about your career journey
              </h3>
              <textarea
                className="w-full h-40 p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                placeholder={PROFILE_PLACEHOLDER}
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
              />
              <div className="mt-4 flex justify-end">
                <button
                  onClick={generateTree}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={isGenerating}
                >
                  {isGenerating ? 'Generating...' : 'Generate Dynamic Career Tree'}
                </button>
              </div>
            </div>
          </div>
        ) : isGenerating ? (
          <LoadingScreen message="Generating your dynamic career tree with GraphSage..." />
        ) : generationError ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg border border-red-200 dark:border-red-800 max-w-md">
              <p className="text-red-700 dark:text-red-300 mb-4">{generationError}</p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setIsSubmitted(false)}
                  className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 px-4 py-2 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Edit Profile
                </button>
                <button
                  onClick={handleRetry}
                  className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1">
            <ReactFlowProvider>
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
                minZoom={0.3}
                maxZoom={2}
                proOptions={{ hideAttribution: true }}
              >
                <Background
                  color="#f8fafc"
                  gap={16}
                  size={1}
                  className="dark:bg-gray-800"
                />
                <Controls className="dark:bg-gray-800 dark:text-gray-100" />
                
                {/* Real-time Status Panel */}
                <Panel position="top-right" className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-md border border-gray-100 dark:border-gray-700">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        isRecalculating ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'
                      }`} />
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {isRecalculating ? 'Recalculating...' : 'Ready'}
                      </span>
                    </div>
                    
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      Depth: {parameters.depth}/{maxDepth}
                    </div>
                    
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      Nodes: {currentNodes.length}
                    </div>
                    
                    {isAutoRecalculationEnabled && (
                      <div className="text-xs text-blue-600 dark:text-blue-400">
                        Auto-sync enabled
                      </div>
                    )}
                  </div>
                </Panel>
              </ReactFlow>
            </ReactFlowProvider>
          </div>
        )}
      </div>
      
      {/* Alternative Paths Explorer */}
      <AlternativePathsExplorer
        originalNodes={currentNodes}
        originalEdges={currentEdges}
        currentDepth={parameters.depth}
        onPathSelect={handlePathSelect}
        onClose={() => toggleAlternativePathsExplorer()}
        isVisible={showAlternativePathsExplorer}
        userProfile={profile}
      />
    </motion.div>
  );
};

export default EnhancedDynamicCareerTree;
