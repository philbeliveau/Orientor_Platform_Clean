import axios from 'axios';
import { Node, Edge } from 'reactflow';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface GraphSageRecalculationRequest {
  nodes: Node[];
  edges: Edge[];
  depth: number;
  userProfile: string;
  parameters?: {
    maxNodes?: number;
    focusAreas?: string[];
    priorityWeights?: Record<string, number>;
  };
}

interface GraphSageRecalculationResponse {
  updatedNodes: Node[];
  updatedEdges: Edge[];
  confidence: number;
  processingTime: number;
  cacheKey: string;
  alternativePaths?: {
    pathId: string;
    nodes: Node[];
    edges: Edge[];
    score: number;
  }[];
}

interface CacheEntry {
  key: string;
  data: GraphSageRecalculationResponse;
  timestamp: number;
  ttl: number;
}

class RealTimeGraphSageService {
  private cache: Map<string, CacheEntry> = new Map();
  private pendingRequests: Map<string, Promise<GraphSageRecalculationResponse>> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_CACHE_SIZE = 50;
  private readonly DEBOUNCE_DELAY = 300; // 300ms
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private getToken: (() => Promise<string | null>) | null = null;

  constructor(getToken?: () => Promise<string | null>) {
    this.getToken = getToken || null;
  }

  /**
   * Recalculate GraphSage with real-time optimization
   */
  async recalculateGraphSage(
    request: GraphSageRecalculationRequest,
    options: {
      useCache?: boolean;
      priority?: 'high' | 'normal' | 'low';
      abortSignal?: AbortSignal;
    } = {}
  ): Promise<GraphSageRecalculationResponse> {
    const { useCache = true, priority = 'normal', abortSignal } = options;
    
    // Generate cache key
    const cacheKey = this.generateCacheKey(request);
    
    // Check cache first
    if (useCache) {
      const cachedResult = this.getCachedResult(cacheKey);
      if (cachedResult) {
        console.log('RealTimeGraphSageService: Using cached result');
        return cachedResult;
      }
    }
    
    // Check if same request is already pending
    const pendingRequest = this.pendingRequests.get(cacheKey);
    if (pendingRequest) {
      console.log('RealTimeGraphSageService: Joining pending request');
      return pendingRequest;
    }
    
    // Create new request
    const requestPromise = this.performRecalculation(request, priority, abortSignal);
    this.pendingRequests.set(cacheKey, requestPromise);
    
    try {
      const result = await requestPromise;
      
      // Cache the result
      if (useCache) {
        this.setCachedResult(cacheKey, result);
      }
      
      return result;
    } finally {
      // Clean up pending request
      this.pendingRequests.delete(cacheKey);
    }
  }

  /**
   * Recalculate with debouncing for rapid parameter changes
   */
  async recalculateWithDebounce(
    request: GraphSageRecalculationRequest,
    debounceKey: string,
    options: Parameters<typeof this.recalculateGraphSage>[1] = {}
  ): Promise<GraphSageRecalculationResponse> {
    return new Promise((resolve, reject) => {
      // Clear existing timer
      const existingTimer = this.debounceTimers.get(debounceKey);
      if (existingTimer) {
        clearTimeout(existingTimer);
      }
      
      // Set new timer
      const timer = setTimeout(async () => {
        try {
          const result = await this.recalculateGraphSage(request, options);
          resolve(result);
        } catch (error) {
          reject(error);
        } finally {
          this.debounceTimers.delete(debounceKey);
        }
      }, this.DEBOUNCE_DELAY);
      
      this.debounceTimers.set(debounceKey, timer);
    });
  }

  /**
   * Perform the actual GraphSage recalculation
   */
  private async performRecalculation(
    request: GraphSageRecalculationRequest,
    priority: string,
    abortSignal?: AbortSignal
  ): Promise<GraphSageRecalculationResponse> {
    const startTime = Date.now();
    
    try {
      console.log('RealTimeGraphSageService: Starting GraphSage recalculation');
      console.log(`Request depth: ${request.depth}, nodes: ${request.nodes.length}`);
      
      // Get auth token
      const token = this.getToken ? await this.getToken() : null;
      
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        signal: abortSignal,
        timeout: 30000 // 30 second timeout
      };
      
      // Prepare request payload
      const payload = {
        ...request,
        priority,
        timestamp: Date.now()
      };
      
      // Make API call to GraphSage recalculation endpoint
      const response = await axios.post<GraphSageRecalculationResponse>(
        `${API_URL}/graphsage/recalculate`,
        payload,
        config
      );
      
      const processingTime = Date.now() - startTime;
      
      console.log(`RealTimeGraphSageService: Recalculation completed in ${processingTime}ms`);
      console.log(`Updated nodes: ${response.data.updatedNodes.length}`);
      console.log(`Confidence: ${response.data.confidence}`);
      
      return {
        ...response.data,
        processingTime
      };
    } catch (error: any) {
      const processingTime = Date.now() - startTime;
      
      console.error('RealTimeGraphSageService: Recalculation failed:', error);
      
      if (error.name === 'AbortError') {
        throw new Error('GraphSage recalculation was cancelled');
      }
      
      if (error.response?.status === 404) {
        // Fallback to mock recalculation if endpoint doesn't exist
        console.log('RealTimeGraphSageService: Using fallback mock recalculation');
        return this.mockRecalculation(request, processingTime);
      }
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'GraphSage recalculation failed'
      );
    }
  }

  /**
   * Mock recalculation for development/fallback
   */
  private async mockRecalculation(
    request: GraphSageRecalculationRequest,
    processingTime: number
  ): Promise<GraphSageRecalculationResponse> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
    
    // Filter nodes by depth
    const filteredNodes = request.nodes.filter(
      node => (node.data?.level || 0) <= request.depth
    );
    
    // Update node positions for better layout
    const updatedNodes = filteredNodes.map((node, index) => ({
      ...node,
      position: {
        x: node.position.x + (Math.random() - 0.5) * 20, // Small random adjustment
        y: node.position.y + (Math.random() - 0.5) * 20
      },
      data: {
        ...node.data,
        confidence: 0.7 + Math.random() * 0.3, // Mock confidence score
        graphsageScore: Math.random() * 100
      }
    }));
    
    // Filter edges to match nodes
    const nodeIds = new Set(updatedNodes.map(n => n.id));
    const updatedEdges = request.edges.filter(
      edge => nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
    
    return {
      updatedNodes,
      updatedEdges,
      confidence: 0.75 + Math.random() * 0.2,
      processingTime,
      cacheKey: this.generateCacheKey(request)
    };
  }

  /**
   * Generate alternative paths using different GraphSage parameters
   */
  async generateAlternativePaths(
    request: GraphSageRecalculationRequest,
    pathCount: number = 5
  ): Promise<GraphSageRecalculationResponse[]> {
    console.log(`RealTimeGraphSageService: Generating ${pathCount} alternative paths`);
    
    const alternatives: GraphSageRecalculationResponse[] = [];
    
    // Generate different parameter combinations
    const parameterSets = this.generateParameterVariations(pathCount);
    
    // Process alternatives in parallel with concurrency limit
    const batchSize = 3;
    for (let i = 0; i < parameterSets.length; i += batchSize) {
      const batch = parameterSets.slice(i, i + batchSize);
      
      const batchPromises = batch.map(async (params) => {
        const altRequest = {
          ...request,
          parameters: { ...request.parameters, ...params }
        };
        
        try {
          return await this.recalculateGraphSage(altRequest, { priority: 'low' });
        } catch (error) {
          console.warn('Alternative path generation failed:', error);
          return null;
        }
      });
      
      const batchResults = await Promise.all(batchPromises);
      alternatives.push(...batchResults.filter(result => result !== null) as GraphSageRecalculationResponse[]);
    }
    
    console.log(`RealTimeGraphSageService: Generated ${alternatives.length} alternative paths`);
    return alternatives;
  }

  /**
   * Generate parameter variations for alternative paths
   */
  private generateParameterVariations(count: number): Record<string, any>[] {
    const variations = [];
    
    const strategies = [
      { focusAreas: ['technical'], priorityWeights: { 'skill': 1.0, 'time': 0.8 } },
      { focusAreas: ['leadership'], priorityWeights: { 'outcome': 1.0, 'expertise': 0.9 } },
      { focusAreas: ['creative'], priorityWeights: { 'innovation': 1.0, 'diversity': 0.8 } },
      { focusAreas: ['analytical'], priorityWeights: { 'logic': 1.0, 'depth': 0.9 } },
      { focusAreas: ['interpersonal'], priorityWeights: { 'social': 1.0, 'communication': 0.8 } }
    ];
    
    for (let i = 0; i < Math.min(count, strategies.length); i++) {
      variations.push(strategies[i]);
    }
    
    return variations;
  }

  /**
   * Cache management methods
   */
  private generateCacheKey(request: GraphSageRecalculationRequest): string {
    const keyData = {
      nodeCount: request.nodes.length,
      edgeCount: request.edges.length,
      depth: request.depth,
      profileHash: this.hashString(request.userProfile),
      parameters: request.parameters
    };
    
    return this.hashString(JSON.stringify(keyData));
  }

  private getCachedResult(key: string): GraphSageRecalculationResponse | null {
    const entry = this.cache.get(key);
    
    if (!entry) return null;
    
    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }

  private setCachedResult(key: string, data: GraphSageRecalculationResponse): void {
    // Clean cache if too large
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    
    this.cache.set(key, {
      key,
      data,
      timestamp: Date.now(),
      ttl: this.CACHE_TTL
    });
  }

  /**
   * Utility methods
   */
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * Clear cache and pending requests
   */
  public clearCache(): void {
    this.cache.clear();
    this.pendingRequests.clear();
    
    // Clear debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
    
    console.log('RealTimeGraphSageService: Cache cleared');
  }

  /**
   * Get cache statistics
   */
  public getCacheStats(): {
    size: number;
    maxSize: number;
    hitRate: number;
    pendingRequests: number;
  } {
    return {
      size: this.cache.size,
      maxSize: this.MAX_CACHE_SIZE,
      hitRate: 0, // Would need to track hits/misses for actual calculation
      pendingRequests: this.pendingRequests.size
    };
  }
}

// Factory function to create service instance with token provider
export const createRealTimeGraphSageService = (getToken: () => Promise<string | null>) => {
  return new RealTimeGraphSageService(getToken);
};

// Default export for backward compatibility (will need token injection)
export const realTimeGraphSageService = new RealTimeGraphSageService();
export type { GraphSageRecalculationRequest, GraphSageRecalculationResponse };
