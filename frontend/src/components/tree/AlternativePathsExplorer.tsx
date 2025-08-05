import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Node, Edge } from 'reactflow';

interface AlternativePath {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
  score: number;
  description: string;
  topSkills: string[];
  estimatedTime: string;
  careerOutcomes: string[];
}

interface AlternativePathsExplorerProps {
  originalNodes: Node[];
  originalEdges: Edge[];
  currentDepth: number;
  onPathSelect: (path: AlternativePath) => void;
  onClose: () => void;
  isVisible: boolean;
  userProfile: string;
}

const AlternativePathsExplorer: React.FC<AlternativePathsExplorerProps> = ({
  originalNodes,
  originalEdges,
  currentDepth,
  onPathSelect,
  onClose,
  isVisible,
  userProfile
}) => {
  const [alternativePaths, setAlternativePaths] = useState<AlternativePath[]>([]);
  const [selectedPath, setSelectedPath] = useState<AlternativePath | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([]);

  // Generate alternative paths based on different top-5 combinations
  const generateAlternativePaths = useCallback(async () => {
    setIsGenerating(true);
    
    try {
      // Simulate alternative path generation by creating variations
      const basePaths = await generatePathVariations(originalNodes, originalEdges, currentDepth, userProfile);
      setAlternativePaths(basePaths);
    } catch (error) {
      console.error('Error generating alternative paths:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [originalNodes, originalEdges, currentDepth, userProfile]);

  // Generate path variations based on different prioritization strategies
  const generatePathVariations = async (
    nodes: Node[], 
    edges: Edge[], 
    depth: number, 
    profile: string
  ): Promise<AlternativePath[]> => {
    const strategies = [
      {
        id: 'speed-focused',
        name: 'Fast Track Path',
        description: 'Optimized for quickest skill acquisition',
        weight: 'time'
      },
      {
        id: 'depth-focused',
        name: 'Deep Expertise Path',
        description: 'Focused on mastering core competencies',
        weight: 'expertise'
      },
      {
        id: 'breadth-focused',
        name: 'Versatile Skills Path',
        description: 'Balanced approach across multiple domains',
        weight: 'diversity'
      },
      {
        id: 'market-focused',
        name: 'Market Demand Path',
        description: 'Prioritizes high-demand skills',
        weight: 'demand'
      },
      {
        id: 'innovation-focused',
        name: 'Cutting-Edge Path',
        description: 'Emphasizes emerging technologies',
        weight: 'innovation'
      }
    ];

    const paths: AlternativePath[] = [];
    
    for (const strategy of strategies) {
      const pathNodes = reorderNodesByStrategy(nodes, strategy.weight, depth);
      const pathEdges = regenerateEdgesForPath(pathNodes, edges);
      
      paths.push({
        id: strategy.id,
        name: strategy.name,
        description: strategy.description,
        nodes: pathNodes,
        edges: pathEdges,
        score: calculatePathScore(pathNodes, strategy.weight),
        topSkills: extractTopSkills(pathNodes, 5),
        estimatedTime: estimateCompletionTime(pathNodes),
        careerOutcomes: extractCareerOutcomes(pathNodes)
      });
    }
    
    return paths.sort((a, b) => b.score - a.score);
  };

  // Reorder nodes based on prioritization strategy
  const reorderNodesByStrategy = (nodes: Node[], strategy: string, depth: number): Node[] => {
    const filteredNodes = nodes.filter(node => (node.data?.level || 0) <= depth);
    
    switch (strategy) {
      case 'time':
        return filteredNodes.sort((a, b) => {
          const aActions = a.data?.actions?.length || 0;
          const bActions = b.data?.actions?.length || 0;
          return aActions - bActions; // Fewer actions = faster
        });
      
      case 'expertise':
        return filteredNodes.sort((a, b) => {
          const aLevel = a.data?.level || 0;
          const bLevel = b.data?.level || 0;
          return bLevel - aLevel; // Higher level = more expertise
        });
      
      case 'diversity':
        return shuffleArrayWithBalance(filteredNodes);
      
      case 'demand':
        return filteredNodes.sort((a, b) => {
          const aScore = calculateMarketDemandScore(a.data?.label || '');
          const bScore = calculateMarketDemandScore(b.data?.label || '');
          return bScore - aScore;
        });
      
      case 'innovation':
        return filteredNodes.sort((a, b) => {
          const aScore = calculateInnovationScore(a.data?.label || '');
          const bScore = calculateInnovationScore(b.data?.label || '');
          return bScore - aScore;
        });
      
      default:
        return filteredNodes;
    }
  };

  // Calculate market demand score based on skill keywords
  const calculateMarketDemandScore = (skillLabel: string): number => {
    const highDemandKeywords = [
      'ai', 'machine learning', 'python', 'react', 'typescript', 'cloud', 
      'kubernetes', 'data science', 'cybersecurity', 'blockchain'
    ];
    
    const lowercaseLabel = skillLabel.toLowerCase();
    return highDemandKeywords.reduce((score, keyword) => {
      return lowercaseLabel.includes(keyword) ? score + 1 : score;
    }, 0);
  };

  // Calculate innovation score based on emerging tech keywords
  const calculateInnovationScore = (skillLabel: string): number => {
    const innovationKeywords = [
      'gpt', 'transformer', 'neural', 'quantum', 'edge computing', 'iot',
      'ar', 'vr', 'web3', 'defi', 'nft', 'metaverse'
    ];
    
    const lowercaseLabel = skillLabel.toLowerCase();
    return innovationKeywords.reduce((score, keyword) => {
      return lowercaseLabel.includes(keyword) ? score + 2 : score;
    }, 0);
  };

  // Shuffle array while maintaining some structural balance
  const shuffleArrayWithBalance = (array: Node[]): Node[] => {
    const levels = new Map<number, Node[]>();
    array.forEach(node => {
      const level = node.data?.level || 0;
      if (!levels.has(level)) levels.set(level, []);
      levels.get(level)!.push(node);
    });
    
    const result: Node[] = [];
    const maxLevel = Math.max(...Array.from(levels.keys()));
    
    for (let level = 0; level <= maxLevel; level++) {
      const levelNodes = levels.get(level) || [];
      const shuffled = [...levelNodes].sort(() => Math.random() - 0.5);
      result.push(...shuffled);
    }
    
    return result;
  };

  // Regenerate edges for reordered path
  const regenerateEdgesForPath = (nodes: Node[], originalEdges: Edge[]): Edge[] => {
    const nodeIds = new Set(nodes.map(n => n.id));
    return originalEdges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
  };

  // Calculate overall path score
  const calculatePathScore = (nodes: Node[], strategy: string): number => {
    let score = 0;
    
    nodes.forEach(node => {
      const level = node.data?.level || 0;
      const actions = node.data?.actions?.length || 0;
      
      switch (strategy) {
        case 'time':
          score += Math.max(0, 10 - actions); // Prefer fewer actions
          break;
        case 'expertise':
          score += level * 2; // Prefer higher levels
          break;
        case 'diversity':
          score += 5; // Equal weight
          break;
        case 'demand':
          score += calculateMarketDemandScore(node.data?.label || '') * 3;
          break;
        case 'innovation':
          score += calculateInnovationScore(node.data?.label || '') * 2;
          break;
      }
    });
    
    return score;
  };

  // Extract top skills from path
  const extractTopSkills = (nodes: Node[], count: number): string[] => {
    const skills = nodes
      .filter(node => node.data?.nodeType === 'skill')
      .map(node => node.data?.label || '')
      .filter(label => label.length > 0)
      .slice(0, count);
    
    return skills;
  };

  // Estimate completion time
  const estimateCompletionTime = (nodes: Node[]): string => {
    const totalActions = nodes.reduce((sum, node) => {
      return sum + (node.data?.actions?.length || 0);
    }, 0);
    
    const estimatedWeeks = Math.ceil(totalActions * 1.5); // Assume 1.5 weeks per action
    
    if (estimatedWeeks < 12) {
      return `${estimatedWeeks} weeks`;
    } else {
      const months = Math.ceil(estimatedWeeks / 4.33);
      return `${months} months`;
    }
  };

  // Extract career outcomes
  const extractCareerOutcomes = (nodes: Node[]): string[] => {
    return nodes
      .filter(node => node.data?.nodeType === 'career')
      .map(node => node.data?.label || '')
      .filter(label => label.length > 0);
  };

  // Handle path comparison
  const toggleComparison = (pathId: string) => {
    setSelectedForComparison(prev => {
      if (prev.includes(pathId)) {
        return prev.filter(id => id !== pathId);
      } else if (prev.length < 3) {
        return [...prev, pathId];
      }
      return prev;
    });
  };

  // Generate paths when component becomes visible
  useEffect(() => {
    if (isVisible && alternativePaths.length === 0) {
      generateAlternativePaths();
    }
  }, [isVisible, generateAlternativePaths, alternativePaths.length]);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                Alternative Career Paths
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Explore different combinations of top-5 skills for your career progression
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setComparisonMode(!comparisonMode)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  comparisonMode
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                }`}
              >
                Compare Paths
              </button>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {isGenerating ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"
                />
                <p className="text-gray-600 dark:text-gray-400">
                  Generating alternative paths using GraphSage...
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {alternativePaths.map((path) => (
                <motion.div
                  key={path.id}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    selectedPath?.id === path.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedPath(path)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {/* Path Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-800 dark:text-gray-200">
                        {path.name}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex items-center space-x-1">
                          <span className="text-xs text-gray-500">Score:</span>
                          <span className="text-xs font-medium text-blue-600">
                            {path.score}
                          </span>
                        </div>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">
                          {path.estimatedTime}
                        </span>
                      </div>
                    </div>
                    {comparisonMode && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleComparison(path.id);
                        }}
                        className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                          selectedForComparison.includes(path.id)
                            ? 'bg-blue-600 border-blue-600 text-white'
                            : 'border-gray-300 dark:border-gray-600'
                        }`}
                      >
                        {selectedForComparison.includes(path.id) && '✓'}
                      </button>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {path.description}
                  </p>

                  {/* Top Skills */}
                  <div className="mb-3">
                    <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Top Skills:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {path.topSkills.map((skill, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded-full text-gray-700 dark:text-gray-300"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Career Outcomes */}
                  {path.careerOutcomes.length > 0 && (
                    <div>
                      <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Career Outcomes:
                      </div>
                      <div className="space-y-1">
                        {path.careerOutcomes.slice(0, 2).map((outcome, index) => (
                          <div
                            key={index}
                            className="text-xs text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded"
                          >
                            {outcome}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Select Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onPathSelect(path);
                    }}
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
                  >
                    Use This Path
                  </button>
                </motion.div>
              ))}
            </div>
          )}

          {/* Comparison Panel */}
          {comparisonMode && selectedForComparison.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl"
            >
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
                Path Comparison ({selectedForComparison.length}/3)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedForComparison.map(pathId => {
                  const path = alternativePaths.find(p => p.id === pathId);
                  if (!path) return null;
                  
                  return (
                    <div key={pathId} className="bg-white dark:bg-gray-800 rounded-lg p-4">
                      <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">
                        {path.name}
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Score:</span>
                          <span className="font-medium">{path.score}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Time:</span>
                          <span className="font-medium">{path.estimatedTime}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Skills:</span>
                          <span className="font-medium">{path.topSkills.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Careers:</span>
                          <span className="font-medium">{path.careerOutcomes.length}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AlternativePathsExplorer;
export type { AlternativePath };
