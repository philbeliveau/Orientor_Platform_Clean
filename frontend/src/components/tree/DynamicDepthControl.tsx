import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Node, Edge } from 'reactflow';

interface DynamicDepthControlProps {
  nodes: Node[];
  edges: Edge[];
  onDepthChange: (depth: number) => void;
  onAlternativePathsToggle: () => void;
  onRecalculate: () => void;
  isRecalculating: boolean;
  currentDepth: number;
  maxDepth: number;
  showAlternativePaths: boolean;
  alternativePathsCount: number;
}

interface DepthStats {
  totalNodes: number;
  visibleNodes: number;
  hiddenNodes: number;
  pathsCount: number;
}

const DynamicDepthControl: React.FC<DynamicDepthControlProps> = ({
  nodes,
  edges,
  onDepthChange,
  onAlternativePathsToggle,
  onRecalculate,
  isRecalculating,
  currentDepth,
  maxDepth,
  showAlternativePaths,
  alternativePathsCount
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [localDepth, setLocalDepth] = useState(currentDepth);
  const [isDragging, setIsDragging] = useState(false);

  // Calculate depth statistics
  const depthStats = useMemo((): DepthStats => {
    const nodesByLevel = new Map<number, number>();
    let maxLevel = 0;
    
    nodes.forEach(node => {
      const level = node.data?.level || 0;
      nodesByLevel.set(level, (nodesByLevel.get(level) || 0) + 1);
      maxLevel = Math.max(maxLevel, level);
    });
    
    const visibleNodes = nodes.filter(node => (node.data?.level || 0) <= currentDepth).length;
    const totalNodes = nodes.length;
    const hiddenNodes = totalNodes - visibleNodes;
    
    // Count unique paths from root to leaves within depth
    const pathsCount = calculatePathsCount(nodes, edges, currentDepth);
    
    return {
      totalNodes,
      visibleNodes,
      hiddenNodes,
      pathsCount
    };
  }, [nodes, edges, currentDepth]);

  // Calculate number of unique paths within depth
  const calculatePathsCount = useCallback((nodes: Node[], edges: Edge[], depth: number): number => {
    const visibleNodes = nodes.filter(node => (node.data?.level || 0) <= depth);
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    const visibleEdges = edges.filter(edge => 
      visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    );
    
    // Find leaf nodes (nodes with no outgoing edges)
    const leafNodes = visibleNodes.filter(node => 
      !visibleEdges.some(edge => edge.source === node.id)
    );
    
    return leafNodes.length;
  }, []);

  // Handle slider change with debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localDepth !== currentDepth && !isDragging) {
        onDepthChange(localDepth);
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, [localDepth, currentDepth, isDragging, onDepthChange]);

  const handleSliderChange = useCallback((value: number) => {
    setLocalDepth(value);
  }, []);

  const handleSliderMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleSliderMouseUp = useCallback(() => {
    setIsDragging(false);
    onDepthChange(localDepth);
  }, [localDepth, onDepthChange]);

  return (
    <motion.div
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <motion.div
              className="w-3 h-3 bg-blue-500 rounded-full"
              animate={{ scale: isRecalculating ? [1, 1.2, 1] : 1 }}
              transition={{ duration: 0.5, repeat: isRecalculating ? Infinity : 0 }}
            />
            <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              Dynamic Depth Control
            </h3>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              ⌄
            </motion.div>
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="p-4 space-y-4"
          >
            {/* Depth Slider */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Career Progression Depth
                </label>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {localDepth} / {maxDepth} levels
                </span>
              </div>
              
              <div className="relative">
                <input
                  type="range"
                  min="1"
                  max={maxDepth}
                  value={localDepth}
                  onChange={(e) => handleSliderChange(parseInt(e.target.value))}
                  onMouseDown={handleSliderMouseDown}
                  onMouseUp={handleSliderMouseUp}
                  onTouchStart={handleSliderMouseDown}
                  onTouchEnd={handleSliderMouseUp}
                  className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                  style={{
                    background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((localDepth - 1) / (maxDepth - 1)) * 100}%, #e5e7eb ${((localDepth - 1) / (maxDepth - 1)) * 100}%, #e5e7eb 100%)`
                  }}
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>Basic</span>
                  <span>Intermediate</span>
                  <span>Advanced</span>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">
                  Visible Skills
                </div>
                <div className="text-lg font-bold text-blue-800 dark:text-blue-300">
                  {depthStats.visibleNodes}
                </div>
                <div className="text-xs text-blue-600 dark:text-blue-400">
                  of {depthStats.totalNodes} total
                </div>
              </div>
              
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                <div className="text-xs text-green-600 dark:text-green-400 font-medium mb-1">
                  Career Paths
                </div>
                <div className="text-lg font-bold text-green-800 dark:text-green-300">
                  {depthStats.pathsCount}
                </div>
                <div className="text-xs text-green-600 dark:text-green-400">
                  available routes
                </div>
              </div>
            </div>

            {/* Alternative Paths Toggle */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Alternative Paths
                </label>
                <button
                  onClick={onAlternativePathsToggle}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    showAlternativePaths
                      ? 'bg-blue-600'
                      : 'bg-gray-200 dark:bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      showAlternativePaths ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {showAlternativePaths && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3"
                >
                  <div className="text-xs text-amber-600 dark:text-amber-400 font-medium mb-1">
                    Exploring Alternatives
                  </div>
                  <div className="text-sm text-amber-800 dark:text-amber-300">
                    Showing {alternativePathsCount} different top-5 combinations
                  </div>
                </motion.div>
              )}
            </div>

            {/* Recalculate Button */}
            <button
              onClick={onRecalculate}
              disabled={isRecalculating}
              className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                isRecalculating
                  ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md'
              }`}
            >
              {isRecalculating ? (
                <div className="flex items-center justify-center space-x-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full"
                  />
                  <span>Recalculating...</span>
                </div>
              ) : (
                'Recalculate GraphSage'
              )}
            </button>

            {/* Performance Indicator */}
            {isRecalculating && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-xs text-gray-500 dark:text-gray-400 text-center"
              >
                Real-time GraphSage processing...
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default DynamicDepthControl;

// CSS for custom slider styling
export const sliderStyles = `
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
`;
