import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { Node, Edge } from 'reactflow';
import { realTimeGraphSageService, GraphSageRecalculationResponse } from '../services/realTimeGraphSageService';
import { AlternativePath } from '../components/tree/AlternativePathsExplorer';

interface DynamicParameters {
  depth: number;
  maxNodes: number;
  focusAreas: string[];
  priorityWeights: Record<string, number>;
  showAlternativePaths: boolean;
  recalculationMode: 'auto' | 'manual';
  optimizationStrategy: 'speed' | 'accuracy' | 'balanced';
}

interface PerformanceMetrics {
  lastRecalculationTime: number;
  averageRecalculationTime: number;
  cacheHitRate: number;
  totalRecalculations: number;
  errorCount: number;
}

interface DynamicTreeState {
  // Core tree data
  originalNodes: Node[];
  originalEdges: Edge[];
  currentNodes: Node[];
  currentEdges: Edge[];
  userProfile: string;
  
  // Dynamic parameters
  parameters: DynamicParameters;
  maxDepth: number;
  
  // Alternative paths
  alternativePaths: AlternativePath[];
  selectedAlternativePath: AlternativePath | null;
  showAlternativePathsExplorer: boolean;
  
  // State management
  isRecalculating: boolean;
  lastRecalculation: GraphSageRecalculationResponse | null;
  recalculationError: string | null;
  
  // Performance tracking
  performanceMetrics: PerformanceMetrics;
  
  // UI state
  showDynamicControls: boolean;
  isAutoRecalculationEnabled: boolean;
  pendingChanges: boolean;
}

interface DynamicTreeActions {
  // Initialization
  initializeTree: (nodes: Node[], edges: Edge[], profile: string) => void;
  
  // Parameter updates
  updateDepth: (depth: number) => void;
  updateFocusAreas: (areas: string[]) => void;
  updatePriorityWeights: (weights: Record<string, number>) => void;
  updateOptimizationStrategy: (strategy: DynamicParameters['optimizationStrategy']) => void;
  
  // Recalculation
  triggerRecalculation: (force?: boolean) => Promise<void>;
  enableAutoRecalculation: (enabled: boolean) => void;
  
  // Alternative paths
  toggleAlternativePathsExplorer: () => void;
  generateAlternativePaths: () => Promise<void>;
  selectAlternativePath: (path: AlternativePath) => void;
  
  // UI actions
  toggleDynamicControls: () => void;
  clearError: () => void;
  resetToOriginal: () => void;
  
  // Performance
  updatePerformanceMetrics: (metrics: Partial<PerformanceMetrics>) => void;
  
  // Cleanup
  cleanup: () => void;
}

type DynamicTreeStore = DynamicTreeState & DynamicTreeActions;

const defaultParameters: DynamicParameters = {
  depth: 3,
  maxNodes: 50,
  focusAreas: [],
  priorityWeights: {
    'skill': 1.0,
    'time': 0.8,
    'expertise': 0.9,
    'market_demand': 0.7
  },
  showAlternativePaths: false,
  recalculationMode: 'auto',
  optimizationStrategy: 'balanced'
};

const defaultPerformanceMetrics: PerformanceMetrics = {
  lastRecalculationTime: 0,
  averageRecalculationTime: 0,
  cacheHitRate: 0,
  totalRecalculations: 0,
  errorCount: 0
};

export const useDynamicTreeStore = create<DynamicTreeStore>()(subscribeWithSelector(devtools(
  (set, get) => ({
    // Initial state
    originalNodes: [],
    originalEdges: [],
    currentNodes: [],
    currentEdges: [],
    userProfile: '',
    parameters: defaultParameters,
    maxDepth: 5,
    alternativePaths: [],
    selectedAlternativePath: null,
    showAlternativePathsExplorer: false,
    isRecalculating: false,
    lastRecalculation: null,
    recalculationError: null,
    performanceMetrics: defaultPerformanceMetrics,
    showDynamicControls: true,
    isAutoRecalculationEnabled: true,
    pendingChanges: false,

    // Actions
    initializeTree: (nodes, edges, profile) => {
      const maxDepth = Math.max(...nodes.map(node => node.data?.level || 0));
      
      set({
        originalNodes: nodes,
        originalEdges: edges,
        currentNodes: nodes,
        currentEdges: edges,
        userProfile: profile,
        maxDepth,
        parameters: {
          ...defaultParameters,
          depth: Math.min(defaultParameters.depth, maxDepth)
        }
      }, false, 'initializeTree');
    },

    updateDepth: (depth) => {
      const { parameters, isAutoRecalculationEnabled } = get();
      
      set({
        parameters: { ...parameters, depth },
        pendingChanges: !isAutoRecalculationEnabled
      }, false, 'updateDepth');
      
      if (isAutoRecalculationEnabled) {
        get().triggerRecalculation();
      }
    },

    updateFocusAreas: (areas) => {
      const { parameters, isAutoRecalculationEnabled } = get();
      
      set({
        parameters: { ...parameters, focusAreas: areas },
        pendingChanges: !isAutoRecalculationEnabled
      }, false, 'updateFocusAreas');
      
      if (isAutoRecalculationEnabled) {
        get().triggerRecalculation();
      }
    },

    updatePriorityWeights: (weights) => {
      const { parameters, isAutoRecalculationEnabled } = get();
      
      set({
        parameters: { ...parameters, priorityWeights: weights },
        pendingChanges: !isAutoRecalculationEnabled
      }, false, 'updatePriorityWeights');
      
      if (isAutoRecalculationEnabled) {
        get().triggerRecalculation();
      }
    },

    updateOptimizationStrategy: (strategy) => {
      const { parameters } = get();
      
      set({
        parameters: { ...parameters, optimizationStrategy: strategy }
      }, false, 'updateOptimizationStrategy');
    },

    triggerRecalculation: async (force = false) => {
      const state = get();
      
      if (state.isRecalculating && !force) {
        console.log('DynamicTreeStore: Recalculation already in progress');
        return;
      }
      
      set({ isRecalculating: true, recalculationError: null }, false, 'startRecalculation');
      
      try {
        const startTime = Date.now();
        
        const request = {
          nodes: state.originalNodes,
          edges: state.originalEdges,
          depth: state.parameters.depth,
          userProfile: state.userProfile,
          parameters: {
            maxNodes: state.parameters.maxNodes,
            focusAreas: state.parameters.focusAreas,
            priorityWeights: state.parameters.priorityWeights
          }
        };
        
        const result = await realTimeGraphSageService.recalculateWithDebounce(
          request,
          'main-tree-recalculation',
          {
            priority: 'high',
            useCache: state.parameters.optimizationStrategy !== 'accuracy'
          }
        );
        
        const recalculationTime = Date.now() - startTime;
        
        // Update performance metrics
        const newMetrics = {
          ...state.performanceMetrics,
          lastRecalculationTime: recalculationTime,
          averageRecalculationTime: state.performanceMetrics.totalRecalculations === 0
            ? recalculationTime
            : (state.performanceMetrics.averageRecalculationTime * state.performanceMetrics.totalRecalculations + recalculationTime) / (state.performanceMetrics.totalRecalculations + 1),
          totalRecalculations: state.performanceMetrics.totalRecalculations + 1
        };
        
        set({
          currentNodes: result.updatedNodes,
          currentEdges: result.updatedEdges,
          lastRecalculation: result,
          performanceMetrics: newMetrics,
          pendingChanges: false
        }, false, 'recalculationSuccess');
        
        console.log(`DynamicTreeStore: Recalculation completed in ${recalculationTime}ms`);
        
      } catch (error: any) {
        console.error('DynamicTreeStore: Recalculation failed:', error);
        
        const newMetrics = {
          ...state.performanceMetrics,
          errorCount: state.performanceMetrics.errorCount + 1
        };
        
        set({
          recalculationError: error.message || 'Recalculation failed',
          performanceMetrics: newMetrics
        }, false, 'recalculationError');
      } finally {
        set({ isRecalculating: false }, false, 'endRecalculation');
      }
    },

    enableAutoRecalculation: (enabled) => {
      set({
        isAutoRecalculationEnabled: enabled,
        parameters: {
          ...get().parameters,
          recalculationMode: enabled ? 'auto' : 'manual'
        }
      }, false, 'enableAutoRecalculation');
      
      // Trigger recalculation if enabling auto and there are pending changes
      if (enabled && get().pendingChanges) {
        get().triggerRecalculation();
      }
    },

    toggleAlternativePathsExplorer: () => {
      const { showAlternativePathsExplorer } = get();
      set({ showAlternativePathsExplorer: !showAlternativePathsExplorer }, false, 'toggleAlternativePathsExplorer');
      
      // Generate alternative paths if opening for the first time
      if (!showAlternativePathsExplorer && get().alternativePaths.length === 0) {
        get().generateAlternativePaths();
      }
    },

    generateAlternativePaths: async () => {
      const state = get();
      
      try {
        console.log('DynamicTreeStore: Generating alternative paths');
        
        const request = {
          nodes: state.originalNodes,
          edges: state.originalEdges,
          depth: state.parameters.depth,
          userProfile: state.userProfile,
          parameters: {
            maxNodes: state.parameters.maxNodes,
            focusAreas: state.parameters.focusAreas,
            priorityWeights: state.parameters.priorityWeights
          }
        };
        
        const alternatives = await realTimeGraphSageService.generateAlternativePaths(request, 5);
        
        // Convert GraphSage responses to AlternativePath format
        const alternativePaths: AlternativePath[] = alternatives.map((alt, index) => ({
          id: `alt-${index}`,
          name: `Alternative Path ${index + 1}`,
          description: `Generated using strategy ${index + 1}`,
          nodes: alt.updatedNodes,
          edges: alt.updatedEdges,
          score: alt.confidence * 100,
          topSkills: alt.updatedNodes
            .filter(node => node.data?.nodeType === 'skill')
            .slice(0, 5)
            .map(node => node.data?.label || ''),
          estimatedTime: `${Math.ceil(alt.updatedNodes.length * 1.5)} weeks`,
          careerOutcomes: alt.updatedNodes
            .filter(node => node.data?.nodeType === 'career')
            .map(node => node.data?.label || '')
        }));
        
        set({ alternativePaths }, false, 'setAlternativePaths');
        
        console.log(`DynamicTreeStore: Generated ${alternativePaths.length} alternative paths`);
        
      } catch (error: any) {
        console.error('DynamicTreeStore: Failed to generate alternative paths:', error);
      }
    },

    selectAlternativePath: (path) => {
      set({
        selectedAlternativePath: path,
        currentNodes: path.nodes,
        currentEdges: path.edges,
        showAlternativePathsExplorer: false
      }, false, 'selectAlternativePath');
      
      console.log(`DynamicTreeStore: Selected alternative path: ${path.name}`);
    },

    toggleDynamicControls: () => {
      set({ showDynamicControls: !get().showDynamicControls }, false, 'toggleDynamicControls');
    },

    clearError: () => {
      set({ recalculationError: null }, false, 'clearError');
    },

    resetToOriginal: () => {
      const { originalNodes, originalEdges } = get();
      
      set({
        currentNodes: originalNodes,
        currentEdges: originalEdges,
        selectedAlternativePath: null,
        alternativePaths: [],
        recalculationError: null,
        pendingChanges: false,
        parameters: {
          ...defaultParameters,
          depth: Math.min(defaultParameters.depth, get().maxDepth)
        }
      }, false, 'resetToOriginal');
      
      console.log('DynamicTreeStore: Reset to original tree');
    },

    updatePerformanceMetrics: (metrics) => {
      set({
        performanceMetrics: { ...get().performanceMetrics, ...metrics }
      }, false, 'updatePerformanceMetrics');
    },

    cleanup: () => {
      // Clear any pending operations
      realTimeGraphSageService.clearCache();
      
      set({
        isRecalculating: false,
        pendingChanges: false,
        recalculationError: null
      }, false, 'cleanup');
      
      console.log('DynamicTreeStore: Cleanup completed');
    }
  }),
  {
    name: 'dynamic-tree-store'
  }
)));

// Subscribe to parameter changes for automatic recalculation
useDynamicTreeStore.subscribe(
  (state) => ({
    depth: state.parameters.depth,
    focusAreas: state.parameters.focusAreas,
    priorityWeights: state.parameters.priorityWeights,
    isAutoEnabled: state.isAutoRecalculationEnabled
  }),
  (params, prevParams) => {
    // Only trigger if auto recalculation is enabled and parameters actually changed
    if (params.isAutoEnabled && prevParams && (
      params.depth !== prevParams.depth ||
      JSON.stringify(params.focusAreas) !== JSON.stringify(prevParams.focusAreas) ||
      JSON.stringify(params.priorityWeights) !== JSON.stringify(prevParams.priorityWeights)
    )) {
      console.log('DynamicTreeStore: Parameters changed, triggering auto recalculation');
      // Small delay to allow UI to update
      setTimeout(() => {
        useDynamicTreeStore.getState().triggerRecalculation();
      }, 100);
    }
  }
);

export type { DynamicParameters, PerformanceMetrics, DynamicTreeState, DynamicTreeActions };
